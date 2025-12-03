# ASK-0025: Linear Sync Verification - Implementation Handoff

**Date**: 2025-11-29
**From**: Planner Agent
**To**: Feature Developer
**Task**: delegation/tasks/2-todo/ASK-0025-linear-sync-verification.md
**Status**: Ready for implementation
**Evaluation**: N/A (straightforward enhancement)

---

## Task Summary

Add verification capabilities to the Linear sync workflow. Currently we sync to Linear but don't verify the results, leading to undetected sync failures (e.g., 4 tasks stuck in "Todo" despite being in `5-done/` folder).

## Current Situation

- `./scripts/project linearsync` syncs tasks but outputs only "Updated" messages
- No way to verify Linear board matches local state
- CI shows "success" but doesn't verify actual Linear state
- COMMIT-PROTOCOL.md doesn't include sync verification step
- Agent prompts don't mention sync verification

**Recent Incident**: 24 tasks in `5-done/` folder showed as "Todo" in Linear because their Status field was wrong. Discovered only through manual checking.

## Your Mission

Add sync verification at three levels:

1. **CLI Command**: `./scripts/project sync-status` to check sync state
2. **Process Update**: Add verification steps to COMMIT-PROTOCOL.md
3. **Agent Prompts**: Update planner.md and tycho.md with verification guidance

### Phase 1: Sync Status Command (1 hour)

Create `./scripts/project sync-status` that:
- Shows last sync timestamp
- Counts local tasks vs Linear issues
- Reports "In sync" or "Mismatch detected"
- Optional: `--verbose` to show task-by-task comparison

### Phase 2: Process Documentation (30 min)

Update `.agent-context/workflows/COMMIT-PROTOCOL.md`:
- Add "Post-Push Verification" section
- Document when to verify sync
- Document how to fix mismatches

### Phase 3: Agent Prompts (30 min)

Update `.claude/agents/planner.md` and `.claude/agents/tycho.md`:
- Add "Linear Sync Verification" section
- Document when agents should verify sync
- Show `./scripts/project sync-status` usage

## Acceptance Criteria (Must Have)

- [ ] `./scripts/project sync-status` command returns sync state
- [ ] Command shows local task count and Linear issue count
- [ ] Command indicates "In sync" or "Mismatch" status
- [ ] COMMIT-PROTOCOL.md updated with verification step
- [ ] Agent prompts include sync verification guidance

## Success Metrics

**Quantitative**:
- 1 new CLI command (`sync-status`)
- 2 documentation files updated (COMMIT-PROTOCOL.md, agent prompts)
- 0 undetected sync failures (after implementation)

**Qualitative**:
- Clear, actionable sync status output
- Easy-to-follow verification process
- Agents know when and how to verify sync

## Critical Implementation Details

### 1. Sync Status Command Location

Add to `./scripts/project` CLI (already has task management commands):

```python
elif command == "sync-status":
    # Compare local tasks vs Linear issues
    print_sync_status(project_dir)
    sys.exit(0)
```

### 2. Getting Linear Issue Count

Use GraphQL to query team issues:

```python
from gql import gql, Client

query = gql('''
    query TeamIssues($teamId: String!) {
        team(id: $teamId) {
            issues {
                nodes { identifier state { name } }
            }
        }
    }
''')
```

### 3. Output Format

```
Linear Sync Status
==================
Local tasks:  26
Linear issues: 26
Status: ✅ In sync

Last sync: 2025-11-29 02:32:31
```

Or on mismatch:

```
Linear Sync Status
==================
Local tasks:  26
Linear issues: 24
Status: ⚠️  Mismatch detected

Missing in Linear: ASK-0025, ASK-0026
Run: ./scripts/project linearsync
```

## Resources for Implementation

- `./scripts/project` CLI: Current implementation pattern
- `scripts/sync_tasks_to_linear.py`: GraphQL examples
- `.agent-context/workflows/COMMIT-PROTOCOL.md`: Documentation to update
- `.claude/agents/planner.md`: Agent prompt to update
- `.claude/agents/tycho.md`: Agent prompt to update

## Time Estimate

1.5-2 hours total:
- Phase 1 (CLI Command): 1 hour
- Phase 2 (COMMIT-PROTOCOL.md): 30 min
- Phase 3 (Agent Prompts): 30 min

## Starting Point

1. Open `./scripts/project` and add `sync-status` command handler
2. Create `get_linear_issue_count()` function using existing Linear API pattern
3. Create `print_sync_status()` that compares local vs Linear counts
4. Test with `./scripts/project sync-status`
5. Update documentation files

## Questions for Planner

If blocked on:
- Linear API issues: Check `.env` for `LINEAR_API_KEY`
- GraphQL query format: Reference `scripts/sync_tasks_to_linear.py`
- Agent prompt structure: Reference existing sections

## Success Looks Like

```bash
$ ./scripts/project sync-status
Linear Sync Status
==================
Local tasks:  26
Linear issues: 26
Status: ✅ In sync

$ # After commit and push...
$ ./scripts/project sync-status  # Quick verification
```

And agents including sync verification in their workflows:
> "After completing task status changes, I'll run `./scripts/project sync-status` to verify Linear is updated..."

## Notes

- Keep command simple and fast (single API call)
- Don't over-engineer (basic count comparison is sufficient for v1)
- Verbose mode can be added later if needed
- Related to ASK-0026 (Status Field Validation) - tooling improvements

---

**Task File**: `delegation/tasks/2-todo/ASK-0025-linear-sync-verification.md`
**Handoff Date**: 2025-11-29
**Coordinator**: Planner Agent
