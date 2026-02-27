---
description: Fetch and triage all review threads on the current PR
argument-hint: "[optional PR number]"
version: 1.0.0
origin: dispatch-kit
origin-version: 0.3.2
last-updated: 2026-02-27
created-by: "@movito with planner2"
---

# Triage Review Threads

Triage all unresolved review threads on the current PR (or PR `$ARGUMENTS` if specified).

> **Shell rule**: Never use `$()` subshells in Bash calls — they trigger
> permission prompts. Run each command as a **separate Bash call** and capture
> values yourself (e.g., run `gh pr view --json number --jq .number`, note the
> number, then use it in the next call).

## Step 1: Gather thread data

Run these commands **as separate Bash calls** to collect review data.
Capture the PR number from the first call and substitute it into later calls.

```bash
# Get PR number (capture the output — e.g., "40")
gh pr view --json number,url,headRefOid --jq '"PR #\(.number) | URL: \(.url) | HEAD: \(.headRefOid)"'
```

```bash
# All review comments — use the PR number from above
./scripts/gh-review-helper.sh comments PR_NUMBER
```

```bash
# Thread resolution status (resolved, comment-ID, author, GraphQL-ID, body excerpt)
./scripts/gh-review-helper.sh threads PR_NUMBER
```

```bash
# Thread summary
./scripts/gh-review-helper.sh summary PR_NUMBER
```

Replace `PR_NUMBER` with the actual number from the first command.

## Step 2: Present triage table

For all unresolved threads, present a triage table:

| # | Bot | File:Line | Issue (excerpt) | Severity | Verdict |
|---|-----|-----------|-----------------|----------|---------|
| 1 | CodeRabbit | `path.py:42` | ... | Medium | Fix |
| 2 | BugBot | `path.py:88` | ... | Low | Resolve |

Use the severity triage from the `bot-triage` skill:
- **Fix**: Major/Critical, real bugs, security, compatibility
- **Fix (easy)**: Medium severity, reasonable, quick
- **Resolve without fixing**: Trivial/Low, cosmetic, platform-irrelevant

## Step 3: Summarize and confirm

Report: "N threads to fix, M to resolve without fixing"

Ask for confirmation before proceeding with fixes.

## Step 4: Execute (after confirmation)

1. Implement all fixes in a batch
2. Commit and push once
3. Reply to all threads using the **correct endpoint** (see below)
4. Resolve all threads via GraphQL

### Reply to threads

```bash
./scripts/gh-review-helper.sh reply PR_NUMBER COMMENT_ID 'Fixed in {sha}: {description}.'
```

- `COMMENT_ID` is the numeric ID from the `threads` or `comments` output (e.g., `2861292837`)
- Do NOT use node IDs (starting with `PRRC_`)

### Resolve threads

```bash
./scripts/gh-review-helper.sh resolve PRRT_node_id
```

After push: Run `/check-bots` to wait for re-scan, then re-run `/triage-threads` if new findings appear.

**Fix-everything policy**: Fix all legitimate findings regardless of round count. See the `bot-triage` skill for the full policy. Only resolve without fixing when findings are false positives, platform-irrelevant, or contradict project conventions.
