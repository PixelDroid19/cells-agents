"""Structured work routing; the host supplies intent instead of guessing from prose."""

INTENTS = {"question", "edit", "feature", "component-choice", "docs", "test-command", "test-authoring", "coverage", "verify"}


def route_work(intent: str, complexity: str = "small", governed: bool = False, delegation: bool = False) -> dict:
    if intent not in INTENTS or complexity not in {"small", "substantial"}:
        raise ValueError("Unknown work intent or complexity")
    if not isinstance(governed, bool) or not isinstance(delegation, bool):
        raise ValueError("governed and delegation must be booleans")
    if governed or complexity == "substantial" or intent == "feature":
        mode = "full-workflow"
    elif intent in {"question", "component-choice", "docs", "test-command"}:
        mode = "fast-path"
    else:
        mode = "scoped-change"
    skills = {"question": [], "edit": ["cells-apply"], "feature": ["cells-design", "cells-apply"],
              "component-choice": ["cells-components-catalog"], "docs": ["cells-official-docs-catalog"],
              "test-command": ["cells-cli-usage"], "test-authoring": ["cells-cli-usage", "cells-test-creator"],
              "coverage": ["cells-cli-usage", "cells-coverage"], "verify": ["cells-verify"]}[intent]
    return {"mode": mode, "skills": skills, "delegation": delegation and mode == "full-workflow",
            "governed_phases": ["proposal", "spec", "design", "tasks", "apply", "verify"] if governed else [],
            "artifacts_required": governed, "memory_required": False,
            "source_edits_authorized_by": "user task scope, independent of artifact persistence",
            "reason": "Structured host intent; the user may refine scope. No files or agents were created."}
