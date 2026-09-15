#!/usr/bin/env python3
"""Read-only search for the bundled BBVA Cells component catalog.

The query command never rebuilds an index. A missing, stale, or corrupted
bundle is an actionable error because rebuilding at query time would mutate an
installed skill and can hide provenance failures.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sqlite3
import sys
import unicodedata
from urllib.parse import quote


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from build_index import (  # noqa: E402
    DATABASE_RELATIVE_PATH,
    MANIFEST_RELATIVE_PATH,
    RECORDS_RELATIVE_PATH,
    SCHEMA_VERSION,
    aggregate_source_fingerprint,
    load_records,
    sha256_file,
)


SKILL_DIR = SCRIPT_DIR.parent
DEFAULT_DB = SKILL_DIR / "assets" / "bbva_cells_components.db"
DEFAULT_MANIFEST = SKILL_DIR / "assets" / "component_manifest.json"
DEFAULT_RECORDS = SKILL_DIR / "assets" / "component_records.json"
MAX_LIMIT = 12
DEFAULT_LIMIT = 5
MAX_QUERY_LENGTH = 512
# \w is Unicode aware in Python. The explicit shape accepts selectors such as
# bbva-button-default and bbva_button_default while rejecting punctuation-only
# FTS expressions.
TOKEN_RE = re.compile(r"[^\W_]+(?:[-_][^\W_]+)*", re.UNICODE)


class CatalogIntegrityError(RuntimeError):
    """The on-disk bundle is missing, mixed, or not source-verifiable."""


class QueryValidationError(ValueError):
    """The input cannot safely produce a useful FTS query."""


def load_json(path: Path, label: str) -> dict:
    if not path.is_file():
        raise CatalogIntegrityError(f"{label} is missing: {path.name}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CatalogIntegrityError(f"{label} is not valid JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise CatalogIntegrityError(f"{label} must be a JSON object")
    return value


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


def immutable_connect(db_path: Path) -> sqlite3.Connection:
    """Open a bundled database without journals, locks, or write capability."""
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


def record_fingerprint(record: dict) -> str:
    source = record.get("source")
    if not isinstance(source, dict):
        raise CatalogIntegrityError(f"record {record.get('slug', '<unknown>')} has no source fingerprint")
    if source.get("algorithm") != "sha256":
        raise CatalogIntegrityError(f"record {record.get('slug', '<unknown>')} uses an unsupported source fingerprint algorithm")
    files = source.get("files")
    if not isinstance(files, list) or not files:
        raise CatalogIntegrityError(f"record {record.get('slug', '<unknown>')} has no source file hashes")
    digest = hashlib.sha256()
    for item in files:
        if not isinstance(item, dict):
            raise CatalogIntegrityError("record source file list is malformed")
        path = item.get("path")
        file_hash = item.get("sha256")
        if not isinstance(path, str) or not isinstance(file_hash, str) or not re.fullmatch(r"[0-9a-f]{64}", file_hash):
            raise CatalogIntegrityError("record source file hash is malformed")
        if Path(path).is_absolute() or not path.startswith("packages/"):
            raise CatalogIntegrityError("record provenance contains a non-portable source path")
        digest.update(path.encode("utf-8"))
        digest.update(b"\0")
        digest.update(file_hash.encode("ascii"))
        digest.update(b"\n")
    result = digest.hexdigest()
    if source.get("fingerprint") != result:
        raise CatalogIntegrityError(f"record {record.get('slug', '<unknown>')} source fingerprint does not match its file hashes")
    return result


def validate_records(records_path: Path, manifest: dict) -> list[dict]:
    expected_hash = ((manifest.get("integrity") or {}).get("records_sha256"))
    if not isinstance(expected_hash, str) or not re.fullmatch(r"[0-9a-f]{64}", expected_hash):
        raise CatalogIntegrityError("manifest is missing integrity.records_sha256")
    if not records_path.is_file():
        raise CatalogIntegrityError(f"component records are missing: {records_path.name}")
    actual_hash = sha256_file(records_path)
    if actual_hash != expected_hash:
        raise CatalogIntegrityError("component records hash does not match the manifest")
    try:
        records = load_records(records_path)
    except ValueError as exc:
        raise CatalogIntegrityError(str(exc)) from exc
    for record in records:
        record_fingerprint(record)
    try:
        source_fingerprint = aggregate_source_fingerprint(records)
    except ValueError as exc:
        raise CatalogIntegrityError(str(exc)) from exc
    integrity = manifest.get("integrity") or {}
    metadata = manifest.get("metadata") or {}
    if integrity.get("source_fingerprint") != source_fingerprint or metadata.get("source_fingerprint") != source_fingerprint:
        raise CatalogIntegrityError("component source fingerprint does not match the manifest")
    if manifest.get("package_count") != len(records):
        raise CatalogIntegrityError("component record count does not match the manifest")
    package_entries = manifest.get("packages")
    if not isinstance(package_entries, list) or len(package_entries) != len(records):
        raise CatalogIntegrityError("manifest package list does not match the component records")
    expected_by_slug = {record["slug"]: record_fingerprint(record) for record in records}
    manifest_by_slug = {
        entry.get("slug"): entry.get("source_fingerprint")
        for entry in package_entries
        if isinstance(entry, dict) and entry.get("slug")
    }
    if manifest_by_slug != expected_by_slug:
        raise CatalogIntegrityError("manifest package source fingerprints do not match component records")
    return records


def validate_bundle(db_path: Path, manifest_path: Path, records_path: Path) -> tuple[sqlite3.Connection, dict]:
    """Verify records, manifest and database agree before exposing any result."""
    manifest = load_json(manifest_path, "component manifest")
    metadata = manifest.get("metadata")
    integrity = manifest.get("integrity")
    if not isinstance(metadata, dict) or not isinstance(integrity, dict):
        raise CatalogIntegrityError("component manifest is missing metadata or integrity")
    if metadata.get("schema_version") != SCHEMA_VERSION:
        raise CatalogIntegrityError(f"component manifest schema is unsupported; expected {SCHEMA_VERSION}")
    if metadata.get("source_root") != "packages" or not metadata.get("source_revision"):
        raise CatalogIntegrityError("component manifest has incomplete portable source provenance")
    if manifest.get("database") != DATABASE_RELATIVE_PATH or manifest.get("source_records") != RECORDS_RELATIVE_PATH:
        raise CatalogIntegrityError("component manifest has non-portable artifact paths")
    if integrity.get("algorithm") != "sha256":
        raise CatalogIntegrityError("component manifest uses an unsupported integrity algorithm")
    records = validate_records(records_path, manifest)
    expected_db_hash = integrity.get("database_sha256")
    if not isinstance(expected_db_hash, str) or not re.fullmatch(r"[0-9a-f]{64}", expected_db_hash):
        raise CatalogIntegrityError("manifest is missing integrity.database_sha256")
    if not db_path.is_file() or sha256_file(db_path) != expected_db_hash:
        raise CatalogIntegrityError("component database hash does not match the manifest")

    conn = immutable_connect(db_path)
    try:
        db_metadata = metadata_from_db(conn)
        expected_metadata = {
            "schema_version": metadata.get("schema_version"),
            "source_root": metadata.get("source_root"),
            "source_revision": metadata.get("source_revision"),
            "source_fingerprint": metadata.get("source_fingerprint"),
            "records_sha256": integrity.get("records_sha256"),
            "package_count": manifest.get("package_count"),
        }
        for key, expected in expected_metadata.items():
            if db_metadata.get(key) != expected:
                raise CatalogIntegrityError(f"database metadata.{key} does not match the manifest")
        package_count = conn.execute("SELECT count(*) FROM packages").fetchone()[0]
        fts_count = conn.execute("SELECT count(*) FROM package_fts").fetchone()[0]
        if package_count != len(records) or fts_count != package_count:
            raise CatalogIntegrityError("component database row counts do not match the records")
        expected_sources = {
            record["slug"]: (record["npm_package"], record["source"])
            for record in records
        }
        database_sources: dict[str, tuple[str, object]] = {}
        for row in conn.execute("SELECT slug, npm_package, source_json FROM packages"):
            try:
                database_sources[row["slug"]] = (row["npm_package"], json.loads(row["source_json"]))
            except json.JSONDecodeError as exc:
                raise CatalogIntegrityError("component database contains invalid package source JSON") from exc
        if database_sources != expected_sources:
            raise CatalogIntegrityError("component database package source records do not match the JSON records")
    except Exception:
        conn.close()
        raise
    return conn, manifest


def tokenize_query(query: str) -> tuple[str, list[str]]:
    normalized = unicodedata.normalize("NFC", query or "").strip()
    if len(normalized) > MAX_QUERY_LENGTH:
        raise QueryValidationError(f"query must be at most {MAX_QUERY_LENGTH} characters")
    tokens = [match.group(0).strip("-_").casefold() for match in TOKEN_RE.finditer(normalized)]
    tokens = [token for token in tokens if token]
    if not tokens:
        raise QueryValidationError("query must include at least one Unicode letter or number")
    # FTS tokenizes hyphen and underscore separators, while selector lookup below
    # retains them. This gives both natural language and exact selector coverage.
    fts_tokens: list[str] = []
    for token in tokens:
        fts_tokens.extend(part for part in re.split(r"[-_]", token) if part)
    ordered: list[str] = []
    seen: set[str] = set()
    for token in fts_tokens:
        if token not in seen:
            seen.add(token)
            ordered.append(token)
        if len(ordered) == 16:
            break
    return normalized, ordered


def fts_expression(tokens: list[str], operator: str) -> str:
    return f" {operator} ".join(f'"{token.replace(chr(34), " ")}"' for token in tokens)


def selector_key(value: str) -> str:
    return unicodedata.normalize("NFKC", value).strip().casefold().replace("_", "-")


def get_package(conn: sqlite3.Connection, package_ref: str) -> sqlite3.Row | None:
    key = selector_key(package_ref)
    if not key:
        return None
    return conn.execute(
        """
        SELECT * FROM packages
        WHERE lower(replace(slug, '_', '-')) = ?
           OR lower(replace(npm_package, '_', '-')) = ?
        LIMIT 1
        """,
        (key, key),
    ).fetchone()


def search_fts(conn: sqlite3.Connection, expression: str, limit: int) -> list[sqlite3.Row]:
    return conn.execute(
        """
        SELECT
            p.*,
            bm25(package_fts, 0.8, 1.2, 0.7, 1.4, 1.2, 1.0, 1.0, 0.9, 0.7, 0.7, 0.6, 0.5, 0.5, 1.4) AS score,
            snippet(package_fts, 14, '[', ']', ' ... ', 18) AS match_snippet
        FROM package_fts
        JOIN packages p ON p.id = package_fts.package_id
        WHERE package_fts MATCH ?
        ORDER BY score ASC
        LIMIT ?
        """,
        (expression, limit),
    ).fetchall()


def search_packages(conn: sqlite3.Connection, raw_query: str, tokens: list[str], limit: int) -> tuple[list[sqlite3.Row], str]:
    exact = get_package(conn, raw_query)
    if exact is not None:
        return [exact], "exact_selector"
    strict = search_fts(conn, fts_expression(tokens, "AND"), limit)
    if strict:
        return strict, "and"
    return search_fts(conn, fts_expression(tokens, "OR"), limit), "or_fallback"


def load_json_field(row: sqlite3.Row, field_name: str) -> list | dict:
    raw = row[field_name]
    return json.loads(raw) if raw else []


def summary_from_row(row: sqlite3.Row) -> dict:
    """Bounded default payload. Full CEM APIs require --detail or --dossier."""
    properties = load_json_field(row, "properties_json")
    events = load_json_field(row, "events_json")
    methods = load_json_field(row, "methods_json")
    return {
        "slug": row["slug"],
        "npm_package": row["npm_package"],
        "version": row["version"],
        "category": row["category"],
        "description": row["description"],
        "custom_elements": load_json_field(row, "custom_elements_json"),
        "classes": load_json_field(row, "classes_json"),
        "api_counts": {"properties": len(properties), "events": len(events), "methods": len(methods)},
        "catalog_record": row["catalog_record"],
        "match_hint": row["match_snippet"] if "match_snippet" in row.keys() else None,
    }


def dossier_from_row(row: sqlite3.Row) -> dict:
    payload = summary_from_row(row)
    payload.update(
        {
            "keywords": load_json_field(row, "keywords_json"),
            "dependencies": load_json_field(row, "dependencies_json"),
            "properties": load_json_field(row, "properties_json"),
            "events": load_json_field(row, "events_json"),
            "methods": load_json_field(row, "methods_json"),
            "css_properties": load_json_field(row, "css_properties_json"),
            "mixins": load_json_field(row, "mixins_json"),
            "usage_examples": load_json_field(row, "usage_examples_json"),
            "source": load_json_field(row, "source_json"),
        }
    )
    return payload


def format_search_results(query: str, results: list[dict], strategy: str) -> str:
    lines = ["## BBVA Cells Search Results", "", f"Query: `{query}`", f"Strategy: `{strategy}`", ""]
    if not results:
        lines.append("No packages matched the query.")
        return "\n".join(lines)
    for index, result in enumerate(results, start=1):
        counts = result["api_counts"]
        lines.extend(
            [
                f"### {index}. `{result['slug']}`",
                f"- Package: `{result['npm_package']}`",
                f"- Category: `{result['category']}`",
                f"- Description: {result['description'] or 'No description found.'}",
                f"- Custom elements: {', '.join(result['custom_elements']) or 'None detected'}",
                f"- API: {counts['properties']} properties, {counts['events']} events, {counts['methods']} methods",
                f"- Catalog record: `{result['catalog_record']}`",
                "",
            ]
        )
    return "\n".join(lines).rstrip()


def format_dossier(result: dict) -> str:
    lines = [
        f"## Package Dossier: `{result['slug']}`",
        "",
        f"- Package: `{result['npm_package']}`",
        f"- Version: `{result['version']}`",
        f"- Category: `{result['category']}`",
        f"- Description: {result['description'] or 'No description found.'}",
        f"- Custom elements: {', '.join(result['custom_elements']) or 'None detected'}",
        "",
        "### Properties",
    ]
    for item in result["properties"][:30]:
        attribute = f" attribute=`{item['attribute']}`" if item.get("attribute") else ""
        lines.append(f"- `{item['name']}` ({item.get('type') or 'unknown'}){attribute}: {item.get('description') or 'No description'}")
    if not result["properties"]:
        lines.append("- None detected")
    lines.extend(["", "### Events"])
    for item in result["events"][:24]:
        lines.append(f"- `{item['name']}`: {item.get('description') or 'No description'}")
    if not result["events"]:
        lines.append("- None detected")
    lines.extend(["", "### Methods"])
    for item in result["methods"][:24]:
        parameters = ", ".join(parameter["name"] for parameter in item.get("parameters", []))
        lines.append(f"- `{item['name']}({parameters})`: {item.get('description') or 'No description'}")
    if not result["methods"]:
        lines.append("- None detected")
    lines.extend(["", "### Catalog Record", f"- `{result['catalog_record']}`"])
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Search the portable BBVA Cells component catalog")
    selector = parser.add_mutually_exclusive_group(required=True)
    selector.add_argument("--query", help="Natural-language or selector query")
    selector.add_argument("--package", "--dossier", dest="package", help="Exact package slug or npm package for a full dossier")
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT, help=f"Maximum search results (1-{MAX_LIMIT})")
    parser.add_argument("--detail", action="store_true", help="Include full CEM API fields for --query results")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown", help="Output format")
    parser.add_argument("--json", action="store_true", help="Legacy alias for --format json")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB, help="Bundled SQLite database")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST, help="Bundled manifest JSON")
    parser.add_argument("--records", type=Path, default=DEFAULT_RECORDS, help="Bundled component records JSON")
    args = parser.parse_args()
    if args.json:
        args.format = "json"
    if not 1 <= args.limit <= MAX_LIMIT:
        parser.error(f"--limit must be between 1 and {MAX_LIMIT}")
    return args


def fail(message: str) -> int:
    print(f"error: {message}", file=sys.stderr)
    return 2


def main() -> int:
    args = parse_args()
    try:
        raw_selector = args.package or args.query or ""
        query, tokens = tokenize_query(raw_selector)
        conn, manifest = validate_bundle(args.db.resolve(), args.manifest.resolve(), args.records.resolve())
        try:
            if args.package:
                row = get_package(conn, query)
                if row is None:
                    payload: dict = {"status": "not_found", "package": args.package}
                    status = 1
                else:
                    payload = {"status": "ok", **dossier_from_row(row)}
                    status = 0
            else:
                rows, strategy = search_packages(conn, query, tokens, args.limit)
                transform = dossier_from_row if args.detail else summary_from_row
                payload = {
                    "status": "ok",
                    "query": query,
                    "search_strategy": strategy,
                    "count": len(rows),
                    "results": [transform(row) for row in rows],
                    "catalog": {"database": manifest["database"], "manifest": MANIFEST_RELATIVE_PATH},
                }
                status = 0
        finally:
            conn.close()
    except QueryValidationError as exc:
        return fail(str(exc))
    except (CatalogIntegrityError, OSError, sqlite3.DatabaseError) as exc:
        return fail(f"component catalog is stale or corrupt: {exc}. Rebuild explicitly with scripts/build_index.py --packages-root <packages-dir>.")

    if args.format == "json":
        print(json.dumps(payload, indent=2, ensure_ascii=True))
    elif args.package and payload.get("status") == "ok":
        print(format_dossier(payload))
    elif payload.get("status") == "not_found":
        print(f"Package not found: `{payload['package']}`")
    elif args.detail and payload["results"]:
        print("\n\n".join(format_dossier(result) for result in payload["results"]))
    else:
        print(format_search_results(payload["query"], payload["results"], payload["search_strategy"]))
    return status


if __name__ == "__main__":
    raise SystemExit(main())
