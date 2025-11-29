# ASK-0025: Linear Sync Verification

**Status**: Done
**Priority**: medium
**Assigned To**: feature-developer
**Estimated Effort**: 1-2 hours
**Created**: 2025-11-29

## Related Tasks

**Parent Task**: None
**Depends On**: ASK-0005 (Linear Sync Infrastructure)
**Blocks**: None
**Related**: KIT-ADR-0012 (Task Status Linear Alignment)

## Overview

Add verification steps to ensure Linear sync is working after task status changes. Currently, we rely on CI running successfully but don't verify the actual Linear board state, leading to undetected sync failures.

**Why Valuable**: Prevents silent sync failures. Discovered when Linear showed 4 stale tasks in Todo while 24 tasks were actually in Done locally.

## Problem Statement

1. CI shows "success" but we don't verify Linear actually updated
2. No alerting when sync produces unexpected results
3. Process gap: no verification step in commit protocol
4. Stale Linear board discovered only through manual checking

## Acceptance Criteria

### Must Have

- [ ] Add `./project sync-status` command to check last sync
- [ ] Update COMMIT-PROTOCOL.md with sync verification step
- [ ] Add sync verification to planner/tycho agent prompts
- [ ] Log sync results with task counts (created/updated/unchanged)

### Should Have

- [ ] Add `--verify` flag to `./project linearsync` that checks Linear state
- [ ] Warning if local task count differs from Linear issue count
- [ ] Summary of sync in CI job output with link to Linear board

### Could Have

- [ ] Slack/webhook notification on sync completion
- [ ] Dashboard showing sync health metrics
- [ ] Automatic retry on transient failures

## Implementation Notes

### Sync Status Command

```bash
./project sync-status
# Output:
# Last sync: 2025-11-29 02:19:17
# Tasks synced: 24
# Linear issues: 24
# Status: ✅ In sync
```

### Verification in Commit Protocol

Add to `.agent-context/workflows/COMMIT-PROTOCOL.md`:

```markdown
## Post-Push Verification

After pushing changes that affect tasks:
1. Wait for CI to complete
2. Run `./project sync-status` to verify Linear sync
3. Check Linear board if counts don't match
```

### Agent Prompt Addition

Add to planner.md and tycho.md:

```markdown
## Linear Sync Verification

After completing task status changes:
1. Push changes to GitHub
2. Verify CI passes
3. Run `./project sync-status` to confirm Linear is updated
4. If mismatch, run `./project linearsync` manually
```

## Success Metrics

- Zero undetected sync failures
- Sync verification takes < 30 seconds
- Clear error messages when sync fails

## Notes

- Discovered from real incident: 24 tasks in 5-done, Linear showed 4 in Todo
- Root cause: assumed CI success = sync success
- This is a process improvement, not a bug fix

---

**Template Version**: 1.0.0
**Created**: 2025-11-29
