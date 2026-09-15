#!/usr/bin/env python3
"""Search the structural Cells official docs SQLite FTS5 index.

Why this script exists
----------------------
The skill needs a predictable local search tool that an agent can call instead
of depending on a live RAG service. build_index.py prepares the database; this
script is the query interface for both humans and agents.

The CLI is designed for agents as well as humans:

- JSON mode writes only JSON to stdout.
- Errors are deterministic and go to stderr.
- Search combines FTS5 phases with a small lexical reranker.

How to use it from a fresh checkout
-----------------------------------
1. Build the index:

       python scripts/build_index.py --docs-root /path/to/cells-docs/docs

2. Search current documentation:

       python scripts/search_docs.py --query "how to test a lit component"

3. Search historical documentation:

       python scripts/search_docs.py --query "CLI4 Bridge3 old component command" --area legacy

4. Open an exact document:

       python scripts/search_docs.py --path cli/working-with-applications.md --content

5. Use agent-safe JSON:

       python scripts/search_docs.py --query "IntlMsg locales-app" --format json

What each search phase does
---------------------------
1. Exact phase: title, heading, or path contains the query.
2. Phrase phase: FTS5 phrase search over the raw query tokens.
3. Expanded AND phase: key query terms and Cells synonyms must all match.
4. Expanded OR phase: broad fallback to avoid empty results.
5. Rerank phase: combine bm25, term coverage, source area, exact matches,
   current-vs-legacy intent, and heading locality.

Ranking rule:

    Current docs are preferred for normal Cells work. Historical docs under
    older-versions/ are still indexed and become preferred when the query asks
    for legacy, old, older-versions, CLI4, or Bridge3 material.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import json
import re
import sqlite3
import sys
import unicodedata
from pathlib import Path
from typing import Iterable
from urllib.parse import quote


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
DEFAULT_DB = SKILL_DIR / "assets" / "cells_official_docs.db"
DEFAULT_MANIFEST = SKILL_DIR / "assets" / "manifest.json"
SCHEMA_VERSION = "3"
MAX_LIMIT = 12
MAX_QUERY_LENGTH = 512

TOKEN_RE = re.compile(r"[^\W_]+(?:[-_][^\W_]+)*", re.UNICODE)

# Query expansion is intentionally small and explicit. It covers Cells terms
# that users and docs spell differently, without requiring embeddings.
QUERY_EXPANSIONS = {
    "i18n": ["internationalization", "intlmsg", "locale", "locales-app", "translation"],
    "intlmsg": ["i18n", "internationalization", "locale", "forTesting", "resources"],
    "locales-app": ["i18n", "internationalization", "IntlMsg", "locale"],
    "fortesting": ["forTesting", "IntlMsg", "unit", "testing"],
    "scopedelements": ["scopedElements", "custom", "elements", "reuse", "composition"],
    "widgetmixin": ["WidgetMixin", "widget", "mixin", "component", "application"],
    "emitevent": ["emitEvent", "event", "events", "channel", "communication"],
    "open-wc": ["open", "wc", "open-wc", "fixture", "testing"],
    "@open-wc": ["open", "wc", "fixture", "testing"],
    "sinon": ["spy", "stub", "mock", "testing"],
    "bridge": ["bridge", "channel", "native", "routing", "communication"],
    "channels": ["channel", "channels", "pubsub", "state", "communication"],
    "theming": ["theme", "theming", "tokens", "dark", "mode", "styles"],
    "tokens": ["theming", "theme", "styles", "css", "dark"],
    "spherica": ["spherica", "component", "bbva", "integration"],
    "app:test": ["app", "test", "testing", "unit", "application", "coverage"],
    "component:test": ["component", "test", "testing", "coverage", "web-components"],
    "legacy": ["legacy", "older-versions", "old", "cli4", "bridge3"],
    "older-versions": ["legacy", "older", "old", "cli4", "bridge3"],
    "cli4": ["legacy", "older-versions", "cli4", "bridge3"],
    "bridge3": ["legacy", "older-versions", "cli4", "bridge3"],
}

# Base area priority before query-specific boosts. Legacy starts lower so old
# docs do not answer modern Cells questions unless the query asks for them.
AREA_PRIORITY = {
    "applications": 7.0,
    "web-components": 7.0,
    "cli": 5.0,
    "legacy": -4.0,
    "guides": 1.0,
    "introduction": 1.0,
    "learn": 0.5,
    "help": 0.0,
}


@dataclass
class SearchCandidate:
    """One raw candidate returned by an FTS/exact phase before reranking."""

    row: sqlite3.Row
    phase: str
    bm25: float


class CatalogIntegrityError(RuntimeError):
    """The bundle cannot safely answer a query until it is rebuilt."""


def fail(message: str, code: int = 2) -> None:
    """Exit with a deterministic CLI error on stderr."""
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(code)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_manifest(path: Path) -> dict:
    if not path.is_file():
        raise CatalogIntegrityError(f"manifest is missing: {path.name}")
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CatalogIntegrityError(f"manifest is not valid JSON: {exc}") from exc
    if not isinstance(manifest, dict):
        raise CatalogIntegrityError("manifest must be a JSON object")
    return manifest


def immutable_connect(db_path: Path) -> sqlite3.Connection:
    """Open the packaged index without permitting journals or writes."""
    if not db_path.is_file():
        raise CatalogIntegrityError(f"index database is missing: {db_path.name}")
    uri = f"file:{quote(db_path.resolve().as_posix())}?mode=ro&immutable=1"
    try:
        conn = sqlite3.connect(uri, uri=True)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA query_only = ON")
        return conn
    except sqlite3.DatabaseError as exc:
        raise CatalogIntegrityError(f"could not open index database read-only: {exc}") from exc


def metadata_from_db(conn: sqlite3.Connection) -> dict:
    try:
        rows = conn.execute("SELECT key, value FROM metadata").fetchall()
    except sqlite3.DatabaseError as exc:
        raise CatalogIntegrityError(f"database metadata is unavailable: {exc}") from exc
    metadata: dict[str, object] = {}
    for row in rows:
        try:
            metadata[row["key"]] = json.loads(row["value"])
        except (KeyError, json.JSONDecodeError) as exc:
            raise CatalogIntegrityError("database metadata contains invalid JSON") from exc
    return metadata


def document_fingerprint(documents: Iterable[tuple[str, str]]) -> str:
    digest = hashlib.sha256()
    for path, content_hash in sorted(documents):
        digest.update(path.encode("utf-8"))
        digest.update(content_hash.encode("ascii"))
    return digest.hexdigest()


def validate_bundle(db_path: Path, manifest_path: Path) -> sqlite3.Connection:
    """Verify the package bytes and metadata agree before querying the index."""
    manifest = load_manifest(manifest_path)
    metadata = manifest.get("metadata")
    integrity = manifest.get("integrity")
    docs = manifest.get("docs")
    if not isinstance(metadata, dict) or not isinstance(integrity, dict) or not isinstance(docs, list):
        raise CatalogIntegrityError("manifest is missing metadata, integrity, or docs")
    if metadata.get("schema_version") != SCHEMA_VERSION:
        raise CatalogIntegrityError(f"manifest schema is unsupported; expected {SCHEMA_VERSION}")
    if metadata.get("source_root") != "docs" or not metadata.get("source_revision"):
        raise CatalogIntegrityError("manifest has incomplete portable source provenance")
    if manifest.get("database") != "skills/cells-official-docs-catalog/assets/cells_official_docs.db":
        raise CatalogIntegrityError("manifest has a non-portable database path")
    if integrity.get("algorithm") != "sha256":
        raise CatalogIntegrityError("manifest uses an unsupported integrity algorithm")
    expected_db_hash = integrity.get("database_sha256")
    if not isinstance(expected_db_hash, str) or not re.fullmatch(r"[0-9a-f]{64}", expected_db_hash):
        raise CatalogIntegrityError("manifest is missing integrity.database_sha256")
    if not db_path.is_file() or sha256_file(db_path) != expected_db_hash:
        raise CatalogIntegrityError("database hash does not match the manifest")

    manifest_documents: list[tuple[str, str]] = []
    for item in docs:
        if not isinstance(item, dict) or not isinstance(item.get("path"), str) or not isinstance(item.get("hash"), str):
            raise CatalogIntegrityError("manifest document fingerprint is malformed")
        manifest_documents.append((item["path"], item["hash"]))
    source_fingerprint = document_fingerprint(manifest_documents)
    if metadata.get("content_hash") != source_fingerprint or metadata.get("source_fingerprint") != source_fingerprint:
        raise CatalogIntegrityError("manifest document fingerprint does not match its document list")
    if integrity.get("source_fingerprint") != source_fingerprint:
        raise CatalogIntegrityError("manifest integrity source fingerprint does not match its document list")

    conn = immutable_connect(db_path)
    try:
        db_metadata = metadata_from_db(conn)
        expected_metadata = {
            "schema_version": metadata.get("schema_version"),
            "source_root": metadata.get("source_root"),
            "source_revision": metadata.get("source_revision"),
            "content_hash": metadata.get("content_hash"),
            "source_fingerprint": metadata.get("source_fingerprint"),
            "document_count": manifest.get("document_count"),
            "chunk_count": manifest.get("chunk_count"),
            "legacy_document_count": manifest.get("legacy_document_count"),
        }
        for key, expected in expected_metadata.items():
            if db_metadata.get(key) != expected:
                raise CatalogIntegrityError(f"database metadata.{key} does not match the manifest")
        database_documents = [
            (row["path"], row["content_hash"])
            for row in conn.execute("SELECT path, content_hash FROM documents ORDER BY path")
        ]
        if database_documents != sorted(manifest_documents):
            raise CatalogIntegrityError("database document hashes do not match the manifest")
        if document_fingerprint(database_documents) != source_fingerprint:
            raise CatalogIntegrityError("database document fingerprint does not match the manifest")
        source_paths = conn.execute("SELECT source_path FROM documents UNION SELECT source_path FROM chunks").fetchall()
        if any(Path(row[0]).is_absolute() or not str(row[0]).startswith("docs/") for row in source_paths):
            raise CatalogIntegrityError("database contains non-portable source paths")
        document_count = conn.execute("SELECT count(*) FROM documents").fetchone()[0]
        chunk_count = conn.execute("SELECT count(*) FROM chunks").fetchone()[0]
        fts_count = conn.execute("SELECT count(*) FROM chunks_fts").fetchone()[0]
        if document_count != manifest.get("document_count") or chunk_count != manifest.get("chunk_count") or fts_count != chunk_count:
            raise CatalogIntegrityError("database row counts do not match the manifest")
    except Exception:
        conn.close()
        raise
    return conn


def connect(db_path: Path, manifest_path: Path = DEFAULT_MANIFEST) -> sqlite3.Connection:
    """Compatibility wrapper used by the CLI and callers importing this script."""
    return validate_bundle(db_path, manifest_path)


def tokens(text: str) -> list[str]:
    """Tokenize user text for FTS and lexical reranking."""
    normalized = unicodedata.normalize("NFC", text or "")
    if len(normalized) > MAX_QUERY_LENGTH:
        fail(f"query must be at most {MAX_QUERY_LENGTH} characters")
    found: list[str] = []
    for match in TOKEN_RE.finditer(normalized):
        token = match.group(0).strip("-_").casefold()
        if token:
            found.append(token)
    return found


def unique(items: Iterable[str]) -> list[str]:
    """Preserve order while removing duplicates case-insensitively."""
    seen: set[str] = set()
    output: list[str] = []
    for item in items:
        lowered = item.lower()
        if lowered not in seen:
            seen.add(lowered)
            output.append(item)
    return output


def expanded_terms(query: str) -> list[str]:
    """Add domain synonyms so natural-language queries hit official wording."""
    base = tokens(query)
    additions: list[str] = []
    lowered_query = query.lower()
    for key, values in QUERY_EXPANSIONS.items():
        if key.lower() in lowered_query or key.lower() in base:
            additions.extend(values)
    if "open" in base and "wc" in base:
        additions.extend(QUERY_EXPANSIONS["open-wc"])
    if "app" in base and "test" in base:
        additions.extend(QUERY_EXPANSIONS["app:test"])
    if "component" in base and "test" in base:
        additions.extend(QUERY_EXPANSIONS["component:test"])
    return unique(base + [term.lower() for term in additions])


def quote_fts(term: str) -> str:
    """Escape one term/phrase for SQLite FTS5 MATCH."""
    cleaned = unicodedata.normalize("NFC", term).replace('"', " ").strip()
    return f'"{cleaned}"' if cleaned else ""


def fts_and_query(terms: list[str]) -> str:
    """Build a strict FTS query used after exact/phrase matching."""
    return " AND ".join(quote for quote in (quote_fts(term) for term in terms[:12]) if quote)


def fts_or_query(terms: list[str]) -> str:
    """Build a broad fallback FTS query."""
    return " OR ".join(quote for quote in (quote_fts(term) for term in terms[:24]) if quote)


def like_pattern(text: str) -> str:
    """Create a literal, case-insensitive LIKE pattern for exact lookup."""
    escaped = text.casefold().replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escaped}%"


def like_prefix(text: str) -> str:
    escaped = text.casefold().replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"{escaped}%"


def filters_sql(args: argparse.Namespace, alias: str = "c") -> tuple[str, list[str]]:
    """Convert optional CLI filters into SQL fragments and bound values."""
    clauses: list[str] = []
    values: list[str] = []
    if args.area:
        clauses.append(f"{alias}.area = ?")
        values.append(args.area)
    if args.path_prefix:
        clauses.append(f"{alias}.path LIKE ? ESCAPE '\\'")
        values.append(like_prefix(args.path_prefix))
    if args.kind:
        clauses.append(f"{alias}.kind = ?")
        values.append(args.kind)
    if clauses:
        return " AND " + " AND ".join(clauses), values
    return "", values


def run_fts_phase(
    conn: sqlite3.Connection,
    args: argparse.Namespace,
    phase: str,
    match_query: str,
    candidate_limit: int,
) -> list[SearchCandidate]:
    """Run one FTS5 MATCH phase and return candidates without final ranking."""
    if not match_query:
        return []
    filter_sql, filter_values = filters_sql(args, "c")
    sql = f"""
        SELECT
            c.*,
            bm25(chunks_fts, 3.4, 2.8, 1.8, 1.2, 0.9, 0.7) AS bm25_score,
            snippet(chunks_fts, 5, '[', ']', ' ... ', 36) AS match_snippet
        FROM chunks_fts
        JOIN chunks c ON c.id = chunks_fts.chunk_id
        WHERE chunks_fts MATCH ?{filter_sql}
        ORDER BY bm25_score ASC
        LIMIT ?
    """
    try:
        rows = conn.execute(sql, [match_query, *filter_values, candidate_limit]).fetchall()
    except sqlite3.OperationalError:
        return []
    return [SearchCandidate(row=row, phase=phase, bm25=float(row["bm25_score"])) for row in rows]


def run_exact_phase(
    conn: sqlite3.Connection, args: argparse.Namespace, query: str, candidate_limit: int
) -> list[SearchCandidate]:
    """Find obvious title, heading, or path hits before fuzzy search."""
    filter_sql, filter_values = filters_sql(args, "c")
    pattern = like_pattern(query)
    sql = f"""
        SELECT c.*, 0.0 AS bm25_score, '' AS match_snippet
        FROM chunks c
        WHERE (
            lower(c.title) LIKE ? ESCAPE '\\'
            OR lower(c.heading_path) LIKE ? ESCAPE '\\'
            OR lower(c.path) LIKE ? ESCAPE '\\'
        ){filter_sql}
        LIMIT ?
    """
    rows = conn.execute(sql, [pattern, pattern, pattern, *filter_values, candidate_limit]).fetchall()
    return [SearchCandidate(row=row, phase="exact", bm25=0.0) for row in rows]


def canonical_boost(row: sqlite3.Row, query_terms: set[str]) -> float:
    """Apply Cells-specific source preference on top of lexical search.

    FTS5 is good at matching words but does not know that current docs should
    beat older-versions/ for normal questions, or that old/CLI4/Bridge3 queries
    should prefer historical docs. Those rules live here so they are auditable.
    """
    path = row["path"].lower()
    score = AREA_PRIORITY.get(row["area"], 0.0)
    legacy_intent = bool(
        {"legacy", "old", "older", "older-versions", "cli4", "bridge3"} & query_terms
    )

    if path.startswith("older-versions/"):
        score += 38.0 if legacy_intent else -32.0

    if {"test", "testing", "sinon", "open-wc", "wc"} & query_terms:
        if "web-components/reference/testing" in path:
            score += 28.0
        if path == "cells-applications/testing/unit-testing.md":
            score += 18.0
        elif "cells-applications/testing/e2e-testing" in path:
            score += 4.0
        if ("bridge4-cli5" in path or "migration" in path) and not legacy_intent:
            score -= 16.0

    if "app" in query_terms and {"test", "testing"} & query_terms:
        if path == "cells-applications/testing/unit-testing.md":
            score += 30.0
        if path == "cli/working-with-applications.md":
            score += 58.0
        if path == "cli/working-with-components.md":
            score -= 18.0

    if "component" in query_terms and {"test", "testing"} & query_terms:
        if "web-components/reference/testing" in path:
            score += 24.0
        if path == "cli/working-with-components.md":
            score += 16.0

    if {"i18n", "intlmsg", "internationalization", "locales-app"} & query_terms:
        if path == "cells-applications/internationalization.md":
            score += 42.0

    if {"scopedelements", "scoped-elements"} & query_terms:
        if "custom-elements" in path or "reuse-composition" in path:
            score += 22.0

    if {"widgetmixin", "emitevent", "channels", "bridge"} & query_terms:
        if "state-management/channels" in path:
            score += 18.0
        if "bootstrapping/the-bridge-instance" in path:
            score += 16.0
        if "overview/technical-design" in path:
            score += 12.0

    if {"theming", "tokens", "theme"} & query_terms:
        if "web-components/reference/theming" in path:
            score += 28.0
        if "web-components/reference/styles" in path:
            score += 16.0

    return score


def score_candidate(candidate: SearchCandidate, query: str, terms_for_query: list[str]) -> tuple[float, dict]:
    """Combine FTS score, coverage, exact matches, and source boosts."""
    row = candidate.row
    lowered_query = query.lower()
    query_terms = set(terms_for_query)
    title = row["title"].lower()
    heading = row["heading_path"].lower()
    summary = row["summary"].lower()
    content = row["content"].lower()
    path = row["path"].lower()
    haystack = " ".join([title, heading, summary, content, path])

    matched = sum(1 for term in query_terms if term.lower() in haystack)
    coverage = matched / max(len(query_terms), 1)
    exact = 0.0
    if lowered_query and lowered_query in title:
        exact += 32.0
    if lowered_query and lowered_query in heading:
        exact += 26.0
    if lowered_query and lowered_query in path:
        exact += 22.0
    if lowered_query and lowered_query in content:
        exact += 14.0

    bm25_component = max(0.0, 20.0 - min(abs(candidate.bm25), 20.0))
    phase_bonus = {"exact": 20.0, "phrase": 14.0, "expanded-and": 10.0, "expanded-or": 3.0}.get(
        candidate.phase, 0.0
    )
    locality = max(0.0, 8.0 - (float(row["ordinal"]) * 0.25))
    canonical = canonical_boost(row, query_terms)
    total = bm25_component + phase_bonus + (coverage * 40.0) + exact + canonical + locality

    return total, {
        "total": round(total, 4),
        "bm25": round(candidate.bm25, 4),
        "phase": candidate.phase,
        "coverage": round(coverage, 4),
        "matched_terms": matched,
        "exact_boost": round(exact, 4),
        "canonical_boost": round(canonical, 4),
        "locality_boost": round(locality, 4),
    }


def result_from_candidate(
    candidate: SearchCandidate,
    query: str,
    terms_for_query: list[str],
    include_content: bool,
    include_snippets: bool,
    explain: bool,
) -> dict:
    """Convert a reranked candidate into the stable JSON/Markdown payload."""
    row = candidate.row
    score, score_breakdown = score_candidate(candidate, query, terms_for_query)
    snippet = row["match_snippet"] or make_snippet(row["content"], terms_for_query)
    result = {
        "chunk_id": row["id"],
        "slug": row["slug"],
        "title": row["title"],
        "area": row["area"],
        "path": row["path"],
        "kind": row["kind"],
        "heading": row["heading"],
        "heading_path": row["heading_path"],
        "summary": row["summary"],
        "score": round(score, 4),
    }
    if include_snippets:
        result["snippet"] = snippet
    if explain:
        result["score_breakdown"] = score_breakdown
    if include_content:
        result["content"] = row["content"]
    return result


def make_snippet(content: str, terms_for_query: list[str], width: int = 260) -> str:
    """Create a fallback snippet when SQLite cannot produce one."""
    normalized = re.sub(r"\s+", " ", content).strip()
    lowered = normalized.lower()
    positions = [lowered.find(term.lower()) for term in terms_for_query if lowered.find(term.lower()) >= 0]
    if not positions:
        return normalized[:width]
    start = max(0, min(positions) - 80)
    end = min(len(normalized), start + width)
    prefix = "..." if start else ""
    suffix = "..." if end < len(normalized) else ""
    return prefix + normalized[start:end] + suffix


def search(conn: sqlite3.Connection, args: argparse.Namespace) -> dict:
    """Run all search phases, dedupe candidates, rerank, and return results."""
    query = args.query or ""
    terms_for_query = expanded_terms(query)
    candidate_limit = max(args.limit * 8, 40)
    candidates: dict[int, SearchCandidate] = {}

    strict_phases = [
        *run_exact_phase(conn, args, query, candidate_limit),
        *run_fts_phase(conn, args, "expanded-and", fts_and_query(terms_for_query[:8]), candidate_limit),
        *run_fts_phase(conn, args, "phrase", quote_fts(" ".join(tokens(query))), candidate_limit),
    ]
    # OR is intentionally a fallback. Returning an OR union while a strict
    # phrase/AND answer exists made generic token matches drown out the query.
    phases = strict_phases
    search_strategy = "strict"
    if not strict_phases:
        phases = [*run_fts_phase(conn, args, "expanded-or", fts_or_query(terms_for_query), candidate_limit)]
        search_strategy = "or_fallback"

    for candidate in phases:
        existing = candidates.get(candidate.row["id"])
        if existing is None:
            candidates[candidate.row["id"]] = candidate
            continue
        existing_score, _ = score_candidate(existing, query, terms_for_query)
        candidate_score, _ = score_candidate(candidate, query, terms_for_query)
        if candidate_score > existing_score:
            candidates[candidate.row["id"]] = candidate

    ranked = sorted(
        candidates.values(),
        key=lambda candidate: score_candidate(candidate, query, terms_for_query)[0],
        reverse=True,
    )[: args.limit]

    return {
        "status": "ok",
        "query": query,
        "expanded_terms": terms_for_query,
        "search_strategy": search_strategy,
        "count": len(ranked),
        "results": [
            result_from_candidate(
                candidate,
                query,
                terms_for_query,
                include_content=args.content,
                include_snippets=not args.no_snippets,
                explain=args.explain,
            )
            for candidate in ranked
        ],
    }


def by_topic(conn: sqlite3.Connection, args: argparse.Namespace) -> dict:
    """Open a document by generated slug."""
    row = conn.execute("SELECT * FROM documents WHERE slug = ?", (args.topic,)).fetchone()
    if not row:
        return {"status": "not_found", "topic": args.topic, "results": []}
    chunks = conn.execute(
        "SELECT * FROM chunks WHERE slug = ? ORDER BY ordinal ASC", (args.topic,)
    ).fetchall()
    return document_payload(row, chunks, args.content)


def by_path(conn: sqlite3.Connection, args: argparse.Namespace) -> dict:
    """Open a document by its relative docs path."""
    row = conn.execute("SELECT * FROM documents WHERE path = ?", (args.path,)).fetchone()
    if not row:
        return {"status": "not_found", "path": args.path, "results": []}
    chunks = conn.execute(
        "SELECT * FROM chunks WHERE path = ? ORDER BY ordinal ASC", (args.path,)
    ).fetchall()
    return document_payload(row, chunks, args.content)


def document_payload(row: sqlite3.Row, chunks: list[sqlite3.Row], include_content: bool) -> dict:
    """Build the topic/path response shared by --topic and --path."""
    payload_chunks = []
    for chunk in chunks:
        payload = {
            "chunk_id": chunk["id"],
            "kind": chunk["kind"],
            "heading": chunk["heading"],
            "heading_path": chunk["heading_path"],
            "summary": chunk["summary"],
            "word_count": chunk["word_count"],
        }
        if include_content:
            payload["content"] = chunk["content"]
        payload_chunks.append(payload)
    return {
        "status": "ok",
        "document": {
            "slug": row["slug"],
            "title": row["title"],
            "area": row["area"],
            "path": row["path"],
            "content_hash": row["content_hash"],
            "word_count": row["word_count"],
            "chunk_count": row["chunk_count"],
            "code_languages": json.loads(row["code_languages"]),
        },
        "chunks": payload_chunks,
    }


def stats(conn: sqlite3.Connection) -> dict:
    """Return index health, metadata, area counts, and legacy coverage."""
    metadata = {}
    for row in conn.execute("SELECT key, value FROM metadata ORDER BY key"):
        try:
            metadata[row["key"]] = json.loads(row["value"])
        except json.JSONDecodeError:
            metadata[row["key"]] = row["value"]
    areas = [
        {"area": row["area"], "documents": row["documents"], "chunks": row["chunks"]}
        for row in conn.execute(
            """
            SELECT d.area, count(DISTINCT d.id) AS documents, count(c.id) AS chunks
            FROM documents d
            JOIN chunks c ON c.document_id = d.id
            GROUP BY d.area
            ORDER BY d.area
            """
        )
    ]
    legacy_indexed = conn.execute(
        "SELECT count(*) AS count FROM documents WHERE path LIKE 'older-versions/%'"
    ).fetchone()["count"]
    return {
        "status": "ok",
        "metadata": metadata,
        "areas": areas,
        "legacy_indexed": legacy_indexed,
    }


def list_areas(conn: sqlite3.Connection) -> dict:
    """Return the available --area filter values."""
    return {
        "status": "ok",
        "areas": [
            {"area": row["area"], "documents": row["documents"]}
            for row in conn.execute(
                "SELECT area, count(*) AS documents FROM documents GROUP BY area ORDER BY area"
            )
        ],
    }


def print_json(payload: dict) -> None:
    """Print machine-readable output only; no extra logs on stdout."""
    print(json.dumps(payload, indent=2, ensure_ascii=True))


def print_markdown(payload: dict) -> None:
    """Render the same payload as concise human-readable Markdown."""
    status = payload.get("status")
    if "results" in payload and "query" in payload:
        print("## Cells Official Docs Results\n")
        print(f"Query: `{payload['query']}`")
        if payload.get("expanded_terms"):
            print(f"Expanded terms: `{', '.join(payload['expanded_terms'])}`")
        print()
        if not payload["results"]:
            print("No matches found.")
            return
        for index, result in enumerate(payload["results"], start=1):
            print(f"### {index}. `{result['slug']}`")
            print(f"- Title: {result['title']}")
            print(f"- Source: `{result['path']}`")
            print(f"- Area: {result['area']}")
            print(f"- Heading: {result['heading_path']}")
            print(f"- Score: {result['score']}")
            if result.get("summary"):
                print(f"- Summary: {result['summary']}")
            if result.get("snippet"):
                print(f"- Snippet: {result['snippet']}")
            if result.get("score_breakdown"):
                print(f"- Explain: `{json.dumps(result['score_breakdown'], ensure_ascii=True)}`")
            if result.get("content"):
                print("\n```markdown")
                print(result["content"])
                print("```")
            print()
        return

    if "document" in payload:
        if status != "ok":
            print(f"Document not found: `{payload.get('topic') or payload.get('path')}`")
            return
        doc = payload["document"]
        print(f"## Cells Official Topic: `{doc['slug']}`\n")
        print(f"- Title: {doc['title']}")
        print(f"- Area: {doc['area']}")
        print(f"- Source: `{doc['path']}`")
        print(f"- Chunks: {doc['chunk_count']}\n")
        for chunk in payload["chunks"]:
            print(f"### {chunk['heading_path']}")
            if chunk.get("summary"):
                print(f"{chunk['summary']}\n")
            if chunk.get("content"):
                print("```markdown")
                print(chunk["content"])
                print("```\n")
        return

    if "areas" in payload and "metadata" not in payload:
        print("## Cells Official Docs Areas\n")
        for area in payload["areas"]:
            print(f"- `{area['area']}`: {area['documents']} documents")
        return

    if "metadata" in payload:
        print("## Cells Official Docs Index Stats\n")
        meta = payload["metadata"]
        print(f"- Schema: {meta.get('schema_version')}")
        print(f"- Generated: {meta.get('generated_at')}")
        print(f"- Source root: `{meta.get('source_root')}`")
        print(f"- Documents: {meta.get('document_count')}")
        print(f"- Chunks: {meta.get('chunk_count')}")
        print(f"- Legacy indexed: {payload.get('legacy_indexed')}")
        print(f"- Skipped: `{json.dumps(meta.get('skipped'), ensure_ascii=True)}`\n")
        for area in payload["areas"]:
            print(f"- `{area['area']}`: {area['documents']} documents, {area['chunks']} chunks")
        return

    print_json(payload)


def parse_args() -> argparse.Namespace:
    """Define the public search CLI and examples for new users."""
    epilog = """
Examples:
  python scripts/search_docs.py --query "how to test a lit component with sinon"
  python scripts/search_docs.py --query "CLI4 Bridge3 old app command" --area legacy
  python scripts/search_docs.py --query "IntlMsg locales-app forTesting" --format json
  python scripts/search_docs.py --path cli/working-with-applications.md --content
  python scripts/search_docs.py --stats

Exit codes:
  0  command succeeded
  1  requested topic/path was not found
  2  invalid input, missing DB, or unsupported index schema
"""
    parser = argparse.ArgumentParser(
        description="Search official Cells docs.",
        epilog=epilog,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    selector = parser.add_mutually_exclusive_group(required=True)
    selector.add_argument("--query", help="Natural-language search query")
    selector.add_argument("--topic", help="Document slug to open")
    selector.add_argument("--path", help="Relative documentation path to open")
    selector.add_argument("--list-areas", action="store_true", help="List indexed areas")
    selector.add_argument("--stats", action="store_true", help="Show index statistics")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB, help="SQLite index path")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST, help="Bundled manifest path")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    parser.add_argument("--json", action="store_true", help="Legacy alias for --format json")
    parser.add_argument("--area", help="Filter search results by indexed area")
    parser.add_argument("--path-prefix", help="Filter search results by relative path prefix")
    parser.add_argument("--kind", choices=("intro", "section", "document"), help="Filter chunk kind")
    parser.add_argument("--limit", type=int, default=8, help="Maximum search results")
    parser.add_argument("--content", "--detail", dest="content", action="store_true", help="Include full chunk content")
    parser.add_argument("--no-snippets", action="store_true", help="Do not include snippets")
    parser.add_argument("--explain", action="store_true", help="Include lexical score breakdown")
    args = parser.parse_args()
    if args.json:
        args.format = "json"
    if not 1 <= args.limit <= MAX_LIMIT:
        parser.error(f"--limit must be between 1 and {MAX_LIMIT}")
    return args


def main() -> int:
    """CLI entry point."""
    args = parse_args()
    if args.query and not tokens(args.query):
        fail("query must include at least one Unicode letter or number")
    try:
        conn = connect(args.db.resolve(), args.manifest.resolve())
    except (CatalogIntegrityError, OSError, sqlite3.DatabaseError) as exc:
        fail(
            "official docs catalog is stale or corrupt: "
            f"{exc}. Rebuild explicitly with scripts/build_index.py --docs-root <docs-dir>."
        )
    try:
        if args.query:
            payload = search(conn, args)
        elif args.topic:
            payload = by_topic(conn, args)
        elif args.path:
            payload = by_path(conn, args)
        elif args.list_areas:
            payload = list_areas(conn)
        else:
            payload = stats(conn)
    finally:
        conn.close()

    if args.format == "json":
        print_json(payload)
    else:
        print_markdown(payload)
    return 1 if payload.get("status") == "not_found" else 0


if __name__ == "__main__":
    raise SystemExit(main())
