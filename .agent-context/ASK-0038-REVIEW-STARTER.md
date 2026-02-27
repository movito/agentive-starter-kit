# ASK-0038 Review Starter: Architecture Overview (CLAUDE.md)

## Quick Context

**Task**: Create root-level `CLAUDE.md` as the primary architecture overview for agents.
**PR**: #21 - `feature/ASK-0038-architecture-overview`
**Agent**: feature-developer-v3
**Type**: Verification task (exercises pre-implementation, bot-triage, review-handoff phases)

## What Changed

1. **`CLAUDE.md`** (new, 103 lines) -- Root-level architecture overview for agent consumption.
   Contains: project description, directory structure, project rules (Python formatting,
   branching/CI, task workflow, defensive coding), agent context (key agents, workflow
   reference), and key scripts table.

2. **Task file moves** -- ASK-0037 moved to `5-done/`, ASK-0038 moved from `2-todo/`
   to `3-in-progress/` then `4-in-review/`.

## Review Checklist

- [ ] CLAUDE.md content is accurate and up-to-date with current project state
- [ ] Directory structure annotations match actual directories
- [ ] Pre-commit hook IDs match `.pre-commit-config.yaml` (fixed in 22830c9)
- [ ] Agent table covers the important agents
- [ ] Workflow reference table links are valid
- [ ] Key scripts table covers essential scripts
- [ ] File is 60-120 lines (actual: 103)
- [ ] References README.md rather than duplicating content

## Bot Review Summary

| Bot | Status | Findings | Actions |
|-----|--------|----------|---------|
| CodeRabbit | Reviewed | 1 actionable (Minor) | Fixed: pre-commit hook names (22830c9) |
| BugBot | Not configured | N/A | N/A |

**Unresolved threads**: 0

## Workflow Verification Notes

This task was also a verification exercise. Phases exercised:

| Phase | Status | Notes |
|-------|--------|-------|
| Pre-implementation | Passed | patterns.yml consulted, no existing CLAUDE.md found |
| Start task | Passed | Branch created, `./scripts/project start` worked |
| Implement | Passed | CLAUDE.md created, 103 lines |
| Commit/PR | Passed | PR #21 created with description |
| CI | Passed | Both runs (initial + fix) succeeded |
| Bot review | Passed | CodeRabbit posted 1 finding, triaged and fixed |
| Bot triage | Passed | Thread replied to and resolved via GraphQL |
| Review handoff | Passed | This file |

### Issues Encountered

- **Branch contamination**: Between CI check and bot review, another tab switched
  the working directory to `main` and a commit from `main` leaked onto the local
  feature branch. Resolved by soft-resetting to the remote branch HEAD.
  Recommendation: enforce branch awareness in the workflow (log current branch
  before each phase gate).

## Files to Review

- `CLAUDE.md`
- `delegation/tasks/4-in-review/ASK-0038-workflow-verify-architecture-overview.md`
