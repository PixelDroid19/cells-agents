#!/usr/bin/env python3
"""Validate the portable BBVA Cells component catalog and its optional ZIP."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sqlite3
import subprocess
import sys
from urllib.parse import quote
import zipfile


ROOT = Path(__file__).resolve().parent.parent
SKILL_ROOT = ROOT / "skills" / "cells-components-catalog"
REQUIRED_FILES = [
    "SKILL.md",
    "scripts/build_index.py",
    "scripts/search_docs.py",
    "assets/component_records.json",
    "assets/bbva_cells_components.db",
    "assets/component_manifest.json",
]
SCHEMA_VERSION = "3"
DATABASE_PATH = "skills/cells-components-catalog/assets/bbva_cells_components.db"
RECORDS_PATH = "skills/cells-components-catalog/assets/component_records.json"


def display(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_manifest(skill_root: Path) -> dict:
    return json.loads((skill_root / "assets" / "component_manifest.json").read_text(encoding="utf-8"))


def source_record_fingerprint(record: dict) -> str | None:
    source = record.get("source")
    if (
        not isinstance(source, dict)
        or source.get("algorithm") != "sha256"
        or not isinstance(source.get("files"), list)
        or not source["files"]
    ):
        return None
    digest = hashlib.sha256()
    for item in source["files"]:
        if not isinstance(item, dict):
            return None
        path, file_hash = item.get("path"), item.get("sha256")
        if not isinstance(path, str) or not isinstance(file_hash, str) or not re.fullmatch(r"[0-9a-f]{64}", file_hash):
            return None
        if Path(path).is_absolute() or not path.startswith("packages/"):
            return None
        digest.update(path.encode("utf-8"))
        digest.update(b"\0")
        digest.update(file_hash.encode("ascii"))
        digest.update(b"\n")
    result = digest.hexdigest()
    return result if source.get("fingerprint") == result else None


def aggregate_fingerprint(records: list[dict]) -> str | None:
    digest = hashlib.sha256()
    for record in sorted(records, key=lambda item: str(item.get("slug", ""))):
        slug = record.get("slug")
        fingerprint = source_record_fingerprint(record)
        if not isinstance(slug, str) or not fingerprint:
            return None
        digest.update(slug.encode("utf-8"))
        digest.update(b"\0")
        digest.update(fingerprint.encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest()


def immutable_connect(path: Path) -> sqlite3.Connection:
    uri = f"file:{quote(path.resolve().as_posix())}?mode=ro&immutable=1"
    connection = sqlite3.connect(uri, uri=True)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA query_only = ON")
    return connection


def db_metadata(connection: sqlite3.Connection) -> dict:
    return {row["key"]: json.loads(row["value"]) for row in connection.execute("SELECT key, value FROM metadata")}


def validate_required_files(skill_root: Path) -> list[str]:
    return [f"Missing required file: {display(skill_root / relative)}" for relative in REQUIRED_FILES if not (skill_root / relative).is_file()]


def validate_manifest(skill_root: Path) -> list[str]:
    invalid: list[str] = []
    try:
        manifest = load_manifest(skill_root)
    except (OSError, json.JSONDecodeError) as exc:
        return [f"Could not read component manifest: {exc}"]
    metadata = manifest.get("metadata")
    integrity = manifest.get("integrity")
    if not isinstance(metadata, dict) or not isinstance(integrity, dict):
        return ["component manifest must contain metadata and integrity objects"]
    if metadata.get("schema_version") != SCHEMA_VERSION:
        invalid.append(f"component manifest must use schema_version {SCHEMA_VERSION}")
    for key in ("generated_at", "generator", "source_root", "source_revision", "source_fingerprint"):
        if not metadata.get(key):
            invalid.append(f"component manifest missing metadata.{key}")
    if metadata.get("source_root") != "packages":
        invalid.append("component manifest source_root must be the portable value packages")
    if Path(str(metadata.get("generator", ""))).is_absolute():
        invalid.append("component manifest generator must not be an absolute path")
    if manifest.get("database") != DATABASE_PATH or manifest.get("source_records") != RECORDS_PATH:
        invalid.append("component manifest must use portable artifact paths")
    if integrity.get("algorithm") != "sha256":
        invalid.append("component manifest integrity.algorithm must be sha256")
    for key in ("records_sha256", "database_sha256", "source_fingerprint"):
        if not isinstance(integrity.get(key), str) or not re.fullmatch(r"[0-9a-f]{64}", integrity[key]):
            invalid.append(f"component manifest integrity.{key} must be a SHA-256 hash")
    if not isinstance(manifest.get("package_count"), int) or manifest["package_count"] <= 0:
        invalid.append("component manifest package_count must be positive")
    packages = manifest.get("packages")
    if not isinstance(packages, list) or len(packages) != manifest.get("package_count"):
        invalid.append("component manifest package list must match package_count")
    return invalid


def validate_database(skill_root: Path) -> list[str]:
    invalid: list[str] = []
    try:
        manifest = load_manifest(skill_root)
        records_path = skill_root / "assets" / "component_records.json"
        db_path = skill_root / "assets" / "bbva_cells_components.db"
        records = json.loads(records_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"Could not read component assets: {exc}"]
    if not isinstance(records, list):
        return ["component records must be a JSON array"]
    integrity = manifest.get("integrity") or {}
    if sha256_file(records_path) != integrity.get("records_sha256"):
        invalid.append("component records hash does not match manifest")
    aggregate = aggregate_fingerprint(records)
    if not aggregate:
        invalid.append("component records have malformed or non-portable source fingerprints")
    elif aggregate != integrity.get("source_fingerprint") or aggregate != (manifest.get("metadata") or {}).get("source_fingerprint"):
        invalid.append("component source fingerprint does not match manifest")
    package_entries = manifest.get("packages")
    expected_by_slug = {record.get("slug"): source_record_fingerprint(record) for record in records}
    manifest_by_slug = {
        entry.get("slug"): entry.get("source_fingerprint")
        for entry in package_entries
        if isinstance(entry, dict) and entry.get("slug")
    } if isinstance(package_entries, list) else {}
    if expected_by_slug != manifest_by_slug:
        invalid.append("component manifest package fingerprints do not match records")
    if not db_path.is_file() or sha256_file(db_path) != integrity.get("database_sha256"):
        invalid.append("component database hash does not match manifest")
        return invalid
    try:
        connection = immutable_connect(db_path)
        try:
            names = {row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type IN ('table', 'view')")}
            for name in ("metadata", "packages", "package_fts"):
                if name not in names:
                    invalid.append(f"component database missing table: {name}")
            metadata = db_metadata(connection)
            manifest_metadata = manifest.get("metadata") or {}
            expected = {
                "schema_version": manifest_metadata.get("schema_version"),
                "source_root": manifest_metadata.get("source_root"),
                "source_revision": manifest_metadata.get("source_revision"),
                "source_fingerprint": manifest_metadata.get("source_fingerprint"),
                "records_sha256": integrity.get("records_sha256"),
                "package_count": manifest.get("package_count"),
            }
            for key, value in expected.items():
                if metadata.get(key) != value:
                    invalid.append(f"component database metadata.{key} does not match manifest")
            package_count = connection.execute("SELECT count(*) FROM packages").fetchone()[0]
            fts_count = connection.execute("SELECT count(*) FROM package_fts").fetchone()[0]
            if package_count != len(records) or package_count != manifest.get("package_count") or fts_count != package_count:
                invalid.append("component database counts do not match records and manifest")
            source_rows = connection.execute("SELECT source_json FROM packages").fetchall()
            source_paths = [
                item.get("path", "")
                for row in source_rows
                for item in json.loads(row[0]).get("files", [])
                if isinstance(item, dict)
            ]
            if any(Path(path).is_absolute() or not path.startswith("packages/") for path in source_paths):
                invalid.append("component database has absolute source provenance")
            expected_sources = {
                record.get("slug"): (record.get("npm_package"), record.get("source"))
                for record in records
            }
            database_sources = {
                row["slug"]: (row["npm_package"], json.loads(row["source_json"]))
                for row in connection.execute("SELECT slug, npm_package, source_json FROM packages")
            }
            if database_sources != expected_sources:
                invalid.append("component database package source records do not match JSON records")
        finally:
            connection.close()
    except (sqlite3.DatabaseError, json.JSONDecodeError, OSError) as exc:
        invalid.append(f"could not validate component database: {exc}")
    return invalid


def run_search(skill_root: Path, *args: str) -> tuple[int, str, str]:
    result = subprocess.run(
        [sys.executable, str(skill_root / "scripts" / "search_docs.py"), *args],
        cwd=skill_root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    return result.returncode, result.stdout, result.stderr


def validate_search_cli(skill_root: Path) -> list[str]:
    invalid: list[str] = []
    try:
        code, stdout, stderr = run_search(skill_root, "--query", "bbva_button_default", "--format", "json")
        exact = json.loads(stdout)
        if code != 0 or exact.get("search_strategy") != "exact_selector" or exact.get("results", [{}])[0].get("slug") != "bbva-button-default":
            invalid.append(f"component underscore selector smoke failed: {stderr or stdout}")
        code, stdout, stderr = run_search(skill_root, "--query", "form input", "--limit", "3", "--format", "json")
        normal = json.loads(stdout)
        if code != 0 or normal.get("search_strategy") != "and" or len(normal.get("results", [])) > 3:
            invalid.append(f"component AND search smoke failed: {stderr or stdout}")
        if "properties" in normal.get("results", [{}])[0] or len(stdout.encode("utf-8")) > 14000:
            invalid.append("component summary search is not bounded; use --detail for full APIs")
        code, _, stderr = run_search(skill_root, "--query", "!!!", "--format", "json")
        if code != 2 or "Unicode letter or number" not in stderr:
            invalid.append("component invalid-token search must fail clearly without FTS parsing")
    except (json.JSONDecodeError, IndexError) as exc:
        invalid.append(f"component search smoke failed: {exc}")
    return invalid


def validate_zip(zip_path: Path, skill_root: Path) -> list[str]:
    if not zip_path.exists():
        return [f"Missing catalog ZIP: {display(zip_path)}"]
    invalid: list[str] = []
    try:
        with zipfile.ZipFile(zip_path) as archive:
            bad_member = archive.testzip()
            if bad_member:
                invalid.append(f"{display(zip_path)} has corrupt member: {bad_member}")
            names = set(archive.namelist())
            for relative in REQUIRED_FILES:
                member = f"cells-components-catalog/{relative}"
                if member not in names:
                    invalid.append(f"{display(zip_path)} missing member: {member}")
                    continue
                if sha256_file(skill_root / relative) != hashlib.sha256(archive.read(member)).hexdigest():
                    invalid.append(f"{display(zip_path)} stale or mismatched member: {member}")
    except (OSError, zipfile.BadZipFile) as exc:
        invalid.append(f"{display(zip_path)} is not a valid ZIP: {exc}")
    return invalid


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the bundled BBVA Cells component catalog")
    parser.add_argument("--skill-root", type=Path, default=SKILL_ROOT)
    parser.add_argument("--zip", type=Path, default=ROOT / "skills" / "cells-components-catalog.zip")
    args = parser.parse_args()
    skill_root = args.skill_root.resolve()
    errors = validate_required_files(skill_root)
    if not errors:
        errors.extend(validate_manifest(skill_root))
        errors.extend(validate_database(skill_root))
        if not errors:
            errors.extend(validate_search_cli(skill_root))
    errors.extend(validate_zip(args.zip.resolve(), skill_root))
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print("Cells component catalog is valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
