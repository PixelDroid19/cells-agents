#!/usr/bin/env python3
"""Build a SQLite FTS5 index for the bundled BBVA Cells component catalog."""

from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    current = start.resolve()
    for parent in [current, *current.parents]:
        if (parent / "skills").exists():
            return parent
    raise FileNotFoundError("Could not locate skills root")


def normalize_text(value: str) -> str:
    return " ".join(str(value or "").split())


def load_records(records_path: Path) -> list[dict]:
    return json.loads(records_path.read_text(encoding="utf-8"))


def summarize_record(record: dict) -> str:
    prop_names = ", ".join(item.get("name", "") for item in record.get("properties", [])[:8] if item.get("name")) or "None detected"
    event_names = ", ".join(item.get("name", "") for item in record.get("events", [])[:6] if item.get("name")) or "None detected"
    elements = ", ".join(record.get("custom_elements", [])[:8]) or "None detected"
    return "\n".join([
        f"# {record['slug']}",
        "",
        f"- Package: `{record['npm_package']}`",
        f"- Version: `{record.get('version') or 'unknown'}`",
        f"- Category: `{record.get('category') or 'other'}`",
        f"- Description: {record.get('description') or 'No description found.'}",
        f"- Custom elements: {elements}",
        f"- Key properties: {prop_names}",
        f"- Key events: {event_names}",
        f"- Catalog record: `{record.get('catalog_record')}`",
    ])


def make_search_text(record: dict, summary_markdown: str) -> str:
    parts = [
        record.get("slug", ""),
        record.get("npm_package", ""),
        record.get("category", ""),
        record.get("description", ""),
        " ".join(record.get("keywords", [])),
        " ".join(record.get("dependencies", [])),
        " ".join(record.get("custom_elements", [])),
        " ".join(record.get("classes", [])),
        " ".join(item.get("name", "") for item in record.get("properties", [])),
        " ".join(item.get("name", "") for item in record.get("events", [])),
        " ".join(item.get("name", "") for item in record.get("css_properties", [])),
        " ".join(record.get("mixins", [])),
        " ".join(record.get("usage_examples", [])),
        summary_markdown,
    ]
    return normalize_text(" ".join(parts))


def create_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        DROP TABLE IF EXISTS package_fts;
        DROP TABLE IF EXISTS packages;

        CREATE TABLE packages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            slug TEXT UNIQUE NOT NULL,
            npm_package TEXT NOT NULL,
            version TEXT,
            category TEXT,
            description TEXT,
            keywords_json TEXT,
            dependencies_json TEXT,
            custom_elements_json TEXT,
            classes_json TEXT,
            properties_json TEXT,
            events_json TEXT,
            methods_json TEXT,
            css_properties_json TEXT,
            mixins_json TEXT,
            usage_examples_json TEXT,
            readme_path TEXT,
            custom_elements_path TEXT,
            package_json_path TEXT,
            summary_markdown TEXT,
            search_text TEXT
        );

        CREATE VIRTUAL TABLE package_fts USING fts5(
            package_id UNINDEXED,
            slug,
            npm_package,
            category,
            description,
            custom_elements,
            class_names,
            property_names,
            event_names,
            css_property_names,
            keywords,
            dependencies,
            usage_examples,
            summary_markdown,
            search_text,
            tokenize = 'porter unicode61 remove_diacritics 2'
        );
        """
    )


def build_index(records_path: Path, db_path: Path, manifest_path: Path) -> None:
    records = load_records(records_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    create_schema(conn)

    for record in records:
        summary_markdown = summarize_record(record)
        search_text = make_search_text(record, summary_markdown)
        catalog_record = record.get("catalog_record", "skills/cells-components-catalog/assets/component_records.json")
        payload = (
            record["slug"],
            record["npm_package"],
            record.get("version"),
            record.get("category"),
            record.get("description"),
            json.dumps(record.get("keywords", []), ensure_ascii=True),
            json.dumps(record.get("dependencies", []), ensure_ascii=True),
            json.dumps(record.get("custom_elements", []), ensure_ascii=True),
            json.dumps(record.get("classes", []), ensure_ascii=True),
            json.dumps(record.get("properties", []), ensure_ascii=True),
            json.dumps(record.get("events", []), ensure_ascii=True),
            json.dumps(record.get("methods", []), ensure_ascii=True),
            json.dumps(record.get("css_properties", []), ensure_ascii=True),
            json.dumps(record.get("mixins", []), ensure_ascii=True),
            json.dumps(record.get("usage_examples", []), ensure_ascii=True),
            catalog_record,
            catalog_record,
            catalog_record,
            summary_markdown,
            search_text,
        )
        cur = conn.execute(
            """
            INSERT INTO packages (
                slug, npm_package, version, category, description,
                keywords_json, dependencies_json, custom_elements_json, classes_json,
                properties_json, events_json, methods_json, css_properties_json,
                mixins_json, usage_examples_json, readme_path, custom_elements_path,
                package_json_path, summary_markdown, search_text
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            payload,
        )
        package_id = cur.lastrowid
        conn.execute(
            """
            INSERT INTO package_fts (
                package_id, slug, npm_package, category, description,
                custom_elements, class_names, property_names, event_names,
                css_property_names, keywords, dependencies, usage_examples,
                summary_markdown, search_text
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                package_id,
                record["slug"],
                record["npm_package"],
                record.get("category", ""),
                record.get("description", ""),
                " ".join(record.get("custom_elements", [])),
                " ".join(record.get("classes", [])),
                " ".join(item.get("name", "") for item in record.get("properties", [])),
                " ".join(item.get("name", "") for item in record.get("events", [])),
                " ".join(item.get("name", "") for item in record.get("css_properties", [])),
                " ".join(record.get("keywords", [])),
                " ".join(record.get("dependencies", [])),
                " ".join(record.get("usage_examples", [])),
                summary_markdown,
                search_text,
            ),
        )

    conn.commit()
    conn.close()

    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps(
            {
                "package_count": len(records),
                "database": "skills/cells-components-catalog/assets/bbva_cells_components.db",
                "source_records": "skills/cells-components-catalog/assets/component_records.json",
                "packages": [
                    {"slug": record["slug"], "package": record["npm_package"], "category": record.get("category")}
                    for record in records
                ],
            },
            indent=2,
            ensure_ascii=True,
        ) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    repo_root = find_repo_root(Path(__file__).resolve().parent)
    parser = argparse.ArgumentParser(description="Build the bundled BBVA Cells component SQLite FTS5 index")
    parser.add_argument(
        "--source-records",
        type=Path,
        default=repo_root / "skills" / "cells-components-catalog" / "assets" / "component_records.json",
        help="Path to bundled component_records.json",
    )
    parser.add_argument(
        "--db",
        type=Path,
        default=repo_root / "skills" / "cells-components-catalog" / "assets" / "bbva_cells_components.db",
        help="Target SQLite database path",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=repo_root / "skills" / "cells-components-catalog" / "assets" / "component_manifest.json",
        help="Target manifest path",
    )
    args = parser.parse_args()
    build_index(args.source_records, args.db, args.manifest)
    print(json.dumps({"status": "ok", "packages": len(load_records(args.source_records))}, indent=2))


if __name__ == "__main__":
    main()
