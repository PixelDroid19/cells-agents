---
name: branch-pr
description: >
  PR creation workflow for Cells Agent Bundle following the issue-first enforcement system.
  Trigger: When creating a pull request, opening a PR, or preparing changes for review.
license: MIT
metadata:
  author: Cells Agent Bundle
  version: "1.0"
---

## When to Use

Use this skill when:
- Creating a pull request for any change
- Preparing a branch for submission
- Helping a contributor open a PR

## Critical Rules

1. **Every PR MUST link an approved issue** — no exceptions
2. **Every PR MUST have exactly one `type:*` label**
3. **Automated checks must pass** before merge is possible
4. **Blank PRs without issue linkage will be blocked** by CI validation

## Workflow

```
1. Verify issue has `status:approved` label
2. Create branch: type/description (see Branch Naming below)
3. Implement changes with conventional commits
4. Run validation scripts on modified code
5. Open PR using the template
6. Add exactly one type:* label
7. Wait for automated checks to pass
```

## Branch Naming

Branch names MUST match this regex:

```
^(feat|fix|chore|docs|style|refactor|perf|test|build|ci|revert)\/[a-z0-9._-]+$
```

| Type | Branch pattern | Example |
|------|---------------|---------|
| Feature | `feat/<description>` | `feat/add-cells-coverage-skill` |
| Bug fix | `fix/<description>` | `fix/cells-apply-env-var` |
| Chore | `chore/<description>` | `chore/update-ci-actions` |
| Docs | `docs/<description>` | `docs/update-architecture-doc` |
| Style | `style/<description>` | `style/format-readme` |
| Refactor | `refactor/<description>` | `refactor/extract-shared-logic` |
| Performance | `perf/<description>` | `perf/reduce-setup-time` |
| Test | `test/<description>` | `test/add-setup-coverage` |
| Build | `build/<description>` | `build/update-dependencies` |
| CI | `ci/<description>` | `ci/add-shellcheck` |
| Revert | `revert/<description>` | `revert/broken-setup-change` |

## PR Body Format

Every PR body MUST contain:

### 1. Linked Issue (REQUIRED)

```markdown
Closes #<issue-number>
```

Valid keywords: `Closes #N`, `Fixes #N`, `Resolves #N` (case insensitive).
The linked issue MUST have the `status:approved` label.

### 2. PR Type (REQUIRED)

Check exactly ONE:

| Checkbox | Label to add |
|----------|-------------|
| Bug fix | `type:bug` |
| New feature | `type:feature` |
| Documentation only | `type:docs` |
| Code refactoring | `type:refactor` |
| Maintenance/tooling | `type:chore` |
| Breaking change | `type:breaking-change` |

### 3. Summary

1-3 bullet points of what the PR does.

### 4. Test Plan

```markdown
- [x] `python scripts/validate_governance_behavior.py` passes
- [x] `python scripts/validate_vscode_copilot_assets.py` passes
- [x] Skills load correctly in target agent
```

## Conventional Commits

Commit messages MUST match this regex:

```
^(build|chore|ci|docs|feat|fix|perf|refactor|revert|style|test)(\([a-z0-9\._-]+\))?!?: .+
```

Type-to-label mapping:

| Commit type | PR label |
|-------------|----------|
| `feat` | `type:feature` |
| `fix` | `type:bug` |
| `docs` | `type:docs` |
| `refactor` | `type:refactor` |
| `chore` | `type:chore` |
| `style` | `type:chore` |
| `perf` | `type:feature` |
| `test` | `type:chore` |
| `build` | `type:chore` |
| `ci` | `type:chore` |
| `revert` | `type:bug` |
| `feat!` / `fix!` | `type:breaking-change` |

Examples:
```
feat(skills): add issue-creation and branch-pr skills
fix(scripts): remove legacy agent-teams-lite markers from setup
docs(architecture): add Cells-specific capability comparison table
refactor(skills): extract shared governance contract logic
chore(ci): add validation scripts to PR checks
```
