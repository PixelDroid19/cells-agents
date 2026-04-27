import argparse
from datetime import datetime, timezone
import json
import sqlite3
from pathlib import Path


def repo_root() -> Path:
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "skills").exists():
            return parent
    raise FileNotFoundError("Could not locate skills root")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def as_posix(path: Path) -> str:
    return path.as_posix()


def build_metadata(
    generator_path: Path,
    source_root: str | None,
    source_revision: str | None,
    normalization_version: str,
) -> dict:
    return {
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "normalization_version": normalization_version,
        "generator": as_posix(generator_path),
        "source_root": source_root or "bundled-official-docs-references",
        "source_revision": source_revision or "bundled-snapshot",
    }


def extract_title(content: str, fallback: str) -> str:
    for line in content.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return fallback.replace("-", " ").title()


def build_topic_record(path: Path) -> dict:
    slug = path.stem
    content = read_text(path)
    lines = [line.strip() for line in content.splitlines() if line.strip()]
    summary = ""
    for idx, line in enumerate(lines):
        if line.startswith("## Scope") and idx + 1 < len(lines):
            summary = lines[idx + 1]
            break
    if not summary:
        for line in lines:
            if not line.startswith("#") and not line.startswith("-"):
                summary = line
                break
    return {
        "slug": slug,
        "title": extract_title(content, slug),
        "summary": summary,
        "content": content,
        "path": str(path.relative_to(repo_root())),
    }


def create_db(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.executescript(
        """
        DROP TABLE IF EXISTS topics;
        DROP TABLE IF EXISTS topics_fts;

        CREATE TABLE topics (
            slug TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            summary TEXT NOT NULL,
            content TEXT NOT NULL,
            path TEXT NOT NULL
        );

        CREATE VIRTUAL TABLE topics_fts USING fts5(
            slug,
            title,
            summary,
            content,
            tokenize = 'porter unicode61'
        );
        """
    )
    return conn


def main() -> None:
    root = repo_root()
    default_refs = root / "skills" / "cells-official-docs-catalog" / "references"
    default_db = root / "skills" / "cells-official-docs-catalog" / "assets" / "cells_official_docs.db"
    default_manifest = root / "skills" / "cells-official-docs-catalog" / "assets" / "manifest.json"

    parser = argparse.ArgumentParser()
    parser.add_argument("--references", type=Path, default=default_refs)
    parser.add_argument("--db", type=Path, default=default_db)
    parser.add_argument("--manifest", type=Path, default=default_manifest)
    parser.add_argument("--source-root", help="Original source root for the bundled snapshot (for manifest provenance)")
    parser.add_argument("--source-revision", help="Original source revision or snapshot identifier (for manifest provenance)")
    parser.add_argument("--normalization-version", default="1", help="Normalization version for the generated manifest metadata")
    args = parser.parse_args()

    topic_files = sorted(args.references.glob("*.md"))
    records = [build_topic_record(path) for path in topic_files]

    conn = create_db(args.db)
    for record in records:
        conn.execute(
            "INSERT INTO topics (slug, title, summary, content, path) VALUES (?, ?, ?, ?, ?)",
            (record["slug"], record["title"], record["summary"], record["content"], record["path"]),
        )
        conn.execute(
            "INSERT INTO topics_fts (slug, title, summary, content) VALUES (?, ?, ?, ?)",
            (record["slug"], record["title"], record["summary"], record["content"]),
        )
    conn.commit()
    conn.close()

    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(
        json.dumps(
            {
                "metadata": build_metadata(
                    generator_path=Path(__file__).resolve().relative_to(root),
                    source_root=args.source_root,
                    source_revision=args.source_revision,
                    normalization_version=args.normalization_version,
                ),
                "topic_count": len(records),
                "database": as_posix(args.db.relative_to(root)),
                "topics": [{"slug": r["slug"], "title": r["title"], "path": r["path"]} for r in records],
            },
            indent=2,
            ensure_ascii=True,
        ),
        encoding="utf-8",
    )

    print(json.dumps({"status": "ok", "topic_count": len(records), "database": str(args.db)}, indent=2))


if __name__ == "__main__":
    main()
