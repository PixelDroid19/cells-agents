#!/usr/bin/env python3
"""Compare every portable payload with a fresh render of canonical sources."""
import argparse
import json
from pathlib import Path
import tempfile

from bundle import KINDS, ROOT, inventory, render


def validate(base: Path) -> int:
    total = 0
    for kind in sorted(KINDS - {"codex-plugin"}):
        actual_root = base / kind
        if not actual_root.is_dir():
            raise ValueError(f"Missing bundle: {actual_root}")
        with tempfile.TemporaryDirectory(prefix="cells parity ") as temp:
            expected_root = Path(temp)
            render(kind, expected_root)
            expected, actual = inventory(expected_root), inventory(actual_root)
            differences = sorted(name for name in expected.keys() | actual.keys() if expected.get(name) != actual.get(name))
            if differences:
                raise ValueError(f"{kind}: {len(differences)} missing, extra or changed files: {', '.join(differences[:8])}")
            if json.loads((actual_root / ".cells-bundle.json").read_text()) != json.loads((expected_root / ".cells-bundle.json").read_text()):
                raise ValueError(f"{kind}: ownership manifest differs from canonical sources")
            total += len(expected)
            print(f"{kind}: {len(expected)} files match canonical sources")
    return total


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT / "portable")
    args = parser.parse_args()
    try:
        print(f"Portable parity passed: {validate(args.root)} files.")
        return 0
    except (ValueError, OSError) as exc:
        print(f"ERROR: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
