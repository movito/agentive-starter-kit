---
description: Finalize session — run retro, emit phase_complete, and confirm completion
---

# /wrap-up — Finalize Session

Run this as your final action when all work is complete, all gates pass, and the review starter is written.

## Step 1: Gather session info

Determine the task ID, agent name, and review starter path:

```bash
git branch --show-current
```

```bash
gh pr view --json number,title --jq '{pr: .number, title: .title}' 2>/dev/null || echo "No PR found"
```

```bash
ls .kit/context/*-REVIEW-STARTER.md 2>/dev/null || echo "No review starter found"
```

If you can't determine the task ID from the branch name, ask the user.

## Step 2: Run /retro

Invoke the `/retro` skill to capture session learnings. This saves the retro to `.kit/context/retros/<TASK-ID>-retro.md`.

If `/retro` fails (e.g., no PR found), note the failure but continue to Step 3. The phase_complete event is more important than the retro.

## Step 3: Emit phase_complete

Emit the completion event with all relevant metadata. Run each command separately (no `$()` subshells):

First, get the repo owner/name:

```bash
gh repo view --json nameWithOwner --jq .nameWithOwner
```

Then emit the event (substitute values from Steps 1-2):

```bash
dispatch emit phase_complete --agent <AGENT-NAME> --task <TASK-ID> --summary "<brief summary of what was done>"
```

## Step 4: Move task to done

If the PR has been merged (check with `gh pr view --json state --jq .state`), move the task to `5-done`:

```bash
./scripts/core/project complete <TASK-ID>
```

If the PR is not yet merged, skip this step — the task stays in `4-in-review`.

## Step 5: Confirm completion

Print a summary for the user:

```text
🔬 <AGENT-NAME> | Task: <TASK-ID> — COMPLETE

PR: <PR-URL>
Review starter: .kit/context/<TASK-ID>-REVIEW-STARTER.md
Retro: .kit/context/retros/<TASK-ID>-retro.md

Ready for human review.
```

Remind the user to `/rename` the session with the task ID for easy `/resume` later.
