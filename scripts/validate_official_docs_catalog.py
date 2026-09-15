#!/usr/bin/env python3
"""Validate the bundled Cells official-docs catalog and byte-exact ZIP copy."""

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
SKILL_ROOT = ROOT / "skills" / "cells-official-docs-catalog"
REQUIRED_FILES = [
    "SKILL.md",
    "scripts/build_index.py",
    "scripts/search_docs.py",
    "assets/cells_official_docs.db",
    "assets/manifest.json",
]
SCHEMA_VERSION = "3"
DATABASE_PATH = "skills/cells-official-docs-catalog/assets/cells_official_docs.db"


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
    return json.loads((skill_root / "assets" / "manifest.json").read_text(encoding="utf-8"))


def document_fingerprint(documents: list[tuple[str, str]]) -> str:
    digest = hashlib.sha256()
    for path, content_hash in sorted(documents):
        digest.update(path.encode("utf-8"))
        digest.update(content_hash.encode("ascii"))
    return digest.hexdigest()


def immutable_connect(path: Path) -> sqlite3.Connection:
    uri = f"file:{quote(path.resolve().as_posix())}?mode=ro&immutable=1"
    connection = sqlite3.connect(uri, uri=True)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA query_only = ON")
    return connection


def metadata_from_db(connection: sqlite3.Connection) -> dict:
    return {row["key"]: json.loads(row["value"]) for row in connection.execute("SELECT key, value FROM metadata")}


def validate_required_files(skill_root: Path) -> list[str]:
    return [f"Missing required file: {display(skill_root / relative)}" for relative in REQUIRED_FILES if not (skill_root / relative).is_file()]


def validate_manifest(skill_root: Path) -> list[str]:
    try:
        manifest = load_manifest(skill_root)
    except (OSError, json.JSONDecodeError) as exc:
        return [f"Could not read official docs manifest: {exc}"]
    invalid: list[str] = []
    metadata = manifest.get("metadata")
    integrity = manifest.get("integrity")
    docs = manifest.get("docs")
    if not isinstance(metadata, dict) or not isinstance(integrity, dict) or not isinstance(docs, list):
        return ["official docs manifest must contain metadata, integrity, and docs"]
    if metadata.get("schema_version") != SCHEMA_VERSION:
        invalid.append(f"official docs manifest must use schema_version {SCHEMA_VERSION}")
    for key in ("generated_at", "generator", "source_root", "source_revision", "content_hash", "source_fingerprint"):
        if not metadata.get(key):
            invalid.append(f"official docs manifest missing metadata.{key}")
    if metadata.get("source_root") != "docs":
        invalid.append("official docs source_root must be the portable value docs")
    if Path(str(metadata.get("generator", ""))).is_absolute():
        invalid.append("official docs manifest generator must not be an absolute path")
    if manifest.get("database") != DATABASE_PATH:
        invalid.append("official docs manifest must use a portable database path")
    if integrity.get("algorithm") != "sha256":
        invalid.append("official docs integrity.algorithm must be sha256")
    for key in ("database_sha256", "source_fingerprint"):
        if not isinstance(integrity.get(key), str) or not re.fullmatch(r"[0-9a-f]{64}", integrity[key]):
            invalid.append(f"official docs integrity.{key} must be a SHA-256 hash")
    document_count = manifest.get("document_count")
    chunk_count = manifest.get("chunk_count")
    if not isinstance(document_count, int) or document_count < 100 or len(docs) != document_count:
        invalid.append("official docs docs list must match a document_count of at least 100")
    if not isinstance(chunk_count, int) or chunk_count <= document_count:
        invalid.append("official docs chunk_count must exceed document_count")
    if not isinstance(manifest.get("legacy_document_count"), int) or manifest["legacy_document_count"] <= 0:
        invalid.append("official docs catalog must include legacy documents")
    fingerprints: list[tuple[str, str]] = []
    for document in docs:
        if not isinstance(document, dict) or not isinstance(document.get("path"), str) or not isinstance(document.get("hash"), str):
            invalid.append("official docs manifest document entry is malformed")
            break
        if Path(document["path"]).is_absolute() or not re.fullmatch(r"[0-9a-f]{64}", document["hash"]):
            invalid.append("official docs manifest contains non-portable document provenance")
            break
        fingerprints.append((document["path"], document["hash"]))
    if len(fingerprints) == len(docs):
        aggregate = document_fingerprint(fingerprints)
        if metadata.get("content_hash") != aggregate or metadata.get("source_fingerprint") != aggregate or integrity.get("source_fingerprint") != aggregate:
            invalid.append("official docs manifest source fingerprint does not match document hashes")
    return invalid


def validate_database(skill_root: Path) -> list[str]:
    try:
        manifest = load_manifest(skill_root)
    except (OSError, json.JSONDecodeError) as exc:
        return [f"Could not read official docs manifest: {exc}"]
    invalid: list[str] = []
    db_path = skill_root / "assets" / "cells_official_docs.db"
    integrity = manifest.get("integrity") or {}
    if not db_path.is_file() or sha256_file(db_path) != integrity.get("database_sha256"):
        return ["official docs database hash does not match manifest"]
    try:
        connection = immutable_connect(db_path)
        try:
            table_names = {row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type IN ('table', 'view')")}
            for table in ("metadata", "documents", "chunks", "chunks_fts"):
                if table not in table_names:
                    invalid.append(f"official docs database missing table: {table}")
            db_metadata = metadata_from_db(connection)
            manifest_metadata = manifest.get("metadata") or {}
            expected_metadata = {
                "schema_version": manifest_metadata.get("schema_version"),
                "source_root": manifest_metadata.get("source_root"),
                "source_revision": manifest_metadata.get("source_revision"),
                "content_hash": manifest_metadata.get("content_hash"),
                "source_fingerprint": manifest_metadata.get("source_fingerprint"),
                "document_count": manifest.get("document_count"),
                "chunk_count": manifest.get("chunk_count"),
                "legacy_document_count": manifest.get("legacy_document_count"),
            }
            for key, expected in expected_metadata.items():
                if db_metadata.get(key) != expected:
                    invalid.append(f"official docs database metadata.{key} does not match manifest")
            database_docs = [(row["path"], row["content_hash"]) for row in connection.execute("SELECT path, content_hash FROM documents ORDER BY path")]
            manifest_docs = [(item["path"], item["hash"]) for item in manifest.get("docs", []) if isinstance(item, dict) and "path" in item and "hash" in item]
            if database_docs != sorted(manifest_docs):
                invalid.append("official docs database document hashes do not match manifest")
            if document_fingerprint(database_docs) != manifest_metadata.get("source_fingerprint"):
                invalid.append("official docs database source fingerprint does not match manifest")
            source_paths = connection.execute("SELECT source_path FROM documents UNION SELECT source_path FROM chunks").fetchall()
            if any(Path(row[0]).is_absolute() or not str(row[0]).startswith("docs/") for row in source_paths):
                invalid.append("official docs database has non-portable source paths")
            doc_count = connection.execute("SELECT count(*) FROM documents").fetchone()[0]
            chunk_count = connection.execute("SELECT count(*) FROM chunks").fetchone()[0]
            fts_count = connection.execute("SELECT count(*) FROM chunks_fts").fetchone()[0]
            if doc_count != manifest.get("document_count") or chunk_count != manifest.get("chunk_count") or fts_count != chunk_count:
                invalid.append("official docs database counts do not match manifest")
            probe = connection.execute("SELECT count(*) FROM chunks_fts WHERE chunks_fts MATCH ?", ('"testing"',)).fetchone()[0]
            if probe <= 0:
                invalid.append("official docs database FTS probe returned no testing matches")
        finally:
            connection.close()
    except (sqlite3.DatabaseError, json.JSONDecodeError, OSError) as exc:
        invalid.append(f"could not validate official docs database: {exc}")
    return invalid


def run_search(skill_root: Path, *args: str) -> tuple[int, str, str]:
    result = subprocess.run(
        [sys.executable, str(skill_root / "scripts" / "search_docs.py"), *args, "--format", "json"],
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
        code, stdout, stderr = run_search(skill_root, "--stats")
        stats = json.loads(stdout)
        if code != 0 or stats.get("status") != "ok" or stats.get("legacy_indexed", 0) <= 0:
            invalid.append(f"official docs stats smoke failed: {stderr or stdout}")
        code, stdout, stderr = run_search(skill_root, "--query", "cells app test command", "--limit", "3")
        normal = json.loads(stdout)
        if code != 0 or normal.get("search_strategy") != "strict" or not normal.get("results"):
            invalid.append(f"official docs AND search smoke failed: {stderr or stdout}")
        if not any(item.get("path") == "cells-applications/testing/unit-testing.md" for item in normal.get("results", [])):
            invalid.append("official docs normal search did not return current application testing guidance")
        code, stdout, stderr = run_search(skill_root, "--query", "CLI4 Bridge3 old app command", "--area", "legacy", "--limit", "2")
        legacy = json.loads(stdout)
        if code != 0 or not legacy.get("results") or any(item.get("area") != "legacy" for item in legacy["results"]):
            invalid.append(f"official docs legacy search smoke failed: {stderr or stdout}")
        code, _, stderr = run_search(skill_root, "--query", "%")
        if code != 2 or "Unicode letter or number" not in stderr:
            invalid.append("official docs literal percent query must fail safely")
    except (json.JSONDecodeError, IndexError) as exc:
        invalid.append(f"official docs search smoke failed: {exc}")
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
                member = f"cells-official-docs-catalog/{relative}"
                if member not in names:
                    invalid.append(f"{display(zip_path)} missing member: {member}")
                    continue
                if sha256_file(skill_root / relative) != hashlib.sha256(archive.read(member)).hexdigest():
                    invalid.append(f"{display(zip_path)} stale or mismatched member: {member}")
    except (OSError, zipfile.BadZipFile) as exc:
        invalid.append(f"{display(zip_path)} is not a valid ZIP: {exc}")
    return invalid


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the bundled Cells official docs FTS catalog")
    parser.add_argument("--skill-root", type=Path, default=SKILL_ROOT)
    parser.add_argument("--zip", type=Path, default=ROOT / "skills" / "cells-official-docs-catalog.zip")
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
    print("Cells official docs catalog is valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
