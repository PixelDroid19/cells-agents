# CELLS Hooks Policy

Workspace hook template: `.github/hooks/cells-policy.json`.

- Prefer validation checks over destructive automation
- Never default to force push, hard reset, or unsafe archive shortcuts
- Deny destructive terminal commands before tool use
- Ask before generic non-Cells test/start commands when a Cells command exists
- If validation fails, report `status: warning | blocked`
- Do not continue to archive/closeout when critical checks fail
- Hooks are a guardrail, not a substitute for `cells-verify`

## Preview Requirements

VS Code hook loading can depend on Copilot preview availability, workspace trust, extension version, and organization policy. The automated validator confirms JSON shape and script paths; final enablement must be confirmed from VS Code Chat Customizations in the target workspace.

The workspace hook policy runs scripts from `.github/hooks/scripts/`. The optional plugin package installed under `.github/plugin/` uses its own scripts under `.github/plugin/hooks/scripts/` so it can be validated independently from the workspace hook set.
