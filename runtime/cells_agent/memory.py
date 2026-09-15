"""JSON bridge to the separately installed Cells Memory application.

The storage implementation lives in its own repository. This module neither
opens a memory database nor embeds a second copy of that implementation.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess


class LocalMemoryError(RuntimeError):
    """The optional memory application is unavailable or its request failed."""


def memory_database(override: Path | None = None) -> Path:
    """Use the standalone application's store unless an explicit directory is set."""
    if override is not None:
        return override.expanduser().resolve() / "memory.db"
    configured = os.environ.get("CELLS_MEMORY_HOME")
    if configured is not None:
        if not configured.strip():
            raise ValueError("CELLS_MEMORY_HOME must not be blank")
        return Path(configured).expanduser().resolve() / "memory.db"
    base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData/Local")) if os.name == "nt" else Path(os.environ.get("XDG_STATE_HOME", Path.home() / ".local/state"))
    return (base / "cells-memory/memory.db").resolve()


def memory_executable() -> str | None:
    configured = os.environ.get("CELLS_MEMORY_COMMAND")
    if configured:
        return shutil.which(configured)
    command = shutil.which("cells-memory")
    if command:
        return command
    base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData/Local"))
    candidates = [Path.home() / ".local/bin/cells-memory"] if os.name != "nt" else [
        base / "Programs/cells-memory/bin/cells-memory.exe",
        base / "Programs/cells-memory/bin/cells-memory.cmd",
    ]
    return next((str(path) for path in candidates if path.is_file() and os.access(path, os.X_OK)), None)


class LocalMemory:
    """Keep the Cells adapter API while forwarding to one installed backend."""

    def __init__(self, path: str | Path):
        self.path = Path(path).expanduser().resolve()
        self.command = memory_executable()
        if self.command is None:
            raise LocalMemoryError("Cells Memory is not installed. Install the standalone cells-memory application or set CELLS_MEMORY_COMMAND to its executable. See docs/memory.md.")

    def close(self):
        """Requests have no persistent child processes or open databases."""

    def _request(self, project: str, operation: str, arguments: dict | None = None):
        if not isinstance(project, str) or not project.strip():
            raise ValueError("Memory project must be a nonblank string")
        request = {"protocol_version": 1, "database": str(self.path), "project": project,
                   "operation": operation, "arguments": arguments or {}}
        payload = json.dumps(request, ensure_ascii=False, allow_nan=False)
        if len(payload.encode("utf-8")) > 16 * 1024 * 1024:
            raise ValueError("Memory request exceeds 16 MiB")
        try:
            result = subprocess.run([self.command, "request"], input=payload, capture_output=True,
                                    text=True, encoding="utf-8", timeout=30)
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise LocalMemoryError(f"Cells Memory request failed: {exc}") from exc
        if result.returncode:
            raise LocalMemoryError((result.stderr or result.stdout or "Cells Memory exited without a result")[-2000:].strip())
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError as exc:
            raise LocalMemoryError("Cells Memory returned invalid JSON") from exc

    def save(self, project, title, content, kind="note", topic_key=None, source=None):
        return self._request(project, "save", {"title": title, "content": content, "kind": kind, "topic_key": topic_key, "source": source})

    def search(self, project, query, limit=5):
        return self._request(project, "search", {"query": query, "limit": limit})

    def context(self, project, limit=5):
        return self._request(project, "context", {"limit": limit})

    def get(self, project, memory_id):
        return self._request(project, "get", {"id": memory_id})

    def delete(self, project, memory_id):
        return self._request(project, "delete", {"id": memory_id})

    def export_project(self, project):
        return self._request(project, "export")

    def import_data(self, project, data, *, apply=False):
        return self._request(project, "import", {"data": data, "apply": apply})

    def import_engram(self, project, data, source_project=None, *, apply=False):
        return self._request(project, "import-engram", {"data": data, "source_project": source_project or project, "apply": apply})
