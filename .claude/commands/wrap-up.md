---
description: Finalize session — run retro, emit phase_complete, and confirm completion
version: 1.3.0
last-updated: 2026-04-27
---

# /wrap-up — Finalize Session

Run this as your final action when all work is complete, all gates pass, and the review starter is written.

## Step 0: Detect cross-repo mode

Check if `CLAUDE.md` contains a `## Target Repository` section:

```bash
grep -A 5 "## Target Repository" CLAUDE.md 2>/dev/null || echo "SINGLE_REPO_MODE"
```

If found, extract:
- **target_path**: the value after `- **Path**:` (e.g., `../my-project-code`)
- **target_github**: the value after `- **GitHub**:` (e.g., `your-org/my-project-code`)

If `SINGLE_REPO_MODE`, run all commands against the current repo as before.

### Planning-repo exception

Some tasks (CI fixes, process improvements, agent-spec edits) target the
**planning repo itself**, not the target repo. Detect this by checking the
task's handoff file for the planning-repo directive:

```bash
TASK_ID=$(git branch --show-current | sed -n 's|^feature/\([A-Z][A-Z0-9]*-[0-9][0-9]*\).*|\1|p')
if [ -n "$TASK_ID" ]; then
    HANDOFF=$(ls .kit/context/${TASK_ID}-HANDOFF-*.md 2>/dev/null | head -1)
    # Anchor to the handoff convention line. Two synonyms have appeared in
    # practice (template drift across planner versions):
    #   **Target Codebase**: This repo ...
    #   **Target repo**: **THIS repo** ...
    # Match either label and look for a case-insensitive "this repo" anywhere
    # after the colon (covers `This repo`, `THIS repo`, `**THIS repo**`).
    # Cross-repo handoffs use a path like `**Target repo**: ../my-project-code`
    # and correctly do NOT match.
    if [ -n "$HANDOFF" ] && grep -qiE '^\*\*(Target Codebase|Target repo)\*\*:.*this repo' "$HANDOFF"; then
        echo "PLANNING_REPO_EXCEPTION"
    fi
fi
```

The matcher distinguishes planning-repo-exception handoffs (which say
`**Target Codebase**: This repo` or `**Target repo**: **THIS repo**`) from
cross-repo handoffs (which give a path like `**Target repo**: ../my-project-code`),
which correctly do not match.

If `TASK_ID` cannot be derived from the current branch, the exception is **not**
applied — fall back to the default cross-repo behavior from the previous block,
or ask the user which repo to target.

If `PLANNING_REPO_EXCEPTION` is detected, **stay in single-repo mode** for
the remainder of `/wrap-up` regardless of what `## Target Repository` says
in CLAUDE.md. Both `GIT_TARGET` and `GH_TARGET` resolve to plain `git` and
`gh` against the current (planning) repo.

**For the rest of this document:**
- `GIT_TARGET` means: use `git -C <target_path>` in cross-repo mode, or plain `git` in single-repo mode
- `GH_TARGET` means: use `gh --repo <target_github>` in cross-repo mode, or plain `gh` in single-repo mode

## Step 1: Gather session info

Determine the task ID, agent name, and review starter path:

```bash
GIT_TARGET branch --show-current
```

```bash
GH_TARGET pr view --json number,title --jq '{pr: .number, title: .title}' 2>/dev/null || echo "No PR found"
```

```bash
ls .kit/context/*-REVIEW-STARTER.md 2>/dev/null || echo "No review starter found"
```

If you can't determine the task ID from the branch name, ask the user.

## Step 2: Run /retro

Invoke the `/retro` skill to capture session learnings. This saves the retro to `.kit/context/retros/<TASK-ID>-retro.md`.

The `/retro` command has its own cross-repo detection — it will automatically use the target repo for git/gh operations if configured.

If `/retro` fails (e.g., no PR found), note the failure but continue to Step 3. The phase_complete event is more important than the retro.

## Step 3: Emit phase_complete

Emit the completion event with all relevant metadata. Run each command separately (no `$()` subshells):

First, get the repo owner/name:

```bash
# In cross-repo mode, use the target repo
GH_TARGET repo view --json nameWithOwner --jq .nameWithOwner
```

Then emit the event (substitute values from Steps 1-2):

```bash
dispatch emit phase_complete --agent <AGENT-NAME> --task <TASK-ID> --summary "<brief summary of what was done>"
```

## Step 4: Move task to done

If the PR has been merged (check with `GH_TARGET pr view --json state --jq .state`), move the task to `5-done`:

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
