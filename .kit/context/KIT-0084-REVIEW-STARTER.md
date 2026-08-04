# KIT-0084 — Review Starter

**PR**: https://github.com/movito/agentive-starter-kit/pull/105
**Branch**: `feature/KIT-0084-working-env-from-day-one`
**Task**: `.kit/tasks/4-in-review/KIT-0084-working-env-from-day-one.md`
**Source issue**: #104 (commented with the PR link)
**Status**: All gates green — ready for human review

## What shipped (F1–F5)

- **F1**: `bootstrap --new` (both shapes) seeds `.env` — preset
  `env-source` when configured, else the target's own `.env.template`;
  discipline shared in `copy_env_into_target` (gitignore refusal,
  born-0600 umask-first write, contents never printed).
- **F2**: `PROJECT_NAME` filled from the target basename; `TASK_PREFIX`
  from the export engine's recorded prefix (single shape, via
  `current-state.json`) or written empty (planning shape). Template
  default is now `TASK_PREFIX=` (empty); doctor env-keys WARNs while
  it is missing, empty, or `TASK` (last-assignment-wins value read).
- **F3**: key carry-over is operator-consented and operator-executed —
  TTY consent question naming the whole file, or a printed
  `install -m 600` command (non-TTY). Agent/classifier constraint
  documented in the door header and `docs/STARTING-A-PROJECT.md`.
- **F4**: consumer `first-session` region gains the doctor/env-keys
  line, with a legacy-body parameter on `remove_region_if_unmodified`
  so pre-change consumers' `--no-kit` re-bootstraps stay clean.
- **F5**: `.env.template` comments describe the real mechanism.

## Review gates already passed

- **Evaluator trio (pre-PR, per KIT-0035)**: fast-v2 CONCERNS→actioned;
  o3 FAIL→2 actioned / 4 rejected with reasoning; claude-code security
  **APPROVED**. Full triage + embedded logs:
  `.kit/context/reviews/KIT-0084-evaluator-review.md`.
- **Bot threads**: 9 total (CodeRabbit round 1: 7, round 2: 2), every
  one replied and resolved — 8 fixed (last-wins doctor value, dedup
  incl. export/indented forms, quote-aware `#` parsing, atomic
  temp-in-.git rewrite, quoted/`install -m 600` printed command,
  bookkeeping), 1 declined with reasoning (allowlist merge for
  carry-over — contradicts spec F3's wholesale-cp remedy; consent
  wording tightened instead). BugBot: pass on all three rounds.
- **CI**: green on every head — dispatched Tests runs 30945602946,
  30947609291, 30949363925 (lint + Python 3.10/3.12/3.14). ⚠️ Note:
  the `pull_request` event never fired for this PR (other PRs today
  triggered normally); each run above was started with
  `gh workflow run test.yml --ref <branch>` on the same head SHA.
  Worth a planner follow-up if it recurs on the next PR.
- **Local caveat**: the 8 `test_doctor.py`/4 `test_setup_door.py`
  local failures are the known KIT-0080 Apple-git-2.30.1 class,
  verified identical on clean `main`; commits used `SKIP_TESTS=1`
  for that reason only, with all KIT-0084 tests run green directly.

## Suggested review focus

- The operator/agent key-material boundary (F3) — wording and
  mechanism both.
- `fill_env_identity`'s awk rewrite (dedup, quoting, atomic replace).
- The declined CodeRabbit allowlist thread — confirm the disagree
  rationale holds for you.
- Doctor `key_value` last-wins vs `key_state` first-non-empty presence
  scan — the divergence is deliberate and documented.
