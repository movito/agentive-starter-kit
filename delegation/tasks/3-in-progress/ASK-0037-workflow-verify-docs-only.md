# ASK-0037: Workflow Verification — Docs-Only Path

**Status**: In Progress
**Priority**: medium
**Assigned To**: feature-developer-v3
**Estimated Effort**: 15-30 minutes
**Created**: 2026-02-27

## Purpose

**This is a verification task.** Its primary goal is to exercise the v3 workflow
(skills, commands, scripts) on a docs-only change and surface any broken references,
missing files, or permission issues. The deliverable is secondary.

### Workflow Phases Exercised

| Phase | Tool | What We're Testing |
|-------|------|--------------------|
| Start | `/start-task` | Branch creation, `project start` moves file |
| Implement | Manual | Writing a markdown file |
| Commit/PR | `/commit-push-pr` | 7-step commit flow, PR creation |
| CI | `/check-ci` | verify-ci.sh, GitHub Actions |
| Bot review | `/check-bots` | check-bots.sh, docs-only auto-pass logic |
| Retro | `/retro` | Session retrospective generation |

### Phases Intentionally Skipped

- Pre-implementation (no code)
- Self-review (no code)
- Code-review evaluator (no code)
- Preflight (skipped for docs-only per workflow)

## Overview

Create `docs/LINEAR-SYNC-BEHAVIOR.md` — a reference document describing how Linear
sync works in this project. The file is referenced by `planner2.md` line 112 but
does not exist yet.

**Context**: This is a real gap — planner2 references this doc as a "Complete Guide"
but the file is missing. Creating it fixes a broken reference.

## Requirements

### Functional Requirements

1. Create `docs/LINEAR-SYNC-BEHAVIOR.md` documenting:
   - How `./scripts/project linearsync` works
   - Folder → Linear status mapping (1-backlog through 8-archive)
   - Status determination priority (Status field > folder > default)
   - Task-monitor behavior (auto-updates status on file move)
   - Common commands (`project sync-status`, `project linearsync`)
2. Content should be derived from existing knowledge in:
   - `scripts/project` (read help output)
   - `scripts/sync_tasks_to_linear.py` (read module docstring)
   - `scripts/linear_sync_utils.py` (read status mapping)
   - Planner2 agent definition (Linear Sync section)

### Non-Functional Requirements

1. Document should be 100-200 lines (concise reference, not exhaustive)
2. Must include at least one example of each: a sync command, a folder mapping table

## Acceptance Criteria

- [ ] `docs/LINEAR-SYNC-BEHAVIOR.md` exists and is well-structured
- [ ] File is 100-200 lines
- [ ] Contains folder → status mapping table
- [ ] Contains common commands section
- [ ] PR opened via `/commit-push-pr`
- [ ] CI passes (`/check-ci`)
- [ ] Bot review status checked (`/check-bots`)

## Verification Criteria (Workflow Health)

After completion, check:

- [ ] `./scripts/project start ASK-0037` moved file to `3-in-progress/`
- [ ] Feature branch `feature/ASK-0037-*` was created
- [ ] `/commit-push-pr` command executed without errors
- [ ] `/check-ci` returned a result (pass or actionable failure)
- [ ] `/check-bots` returned a result (or "no code changes" auto-pass)
- [ ] `/retro` generated a retrospective
- [ ] No "file not found" or "command not found" errors during workflow

## Notes

- **Agent**: Use `feature-developer-v3` — this is a docs-only task so it should
  automatically skip pre-implementation, self-review, and evaluator phases
- **If workflow breaks**: Document exactly which command/skill failed and what
  error was shown. This IS the purpose of the task.
