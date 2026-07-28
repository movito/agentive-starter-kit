# KIT-0076 Evaluator Review — Cut 0.9.0

**Date**: 2026-07-28
**Evaluator**: code-reviewer-fast ONLY (gemini-2.5-flash, ~$0.01)
**Input**: `.adversarial/inputs/KIT-0076-code-review-input.md` (full format, 10,552 lines)
**Verdict**: CONCERNS
**Mode note**: fast-only per the standing rule for deletion-heavy
diffs (KIT-0069/KIT-0073 lesson: evaluators reconstruct pre-fix state
from diff context; planner tree-grounded verification is the real
merge gate for this PR — requested in the review starter).

## Findings triage (reproduce-or-refute, all verified against the tree)

### F1 — [TESTING] trailing-flag usage-error tests removed (Low)

**Disposition: DECLINED — deliberate re-pin.** The two shim tests
(`test_shape_flag_as_last_arg_is_clean_usage_error`,
`test_profile_flag_as_last_arg_is_clean_usage_error`) pinned
bootstrap-consumer.sh behavior that does not map to the door: on the
door, a trailing valueless `--shape`/`--profile` is an EMPTY value,
which `reject_flaglike` deliberately allows (the resolution chain
falls through to defaults/prompt/usage — comment at
`scripts/local/bootstrap:339-340`). The door's actual trailing-flag
hazard — a following flag swallowed as a value — is pinned in
`test_setup_door.py::TestExitContract::test_mode_flag_must_not_swallow_following_flag`.
Rationale also recorded in the KIT-0054 commit message.

### F2 — [ROBUSTNESS] command injection via `--name`/`--prefix` (High)

**Disposition: REFUTED.** The evaluator flagged this as a blind spot
("code not provided"). Verified `scripts/local/engine-export.sh`
directly: `PROJECT_NAME`/`TASK_PREFIX` are double-quoted at every
expansion (lines 80-99), the prefix derivation pipes `echo "$VAR"`
through tr/sed/awk (no eval), and the current-state.json write passes
both through **environment variables into Python** (lines 184-191) —
no shell interpolation path exists. The hostile-input class is also
already characterized for operator-supplied values
(`test_target_values_written_literally_no_expansion`). This surface
is byte-unchanged by this PR (the door passed `--name`/`--prefix` to
the same engine before, via both channels).

### F3 — [TESTING] `run_offers` failure-path untested (Medium)

**Disposition: DECLINED — out of this diff.** `run_offers` is
untouched by this PR (a removal-only change set); its
warn-and-continue contract predates 0.9.0 and matches the documented
exit contract (verdict reported, never encoded). Noted for the
planner as potential backlog test-hardening; not actioned here per
the action-nothing-unreproduced rule for deletion-heavy diffs.

## Outcome

No code changes from evaluator findings (1 refuted, 2 declined with
rationale). Full log:
`.adversarial/logs/KIT-0076-code-review-input--code-reviewer-fast.md`.
Working tree verified clean after the evaluator run (KIT-0044 rule).
