---
description: Check all 7 completion gates before requesting human review
argument-hint: "[optional --pr PR_NUMBER --task TASK_ID --repo owner/name]"
version: 1.2.0
origin: dispatch-kit
origin-version: 0.3.2
last-updated: 2026-07-04
created-by: "@movito with planner2"
---

# Preflight Check

Run all 7 completion gates and present a PASS/FAIL table.

## Cross-repo mode (automatic)

`preflight-check.sh` auto-detects cross-repo mode from the
`## Target Repository` section of `CLAUDE.md`. When configured:

- Gates 1–4 (CI, bots, threads) query the target repo via `gh`.
- Branch and `git log` queries read from the target-repo working tree.
- Gates 5–7 (evaluator review, review starter, task folder) still read
  the planning repo's `.kit/` directory — those artifacts always live
  in planning regardless of where code lives.

Override with `--repo owner/name` if needed:

```bash
./scripts/core/preflight-check.sh --repo owner/name --pr PR_NUMBER
```

## Step 1: Run the preflight script

```bash
./scripts/core/preflight-check.sh $ARGUMENTS
```

The script outputs structured `GATE:<number>:<name>:PASS|FAIL|PENDING:<detail>` lines
and exits 0 (all pass), 1 (any fail), or 2 (no failures, but at least one gate PENDING).

**PENDING** (Gate 1 only, KIT-0034): CI runs are not yet registered for the head
SHA, or are still executing — GitHub takes a few seconds to register runs after a
push. PENDING is not a failure verdict; re-run preflight shortly (or use
`/wait-for-bots` first) instead of treating it as a CI failure. Note: when
no runs are registered yet, the script re-polls briefly before reporting,
so a preflight run may block for up to ~10 seconds.

## Step 2: Present results

Parse the `GATE:` lines and format as a PASS/FAIL table:

| # | Gate | Status | Detail |
|---|------|--------|--------|
| 1 | CI green | PASS/FAIL | [workflow status] |
| 2 | CodeRabbit reviewed | PASS/FAIL | [review state on latest commit] |
| 3 | BugBot reviewed | PASS/FAIL | [review state on latest commit] |
| 4 | Zero unresolved threads | PASS/FAIL | [N fresh unresolved, N lingering unresolved] |
| 5 | Evaluator review persisted | PASS/FAIL | [file path or "missing"] |
| 6 | Review starter exists | PASS/FAIL | [file path or "missing"] |
| 7 | Task in correct folder | PASS/FAIL | [folder/file] |

### Verdict

- If all 7 pass: **READY** — proceed with review handoff (move to `4-in-review`, notify user)
- If no gate fails but one is PENDING: **NOT READY YET (pending)** — wait briefly
  and re-run preflight; do not report a CI failure
- If any fail: **NOT READY (N gates failing)** — list prescriptive actions for each failing gate:
  - Gate 1 fails: "Run `/check-ci` and fix failures"
  - Gate 1 PENDING: "CI not registered/still running — re-run preflight in a minute"
  - Gate 2 fails: "Wait for CodeRabbit (1-2 min) or run `/check-bots`"
  - Gate 3 fails: "Wait for BugBot (4-6 min) or run `/check-bots`"
  - Gate 4 fails: "Run `/triage-threads` to resolve open threads" — but first
    distinguish **fresh** from **lingering** threads (see below)
  - Gate 5 fails: "Run the code-review evaluator and persist output"
  - Gate 6 fails: "Create the review starter file"
  - Gate 7 fails: "Run `./scripts/core/project move <TASK-ID> in-review`"

### Fresh vs lingering threads (Gate 4 nuance)

Gate 4 counts unresolved threads, but **not all unresolved threads are equal**.
Distinguish:

- **Fresh threads** — opened on the latest push (commits since the most recent
  `git push`). These reflect active reviewer concerns on current code and
  **must be addressed** (fix or justify-and-resolve) before proceeding.
- **Lingering threads** — opened on an earlier push, left unresolved, but the
  underlying code has since changed and the concern may no longer apply. These
  need to be **verified as stale** (re-read the thread against current code)
  and then resolved with a brief "no longer applicable in {commit_sha}" reply.
  Skip them only if the finding is demonstrably stale.

How to tell them apart:

```bash
# Latest remote HEAD — prefer upstream, fall back to local HEAD
LATEST_PUSH=$(git rev-parse @{push} 2>/dev/null || git rev-parse HEAD)

# List threads with the commit SHA they were opened on
./scripts/core/gh-review-helper.sh threads {pr_number}
# Cross-reference each thread's original commit against LATEST_PUSH:
#   - opened on LATEST_PUSH itself → fresh
#   - opened on an ancestor of LATEST_PUSH → lingering
#   - opened on a commit not in the current history (rebased/squashed away) →
#     treat as lingering and verify stale, since the referenced code may no
#     longer exist in the same form
```

**Rule of thumb**: fresh threads block completion; lingering threads need a
stale-verification pass but are not a blocker if confirmed stale. The preflight
script may report them as a single count — you must still triage the split
manually when Gate 4 fails. If `@{push}` is unset (no upstream yet) or the
classification is otherwise ambiguous, default to treating everything as
fresh — it's cheaper to triage once more than to ship with an unaddressed
reviewer concern.

## Step 3: Emit milestone event (optional, fire-and-forget — requires dispatch-kit)

```bash
dispatch emit preflight_complete --agent feature-developer --task TASK_ID --payload '{"gates_passed":N_PASSED,"gates_failed":N_FAILED}' 2>/dev/null || true
```

Replace `TASK_ID` with the task ID, `N_PASSED` and `N_FAILED` with the actual gate counts from step 2.
