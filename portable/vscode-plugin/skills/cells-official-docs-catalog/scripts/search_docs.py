import argparse
import sqlite3
from pathlib import Path
import re


def repo_root() -> Path:
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "skills").exists():
            return parent
    raise FileNotFoundError("Could not locate skills root")


def db_path() -> Path:
    return repo_root() / "skills" / "cells-official-docs-catalog" / "assets" / "cells_official_docs.db"


def connect() -> sqlite3.Connection:
    return sqlite3.connect(db_path())


def to_fts_query(text: str) -> str:
    terms = [term for term in re.split(r"[^A-Za-z0-9]+", text.lower()) if term]
    if not terms:
        return '""'
    return " OR ".join(f'"{term}"' for term in terms)


def search(query: str, limit: int) -> None:
    conn = connect()
    rows = conn.execute(
        """
        SELECT t.slug, t.title, t.summary, t.path
        FROM topics_fts f
        JOIN topics t ON t.slug = f.slug
        WHERE topics_fts MATCH ?
        ORDER BY rank
        LIMIT ?
        """,
        (to_fts_query(query), limit),
    ).fetchall()
    conn.close()

    print("## Cells Official Docs Results\n")
    print(f"Query: `{query}`\n")
    if not rows:
        print("No matches found.")
        return

    for idx, row in enumerate(rows, start=1):
        slug, title, summary, path = row
        print(f"### {idx}. `{slug}`")
        print(f"- Title: {title}")
        print(f"- Summary: {summary}")
        print(f"- Internal source: `{path}`\n")


def topic(slug: str) -> None:
    conn = connect()
    row = conn.execute(
        "SELECT slug, title, summary, content, path FROM topics WHERE slug = ?",
        (slug,),
    ).fetchone()
    conn.close()

    if not row:
        print(f"Topic not found: {slug}")
        return

    topic_slug, title, summary, content, path = row
    print(f"## Cells Official Topic: `{topic_slug}`\n")
    print(f"- Title: {title}")
    print(f"- Summary: {summary}")
    print(f"- Internal source: `{path}`\n")
    print(content)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--query")
    parser.add_argument("--topic")
    parser.add_argument("--limit", type=int, default=5)
    args = parser.parse_args()

    if args.topic:
        topic(args.topic)
        return
    if args.query:
        search(args.query, args.limit)
        return
    parser.error("Provide --query or --topic")


if __name__ == "__main__":
    main()
