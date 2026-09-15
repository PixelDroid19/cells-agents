"""Record actual command results separately from reference memory."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import signal
import sqlite3
import subprocess
import tempfile
import time
import uuid

from .policy import assess_command
from .project import project_info, resolve_command


def data_dir() -> Path:
    explicit = os.environ.get("CELLS_AGENT_HOME")
    if explicit:
        return Path(explicit).expanduser().resolve()
    base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData/Local")) if os.name == "nt" else Path(os.environ.get("XDG_STATE_HOME", Path.home() / ".local/state"))
    return base / "cells-agent"


def fingerprint(root: str | Path) -> str:
    """Hash working files, including untracked files, without reading outside symlinks."""
    root = Path(root).resolve()
    proc = subprocess.run(["git", "-C", str(root), "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
                          capture_output=True, timeout=15) if __import__("shutil").which("git") else None
    if proc and proc.returncode == 0:
        names = sorted(set(os.fsdecode(name) for name in proc.stdout.split(b"\0") if name))
    else:
        ignored = {".git", "node_modules", ".cells", "__pycache__", ".venv", "dist", "coverage"}
        names = []
        for base, dirs, files in os.walk(root, followlinks=False):
            dirs[:] = sorted(d for d in dirs if d not in ignored)
            names.extend(str((Path(base) / name).relative_to(root)) for name in files)
        names.sort()
    digest = hashlib.sha256()
    for name in names:
        if Path(name).parts[0] == ".cells":
            continue
        file = root / name
        digest.update(name.encode("utf-8", errors="surrogateescape") + b"\0")
        if file.is_symlink():
            digest.update(b"symlink\0" + os.fsencode(os.readlink(file)))
        elif file.is_file():
            digest.update(str(file.stat().st_mode & 0o111).encode() + b"\0")
            with file.open("rb") as stream:
                for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                    digest.update(chunk)
        else:
            digest.update(b"deleted")
        digest.update(b"\0")
    return digest.hexdigest()


def _connection(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    conn = sqlite3.connect(path, timeout=10)
    conn.execute("CREATE TABLE IF NOT EXISTS evidence (id TEXT PRIMARY KEY, project TEXT NOT NULL, intent TEXT NOT NULL, body TEXT NOT NULL, digest TEXT NOT NULL)")
    if os.name != "nt":
        path.chmod(0o600)
    return conn


def run_check(cwd: str | Path, intent: str, *, timeout: int = 120, store: Path | None = None) -> dict:
    if not 1 <= timeout <= 3600:
        raise ValueError("Timeout must be between 1 and 3600 seconds")
    resolution = resolve_command(cwd, intent)
    if resolution["status"] != "success":
        return resolution
    selected = resolution["selected"]
    for command in selected["commands"]:
        policy = assess_command(command, resolution["root"])
        if policy["decision"] != "allow":
            return {"status": "blocked", "reason": policy["reason"], "resolution": resolution}
    before = fingerprint(resolution["root"])
    started_at = datetime.now(timezone.utc).isoformat()
    started = time.monotonic()
    timed_out = False
    with tempfile.TemporaryFile() as output:
        proc = subprocess.Popen(selected["argv"], cwd=resolution["root"], stdout=output, stderr=subprocess.STDOUT,
                                start_new_session=os.name != "nt")
        try:
            returncode = proc.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
            if os.name != "nt":
                try:
                    os.killpg(proc.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass  # The child can finish between the timeout and the kill.
            else:
                subprocess.run(["taskkill", "/PID", str(proc.pid), "/T", "/F"], capture_output=True)
            returncode = proc.wait()
        size = output.tell()
        output.seek(max(0, size - 16000))
        tail = output.read().decode("utf-8", errors="replace")
    duration = round(time.monotonic() - started, 3)
    after = fingerprint(resolution["root"])
    result = {"id": str(uuid.uuid4()), "project": resolution["project"], "root": resolution["root"],
              "intent": intent, "argv": selected["argv"], "resolved_commands": selected["commands"],
              "started_at": started_at, "duration_seconds": duration,
              "exit_code": returncode, "status": "timed_out" if timed_out else "failed" if returncode else "success" if before == after else "partial",
              "fingerprint_before": before, "fingerprint_after": after, "output_tail": tail,
              "output_truncated": size > 16000, "scope": "working files; ignored files and external environment are not hashed"}
    body = json.dumps(result, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    conn = _connection(store or data_dir() / "evidence.db")
    try:
        with conn:
            conn.execute("INSERT INTO evidence VALUES (?,?,?,?,?)", (result["id"], result["project"], intent, body, hashlib.sha256(body.encode()).hexdigest()))
    finally:
        conn.close()
    return result


def read_evidence(cwd: str | Path, *, store: Path | None = None) -> dict:
    info = project_info(cwd)
    path = store or data_dir() / "evidence.db"
    if not path.exists():
        return {"status": "partial", "records": [], "reason": "No recorded command evidence"}
    conn = sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True)
    try:
        rows = conn.execute("SELECT body,digest FROM evidence WHERE project=? ORDER BY rowid DESC LIMIT 20", (info["project"],)).fetchall()
    finally:
        conn.close()
    current = fingerprint(info["root"])
    records = []
    for body, digest in rows:
        if hashlib.sha256(body.encode()).hexdigest() != digest:
            raise ValueError("Corrupt evidence record")
        value = json.loads(body)
        value.pop("output_tail", None)
        value["current"] = current == value["fingerprint_after"] == value["fingerprint_before"]
        value["passed"] = value["current"] and value["status"] == "success"
        records.append(value)
    latest = {}
    for record in records:
        latest.setdefault(record["intent"], record)
    return {"status": "success" if latest and all(record["passed"] for record in latest.values()) else "partial", "project": info["project"], "records": records,
            "note": "Each record applies only to its command and file fingerprint; it does not prove UI behavior or host authentication."}
