---
description: Wait for BugBot and CodeRabbit to post reviews (polling with backoff)
argument-hint: "[optional PR number]"
version: 1.1.0
origin: dispatch-kit
origin-version: 0.3.2
last-updated: 2026-08-11
created-by: "@movito with planner2"
---

# Wait for Bot Reviews

**First response — open with this transparency header, before any
other output or tool call:**

> 🧭 `/wait-for-bots` — polls until BugBot and CodeRabbit have both
> reviewed the PR's HEAD (30 s interval, 15 min timeout).
> Reads: PR reviews via `scripts/core/wait-for-bots.sh` polling ·
> Writes: nothing
> Source: [wait-for-bots.md](https://github.com/movito/agentive-starter-kit/blob/main/.claude/commands/wait-for-bots.md) · Docs: [review-fix workflow](https://github.com/movito/agentive-starter-kit/blob/main/.kit/context/workflows/REVIEW-FIX-WORKFLOW.md)

Wait for both bots to review the current PR. Polls every 30 seconds for up
to 15 minutes.

## Step 1: Run the wait-for-bots script

```bash
./scripts/core/wait-for-bots.sh $ARGUMENTS
```

The script polls check-bots.sh every 30 seconds and prints progress to stderr.
When both bots are CURRENT, it prints the full status to stdout and exits 0.
If timeout is reached (15 minutes), it exits 1.

## Step 2: Report result

- **If exit 0**: Both bots have reviewed HEAD. Report the final status and
  suggest `/triage-threads` if unresolved threads exist.
- **If exit 1**: Timeout reached. Report which bot(s) are still STALE/MISSING
  and suggest manual investigation with `/check-bots`.

## Options

Override defaults by passing flags:

```bash
./scripts/core/wait-for-bots.sh --interval 15 --timeout 300
```

| Flag | Default | Description |
|------|---------|-------------|
| `--interval SECONDS` | 30 | Poll interval |
| `--timeout SECONDS` | 900 | Max wait time |
| `PR_NUMBER` | auto-detect | Positional PR number |
