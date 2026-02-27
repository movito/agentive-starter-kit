---
description: Check all 7 completion gates before requesting human review
argument-hint: "[optional --pr PR_NUMBER --task TASK_ID]"
version: 1.0.0
origin: dispatch-kit
origin-version: 0.3.2
last-updated: 2026-02-27
created-by: "@movito with planner2"
---

# Preflight Check

Run all 7 completion gates and present a PASS/FAIL table.

## Step 1: Run the preflight script

```bash
./scripts/preflight-check.sh $ARGUMENTS
```

The script outputs structured `GATE:<number>:<name>:PASS|FAIL:<detail>` lines and exits 0 (all pass) or 1 (any fail).

## Step 2: Present results

Parse the `GATE:` lines and format as a PASS/FAIL table:

| # | Gate | Status | Detail |
|---|------|--------|--------|
| 1 | CI green | PASS/FAIL | [workflow status] |
| 2 | CodeRabbit reviewed | PASS/FAIL | [review state on latest commit] |
| 3 | BugBot reviewed | PASS/FAIL | [review state on latest commit] |
| 4 | Zero unresolved threads | PASS/FAIL | [N total, N resolved, N unresolved] |
| 5 | Evaluator review persisted | PASS/FAIL | [file path or "missing"] |
| 6 | Review starter exists | PASS/FAIL | [file path or "missing"] |
| 7 | Task in correct folder | PASS/FAIL | [folder/file] |

### Verdict

- If all 7 pass: **READY** — proceed with review handoff (move to `4-in-review`, notify user)
- If any fail: **NOT READY (N gates failing)** — list prescriptive actions for each failing gate:
  - Gate 1 fails: "Run `/check-ci` and fix failures"
  - Gate 2 fails: "Wait for CodeRabbit (1-2 min) or run `/check-bots`"
  - Gate 3 fails: "Wait for BugBot (4-6 min) or run `/check-bots`"
  - Gate 4 fails: "Run `/triage-threads` to resolve open threads"
  - Gate 5 fails: "Run the code-review evaluator and persist output"
  - Gate 6 fails: "Create the review starter file"
  - Gate 7 fails: "Run `./scripts/project move <TASK-ID> in-review`"

## Step 3: Emit milestone event (optional, fire-and-forget — requires dispatch-kit)

```bash
dispatch emit preflight_complete --agent feature-developer --task TASK_ID --payload '{"gates_passed":N_PASSED,"gates_failed":N_FAILED}' 2>/dev/null || true
```

Replace `TASK_ID` with the task ID, `N_PASSED` and `N_FAILED` with the actual gate counts from step 2.
