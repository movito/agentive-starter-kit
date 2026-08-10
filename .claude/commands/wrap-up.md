---
description: Finalize session — run retro, move the task to done, and confirm completion
version: 2.1.0
last-updated: 2026-08-09
distribution: builder-only
---

# /wrap-up — Finalize Session

> **Builder-side command**: operates the kit factory; not distributed
> via `scripts/.core-manifest.json` (intended — see KIT-0077).

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

If `/retro` fails (e.g., no PR found), note the failure but continue to
Step 3 — the task move and the completion summary still need to happen.
Carry the failure forward: Step 4's summary must report that the retro
was not written, never print a path to a file that does not exist.

## Step 3: Move task to done

If the PR has been merged (check with `GH_TARGET pr view --json state --jq .state`), move the task to `5-done`:

```bash
./scripts/core/project complete <TASK-ID>
```

If the PR is not yet merged, skip this step — the task stays in `4-in-review`.

## Step 4: Confirm completion

Print a summary for the user. **The header line depends on what Step 3
actually did** — pick the variant that matches, never print COMPLETE by
default.

**Variant A — PR merged, Step 3 ran `project complete`:**

```text
🔬 <AGENT-NAME> | Task: <TASK-ID> — COMPLETE

PR: <PR-URL> (merged)
Task: 5-done
Review starter: .kit/context/<TASK-ID>-REVIEW-STARTER.md
Retro: .kit/context/retros/<TASK-ID>-retro.md
```

**Variant B — PR not merged, Step 3 skipped:**

```text
🔬 <AGENT-NAME> | Task: <TASK-ID> — IN REVIEW (not complete)

PR: <PR-URL> (<open|closed|draft>) — not merged
Task: stays in 4-in-review until the PR merges
Review starter: .kit/context/<TASK-ID>-REVIEW-STARTER.md
Retro: .kit/context/retros/<TASK-ID>-retro.md

Ready for human review.
```

Variant B is the common case at the end of an implementation session —
the session ends when the PR is *ready*, not when it is merged. Printing
COMPLETE there tells the operator work is finished when it is still
awaiting their review, and the task file itself says `4-in-review`,
so the summary would contradict the tree.

Every line is a claim — verify before printing it. If Step 2's `/retro`
failed, replace the retro line with the failure, e.g.:

```text
Retro: NOT WRITTEN — /retro failed (<one-line reason>)
```

Remind the user to `/rename` the session with the task ID for easy `/resume` later.
