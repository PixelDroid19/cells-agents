"""Command-line boundary for local Cells services."""
import argparse
import json
import os
from pathlib import Path
import shutil
import sqlite3
import sys

from . import __version__
from .catalogs import search_catalog
from .evidence import data_dir, read_evidence, run_check
from .policy import assess_command, assess_tool
from .project import project_info, resolve_command
from .memory import LocalMemoryError, memory_executable, memory_database
from .workflow import INTENTS as WORK_INTENTS, route_work


def doctor(root: str) -> dict:
    with sqlite3.connect(":memory:") as conn:
        conn.execute("CREATE VIRTUAL TABLE probe USING fts5(text)")
    return {"status": "success", "version": __version__, "python": sys.version.split()[0], "fts5": True,
            "project": project_info(root), "data_directory": str(data_dir()),
            "optional_memory": {"available": memory_executable() is not None, "command": memory_executable(), "database": str(memory_database())},
            "executables": {name: shutil.which(name) for name in ("node", "npm", "cells", "codex", "code", "opencode")},
            "host_execution": "not tested; executable discovery is not an authenticated host run"}


def parser() -> argparse.ArgumentParser:
    top = argparse.ArgumentParser(description="Cells Agent: local project tools, catalogs, evidence and optional memory")
    top.add_argument("--version", action="version", version=__version__)
    top.add_argument("--root", default=os.getcwd(), help="Project directory (defaults to current working directory)")
    top.add_argument("--project", help="Explicit memory namespace; defaults to canonical root identity")
    top.add_argument("--data-dir", type=Path, help="Override user-local memory/evidence directory")
    subs = top.add_subparsers(dest="action", required=True)
    subs.add_parser("doctor")
    subs.add_parser("project")
    route = subs.add_parser("route")
    route.add_argument("intent", choices=sorted(WORK_INTENTS))
    route.add_argument("--complexity", choices=("small", "substantial"), default="small")
    route.add_argument("--governed", action="store_true")
    route.add_argument("--delegation", action="store_true")
    for command in ("resolve", "check"):
        sub = subs.add_parser(command)
        sub.add_argument("intent", choices=("test", "coverage", "lint", "build", "start"))
        if command == "check":
            sub.add_argument("--timeout", type=int, default=120)
    subs.add_parser("evidence")
    policy = subs.add_parser("policy")
    group = policy.add_mutually_exclusive_group(required=True)
    group.add_argument("--command")
    group.add_argument("--stdin", action="store_true", help="Read a native hook payload as JSON")
    hook = subs.add_parser("hook")
    hook.add_argument("event", choices=("SessionStart", "PreToolUse", "Stop"))
    search = subs.add_parser("search")
    search.add_argument("catalog", choices=("components", "docs"))
    search.add_argument("query")
    search.add_argument("--limit", type=int, default=5)
    search.add_argument("--detail", action="store_true")
    memory = subs.add_parser("memory").add_subparsers(dest="operation", required=True)
    save = memory.add_parser("save")
    save.add_argument("--title", required=True)
    save.add_argument("--content", required=True)
    save.add_argument("--kind", default="note")
    save.add_argument("--topic-key")
    save.add_argument("--source")
    for action in ("search", "context"):
        sub = memory.add_parser(action)
        if action == "search":
            sub.add_argument("query")
        sub.add_argument("--limit", type=int, default=5)
    for action in ("get", "delete"):
        memory.add_parser(action).add_argument("id")
    memory.add_parser("export")
    for action in ("import", "import-engram"):
        sub = memory.add_parser(action)
        sub.add_argument("file", type=Path)
        sub.add_argument("--apply", action="store_true", help="Write after inspecting the default dry-run report")
        if action == "import-engram":
            sub.add_argument("--source-project", required=True, help="Select the Engram project explicitly")
    mcp = subs.add_parser("mcp", help="Serve native MCP tools over stdio")
    mcp.add_argument("--memory-write", action="store_true", help="Expose the explicit memory save tool")
    return top


def hook_result(event: str, payload: dict) -> dict:
    if not isinstance(payload, dict):
        raise ValueError("Hook payload must be a JSON object")
    if event == "PreToolUse":
        decision = assess_tool(payload)
        if decision["decision"] == "allow":
            return {}
        return {"hookSpecificOutput": {"hookEventName": event, "permissionDecision": "ask",
                                      "permissionDecisionReason": decision["reason"]}}
    root = payload.get("cwd", os.getcwd()) if isinstance(payload, dict) else os.getcwd()
    if event == "SessionStart":
        info = project_info(root)
        if not info["is_cells"]:
            return {}
        return {"hookSpecificOutput": {"hookEventName": event, "additionalContext":
                f"Cells project {info['name']}. Use the smallest relevant skill and verified project scripts. "
                "Catalog search is bundled. Project memory requires the separately installed Cells Memory application. Memory is optional reference material; validate current files."}}
    # Reminder only: never falsely claim a conversational stop is a verification gate.
    if payload.get("stop_hook_active"):
        return {}
    return {}


def dispatch(args):
    store_dir = args.data_dir.expanduser().resolve() if args.data_dir else data_dir()
    if args.action == "mcp":
        from .mcp import serve
        serve(args.root, args.project, store_dir, memory_write=args.memory_write, memory_path=memory_database(args.data_dir))
        return None
    if args.action == "hook":
        return hook_result(args.event, json.load(sys.stdin))
    if args.action == "policy":
        return assess_tool(json.load(sys.stdin)) if args.stdin else assess_command(args.command, args.root)
    if args.action == "doctor":
        return doctor(args.root)
    if args.action == "project":
        return project_info(args.root)
    if args.action == "route":
        return route_work(args.intent, args.complexity, args.governed, args.delegation)
    if args.action == "resolve":
        return resolve_command(args.root, args.intent)
    if args.action == "check":
        return run_check(args.root, args.intent, timeout=args.timeout, store=store_dir / "evidence.db")
    if args.action == "evidence":
        return read_evidence(args.root, store=store_dir / "evidence.db")
    if args.action == "search":
        return search_catalog(args.catalog, args.query, args.limit, args.detail)
    from .memory import LocalMemory
    namespace = args.project if args.project is not None else project_info(args.root)["project"]
    mem = LocalMemory(memory_database(args.data_dir))
    try:
        op = args.operation
        if op == "save":
            return mem.save(namespace, args.title, args.content, args.kind, args.topic_key, args.source)
        if op == "search":
            return mem.search(namespace, args.query, args.limit)
        if op == "context":
            return mem.context(namespace, args.limit)
        if op in {"get", "delete"}:
            return getattr(mem, op)(namespace, args.id)
        if op == "export":
            return mem.export_project(namespace)
        data = json.loads(args.file.read_text(encoding="utf-8"))
        if op == "import-engram":
            return mem.import_engram(namespace, data, source_project=args.source_project, apply=args.apply)
        return mem.import_data(namespace, data, apply=args.apply)
    finally:
        mem.close()


def main(argv=None) -> int:
    args = parser().parse_args(argv)
    try:
        result = dispatch(args)
        if result is not None:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        unsuccessful = {"blocked", "failed", "timed_out", "error"}
        if args.action == "check":
            unsuccessful.add("partial")
        return 1 if isinstance(result, dict) and result.get("status") in unsuccessful else 0
    except (ValueError, OSError, sqlite3.Error, LocalMemoryError) as exc:
        if args.action == "hook":
            # A broken policy adapter must not silently imply that a command was checked.
            print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "ask", "permissionDecisionReason": f"Cells hook could not validate input: {exc}"}} if args.event == "PreToolUse" else {"systemMessage": f"Cells hook could not validate input: {exc}"}))
        else:
            print(json.dumps({"status": "error", "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2
