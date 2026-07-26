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
import json
import re
import sqlite3
import sys
from pathlib import Path
from typing import Iterable


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
DEFAULT_DB = SKILL_DIR / "assets" / "cells_official_docs.db"
SCHEMA_VERSION = "2"

TOKEN_RE = re.compile(r"[A-Za-z0-9_@:+.-]+")

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


def fail(message: str, code: int = 2) -> None:
    """Exit with a deterministic CLI error on stderr."""
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(code)


def connect(db_path: Path) -> sqlite3.Connection:
    """Open the SQLite index and verify it was built by the current schema."""
    if not db_path.exists():
        fail(f"index database not found: {db_path}")
    conn = sqlite3.connect(
        f"{db_path.resolve().as_uri()}?mode=ro&immutable=1",
        uri=True,
    )
    conn.row_factory = sqlite3.Row
    try:
        version_row = conn.execute(
            "SELECT value FROM metadata WHERE key = 'schema_version'"
        ).fetchone()
    except sqlite3.DatabaseError as exc:
        conn.close()
        fail(f"invalid Cells docs index: {exc}")
    version = json.loads(version_row["value"]) if version_row else None
    if version != SCHEMA_VERSION:
        conn.close()
        fail(
            f"unsupported index schema; expected {SCHEMA_VERSION}. "
            "Rebuild with scripts/build_index.py"
        )
    return conn


def tokens(text: str) -> list[str]:
    """Tokenize user text for FTS and lexical reranking."""
    found: list[str] = []
    for match in TOKEN_RE.finditer(text):
        token = match.group(0).strip("._-/").lower()
        if len(token) >= 2:
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
    cleaned = re.sub(r'"', " ", term)
    cleaned = re.sub(r"[^A-Za-z0-9_@:+.-]+", " ", cleaned).strip()
    return f'"{cleaned}"' if cleaned else ""


def fts_and_query(terms: list[str]) -> str:
    """Build a strict FTS query used after exact/phrase matching."""
    return " AND ".join(quote for quote in (quote_fts(term) for term in terms[:12]) if quote)


def fts_or_query(terms: list[str]) -> str:
    """Build a broad fallback FTS query."""
    return " OR ".join(quote for quote in (quote_fts(term) for term in terms[:24]) if quote)


def like_pattern(text: str) -> str:
    """Create a case-insensitive LIKE pattern for exact path/title lookup."""
    return f"%{text.lower()}%"


def filters_sql(args: argparse.Namespace, alias: str = "c") -> tuple[str, list[str]]:
    """Convert optional CLI filters into SQL fragments and bound values."""
    clauses: list[str] = []
    values: list[str] = []
    if args.area:
        clauses.append(f"{alias}.area = ?")
        values.append(args.area)
    if args.path_prefix:
        clauses.append(f"{alias}.path LIKE ?")
        values.append(f"{args.path_prefix}%")
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
            lower(c.title) LIKE ?
            OR lower(c.heading_path) LIKE ?
            OR lower(c.path) LIKE ?
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

    phases = [
        *run_exact_phase(conn, args, query, candidate_limit),
        *run_fts_phase(conn, args, "phrase", quote_fts(" ".join(tokens(query))), candidate_limit),
        *run_fts_phase(conn, args, "expanded-and", fts_and_query(terms_for_query[:8]), candidate_limit),
        *run_fts_phase(conn, args, "expanded-or", fts_or_query(terms_for_query), candidate_limit),
    ]

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
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    parser.add_argument("--area", help="Filter search results by indexed area")
    parser.add_argument("--path-prefix", help="Filter search results by relative path prefix")
    parser.add_argument("--kind", choices=("intro", "section", "document"), help="Filter chunk kind")
    parser.add_argument("--limit", type=int, default=8, help="Maximum search results")
    parser.add_argument("--content", action="store_true", help="Include chunk content")
    parser.add_argument("--no-snippets", action="store_true", help="Do not include snippets")
    parser.add_argument("--explain", action="store_true", help="Include lexical score breakdown")
    return parser.parse_args()


def main() -> int:
    """CLI entry point."""
    args = parse_args()
    if args.limit < 1:
        fail("--limit must be greater than zero")
    conn = connect(args.db.resolve())
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
