# CELLS Hooks Policy

- Prefer validation checks over destructive automation
- Never default to force push, hard reset, or unsafe archive shortcuts
- If validation fails, report `status: warning | blocked`
- Do not continue to archive/closeout when critical checks fail
