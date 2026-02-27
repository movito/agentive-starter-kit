# ASK-0038: Workflow Verification — Architecture Overview (Pre-Impl + Bot Triage)

**Status**: Todo
**Priority**: medium
**Assigned To**: feature-developer-v3
**Estimated Effort**: 30-60 minutes
**Created**: 2026-02-27
**Depends On**: ASK-0037

## Purpose

**This is a verification task.** Its primary goal is to exercise the pre-implementation
skill, bot-triage skill, and review-handoff skill on a mixed content change (markdown +
configuration). Surfaces broken skill references and bot interaction issues.

### Workflow Phases Exercised

| Phase | Tool | What We're Testing |
|-------|------|--------------------|
| Pre-implementation | `pre-implementation` skill | 10-point checklist, patterns.yml lookup |
| Start | `/start-task` | Branch creation, `project start` |
| Implement | Manual | Creating CLAUDE.md with architecture overview |
| Commit/PR | `/commit-push-pr` | PR creation and description |
| CI | `/check-ci` | CI pipeline |
| Bot review | `/check-bots`, `/triage-threads` | Bot finding receipt and triage |
| Bot triage | `bot-triage` skill | gh-review-helper.sh reply/resolve |
| Review handoff | `review-handoff` skill | Review starter creation |
| Retro | `/retro` | Session retro |

### Phases Intentionally Skipped

- Self-review (no Python code)
- Code-review evaluator (no Python code)
- Full preflight (defer to ASK-0039)

## Overview

Create a root-level `CLAUDE.md` for agentive-starter-kit. This file serves as the
primary architecture overview that agents read when they first enter the project.

**Context**: dispatch-kit has a `CLAUDE.md` at root with architecture overview,
dependency rules, and project rules. The starter-kit has per-agent instructions but
no root-level project overview. Creating one improves agent onboarding and tests
the pre-implementation → bot-triage workflow path.

## Requirements

### Functional Requirements

1. Create `CLAUDE.md` at project root containing:
   - **Project description**: What agentive-starter-kit is (1-2 paragraphs)
   - **Directory structure**: Key directories with brief annotations
   - **Project rules**: TDD, formatting (Black + isort), branching, CI requirements
   - **Agent context**: Where to find agents, skills, commands, workflows, tasks
   - **Key scripts**: `./scripts/project`, `./scripts/ci-check.sh`, etc.
2. Content should be derived from:
   - Existing `README.md` (project description)
   - `.claude/agents/` (agent listing)
   - `.claude/skills/` and `.claude/commands/` (skill/command listing)
   - `.agent-context/workflows/` (workflow listing)
   - `pyproject.toml` (project metadata)

### Non-Functional Requirements

1. File should be 60-120 lines (concise, scannable)
2. Must NOT duplicate README.md content — reference it instead
3. Written for agent consumption (not human documentation)

## Acceptance Criteria

- [ ] `CLAUDE.md` exists at project root
- [ ] Contains project description, directory structure, and project rules
- [ ] References (not duplicates) README.md
- [ ] 60-120 lines
- [ ] Pre-implementation checklist was run (documented in commit or retro)
- [ ] PR opened via `/commit-push-pr`
- [ ] CI passes
- [ ] Bot reviews received and triaged (if any findings)
- [ ] Review starter created at `.agent-context/ASK-0038-REVIEW-STARTER.md`

## Verification Criteria (Workflow Health)

After completion, check:

- [ ] Pre-implementation skill loaded and produced checklist output
- [ ] `patterns.yml` was consulted during pre-implementation
- [ ] `/commit-push-pr` created PR with description
- [ ] `/check-bots` returned bot review status
- [ ] If bots posted findings: `/triage-threads` fetched them successfully
- [ ] If bots posted findings: `bot-triage` skill guided reply/resolve
- [ ] `review-handoff` skill created review starter file
- [ ] `/retro` generated retrospective
- [ ] No "file not found" or "command not found" errors during workflow

## Notes

- **Agent**: Use `feature-developer-v3`
- **Pre-implementation skill**: This is the first real test of the skill in
  starter-kit context. The skill references `patterns.yml` and checks for
  existing implementations — verify it finds our patterns file.
- **Bot findings**: CLAUDE.md may trigger markdown lint findings from bots.
  This is intentional — it exercises the bot-triage path.
- **Depends on ASK-0037**: Run ASK-0037 first to verify the basic workflow
  before exercising more phases.
- **If workflow breaks**: Document exactly which skill/command failed.
