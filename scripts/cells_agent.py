#!/usr/bin/env python3
"""Compatibility harness entrypoint backed by the canonical Cells modules."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

from bundle import ROOT, build
from install import atomic_write, install, safe_destination

sys.path.insert(0, str(ROOT / "runtime"))
from cells_agent.cli import doctor
from cells_agent.project import project_info

HOST_SCOPES = {"vscode": {"workspace"}, "codex": {"user"}, "opencode": {"user", "workspace"}}


def context(workspace: Path, args) -> dict:
    info = project_info(workspace)
    values = {"schema_version": 1, "workspace_root": info["root"], "cells_project": info["is_cells"], "project": info["project"]}
    for argument, key in (("catalog", "component_catalog_root"), ("docs", "official_docs_root"), ("cells_cli", "cells_cli_root")):
        value = getattr(args, argument, None)
        if value is not None:
            path = Path(value).expanduser().resolve(strict=True)
            if not path.is_dir():
                raise ValueError(f"{argument} must identify a directory")
            if argument == "catalog" and (path / "packages").is_dir():
                path = path / "packages"
            values[key] = str(path)
    return values


def render_host(host: str, output: Path, profile: str):
    mapping = {"vscode": [("vscode", "workspace"), ("vscode-plugin", "plugin")],
               "codex": [("codex-home", "home")],
               "opencode": [("opencode-home", "home"), ("project-local", "workspace")]}
    # Each child build verifies ownership before replacing a prior generated tree.
    return [str(build(kind, output / relative, profile)) for kind, relative in mapping[host]]


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="action", required=True)
    for action in ("render", "install"):
        command = commands.add_parser(action)
        command.add_argument("--host", required=True, choices=(*HOST_SCOPES, "all") if action == "render" else tuple(HOST_SCOPES))
        command.add_argument("--profile", choices=("single", "multi"), default="single")
        command.add_argument("--force", action="store_true", help="Install: back up and replace conflicts; render: ownership checks still apply")
        if action == "render":
            command.add_argument("--output", type=Path, default=ROOT / "dist")
        else:
            command.add_argument("--scope", required=True, choices=("user", "workspace"))
            command.add_argument("--target", type=Path)
            command.add_argument("--dry-run", action="store_true")
            command.add_argument("--write-context", action="store_true", help="Explicitly save local source paths in the selected workspace")
    commands.add_parser("doctor")
    commands.add_parser("validate")
    for name in ("install", "doctor"):
        command = commands.choices[name]
        command.add_argument("--workspace", type=Path, default=Path.cwd())
        for flag in ("catalog", "docs", "cells-cli"):
            command.add_argument("--" + flag)
    args = parser.parse_args(argv)
    try:
        if args.action == "render":
            hosts = list(HOST_SCOPES) if args.host == "all" else [args.host]
            result = {host: render_host(host, args.output / host if len(hosts) > 1 else args.output, args.profile) for host in hosts}
        elif args.action == "doctor":
            result = doctor(str(args.workspace))
            result["context"] = context(args.workspace, args)
        elif args.action == "install":
            if args.scope not in HOST_SCOPES[args.host]:
                raise ValueError(f"Unsupported host scope: {args.host}/{args.scope}")
            destination = args.target or (Path.home() if args.scope == "user" else args.workspace)
            agent = "project-local" if args.host == "opencode" and args.scope == "workspace" else args.host
            detected = context(args.workspace, args)
            context_path = safe_destination(args.workspace.absolute(), ".cells-agent/context.json") if args.write_context else None
            result = install(agent, destination, dry_run=args.dry_run, replace=args.force, profile=args.profile)
            result["context"] = detected
            if context_path and result["applied"]:
                atomic_write(context_path, (json.dumps(detected, indent=2) + "\n").encode())
                result["context_file"] = str(context_path)
        else:
            environment = {**os.environ, "PYTHONPATH": str(ROOT / "runtime"), "PYTHONDONTWRITEBYTECODE": "1"}
            checks = [[sys.executable, "-m", "unittest", "discover", "-s", "tests"],
                      *[[sys.executable, "scripts/" + script] for script in ("validate_skill_quality.py", "validate_governance_behavior.py", "validate_component_catalog.py", "validate_official_docs_catalog.py")],
                      [sys.executable, "scripts/generate_adapters.py", "--check"]]
            for command in checks:
                status = subprocess.run(command, cwd=ROOT, env=environment).returncode
                if status:
                    return status
            result = {"status": "success", "checks": len(checks)}
        print(json.dumps(result, indent=2))
        return 1 if result.get("status") == "blocked" else 0
    except (ValueError, OSError) as exc:
        print(json.dumps({"status": "error", "error": str(exc)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
