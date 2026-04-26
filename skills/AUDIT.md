# CELLS Skills — Quality Audit (Skill-Creator Framework)

## Methodology
Using skill-creator evaluation criteria:
- **Progressive disclosure**: SKILL.md <500 lines, details in references/
- **Clarity**: Imperative form + WHY explanations
- **Triggers**: Specific but not too narrow, "pushy" enough to avoid undertriggering
- **Reusability**: Works across many prompts, not hardcoded to examples
- **Lean**: No excessive MUST/NEVER/ALWAYS without reasoning
- **Structure**: Proper anatomy (SKILL.md + scripts/ + references/ + assets/)

## Audit Results

### Tier A (Good — minor tweaks only)
| Skill | Lines | Trigger | Structure | Notes |
|-------|-------|---------|-----------|-------|
| `cells-i18n` | 62 | Specific, includes anti-pattern | Clean | Model skill — lean, explains WHY |
| `cells-component-researcher` | 103 | Good, specific intent | Clean | Could trim output template |
| `cells-composition-architect` | 91 | Good | Clean | Focused, no bloat |
| `cells-feature-analyzer` | 93 | Good | Clean | Good evidence requirements |

### Tier B (Needs fixes)
| Skill | Lines | Issues | Fix Priority |
|-------|-------|--------|--------------|
| `cells-cli-usage` | 124 | Good but references missing troubleshooting.md | P2 |
| `cells-coverage` | 107 | References scripts that may not exist | P2 |
| `cells-app-architecture` | 117 | Good, references well-organized | P2 |
| `cells-component-authoring` | ~170 | Fixed in this session | ✅ Done |
| `cells-explore` | 242 | Heavy template duplication | P2 |
| `cells-design` | 242 | Same as explore | P2 |
| `cells-propose` | 211 | Proposal template is large | P2 |
| `cells-spec` | 240 | RFC 2119 table is reference bloat | P2 |
| `cells-tasks` | ~220 | Fixed Go examples in this session | ✅ Done |
| `cells-init` | ~210 | Config YAML inflates size | P2 |
| `cells-archive` | ~200 | Good, delta spec merge logic clear | P2 |

### Tier C (Needs significant fixes)
| Skill | Lines | Issues | Fix Priority |
|-------|-------|--------|--------------|
| `cells-apply` | ~380 | Fixed in this session | ✅ Done |
| `cells-verify` | ~470 | Fixed in this session | ✅ Done |
| `cells-test-creator` | ~270 | Fixed in this session | ✅ Done |
| `agent-browser` | ~80 | Fixed in this session | ✅ Done |

### Tier D (Not Cells-specific)
| Skill | Issue | Recommendation |
|-------|-------|----------------|
| `branch-pr` | GitHub workflow now scoped to Cells contribution flow | Keep in bundle |
| `issue-creation` | GitHub workflow now scoped to Cells contribution flow | Keep in bundle |
| `skill-registry` | "Always" trigger defeats purpose | Fix trigger text |

### Missing
| Skill | Purpose | Status |
|-------|---------|--------|
| `cells-new` | Bridge between explore and propose | ✅ Created in this session |

## What Was Fixed This Session
1. ✅ Replaced Go examples with Cells examples (cells-apply, cells-tasks, cells-verify)
2. ✅ Trimmed agent-browser from 540 to ~80 lines
3. ✅ Reduced cells-apply rules from 22 to 12 (with WHY explanations + code quality rules)
4. ✅ Reduced cells-verify rules from 18 to 12 (with WHY explanations)
5. ✅ Reduced cells-test-creator rules from 19 to 8 principles (with WHY explanations)
6. ✅ Created missing cells-new/SKILL.md
7. ✅ Updated orchestrator prompt with pre-execution checklist
8. ✅ Added code quality rules to cells-apply, cells-component-authoring, cells-test-creator
9. ✅ Added JSDoc compact rule (no blank lines inside blocks) to all 3 skills

## Remaining Work
1. Trim explore/design/spec/propose/init/archive templates to <200 lines
2. Move verbose templates to references/
3. Create eval test suite for critical skills
4. Verify all referenced scripts exist
