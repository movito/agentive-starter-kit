---
description: Check if BugBot and CodeRabbit have posted reviews on the current PR
argument-hint: "[optional PR number]"
version: 1.0.0
origin: dispatch-kit
origin-version: 0.3.2
last-updated: 2026-02-27
created-by: "@movito with planner2"
---

# Check Bot Review Status

Check bot review status for the current PR (or PR `$ARGUMENTS` if specified).

## Step 1: Run the check-bots script

```bash
./scripts/check-bots.sh $ARGUMENTS
```

The script outputs structured lines and exits 0 (both bots reviewed HEAD) or 1 (missing/stale).

## Step 2: Report status

Parse the output and format a status report:

### Expected Bots

| Bot | Login | Typical Time |
|-----|-------|-------------|
| BugBot | `cursor[bot]` | 4-6 minutes |
| CodeRabbit | `coderabbitai[bot]` | 1-2 minutes |

### Freshness States

| State | Meaning |
|-------|---------|
| `CURRENT` | Bot reviewed the HEAD commit — safe to proceed |
| `STALE` | Bot posted a review, but on an older commit — re-scan pending, wait |
| `MISSING` | Bot has not posted any review — wait |

**Note**: BugBot reports as a check run (not a review) when it finds no bugs. The script handles this automatically — if `Cursor Bugbot` passed on HEAD, BugBot shows `CURRENT` even without a new review.

### Report Format

```text
## Bot Review Status: PR #[number]

| Bot | Freshness | Latest State |
|-----|-----------|--------------|
| CodeRabbit | CURRENT/STALE/MISSING | [latest state or "waiting"] |
| BugBot | CURRENT/STALE/MISSING | [latest state or "waiting"] |

**HEAD**: [sha]
**Threads**: [total] total, [resolved] resolved, [unresolved] unresolved
**Review Decision**: [APPROVED/CHANGES_REQUESTED/NONE]
```

- Use the `BOT_STATUS:` lines to determine freshness (CURRENT/STALE/MISSING)
- Use the `HEAD_SHA:` line to report the commit being checked
- Use the `REVIEW:` lines to find the latest state per bot
- Use the `THREADS:` line for thread counts

### Next Steps

- **If either bot is STALE**: Bot hasn't re-scanned after latest push. Wait and re-run in 2-3 minutes.
- **If either bot is MISSING**: Bot hasn't posted at all. Note their typical timing above.
- **If both are CURRENT**: Report whether there are unresolved threads that need attention.
- **If unresolved threads exist**: Suggest running `/triage-threads`
