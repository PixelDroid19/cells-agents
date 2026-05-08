#!/usr/bin/env python3
"""Validate the bundled Cells official docs FTS catalog."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import zipfile


ROOT = Path(__file__).resolve().parent.parent
SKILL_ROOT = ROOT / "skills" / "cells-official-docs-catalog"
REQUIRED_FILES = [
    "SKILL.md",
    "scripts/build_index.py",
    "scripts/search_docs.py",
    "assets/cells_official_docs.db",
    "assets/manifest.json",
]
SCHEMA_VERSION = "2"


def display(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def load_manifest(skill_root: Path) -> dict:
    return json.loads((skill_root / "assets" / "manifest.json").read_text(encoding="utf-8"))


def validate_required_files(skill_root: Path) -> list[str]:
    invalid: list[str] = []
    for relative in REQUIRED_FILES:
        path = skill_root / relative
        if not path.is_file():
            invalid.append(f"Missing required file: {display(path)}")
    return invalid


def validate_manifest(skill_root: Path) -> list[str]:
    invalid: list[str] = []
    manifest = load_manifest(skill_root)
    metadata = manifest.get("metadata", {})
    if metadata.get("schema_version") != SCHEMA_VERSION:
        invalid.append(f"{display(skill_root / 'assets/manifest.json')} must use schema_version {SCHEMA_VERSION}")
    for key in ("generated_at", "generator", "source_root", "source_revision", "content_hash"):
        if not metadata.get(key):
            invalid.append(f"{display(skill_root / 'assets/manifest.json')} missing metadata.{key}")
    if manifest.get("document_count", 0) < 100:
        invalid.append("official docs catalog should index at least 100 documents")
    if manifest.get("chunk_count", 0) <= manifest.get("document_count", 0):
        invalid.append("official docs catalog chunk_count must exceed document_count")
    if manifest.get("legacy_document_count", 0) <= 0:
        invalid.append("official docs catalog must include older-versions legacy documents")
    docs = manifest.get("docs")
    if not isinstance(docs, list) or len(docs) != manifest.get("document_count"):
        invalid.append("manifest docs list must match document_count")
    database = manifest.get("database")
    if database != "skills/cells-official-docs-catalog/assets/cells_official_docs.db":
        invalid.append(f"manifest database path must be repo-portable, got: {database}")
    return invalid


def validate_database(skill_root: Path) -> list[str]:
    invalid: list[str] = []
    db_path = skill_root / "assets" / "cells_official_docs.db"
    manifest = load_manifest(skill_root)
    con = sqlite3.connect(db_path)
    try:
        table_names = {
            row[0]
            for row in con.execute(
                "SELECT name FROM sqlite_master WHERE type IN ('table', 'view')"
            )
        }
        for name in ("metadata", "documents", "chunks", "chunks_fts"):
            if name not in table_names:
                invalid.append(f"{display(db_path)} missing table: {name}")
        metadata_row = con.execute(
            "SELECT value FROM metadata WHERE key = 'schema_version'"
        ).fetchone()
        schema_version = json.loads(metadata_row[0]) if metadata_row else None
        if schema_version != SCHEMA_VERSION:
            invalid.append(f"{display(db_path)} metadata schema_version must be {SCHEMA_VERSION}")
        doc_count = con.execute("SELECT count(*) FROM documents").fetchone()[0]
        chunk_count = con.execute("SELECT count(*) FROM chunks").fetchone()[0]
        legacy_count = con.execute("SELECT count(*) FROM documents WHERE area = 'legacy'").fetchone()[0]
        if doc_count != manifest.get("document_count"):
            invalid.append(f"{display(db_path)} documents count does not match manifest")
        if chunk_count != manifest.get("chunk_count"):
            invalid.append(f"{display(db_path)} chunks count does not match manifest")
        if legacy_count != manifest.get("legacy_document_count"):
            invalid.append(f"{display(db_path)} legacy count does not match manifest")
        fts_probe = con.execute(
            "SELECT count(*) FROM chunks_fts WHERE chunks_fts MATCH ?",
            ("\"testing\"",),
        ).fetchone()[0]
        if fts_probe <= 0:
            invalid.append(f"{display(db_path)} FTS probe returned no testing matches")
    finally:
        con.close()
    return invalid


def run_search(skill_root: Path, *args: str) -> dict:
    script = skill_root / "scripts" / "search_docs.py"
    result = subprocess.run(
        [sys.executable, str(script), *args, "--format", "json"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip())
    return json.loads(result.stdout)


def validate_search_cli(skill_root: Path) -> list[str]:
    invalid: list[str] = []
    try:
        stats = run_search(skill_root, "--stats")
        if stats.get("status") != "ok" or stats.get("legacy_indexed", 0) <= 0:
            invalid.append("search_docs.py --stats must return ok with legacy_indexed > 0")

        normal = run_search(skill_root, "--query", "cells app test command coverage", "--limit", "3")
        normal_paths = [item.get("path", "") for item in normal.get("results", [])]
        if normal.get("status") != "ok" or not normal_paths:
            invalid.append("normal FTS smoke query returned no results")
        if not any(path == "cli/working-with-applications.md" for path in normal_paths):
            invalid.append("normal FTS smoke query should rank application CLI docs in top results")

        legacy = run_search(
            skill_root,
            "--query",
            "CLI4 Bridge3 old app command",
            "--area",
            "legacy",
            "--limit",
            "2",
        )
        legacy_results = legacy.get("results", [])
        if not legacy_results or any(item.get("area") != "legacy" for item in legacy_results):
            invalid.append("legacy FTS smoke query must return only legacy results")
    except (RuntimeError, json.JSONDecodeError) as exc:
        invalid.append(f"search_docs.py smoke failed: {exc}")
    return invalid


def validate_zip(zip_path: Path) -> list[str]:
    if not zip_path.exists():
        return []
    invalid: list[str] = []
    try:
        with zipfile.ZipFile(zip_path) as archive:
            bad_member = archive.testzip()
            if bad_member:
                invalid.append(f"{display(zip_path)} has corrupt member: {bad_member}")
            names = set(archive.namelist())
    except zipfile.BadZipFile as exc:
        return [f"{display(zip_path)} is not a valid zip: {exc}"]
    for relative in REQUIRED_FILES:
        expected = f"cells-official-docs-catalog/{relative}"
        if expected not in names:
            invalid.append(f"{display(zip_path)} missing member: {expected}")
    return invalid


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate bundled Cells official docs FTS catalog.")
    parser.add_argument("--skill-root", type=Path, default=SKILL_ROOT, help="Skill root to validate")
    parser.add_argument("--zip", type=Path, default=ROOT / "skills" / "cells-official-docs-catalog.zip", help="Optional zip artifact to validate")
    args = parser.parse_args()

    skill_root = args.skill_root.resolve()
    errors: list[str] = []
    errors.extend(validate_required_files(skill_root))
    if not errors:
        errors.extend(validate_manifest(skill_root))
        errors.extend(validate_database(skill_root))
        errors.extend(validate_search_cli(skill_root))
    errors.extend(validate_zip(args.zip.resolve()))

    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print("Cells official docs catalog is valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
