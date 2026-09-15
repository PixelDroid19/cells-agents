#!/usr/bin/env python3
"""Install only declared bundle files, preserving conflicts unless explicitly replaced."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import uuid

from bundle import render


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_write(path: Path, content: bytes):
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temp = tempfile.mkstemp(prefix=".cells-", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


def safe_destination(base: Path, relative: str) -> Path:
    path = Path(relative)
    if path.is_absolute() or not path.parts or any(part in {"..", "."} for part in path.parts):
        raise ValueError("Invalid managed relative path")
    result = base / path
    if result.resolve() != result.absolute():
        raise ValueError(f"Refusing symlink target: {relative}")
    return result


def install(agent: str, destination: Path, *, dry_run=False, replace=False, profile="single") -> dict:
    destination = destination.expanduser().absolute()
    if destination.resolve() != destination or destination == Path(destination.anchor):
        raise ValueError("Install destination must be a real, non-root directory")
    kind = {"codex": "codex-home", "opencode": "opencode-home", "vscode": "vscode", "project-local": "project-local", "custom": "project-local"}[agent]
    marker = safe_destination(destination, f".cells-agent-install-{agent}.json")
    old = json.loads(marker.read_text()) if marker.exists() else {"files": {}}
    if not isinstance(old, dict) or not isinstance(old.get("files"), dict) or (marker.exists() and (old.get("format") != "cells-agent-install" or old.get("agent") != agent or old.get("version") != 3)):
        raise ValueError("Invalid installation ownership manifest")
    with tempfile.TemporaryDirectory(prefix="cells-install-") as temp:
        staged = Path(temp)
        render(kind, staged, profile)
        # The installer can resolve exact paths; copy-only portable templates remain relocatable.
        if agent == "codex":
            config = staged / ".codex/config.toml"
            prefix = config.read_text().split("[mcp_servers.cells]", 1)[0]
            config.write_text(prefix + "[mcp_servers.cells]\ncommand = " + json.dumps(sys.executable) + "\nargs = " +
                              json.dumps([str(destination / ".codex/runtime/cells-agent.py"), "mcp"]) + "\n")
        elif agent in {"opencode", "project-local", "custom"}:
            config = staged / (".config/opencode/opencode.json" if agent == "opencode" else ".opencode/opencode.json")
            data = json.loads(config.read_text())
            data["mcp"]["cells"]["command"] = [sys.executable, str(destination / (".config/opencode/runtime/cells-agent.py" if agent == "opencode" else "runtime/cells-agent.py" if agent == "custom" else ".opencode/runtime/cells-agent.py")), "mcp"]
            config.write_text(json.dumps(data, indent=2) + "\n")
        elif agent == "vscode":
            config = staged / ".vscode/mcp.json"
            data = json.loads(config.read_text())
            data["servers"]["cells"]["command"] = sys.executable
            config.write_text(json.dumps(data, indent=2) + "\n")
        if agent == "custom":
            source_root = staged / ".opencode"
            # Custom uses a bundle root so runtime and skill-relative links remain valid.
            files = {str(p.relative_to(source_root)): p for p in source_root.rglob("*") if p.is_file()}
        else:
            files = {str(path.relative_to(staged)): path for path in staged.rglob("*") if path.is_file() and path.name != ".cells-bundle.json"}
        changes, removals, conflicts, unchanged = [], [], [], 0
        for relative, source in sorted(files.items()):
            target = safe_destination(destination, relative)
            source_hash = digest(source)
            if target.exists() and not target.is_file():
                raise ValueError(f"Target is not a regular file: {relative}")
            current_hash = digest(target) if target.exists() else None
            if current_hash == source_hash:
                unchanged += 1
            elif current_hash and old["files"].get(relative) != current_hash and not replace:
                conflicts.append(relative)
            else:
                changes.append(relative)
        for relative, previous_hash in old["files"].items():
            if relative in files:
                continue
            target = safe_destination(destination, relative)
            if not target.exists():
                continue
            if not target.is_file():
                raise ValueError(f"Obsolete managed target is not a file: {relative}")
            if digest(target) == previous_hash or replace:
                removals.append(relative)
            else:
                conflicts.append(relative)
        result = {"status": "blocked" if conflicts else "success", "agent": agent, "destination": str(destination),
                  "profile": profile, "dry_run": dry_run, "changed_files": len(changes), "removed_files": len(removals), "unchanged_files": unchanged,
                  "conflicts": conflicts, "applied": False, "memory_migrated": False}
        if dry_run or conflicts:
            result["planned_files"] = changes
            result["planned_removals"] = removals
            if conflicts:
                result["reason"] = "Existing files differ from managed versions. Review them; --replace explicitly backs up and replaces these bundle paths. Nothing was written."
            return result
        backup = destination / ".cells-agent-backups" / (datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S") + "-" + uuid.uuid4().hex[:8])
        rollback = []
        try:
            for relative in removals:
                target = safe_destination(destination, relative)
                previous = target.read_bytes()
                rollback.append((target, previous))
                atomic_write(safe_destination(backup, relative), previous)
                target.unlink()
            for relative in changes:
                target = safe_destination(destination, relative)
                previous = target.read_bytes() if target.exists() else None
                rollback.append((target, previous))
                if previous is not None:
                    atomic_write(safe_destination(backup, relative), previous)
                atomic_write(target, files[relative].read_bytes())
            new = {"format": "cells-agent-install", "version": 3, "agent": agent, "profile": profile,
                   "files": {relative: digest(source) for relative, source in sorted(files.items())}}
            marker_bytes = (json.dumps(new, indent=2) + "\n").encode()
            if not marker.exists() or marker.read_bytes() != marker_bytes:
                atomic_write(marker, marker_bytes)
        except OSError:
            for target, previous in reversed(rollback):
                if previous is None:
                    target.unlink(missing_ok=True)
                else:
                    atomic_write(target, previous)
            raise
        result["applied"] = True
        if backup.exists():
            result["backup"] = str(backup)
        result["note"] = "Bundle files installed. Enable native customizations/MCP in the host; this result does not prove an authenticated agent session."
        return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--agent", required=True, choices=("codex", "opencode", "vscode", "project-local", "all-global", "custom"))
    parser.add_argument("--path", type=Path, help="Install root; custom uses a bundle root with skills and runtime")
    parser.add_argument("--home", type=Path, default=Path.home(), help="Explicit home root for global installation/testing")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--replace", action="store_true", help="Back up and replace conflicting bundle files")
    parser.add_argument("--profile", choices=("single", "multi"), default="single")
    args = parser.parse_args()
    try:
        agents = ["opencode", "codex"] if args.agent == "all-global" else [args.agent]
        if args.agent == "custom" and args.path is None:
            parser.error("custom requires --path (bundle root)")
        targets = [(agent, args.path or (args.home if agent in {"codex", "opencode"} else Path.cwd())) for agent in agents]
        # Resolve every conflict before changing either global host installation.
        reports = [install(agent, dest, dry_run=True, replace=args.replace, profile=args.profile) for agent, dest in targets]
        if not args.dry_run and all(report["status"] == "success" for report in reports):
            reports = []
            for agent, dest in targets:
                result = install(agent, dest, replace=args.replace, profile=args.profile)
                reports.append(result)
                if result["status"] == "blocked":
                    break  # A concurrent edit can invalidate the preflight.
        print(json.dumps(reports[0] if len(reports) == 1 else reports, indent=2))
        return 1 if any(report["status"] == "blocked" for report in reports) else 0
    except (ValueError, OSError) as exc:
        print(json.dumps({"status": "error", "error": str(exc)}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
