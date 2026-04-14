---
description: Sweep component for code quality — JSDoc, formatting, conditions, attributes, .map(), mock separation, lifecycle, template binding — without changing logic or behavior
agent: cells-orchestrator
subtask: true
---

# Cells Cleanup Command

You are a CELLS sub-agent. Read the skill file at `~/.config/opencode/skills/cells-cleanup/SKILL.md` FIRST, then follow its instructions exactly.

CONTEXT:

- Working directory: {workdir}
- Current project: {project}
- Target: {argument}

---

## ABSOLUTE CONSTRAINT: ZERO BEHAVIOR CHANGE

You are in **cleanup mode**. This means:

- ✅ You MAY change how code is written (style, structure, docs, bindings)
- ❌ You MUST NOT change what code does (logic, behavior, public API)

If a change would affect behavior, mark it as a **Suggestion** and do NOT apply it.

---

## TASK

Sweep the file(s) at `{argument}` (or the current working file if no argument given) through all 10 cleanup categories defined in the skill:

| # | Category | Auto-apply? |
|---|----------|-------------|
| 1 | **Formatting** — trailing commas, semicolons, blank lines, `ev` naming convention | ✅ Yes |
| 2 | **JSDoc** — public props, methods, handlers, `_xxxTpl` getters; remove narrative comments | ✅ Yes |
| 3 | **Attribute field** — `attribute:'kebab'` for public, `attribute:false` for private, `reflect:true` for styling props | ✅ Yes |
| 4 | **Conditions by method** — max 2 per method, extract helpers, Rules Table for N validations | ✅ Yes |
| 5 | **Repetitive code** — `push` loops → CONFIG+`.map()`, monolithic render → `_xxxTpl` getters | ✅ Yes |
| 6 | **Template & binding** — property binding for non-strings, `ifDefined`/`nothing`, `firstUpdated` DOM refs, named slots | ✅ Yes (bindings only; slot wrapping = suggest) |
| 7 | **Lifecycle correctness** — `super` calls, `disconnectedCallback` cleanup, no `getAttribute` in constructor | ✅ Yes (flag only for cleanup; no logic added) |
| 8 | **Test mock separation** — shared fixtures, `beforeEach` setup, fixture factories | ✅ Yes (only when test files are explicitly targeted) |
| 9 | **Reusability** — hardcoded values, wrong-layer logic, public prop overwrite antipattern | ⚠️ Suggest only |
| 10 | **Constants** — magic values repeated in 2+ places → `constants.js` | ✅ Auto if duplicate, ⚠️ Suggest if single use |

### For each file

1. Read the full file
2. Identify all findings per category (with exact line numbers)
3. Apply safe changes (categories 1–8)
4. Flag suggestions (category 9, and any category 4.3 / lifecycle behavior changes) without applying them
5. Return the structured cleanup report from the skill

### Quality gates before submitting

- [ ] Every changed method still calls the same downstream functions in the same order
- [ ] No public property, event name, or method name was renamed
- [ ] No new conditional logic was introduced
- [ ] Zero behavior changes — purely structural and documentary
- [ ] Test fixture factories are new files, not modifications to existing tests

---

## Return Format

```
status: ok | partial | blocked
executive_summary: {1 sentence}
cleanup_report: {full markdown report per SKILL.md format — table per category}
suggestions: [{file, line, finding, suggestion}]
next_recommended: "Run /cells-verify to confirm tests still pass after structural changes"
```

---

## Important

- Do NOT run tests or the build — that's `/cells-verify`
- Do NOT suggest feature changes or new functionality
- Source files scope: `src/`, `pages/`, `shared-components/`, `utils/`, `data-manager/`
- Test files scope: `test/` — **only if explicitly included by user**
- Do NOT touch: `demo/locales/`, `.scss`, `.css.js`, `custom-elements.json`
