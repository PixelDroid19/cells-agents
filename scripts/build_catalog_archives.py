#!/usr/bin/env python3
"""Produce deterministic catalog ZIPs from canonical skill trees."""
from pathlib import Path
import os
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def build_archive(name):
    folder = ROOT / "skills" / name
    target = folder.with_suffix(".zip")
    descriptor, temp = tempfile.mkstemp(prefix=".catalog-", suffix=".zip", dir=target.parent)
    os.close(descriptor)
    try:
        with zipfile.ZipFile(temp, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for path in sorted(folder.rglob("*")):
                if not path.is_file() or "__pycache__" in path.parts or path.suffix == ".pyc" or path.name.endswith(("-wal", "-shm")):
                    continue
                info = zipfile.ZipInfo(str(path.relative_to(folder.parent)).replace(os.sep, "/"), date_time=(2026, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o100644 << 16
                archive.writestr(info, path.read_bytes())
        os.replace(temp, target)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)
    return target


if __name__ == "__main__":
    for name in ("cells-components-catalog", "cells-official-docs-catalog"):
        print(build_archive(name))
