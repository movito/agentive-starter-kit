# ASK-0036: Expand Reconfigure to Catch All Identity Leaks

**Status**: Todo
**Priority**: high
**Assigned To**: feature-developer
**Estimated Effort**: 2-3 hours
**Created**: 2026-02-24
**Target Completion**: 2026-02-26

## Related Tasks

**Related**: ASK-0027 (Project reconfigure command — original implementation)
**Related**: ASK-0034 (Clean the template — complementary cleanup)

## Status History

- **Todo** (from initial) - 2026-02-24 15:10:00

## Overview

Fix the root cause identified in the dispatch-kit tidy audit: `./scripts/project reconfigure` misses many starter-kit-specific references. When a downstream project runs reconfigure, these remnants leak the starter-kit identity into the new project, causing confusion.

**Context**: The `reconfigure` function in `scripts/project` currently updates Serena activation in agent files but misses at least 5 other categories of identity leaks. This task expands reconfigure to catch all known patterns.

## Requirements

### Functional Requirements

The `reconfigure` function in `scripts/project` must replace these patterns when given a new project name:

1. **pyproject.toml comment line 1**: `"# Project configuration for Python projects using the Agentive Starter Kit"` → generic comment
2. **tests/conftest.py docstring**: `"agentive-starter-kit test suite"` → `"<project-name> test suite"`
3. **CHANGELOG.md header**: `"All notable changes to the Agentive Starter Kit"` → `"All notable changes to <project-name>"`
4. **code-reviewer.md task prefix**: `ASK-XXXX` → project-appropriate prefix (user-provided or derived)
5. **Version comparison URLs in planner.md**: `github.com/movito/agentive-starter-kit` → project repo URL

### Pre-computed patterns to find

```bash
# These should all be caught by reconfigure:
grep -rn "agentive-starter-kit" . --include="*.md" --include="*.toml" --include="*.py" \
  | grep -v ".git/" | grep -v "5-done/" | grep -v "8-archive/" | grep -v "node_modules/" \
  | grep -v "docs/archive/"
```

### Files to modify

| File | Current pattern | Replacement |
|------|----------------|-------------|
| `scripts/project` | Add new sed/awk replacement rules in `reconfigure()` function | N/A (this is the file being enhanced) |
| `pyproject.toml` (line 1) | `"for Python projects using the Agentive Starter Kit"` | `"for <project-name>"` |
| `tests/conftest.py` | `"agentive-starter-kit test suite"` | `"<project-name> test suite"` |
| `CHANGELOG.md` | `"All notable changes to the Agentive Starter Kit"` | `"All notable changes to <project-name>"` |
| `.claude/agents/code-reviewer.md` | `ASK-XXXX` throughout | `<PREFIX>-XXXX` (user-provided prefix) |

## Implementation Plan

### Step 1: Audit current reconfigure function

```bash
# Read the reconfigure function
grep -n "reconfigure" scripts/project | head -20
```

Understand what it currently replaces.

### Step 2: Add new replacement patterns

Add sed/awk replacements for the 5 categories above. Follow the existing pattern in the function.

### Step 3: Add a verification step

After reconfigure runs, echo a summary of patterns found vs. replaced. Optionally add a `--verify` flag that runs the grep from Requirements and reports any remaining leaks.

### Step 4: Test

```bash
# Create a temporary copy and run reconfigure with a test project name
# Verify all patterns are replaced
# Verify no false positives (legitimate references preserved)
```

## Acceptance Criteria

### Must Have
- [ ] Running `./scripts/project reconfigure <new-name>` replaces all 5 pattern categories
- [ ] `pyproject.toml` line 1 no longer mentions "Agentive Starter Kit"
- [ ] `tests/conftest.py` docstring uses the new project name
- [ ] `CHANGELOG.md` header uses the new project name
- [ ] All existing tests pass after reconfigure
- [ ] Running the verification grep (see Requirements) returns only legitimate references

### Should Have
- [ ] Reconfigure prints a summary of replacements made
- [ ] `--verify` flag to check for remaining identity leaks

## Test Requirements

- [ ] Test that reconfigure catches pyproject.toml comment
- [ ] Test that reconfigure catches conftest.py docstring
- [ ] Test that reconfigure catches CHANGELOG header
- [ ] Test that after reconfigure, verification grep finds no unexpected references

## Time Estimate

| Phase | Time |
|-------|------|
| Audit current reconfigure | 15 min |
| Implement new patterns | 45 min |
| Add verification | 20 min |
| Testing | 30 min |
| **Total** | **~2 hours** |

## Notes

- The `scripts/project` file is a bash script — review existing sed patterns before adding new ones
- Be careful with sed regex — some patterns contain special characters
- The task prefix replacement (ASK-XXXX → new prefix) requires a user parameter or convention
