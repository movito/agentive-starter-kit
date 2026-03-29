# ASK-0046: Relocate handoff files to .kit/delegation/handoffs/

**Status**: Backlog
**Priority**: low
**Assigned To**: feature-developer
**Estimated Effort**: 1-2 hours
**Created**: 2026-03-28

## Related Tasks

**Parent Task**: ASK-0044 (Builder/Project Separation)
**Depends On**: ASK-0044 (must merge PR 1/3 first)

## Overview

Move handoff files (`*-HANDOFF-*.md`) from `.kit/context/` to `.kit/delegation/handoffs/`,
which already has a `.gitkeep` placeholder. This aligns with a cleaner conceptual split:

- `.kit/delegation/` = tasks + handoffs (work items and their transfer docs)
- `.kit/context/` = patterns, workflows, reviews, state (shared coordination infrastructure)

Currently handoffs sit alongside review starters, session handovers, and patterns in
`.kit/context/`, which mixes two concerns.

**Context**: The `.kit/delegation/handoffs/` directory already exists (was moved from
`delegation/handoffs/` in ASK-0044). The handoff files are the only items that belong
there semantically but currently live elsewhere.

## Requirements

### Functional Requirements
1. Move all `*-HANDOFF-*.md` files from `.kit/context/` to `.kit/delegation/handoffs/`
2. Update all path references to handoff files across the codebase:
   - Agent definitions (`.claude/agents/*.md`, `.kit/templates/*.md`)
   - Skills (`.kit/skills/review-handoff/SKILL.md`)
   - Workflows (`.kit/context/workflows/*.md`)
   - Templates (`.kit/templates/TASK-STARTER-TEMPLATE.md`)
   - Dispatch config (`.dispatch/config.yml` — `starter_dir` may need adjustment)
   - Scripts if any reference the handoff path
3. Verify grep shows zero stale references

### Non-Functional Requirements
- [ ] Preserve git history via `git mv`
- [ ] All tests pass after move
- [ ] No functional changes — structural only

## Implementation Plan

### Files to Modify

Grep for `.kit/context/.*HANDOFF` and `.kit/context/<TASK-ID>-HANDOFF` patterns to find
all references. Expected locations:

- `.claude/agents/feature-developer.md` — review handoff section
- `.claude/agents/feature-developer-v3.md` — handoff paths
- `.claude/agents/feature-developer-v5.md` — handoff paths
- `.claude/agents/powertest-runner.md` — handoff paths
- `.kit/templates/TASK-STARTER-TEMPLATE.md` — handoff template reference
- `.kit/skills/review-handoff/SKILL.md` — handoff creation instructions
- `.kit/context/workflows/TASK-COMPLETION-PROTOCOL.md` — if referenced
- `.dispatch/config.yml` — `starter_dir` might need splitting or adjusting

### Approach

1. `git mv .kit/context/*-HANDOFF-*.md .kit/delegation/handoffs/`
2. Update all references from `.kit/context/<ID>-HANDOFF-` to `.kit/delegation/handoffs/<ID>-HANDOFF-`
3. Run full grep verification
4. Run tests

## Acceptance Criteria

### Must Have
- [ ] All handoff files live in `.kit/delegation/handoffs/`
- [ ] Zero stale references to handoffs in `.kit/context/`
- [ ] All tests pass
- [ ] Pre-commit hooks pass

## Risks & Mitigations

### Risk 1: Dispatch config `starter_dir` may assume handoffs and review starters are co-located
**Likelihood**: Medium
**Impact**: Low
**Mitigation**: Check how `starter_dir` is used. If it needs to find both handoffs and
review starters, may need to update the lookup logic or add a second config key.

## Time Estimate

| Phase | Time |
|-------|------|
| Move files + update refs | 30 min |
| Verify + test | 30 min |
| **Total** | **~1 hour** |
