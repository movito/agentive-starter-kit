# ASK-0041: Housekeeping — Loose Ends Cleanup

**Status**: Todo
**Priority**: Low
**Created**: 2026-03-04

## Summary

Clean up loose ends identified after the v0.3.3 release.

## Tasks

### 1. Triage stale PR #14

- **PR**: [#14 — Add PR comment triage-reply-resolve workflow to feature-developer](https://github.com/movito/agentive-starter-kit/pull/14)
- **Opened**: 2026-02-12
- **Action**: Review whether this is still relevant. Merge, update, or close.

### 2. Handle untracked runtime artifacts

- `.agent-context/retros/` — retro output directory. Decide: commit (if content is worth keeping) or add to `.gitignore`.
- `.dispatch/bus.jsonl` — dispatch-kit event bus. Runtime artifact, likely should be gitignored.

## Acceptance Criteria

- [ ] PR #14 resolved (merged or closed with explanation)
- [ ] `.agent-context/retros/` either committed or gitignored
- [ ] `.dispatch/bus.jsonl` gitignored
