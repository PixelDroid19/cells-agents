"""Tiny subprocess test double for the private memory service's JSON boundary."""
from pathlib import Path
import sys


def make_backend(folder: Path) -> Path:
    command = folder / "cells-memory-stub"
    command.write_text("#!" + sys.executable + "\n" + '''import json, pathlib, sys
assert sys.argv[1:] == ["request"]
request = json.load(sys.stdin)
database = pathlib.Path(request["database"])
project, operation, arguments = request["project"], request["operation"], request["arguments"]
if operation == "save":
    result = {"id": 1, "project": project, **arguments}
    database.parent.mkdir(parents=True, exist_ok=True)
    database.write_text(json.dumps(result))
elif operation == "get":
    result = json.loads(database.read_text()) if database.exists() else None
    if result and result["project"] != project:
        result = None
elif operation in {"search", "context"}:
    result = []
elif operation == "export":
    result = {"received": request}
elif operation in {"import", "import-engram"}:
    result = {"received": request}
else:
    raise SystemExit(2)
print(json.dumps(result))
''')
    command.chmod(0o700)
    return command
