## KIT-0084 — New projects start with a working .env (PR #105)

**Date**: 2026-08-04
**Agent**: feature-developer-f5
**Mode**: single-repo
**Scorecard**: 10 threads, 1 regression, 3 fix rounds, 8 commits (7 work + 1 merge of main)

### What Worked

1. **Handoff with verified code anchors** — the planner's F1–F5 → line-number map
   (`apply_env_source:563`, `.env.template:78/81`, `engine-consumer.sh:921`) was
   accurate on arrival; pre-implementation verification confirmed every anchor and
   surfaced the one thing the handoff didn't know (the export engine records the
   derived prefix in `current-state.json`, which became the F2 read source).
2. **Evaluator-before-PR ordering (KIT-0035)** — the trio actioned six findings
   (JSON-null → "None", duplicate identity lines, quote-aware `#` parsing, CR/LF
   strip, quoted printed command, kit-.env mode warning) before any bot round
   burned. claude-code security APPROVED pre-PR is exactly the record a
   secrets-handling PR wants attached.
3. **The `sourced()` unit harness in test_setup_door.py** — `fill_env_identity`
   was testable in isolation (dedup, quoting, null-prefix, no-.env noop) at
   sub-second speed; only the seeding invariants needed the slow e2e door runs.
4. **ScheduleWakeup polling loop** — six rounds (CI dispatch, two CodeRabbit
   rounds, bookkeeping nit, merge-conflict rescue, final confirm) with no
   busy-waiting and clean state carried in each wake-up prompt.

### What Was Surprising

1. **The `pull_request` event never fired for PR #105** — no Tests run was ever
   created for the PR head while other PRs the same day triggered normally.
   Every CI verdict came from manual `gh workflow run test.yml --ref <branch>`
   dispatches (4 runs, all green). Cause unknown (GitHub-side event delivery);
   if it recurs on the next PR it stops being a fluke.
2. **Cost≠value inversion in the trio** — o3 (deep, $0.33) returned FAIL with 4
   of 6 findings rejected as unreachable-or-by-design, while fast-v2 (~$0.01)
   found the two real correctness bugs (JSON-null, duplicate lines). A finding I
   rejected from fast-v2 (first-wins vs last-wins) was then re-raised by
   CodeRabbit with a sharper failure example (`DEMO` then `TASK` passes) and
   flipped to accepted — the reject-with-reasoning loop worked, but cost a round.
3. **`"" in "\"'"` is True** — the classic empty-string-substring gotcha in the
   new `_effective_value` was caught within seconds by the pre-existing
   empty-key doctor test. Fixture depth from earlier incidents paid for itself.
4. **`agent-handoffs.json` blocked the squash-merge** — the planner committed
   KIT-0083/0085 handoffs to main mid-task, touching the same `brief_note`
   lines the feature branch's task-status moves had rewritten. A global mutable
   JSON that both main and every feature branch write is a standing conflict
   generator.

### What Should Change

1. **Stop mutating `agent-handoffs.json` on feature branches** — the
   `project start|move` scripts update it as a side effect, which guarantees
   conflicts whenever the planner also updates it on main mid-task. Either the
   status-file updates should be main-only bookkeeping, or the JSON should be
   split per-agent/per-task. Planner decision needed.
2. **Document the CI dispatch fallback** — when a PR's `pull_request` event
   doesn't fire, `gh workflow run test.yml --ref <branch>` on the same head SHA
   is the evidence-equivalent remedy. Belongs in the check-ci/babysit-pr
   guidance (triage-guide entry below).
3. **Worktree pre-commit needs the venv on PATH** — bare `git commit` in a fresh
   worktree fails the pytest-fast hook with `pytest: command not found`;
   `PATH="$PWD/.venv/bin:$PATH" git commit` is the incantation. Either the hook
   entry should prefer `.venv/bin/pytest` when present, or WORKTREE-WORKFLOW.md
   should state the PATH prefix.
4. **KIT-0082 should assert the seeded-.env invariants** — the acceptance test
   task can now pin: `.env` present, 0600, gitignored, `PROJECT_NAME` filled,
   `TASK_PREFIX` never `TASK` (assertions already modeled in
   `TestEnvSeedingE2E`).

### Permission Prompts Hit

1. `cd <scratchpad>/manual-env-app && stat … && rm -rf <scratchpad>/manual-env-app`
   — denied; retried without the `rm -rf` tail (approved), standalone `rm -rf`
   of the scratchpad dir denied again. No time lost (autonomous session);
   cleanup skipped. `rm -rf` inside the session scratchpad is a candidate
   allow-list pattern, though low value given scratchpads are auto-cleaned.

None other — `gh api graphql` mutations, `gh workflow run`, and worktree git
operations all passed without prompts.

### Process Actions Taken

- [ ] Planner: decide the `agent-handoffs.json` conflict-class fix (main-only
      updates vs per-task split) — recurrence is guaranteed under the current
      parallel-planner/feature-branch pattern
- [ ] Add the CI dispatch fallback to check-ci/babysit-pr guidance (symptom:
      PR open, bots run, zero Tests runs on the head; remedy: `gh workflow run
      test.yml --ref <branch>`, verdict attaches to the same SHA)
- [ ] Fix or document worktree pre-commit PATH (`.venv/bin/pytest` preference
      in the hook entry, or a WORKTREE-WORKFLOW.md note)
- [ ] Fold the seeded-.env invariants into KIT-0082's acceptance assertions
- [ ] Watch the next kit PR for a missing `pull_request` event — one recurrence
      upgrades it from fluke to repo-config incident

### Incident Closure

1. **`pull_request` event not firing (PR #105)** — triage-guide entry: the
   symptom→remedy mapping (no Tests run on PR head → dispatch `test.yml` by
   ref) goes in the check-ci/babysit-pr docs (process action above; placement
   is the planner's call since those skills are canonical/distributed).
2. **Worktree pre-commit `pytest: command not found`** — triage-guide entry in
   WORKTREE-WORKFLOW.md (process action above). Not doctor-checkable cheaply:
   the failure is in git's hook environment, not the worktree state the doctor
   inspects (the existing worktree-venv check already confirms `.venv` exists).
3. **Mutating-hook commit abort (end-of-file-fixer on the review record)** —
   already documented in the feature-developer agent doc (KIT-0057/KIT-0066);
   this session's recurrence followed the documented recovery (`git log` +
   `git status` before proceeding, fresh commit, never `--amend`). No new
   closure needed — the doc held.
4. **KIT-0080 Apple-git local failures (8 doctor + 4 door tests)** — already
   tasked (KIT-0080 S3, in backlog); verified identical on clean main before
   every `SKIP_TESTS=1` use. Existing task is the closure.
