"""Reuse packaged catalog implementations through their JSON interfaces."""
import json
from pathlib import Path
import subprocess
import sys


def search_catalog(catalog: str, query: str, limit: int = 5, detail: bool = False) -> dict:
    if catalog not in {"components", "docs"}:
        raise ValueError("Catalog must be components or docs")
    if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 12:
        raise ValueError("Catalog limit must be between 1 and 12")
    if not isinstance(query, str) or len(query) > 1000:
        raise ValueError("Query must contain at most 1000 characters")
    bundle = Path(__file__).resolve().parents[2]
    folder = "cells-components-catalog" if catalog == "components" else "cells-official-docs-catalog"
    script = bundle / "skills" / folder / "scripts/search_docs.py"
    argv = [sys.executable, str(script), "--query", query, "--limit", str(limit), "--format", "json"]
    if detail:
        argv.append("--detail")
    result = subprocess.run(argv, capture_output=True, text=True, timeout=30)
    if result.returncode:
        raise ValueError((result.stderr or result.stdout)[-2000:].strip())
    return json.loads(result.stdout)
