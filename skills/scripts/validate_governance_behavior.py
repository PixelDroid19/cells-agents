#!/usr/bin/env python3
"""Portable smoke checks for the executable work-sizing contract."""
import json
from pathlib import Path
import sys

for ancestor in Path(__file__).resolve().parents:
    if (ancestor / "runtime/cells_agent/workflow.py").is_file():
        sys.path.insert(0, str(ancestor / "runtime"))
        break
else:
    raise SystemExit("Cells runtime missing; install the complete bundle")
from cells_agent.workflow import route_work

checks = {
    "question-no-artifacts": not route_work("question")["artifacts_required"],
    "command-only-skill": route_work("test-command")["skills"] == ["cells-cli-usage"],
    "scoped-no-phase-chain": not route_work("edit")["governed_phases"],
    "memory-optional": not route_work("feature", governed=True)["memory_required"],
    "spec-before-design": route_work("feature", governed=True)["governed_phases"][:4] == ["proposal", "spec", "design", "tasks"],
    "no-automatic-delegation": not route_work("feature")["delegation"],
}
print(json.dumps({"checks": checks, "status": "success" if all(checks.values()) else "failed"}, indent=2))
raise SystemExit(not all(checks.values()))
