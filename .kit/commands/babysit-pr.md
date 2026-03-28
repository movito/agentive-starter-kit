---
description: Monitor a PR through bot reviews, triage threads, fix issues, and repeat until clean
argument-hint: "[optional PR number]"
version: 1.0.0
origin: agentive-starter-kit
last-updated: 2026-03-25
created-by: "@movito with planner2"
---

# Babysit PR

Monitor the current PR (or PR `$ARGUMENTS`) through bot review cycles.
Wait for bots, triage findings, fix issues, push, and repeat until the PR
is clean or the cycle limit is reached.

> **Shell rule**: Never use `$()` subshells in Bash calls — they trigger
> permission prompts. Run each command as a **separate Bash call** and capture
> values yourself.

## Configuration

| Setting | Value | Notes |
|---------|-------|-------|
| Max cycles | 10 | Prevents infinite fix loops |
| Bot wait timeout | 15 min | Per cycle, via `wait-for-bots.sh` |
| Bots tracked | CodeRabbit, BugBot | Both must be CURRENT before triage |

## Procedure

### Cycle Start

Track which cycle you are on (1 through 10). Report at the start of each cycle:

```
## Babysit Cycle [N]/10 — PR #[number]
```

### Phase 1: Wait for Bots

Run the wait-for-bots script. This polls every 30 seconds until both bots
have reviewed the HEAD commit (or timeout after 15 minutes).

```bash
./scripts/core/wait-for-bots.sh $ARGUMENTS
```

- **Exit 0**: Both bots reviewed HEAD. Proceed to Phase 2.
- **Exit 1**: Timeout. Report which bot is still missing/stale. **Stop babysitting** —
  ask the user to investigate manually with `/check-bots`.

### Phase 2: Triage Threads

Gather thread data (run these as separate Bash calls):

```bash
gh pr view --json number,url,headRefOid --jq '"PR #\(.number) | HEAD: \(.headRefOid)"'
```

```bash
./scripts/core/gh-review-helper.sh threads PR_NUMBER
```

```bash
./scripts/core/gh-review-helper.sh summary PR_NUMBER
```

Present the triage table for **unresolved** threads:

| # | Bot | File:Line | Issue | Severity | Verdict |
|---|-----|-----------|-------|----------|---------|
| 1 | ... | ... | ... | ... | Fix / Resolve |

Use the severity triage from the `bot-triage` skill:
- **Fix**: Real bugs, security, compatibility, reasonable improvements
- **Resolve without fixing**: False positives, cosmetic, platform-irrelevant

### Phase 3: Decision Gate

**If no unresolved threads** (or all are resolve-without-fixing):
- Resolve any remaining trivial threads via GraphQL
- Report: "PR is clean after [N] cycle(s). Ready for human review."
- **Stop babysitting.**

**If fixable threads exist AND this is cycle 10**:
- Report the remaining issues
- Say: "Cycle limit reached (10/10). [N] threads still need attention."
- **Stop babysitting** — let the user decide next steps.

**If fixable threads exist AND cycles remain**:
- Proceed to Phase 4.

### Phase 4: Fix and Push

1. Implement all fixes in a batch (read the affected files, make changes)
2. Run local checks: `./scripts/core/ci-check.sh`
3. Commit with a descriptive message referencing the bot findings
4. Push to the feature branch
5. Reply to each fixed thread:

```bash
./scripts/core/gh-review-helper.sh reply PR_NUMBER COMMENT_ID 'Fixed in COMMIT_SHA: description.'
```

6. Resolve all addressed threads:

```bash
./scripts/core/gh-review-helper.sh resolve PRRT_node_id
```

7. **Go back to Cycle Start** (increment cycle counter).

## Exit Conditions

The babysit loop ends when ANY of these are true:

1. **All clean**: No unresolved threads after bot review — report success
2. **Cycle limit**: 10 cycles completed with issues remaining — report what's left
3. **Bot timeout**: Bots didn't review within 15 minutes — ask user to investigate
4. **CI failure**: Local ci-check.sh fails after a fix — report the failure, stop

## Final Report

Always end with a summary:

```
## Babysit Complete — PR #[number]

| Metric | Value |
|--------|-------|
| Cycles run | [N]/10 |
| Threads fixed | [N] |
| Threads resolved (no fix) | [N] |
| Threads remaining | [N] |
| Status | Clean / Needs attention / Bot timeout / CI failure |

[Next step recommendation]
```

If clean: suggest `/preflight` to run the full completion checklist before human review.
If not clean: describe what remains and suggest next action.
