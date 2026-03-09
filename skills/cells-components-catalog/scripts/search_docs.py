#!/usr/bin/env python3
"""Search the bundled BBVA Cells SQLite FTS5 index."""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from build_index import build_index, find_repo_root  # noqa: E402


def normalize_query(query: str) -> str:
    tokens = re.findall(r"[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*", query.lower())
    tokens = [token for token in tokens if len(token) > 1]
    if not tokens:
        return query
    return " OR ".join(tokens[:16])


def ensure_index(db_path: Path, manifest_path: Path, records_path: Path) -> None:
    if db_path.exists() and manifest_path.exists():
        return
    build_index(records_path, db_path, manifest_path)


def open_db() -> tuple[sqlite3.Connection, Path, Path]:
    find_repo_root(SCRIPT_DIR)
    db_path = SCRIPT_DIR.parent / "assets" / "bbva_cells_components.db"
    manifest_path = SCRIPT_DIR.parent / "assets" / "component_manifest.json"
    records_path = SCRIPT_DIR.parent / "assets" / "component_records.json"
    ensure_index(db_path, manifest_path, records_path)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn, db_path, manifest_path


def load_json_field(row: sqlite3.Row, field_name: str) -> list | dict:
    raw = row[field_name]
    return json.loads(raw) if raw else []


def search_packages(conn: sqlite3.Connection, query: str, limit: int) -> list[sqlite3.Row]:
    fts_query = normalize_query(query)
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
        (fts_query, limit),
    ).fetchall()


def get_package(conn: sqlite3.Connection, package_ref: str) -> sqlite3.Row | None:
    return conn.execute(
        "SELECT * FROM packages WHERE slug = ? OR npm_package = ? LIMIT 1",
        (package_ref, package_ref),
    ).fetchone()


def row_to_dict(row: sqlite3.Row) -> dict:
    return {
        "slug": row["slug"],
        "npm_package": row["npm_package"],
        "version": row["version"],
        "category": row["category"],
        "description": row["description"],
        "keywords": load_json_field(row, "keywords_json"),
        "dependencies": load_json_field(row, "dependencies_json"),
        "custom_elements": load_json_field(row, "custom_elements_json"),
        "classes": load_json_field(row, "classes_json"),
        "properties": load_json_field(row, "properties_json"),
        "events": load_json_field(row, "events_json"),
        "methods": load_json_field(row, "methods_json"),
        "css_properties": load_json_field(row, "css_properties_json"),
        "mixins": load_json_field(row, "mixins_json"),
        "usage_examples": load_json_field(row, "usage_examples_json"),
        "catalog_record": row["readme_path"],
    }


def format_search_results(query: str, rows: list[sqlite3.Row]) -> str:
    lines = ["## BBVA Cells Search Results", "", f"Query: `{query}`", ""]
    if not rows:
        lines.append("No packages matched the query.")
        return "\n".join(lines)

    for idx, row in enumerate(rows, start=1):
        data = row_to_dict(row)
        prop_names = [item["name"] for item in data["properties"] if item.get("name")][:8]
        event_names = [item["name"] for item in data["events"] if item.get("name")][:6]
        lines.extend(
            [
                f"### {idx}. `{data['slug']}`",
                f"- Package: `{data['npm_package']}`",
                f"- Category: `{data['category']}`",
                f"- Description: {data['description'] or 'No description found.'}",
                f"- Custom elements: {', '.join(data['custom_elements']) if data['custom_elements'] else 'None detected'}",
                f"- Key properties: {', '.join(prop_names) if prop_names else 'None detected'}",
                f"- Key events: {', '.join(event_names) if event_names else 'None detected'}",
                f"- Match hint: {row['match_snippet'] or 'No snippet available'}",
                f"- Catalog record: `{data['catalog_record']}`",
                "",
            ]
        )
    return "\n".join(lines).rstrip()


def format_package_details(row: sqlite3.Row) -> str:
    data = row_to_dict(row)
    lines = [
        f"## Package Dossier: `{data['slug']}`",
        "",
        f"- Package: `{data['npm_package']}`",
        f"- Version: `{data['version']}`",
        f"- Category: `{data['category']}`",
        f"- Description: {data['description'] or 'No description found.'}",
        f"- Custom elements: {', '.join(data['custom_elements']) if data['custom_elements'] else 'None detected'}",
        f"- Classes: {', '.join(data['classes']) if data['classes'] else 'None detected'}",
        f"- BBVA dependencies: {', '.join(data['dependencies']) if data['dependencies'] else 'None detected'}",
        "",
        "### Key Properties",
    ]
    if data["properties"]:
        for prop in data["properties"][:20]:
            prop_type = prop.get("type") or "unknown"
            attr = f" attribute=`{prop['attribute']}`" if prop.get("attribute") else ""
            lines.append(f"- `{prop['name']}` ({prop_type}){attr}: {prop.get('description') or 'No description'}")
    else:
        lines.append("- None detected")

    lines.extend(["", "### Key Events"])
    if data["events"]:
        for event in data["events"][:16]:
            lines.append(f"- `{event['name']}`: {event.get('description') or 'No description'}")
    else:
        lines.append("- None detected")

    lines.extend(["", "### CSS Custom Properties"])
    if data["css_properties"]:
        for css_prop in data["css_properties"][:16]:
            lines.append(f"- `{css_prop['name']}`: {css_prop.get('description') or 'No description'}")
    else:
        lines.append("- None detected")

    lines.extend(["", "### Usage Examples"])
    if data["usage_examples"]:
        for idx, example in enumerate(data["usage_examples"][:2], start=1):
            lines.extend(["", f"#### Example {idx}", "```", example, "```"])
    else:
        lines.append("- None detected")

    lines.extend(["", "### Catalog Record", f"- `{data['catalog_record']}`"])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Search the BBVA Cells component SQLite FTS5 index")
    parser.add_argument("--query", help="Natural-language query to search the index")
    parser.add_argument("--package", help="Exact package slug or npm package name for a detailed dossier")
    parser.add_argument("--limit", type=int, default=8, help="Maximum number of search results")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of Markdown")
    args = parser.parse_args()

    if not args.query and not args.package:
        parser.error("Provide --query or --package")

    conn, db_path, manifest_path = open_db()
    try:
        if args.package:
            row = get_package(conn, args.package)
            if row is None:
                raise SystemExit(f"Package not found: {args.package}")
            payload = row_to_dict(row)
            if args.json:
                print(json.dumps(payload, indent=2, ensure_ascii=True))
            else:
                print(format_package_details(row))
            return

        rows = search_packages(conn, args.query or "", args.limit)
        if args.json:
            payload = {
                "query": args.query,
                "database": str(db_path),
                "manifest": str(manifest_path),
                "results": [row_to_dict(row) for row in rows],
            }
            print(json.dumps(payload, indent=2, ensure_ascii=True))
        else:
            print(format_search_results(args.query or "", rows))
    finally:
        conn.close()


if __name__ == "__main__":
    main()
