#!/usr/bin/env python3
"""Reject machine-specific paths from the distributable Cells bundle."""

from __future__ import annotations

import json
import re
import sqlite3
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEXT_SUFFIXES = {
    ".json",
    ".md",
    ".toml",
    ".yaml",
    ".yml",
    ".py",
    ".js",
    ".ts",
    ".sh",
    ".ps1",
}
FORBIDDEN = (
    re.compile(r"/home/[^/\s]+/", re.IGNORECASE),
    re.compile(r"/Users/[^/\s]+/", re.IGNORECASE),
    re.compile(r"[A-Za-z]:[\\/](?:Users|cells)[\\/]", re.IGNORECASE),
)


def path_leaks(value: str) -> bool:
    return any(pattern.search(value) for pattern in FORBIDDEN)


def scan_text_files() -> list[str]:
    errors: list[str] = []
    roots = (ROOT / "skills", ROOT / "plugins", ROOT / "examples", ROOT / "harness")
    for base in roots:
        for path in sorted(item for item in base.rglob("*") if item.is_file()):
            if path.suffix.lower() not in TEXT_SUFFIXES:
                continue
            text = path.read_text(encoding="utf-8-sig", errors="replace")
            if path_leaks(text):
                errors.append(f"machine-specific path in {path.relative_to(ROOT).as_posix()}")
    return errors


def scan_sqlite(path: Path) -> list[str]:
    errors: list[str] = []
    connection = sqlite3.connect(
        f"{path.resolve().as_uri()}?mode=ro&immutable=1",
        uri=True,
    )
    try:
        tables = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
            )
        }
        for table in sorted(tables):
            columns = [
                row[1]
                for row in connection.execute(f'PRAGMA table_info("{table}")')
                if str(row[2]).upper() in {"TEXT", ""}
            ]
            for column in columns:
                query = f'SELECT "{column}" FROM "{table}" WHERE "{column}" IS NOT NULL'
                for (value,) in connection.execute(query):
                    if isinstance(value, str) and path_leaks(value):
                        errors.append(
                            f"machine-specific path in {path.relative_to(ROOT).as_posix()}:{table}.{column}"
                        )
                        break
    finally:
        connection.close()
    return errors


def main() -> int:
    errors = scan_text_files()
    for path in sorted((ROOT / "skills").rglob("*.db")):
        errors.extend(scan_sqlite(path))
    for path in sorted((ROOT / "skills").rglob("*.sqlite3")):
        errors.extend(scan_sqlite(path))
    if errors:
        print(json.dumps({"status": "failed", "errors": sorted(set(errors))}, indent=2))
        return 1
    print("Bundle portability validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
