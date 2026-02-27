# ASK-0036: Expand Reconfigure to Catch All Identity Leaks

**Status**: In Progress
**Priority**: high
**Assigned To**: feature-developer-v3
**Estimated Effort**: 2-3 hours
**Created**: 2026-02-24
**Updated**: 2026-02-28

## Related Tasks

**Related**: ASK-0027 (Project reconfigure command — original implementation)

## Status History

- **Todo** (from initial) - 2026-02-24 15:10:00
- **Todo** (spec updated with full audit data) - 2026-02-28

## Overview

Expand `./scripts/project reconfigure` to catch identity leaks beyond Serena activation. Currently the function only replaces `activate_project()` calls in agent `.md` files. After pulling upstream, at least 7 additional files still reference "agentive-starter-kit" or "Agentive Starter Kit", confusing downstream projects.

**Context**: Full audit on 2026-02-28 found references in 40+ files. After excluding legitimate references (onboarding.md, docs/decisions/, .agent-context/, .adversarial/), **8 files** need reconfigure treatment beyond what's already handled.

## Current State of `reconfigure_project()`

- **Location**: `scripts/project`, line 177-270
- **What it does now**: Reads project name from `.serena/project.yml`, replaces `activate_project("...")` calls in `.claude/agents/*.md`
- **What it misses**: Everything below

## Requirements

### Files to Handle (8 new, in addition to existing Serena activation)

| # | File | Line | Current Pattern | Replacement |
|---|------|------|----------------|-------------|
| 1 | `pyproject.toml` | 1 | `# Project configuration for Python projects using the Agentive Starter Kit` | `# Project configuration for <project-name>` |
| 2 | `tests/conftest.py` | 2 | `agentive-starter-kit test suite` | `<project-name> test suite` |
| 3 | `CHANGELOG.md` | 3 | `All notable changes to the Agentive Starter Kit` | `All notable changes to <project-name>` |
| 4 | `CHANGELOG.md` | 138-144 | `github.com/movito/agentive-starter-kit` comparison URLs | `<repo-url>` (derived from git remote) |
| 5 | `CLAUDE.md` | 1 | `# Agentive Starter Kit` | `# <Project Name>` |
| 6 | `README.md` | 1 | `# Agentive Starter Kit` | `# <Project Name>` |
| 7 | `scripts/logging_config.py` | 5 | `agentive-starter-kit` | `<project-name>` |
| 8 | `.claude/agents/planner.md` | 543 | `github.com/movito/agentive-starter-kit` | `<repo-url>` |

### Data Sources

The function already reads `project_name` from `.serena/project.yml`. Additionally derive:

- **`repo_url`**: From `git remote get-url origin` — extract `github.com/<owner>/<repo>` for comparison URLs. If git remote fails, skip URL replacements with a warning.
- **`project_title`**: Title-case version of project_name for headings (e.g., `my-cool-project` → `My Cool Project`)

### Files to EXCLUDE (legitimate references)

These files SHOULD reference "agentive-starter-kit" even in downstream projects:

- `.claude/agents/onboarding.md` — guides users through setup FROM the starter kit
- `docs/decisions/starter-kit-adr/` — inherited ADRs documenting kit decisions
- `docs/decisions/adr/README.md` — explains the inherited ADR pattern
- `docs/UPSTREAM-CHANGES-*.md` — upstream merge guides
- `.agent-context/` — historical handoff/review artifacts
- `.adversarial/` — evaluator inputs/outputs (read-only)
- `.serena/project.yml` — this IS the source of truth (not a leak)

### Functional Requirements

1. **Expand pattern matching**: Add replacement rules for the 8 files above
2. **Derive repo URL**: Parse `git remote get-url origin` to get the GitHub path
3. **Title-case project name**: For heading replacements (README, CLAUDE.md)
4. **Print summary**: Show which files were updated, which were skipped, which had errors
5. **Add `--verify` flag**: Run the audit grep after reconfigure and report remaining leaks
6. **Idempotent**: Running reconfigure twice produces the same result

### Non-Functional Requirements

1. Follow existing code patterns in `reconfigure_project()` (regex + read/write)
2. All existing tests must pass after changes
3. New tests for each replacement category

## Implementation Plan

### Step 1: Add helper functions

```python
def _derive_repo_url(project_dir: Path) -> str | None:
    """Extract GitHub repo path from git remote origin."""

def _title_case_project(name: str) -> str:
    """Convert 'my-project' to 'My Project'."""
```

### Step 2: Expand `reconfigure_project()`

Add replacement rules for each of the 8 files. Each rule:
1. Check if file exists
2. Read content
3. Replace pattern (with `re.sub` or string replacement)
4. Write back
5. Report result

### Step 3: Add `--verify` flag

```bash
./scripts/project reconfigure --verify
```

Runs the audit grep and reports any remaining leaks (excluding legitimate references).

### Step 4: Write tests

Test each replacement category:
- pyproject.toml comment
- conftest.py docstring
- CHANGELOG.md header
- CLAUDE.md title
- README.md title
- logging_config.py docstring
- Comparison URL replacement
- Title-case conversion
- Idempotency (run twice, same result)
- `--verify` flag output

## Acceptance Criteria

### Must Have
- [ ] `./scripts/project reconfigure` replaces all 8 pattern categories (plus existing Serena)
- [ ] Repo URL derived from git remote (with graceful fallback)
- [ ] Title-case project name for headings
- [ ] Summary printed showing replacements made
- [ ] All existing tests pass
- [ ] New tests cover each replacement category
- [ ] Running reconfigure twice is idempotent

### Should Have
- [ ] `--verify` flag reports remaining identity leaks
- [ ] Verification excludes legitimate references (onboarding.md, docs/, etc.)

## Verification Command

After reconfigure, this should return only legitimate references:

```bash
grep -rn "agentive-starter-kit\|Agentive Starter Kit" . \
  --include="*.md" --include="*.toml" --include="*.py" --include="*.sh" \
  | grep -v ".git/" | grep -v "5-done/" | grep -v "8-archive/" \
  | grep -v ".venv/" | grep -v ".adversarial/" | grep -v ".agent-context/" \
  | grep -v ".aider" | grep -v "docs/decisions/" | grep -v "docs/archive/" \
  | grep -v "docs/UPSTREAM" | grep -v "onboarding.md" | grep -v "ASK-0036"
```

**Expected**: Zero results after reconfigure runs successfully.

## Time Estimate

| Phase | Time |
|-------|------|
| Read existing code + plan | 15 min |
| Helper functions | 15 min |
| Expand reconfigure (8 patterns) | 45 min |
| Add --verify flag | 15 min |
| Tests (TDD) | 45 min |
| Self-review + spec check | 15 min |
| **Total** | **~2.5 hours** |

## Notes

- This is a Python code task — full v3 workflow applies (TDD, self-review, spec check, bots, evaluator)
- The `scripts/project` file is Python (despite no `.py` extension) — Serena can navigate it
- Serena activation: `mcp__serena__activate_project("agentive-starter-kit")`
- Be careful with regex special characters in file paths and URLs
- The CHANGELOG comparison URLs contain version numbers — use a pattern that matches the URL structure, not specific versions
