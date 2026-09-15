#!/usr/bin/env python3
"""Validate both profiles in disposable bundles using the shared adapter checks."""
from pathlib import Path
import tempfile

from bundle import render
from validate_adapters import validate


def main():
    with tempfile.TemporaryDirectory(prefix="cells profile portability ") as temporary:
        root = Path(temporary)
        for profile in ("single", "multi"):
            for host, kind in (("codex", "codex-home"), ("vscode", "vscode"), ("opencode", "opencode-home")):
                destination = root / profile / host
                render(kind, destination, profile)
                validate(host, installed=destination / ".github" if host == "vscode" else destination)
            plugin = root / profile / "plugin"
            render("vscode-plugin", plugin, profile)
            validate("vscode", plugin=plugin)
    print("Native profile portability passed for all three hosts.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
