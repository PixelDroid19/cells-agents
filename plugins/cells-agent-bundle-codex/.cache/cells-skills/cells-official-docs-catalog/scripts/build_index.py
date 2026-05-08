#!/usr/bin/env python3
"""Build a structural SQLite FTS5 index for official Cells Markdown docs.

Why this script exists
----------------------
The skill needs fast, offline documentation lookup without a RAG service or MCP
server. This script turns a Markdown documentation tree into two portable
artifacts:

* assets/cells_official_docs.db: SQLite tables plus an FTS5 search index.
* assets/manifest.json: provenance, counts, hashes, and indexed file list.

How to replicate it from a fresh checkout
-----------------------------------------
1. Put the official Cells docs somewhere on disk. The directory must contain
   Markdown files such as cells-applications/*.md, cli/*.md, web-components/*.md,
   and optionally older-versions/*.md.
2. Run one of:

       python scripts/build_index.py --docs-root /path/to/cells-docs/docs
       CELLS_OFFICIAL_DOCS_ROOT=/path/to/cells-docs/docs python scripts/build_index.py
       python scripts/build_index.py --docs-root ./docs --db /tmp/cells.db --manifest /tmp/cells.json

3. Use search_docs.py against the generated database.

Source resolution order
-----------------------
The indexer is self-contained and path-neutral. It resolves the source docs
directory in this order:

1. --docs-root
2. CELLS_OFFICIAL_DOCS_ROOT
3. docs/ beside this skill

What each phase does
--------------------
1. Discover Markdown files under the docs root.
2. Skip only non-documentation files such as assets/ and hidden files.
3. Classify each file into an area (applications, cli, web-components, legacy).
4. Parse Markdown headings outside code fences.
5. Split each file into structural chunks by H1/H2/H3 boundaries.
6. Store document metadata, chunk metadata, and FTS5 searchable text.
7. Atomically replace the DB and manifest only after the build succeeds.

Every run replaces the target database and manifest from scratch so refreshed
documentation cannot leave stale rows behind. The script indexes all Markdown
documentation, including historical docs under older-versions/. Current-vs-old
ranking is handled by search_docs.py, not by dropping source material.
"""

from __future__ import annotations

import argparse
import hashlib
from datetime import datetime, timezone
import json
import os
import re
import sqlite3
import sys
from pathlib import Path
from tempfile import NamedTemporaryFile


# Paths are derived from this file so the script can be copied with the skill
# and run from any working directory.
SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
SCHEMA_VERSION = "2"
DEFAULT_DB = SKILL_DIR / "assets" / "cells_official_docs.db"
DEFAULT_MANIFEST = SKILL_DIR / "assets" / "manifest.json"
LOCAL_DOCS_DIR = SKILL_DIR / "docs"
ENV_DOCS_ROOT = "CELLS_OFFICIAL_DOCS_ROOT"

# Regexes are intentionally simple. We only need enough Markdown structure to
# avoid indexing whole files as one blob; we do not need a full Markdown parser.
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
FENCE_RE = re.compile(r"^\s*(```|~~~)\s*([A-Za-z0-9_+.-]*)")
HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.S)
NON_WORD_RE = re.compile(r"[^A-Za-z0-9_@:/.-]+")

# Top-level folders become search filters. older-versions/ is kept as area
# "legacy" so old Cells stacks are searchable without competing with current
# docs unless search_docs.py detects legacy intent.
AREA_LABELS = {
    "cells-applications": "applications",
    "cli": "cli",
    "guides": "guides",
    "help": "help",
    "introduction": "introduction",
    "learn": "learn",
    "older-versions": "legacy",
    "web-components": "web-components",
}

STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "how",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "the",
    "to",
    "with",
}


def fail(message: str, code: int = 2) -> None:
    """Exit with a deterministic CLI error on stderr."""
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(code)


def utc_now() -> str:
    """Return a compact UTC timestamp for manifests and DB metadata."""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def resolve_docs_root(raw_docs_root: str | None) -> Path:
    """Resolve the documentation source without hardcoding a local path.

    Replication rule: a new user only needs either --docs-root, the environment
    variable, or a docs/ folder beside this script's parent skill directory.
    """
    candidates: list[tuple[str, Path]] = []
    if raw_docs_root:
        candidates.append(("--docs-root", Path(raw_docs_root).expanduser()))
    env_value = os.environ.get(ENV_DOCS_ROOT)
    if env_value:
        candidates.append((ENV_DOCS_ROOT, Path(env_value).expanduser()))
    candidates.append(("skill-local docs/", LOCAL_DOCS_DIR))

    for source, candidate in candidates:
        resolved = candidate.resolve()
        if resolved.is_dir():
            return resolved
        if raw_docs_root and source == "--docs-root":
            fail(f"--docs-root does not exist or is not a directory: {resolved}")
        if env_value and source == ENV_DOCS_ROOT:
            fail(f"{ENV_DOCS_ROOT} does not exist or is not a directory: {resolved}")

    fail(
        "could not find docs directory; pass --docs-root, set "
        f"{ENV_DOCS_ROOT}, or add docs/ beside the skill"
    )


def repo_root() -> Path:
    """Find the bundle root used only for readable relative manifest paths."""
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "skills").is_dir():
            return parent
    return SKILL_DIR


def safe_relative(path: Path, base: Path) -> str:
    """Return a relative path when possible, otherwise an absolute path."""
    try:
        return path.resolve().relative_to(base.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def read_text(path: Path) -> str:
    """Read Markdown as UTF-8, the expected encoding for the docs snapshot."""
    return path.read_text(encoding="utf-8")


def slug_for(rel_path: Path) -> str:
    """Convert docs/foo/bar.md into stable slug docs-foo-bar."""
    return rel_path.with_suffix("").as_posix().replace("/", "-")


def area_for(rel_path: Path) -> str:
    """Map the first path segment to an index area/filter name."""
    first = rel_path.parts[0] if rel_path.parts else ""
    return AREA_LABELS.get(first, first or "root")


def should_skip(rel_path: Path) -> tuple[bool, str | None]:
    """Skip files that are not useful documentation pages.

    Historical docs are not skipped. They are indexed under area "legacy".
    """
    parts = set(rel_path.parts)
    if "assets" in parts:
        return True, "asset"
    if rel_path.name.startswith("."):
        return True, "hidden"
    return False, None


def content_hash(text: str) -> str:
    """Hash raw document content for reproducible manifest provenance."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def normalize_space(text: str) -> str:
    """Collapse whitespace for titles, summaries, and keyword text."""
    return re.sub(r"\s+", " ", text).strip()


def plain_text(markdown: str) -> str:
    """Create a short plain-text view for summaries and keywords.

    Code fences are removed here because summaries should describe the section,
    while the original chunk content is still preserved in the database.
    """
    text = HTML_COMMENT_RE.sub(" ", markdown)
    text = re.sub(r"```.*?```", " ", text, flags=re.S)
    text = re.sub(r"~~~.*?~~~", " ", text, flags=re.S)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"!\[[^\]]*\]\([^)]+\)", " ", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"^#{1,6}\s+", " ", text, flags=re.M)
    text = re.sub(r"^[>\-*+]\s+", " ", text, flags=re.M)
    return normalize_space(text)


def extract_title(content: str, fallback: str) -> str:
    """Use the first H1 as document title; fall back to the slug."""
    for line in content.splitlines():
        match = HEADING_RE.match(line)
        if match and len(match.group(1)) == 1:
            return normalize_space(match.group(2))
    return fallback.replace("-", " ").replace("_", " ").title()


def extract_summary(markdown: str) -> str:
    """Pick the first readable paragraph as a compact chunk summary."""
    for block in re.split(r"\n\s*\n", markdown):
        cleaned = plain_text(block)
        if cleaned and not cleaned.startswith("#"):
            return cleaned[:280]
    return ""


def extract_code_languages(markdown: str) -> list[str]:
    """Collect fenced-code language hints for metadata and future filters."""
    languages: set[str] = set()
    for line in markdown.splitlines():
        match = FENCE_RE.match(line)
        if match and match.group(2):
            languages.add(match.group(2).lower())
    return sorted(languages)


def markdown_heading_events(content: str) -> list[dict]:
    """Return Markdown headings with byte offsets, ignoring code fences.

    This is the core structural parsing step. It deliberately ignores headings
    inside ``` or ~~~ blocks so examples do not split the documentation.
    """
    events: list[dict] = []
    in_fence = False
    fence_marker = ""
    offset = 0

    for raw_line in content.splitlines(keepends=True):
        line = raw_line.rstrip("\n\r")
        fence = FENCE_RE.match(line)
        if fence:
            marker = fence.group(1)
            if not in_fence:
                in_fence = True
                fence_marker = marker
            elif marker == fence_marker:
                in_fence = False
                fence_marker = ""
        if not in_fence:
            heading = HEADING_RE.match(line)
            if heading:
                level = len(heading.group(1))
                events.append(
                    {
                        "level": level,
                        "title": normalize_space(heading.group(2)),
                        "start": offset,
                    }
                )
        offset += len(raw_line)
    return events


def split_chunks(content: str, doc_title: str) -> list[dict]:
    """Split one Markdown document into searchable structural chunks.

    Chunking at H1/H2/H3 keeps results focused enough for snippets while still
    preserving context. Deeper headings remain inside their parent chunk so the
    index does not become too fragmented.
    """
    headings = markdown_heading_events(content)
    structural = [event for event in headings if event["level"] <= 3]

    if structural and structural[0]["level"] == 1:
        first = structural[0]
        next_start = structural[1]["start"] if len(structural) > 1 else len(content)
        intro = content[first["start"]:next_start].strip()
        structural = structural[1:]
    else:
        intro = content[: structural[0]["start"]].strip() if structural else content.strip()

    chunks: list[dict] = []
    if intro:
        chunks.append(
            {
                "kind": "intro",
                "level": 1,
                "heading": doc_title,
                "heading_path": doc_title,
                "content": intro,
            }
        )

    heading_stack: dict[int, str] = {1: doc_title}
    for index, event in enumerate(structural):
        start = event["start"]
        end = structural[index + 1]["start"] if index + 1 < len(structural) else len(content)
        chunk_content = content[start:end].strip()
        if not chunk_content:
            continue
        level = event["level"]
        heading_stack[level] = event["title"]
        for stale_level in range(level + 1, 7):
            heading_stack.pop(stale_level, None)
        path_parts = [
            heading_stack[known_level]
            for known_level in sorted(heading_stack)
            if known_level <= level and heading_stack.get(known_level)
        ]
        chunks.append(
            {
                "kind": "section",
                "level": level,
                "heading": event["title"],
                "heading_path": " > ".join(path_parts),
                "content": chunk_content,
            }
        )

    if not chunks:
        chunks.append(
            {
                "kind": "document",
                "level": 1,
                "heading": doc_title,
                "heading_path": doc_title,
                "content": content.strip(),
            }
        )
    return chunks


def keyword_terms(*texts: str) -> str:
    """Derive lightweight keyword text inserted into the FTS index."""
    terms: set[str] = set()
    for text in texts:
        for raw in NON_WORD_RE.split(text):
            term = raw.strip("._-/").lower()
            if len(term) < 3 or term in STOPWORDS:
                continue
            terms.add(term)
    return " ".join(sorted(terms))


def create_schema(conn: sqlite3.Connection) -> None:
    """Create the complete schema from scratch in a temporary database.

    Tables:
      metadata  build provenance and counts
      documents one row per Markdown file
      chunks    one row per structural section
      chunks_fts FTS5 searchable columns tied back to chunks.id
    """
    # Ordinary tables store rich metadata. chunks_fts stores search text plus
    # row ids so search_docs.py can join back to structured data.
    conn.executescript(
        """
        PRAGMA journal_mode = WAL;

        CREATE TABLE metadata (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );

        CREATE TABLE documents (
            id INTEGER PRIMARY KEY,
            slug TEXT NOT NULL UNIQUE,
            title TEXT NOT NULL,
            area TEXT NOT NULL,
            path TEXT NOT NULL UNIQUE,
            source_path TEXT NOT NULL,
            content_hash TEXT NOT NULL,
            word_count INTEGER NOT NULL,
            heading_count INTEGER NOT NULL,
            chunk_count INTEGER NOT NULL,
            code_languages TEXT NOT NULL
        );

        CREATE TABLE chunks (
            id INTEGER PRIMARY KEY,
            document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
            slug TEXT NOT NULL,
            title TEXT NOT NULL,
            area TEXT NOT NULL,
            path TEXT NOT NULL,
            source_path TEXT NOT NULL,
            kind TEXT NOT NULL,
            heading TEXT NOT NULL,
            heading_path TEXT NOT NULL,
            ordinal INTEGER NOT NULL,
            level INTEGER NOT NULL,
            summary TEXT NOT NULL,
            content TEXT NOT NULL,
            keywords TEXT NOT NULL,
            word_count INTEGER NOT NULL,
            char_count INTEGER NOT NULL,
            code_languages TEXT NOT NULL
        );

        CREATE VIRTUAL TABLE chunks_fts USING fts5(
            chunk_id UNINDEXED,
            document_id UNINDEXED,
            title,
            heading_path,
            summary,
            content,
            keywords,
            path,
            tokenize = 'porter unicode61 remove_diacritics 2'
        );

        CREATE INDEX idx_chunks_slug ON chunks(slug);
        CREATE INDEX idx_chunks_path ON chunks(path);
        CREATE INDEX idx_chunks_area ON chunks(area);
        CREATE INDEX idx_documents_area ON documents(area);
        """
    )


def insert_metadata(conn: sqlite3.Connection, metadata: dict[str, object]) -> None:
    """Store metadata values as JSON so numeric types survive in JSON output."""
    for key, value in metadata.items():
        conn.execute(
            "INSERT INTO metadata (key, value) VALUES (?, ?)",
            (key, json.dumps(value, ensure_ascii=True)),
        )


def build_database(db_path: Path, docs_root: Path, source_revision: str | None) -> dict:
    """Build the SQLite database and return the manifest payload.

    The DB is first written to a temporary file in the destination directory and
    then moved into place. That makes rebuilds safe: a failed run cannot corrupt
    the currently usable bundled index.
    """
    all_markdown = sorted(docs_root.rglob("*.md"))
    skipped_counts = {"asset": 0, "hidden": 0, "empty": 0}
    indexed_docs: list[dict] = []
    aggregate_hash = hashlib.sha256()
    legacy_document_count = 0

    db_path.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile(prefix=f"{db_path.name}.", suffix=".tmp", dir=db_path.parent, delete=False) as tmp:
        tmp_db_path = Path(tmp.name)

    try:
        conn = sqlite3.connect(tmp_db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        create_schema(conn)

        total_chunks = 0
        for path in all_markdown:
            rel_path = path.relative_to(docs_root)
            skip, reason = should_skip(rel_path)
            if skip:
                skipped_counts[reason or "hidden"] += 1
                continue

            content = read_text(path)
            if not content.strip():
                skipped_counts["empty"] += 1
                continue

            doc_slug = slug_for(rel_path)
            title = extract_title(content, doc_slug)
            area = area_for(rel_path)
            if area == "legacy":
                legacy_document_count += 1
            digest = content_hash(content)
            code_languages = extract_code_languages(content)
            chunks = split_chunks(content, title)
            aggregate_hash.update(rel_path.as_posix().encode("utf-8"))
            aggregate_hash.update(digest.encode("ascii"))

            cursor = conn.execute(
                """
                INSERT INTO documents
                (slug, title, area, path, source_path, content_hash, word_count,
                 heading_count, chunk_count, code_languages)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    doc_slug,
                    title,
                    area,
                    rel_path.as_posix(),
                    str(path.resolve()),
                    digest,
                    len(content.split()),
                    len(markdown_heading_events(content)),
                    len(chunks),
                    json.dumps(code_languages, ensure_ascii=True),
                ),
            )
            document_id = int(cursor.lastrowid)

            for ordinal, chunk in enumerate(chunks, start=1):
                chunk_content = chunk["content"]
                summary = extract_summary(chunk_content)
                languages = extract_code_languages(chunk_content)
                keywords = keyword_terms(title, chunk["heading_path"], rel_path.as_posix(), summary)
                cursor = conn.execute(
                    """
                    INSERT INTO chunks
                    (document_id, slug, title, area, path, source_path, kind,
                     heading, heading_path, ordinal, level, summary, content,
                     keywords, word_count, char_count, code_languages)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        document_id,
                        doc_slug,
                        title,
                        area,
                        rel_path.as_posix(),
                        str(path.resolve()),
                        chunk["kind"],
                        chunk["heading"],
                        chunk["heading_path"],
                        ordinal,
                        int(chunk["level"]),
                        summary,
                        chunk_content,
                        keywords,
                        len(chunk_content.split()),
                        len(chunk_content),
                        json.dumps(languages, ensure_ascii=True),
                    ),
                )
                chunk_id = int(cursor.lastrowid)
                conn.execute(
                    """
                    INSERT INTO chunks_fts
                    (chunk_id, document_id, title, heading_path, summary, content, keywords, path)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        chunk_id,
                        document_id,
                        title,
                        chunk["heading_path"],
                        summary,
                        chunk_content,
                        keywords,
                        rel_path.as_posix(),
                    ),
                )
                total_chunks += 1

            indexed_docs.append(
                {
                    "slug": doc_slug,
                    "title": title,
                    "area": area,
                    "path": rel_path.as_posix(),
                    "chunk_count": len(chunks),
                    "hash": digest,
                }
            )

        if not indexed_docs:
            fail(f"no indexable markdown files found under {docs_root}")

        metadata = {
            "schema_version": SCHEMA_VERSION,
            "generated_at": utc_now(),
            "source_root": str(docs_root),
            "source_revision": source_revision or "external-snapshot",
            "document_count": len(indexed_docs),
            "chunk_count": total_chunks,
            "legacy_document_count": legacy_document_count,
            "skipped": skipped_counts,
            "content_hash": aggregate_hash.hexdigest(),
        }
        insert_metadata(conn, metadata)
        conn.commit()
        conn.close()
        tmp_db_path.replace(db_path)

        return {
            **metadata,
            "database": str(db_path),
            "docs": indexed_docs,
            "total_markdown_files": len(all_markdown),
        }
    except Exception:
        try:
            tmp_db_path.unlink(missing_ok=True)
        finally:
            raise


def write_manifest(manifest_path: Path, payload: dict, root: Path) -> None:
    """Write manifest.json atomically after the database build succeeds."""
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest = {
        "metadata": {
            "schema_version": payload["schema_version"],
            "generated_at": payload["generated_at"],
            "generator": safe_relative(Path(__file__), root),
            "source_root": payload["source_root"],
            "source_revision": payload["source_revision"],
            "content_hash": payload["content_hash"],
        },
        "database": safe_relative(Path(payload["database"]), root),
        "document_count": payload["document_count"],
        "chunk_count": payload["chunk_count"],
        "legacy_document_count": payload["legacy_document_count"],
        "total_markdown_files": payload["total_markdown_files"],
        "skipped": payload["skipped"],
        "docs": payload["docs"],
    }

    with NamedTemporaryFile(
        "w",
        prefix=f"{manifest_path.name}.",
        suffix=".tmp",
        dir=manifest_path.parent,
        delete=False,
        encoding="utf-8",
    ) as tmp:
        json.dump(manifest, tmp, indent=2, ensure_ascii=True)
        tmp.write("\n")
        tmp_manifest_path = Path(tmp.name)
    tmp_manifest_path.replace(manifest_path)


def parse_args() -> argparse.Namespace:
    """Define the small public CLI used by humans and automation."""
    epilog = """
Examples:
  python scripts/build_index.py --docs-root /path/to/cells-docs/docs
  CELLS_OFFICIAL_DOCS_ROOT=/path/to/cells-docs/docs python scripts/build_index.py
  python scripts/build_index.py --docs-root ./docs --db /tmp/cells.db --manifest /tmp/cells.json

Notes:
  - The target DB and manifest are replaced atomically on every successful run.
  - All Markdown docs are indexed, including older-versions/ historical docs.
  - Use search_docs.py filters/ranking to prefer current or historical docs.
"""
    parser = argparse.ArgumentParser(
        description="Build a clean SQLite FTS5 index for official Cells docs.",
        epilog=epilog,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--docs-root", help="Markdown docs root to index")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB, help="Output SQLite database")
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_MANIFEST,
        help="Output manifest JSON",
    )
    parser.add_argument("--source-revision", help="Source revision or snapshot id")
    return parser.parse_args()


def main() -> int:
    """CLI entry point."""
    args = parse_args()
    docs_root = resolve_docs_root(args.docs_root)
    root = repo_root()
    payload = build_database(args.db.resolve(), docs_root, args.source_revision)
    write_manifest(args.manifest.resolve(), payload, root)
    print(
        json.dumps(
            {
                "status": "ok",
                "schema_version": payload["schema_version"],
                "documents": payload["document_count"],
                "chunks": payload["chunk_count"],
                "legacy_documents": payload["legacy_document_count"],
                "skipped": payload["skipped"],
                "database": str(args.db.resolve()),
                "manifest": str(args.manifest.resolve()),
            },
            indent=2,
            ensure_ascii=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
