# KIT-0050 Review Starter — Language Profiles (ADR-0027 P1)

**PR**: https://github.com/movito/agentive-starter-kit/pull/80
**Branch**: `feature/KIT-0050-language-profiles` (worktree
`~/Github/ask-worktrees/KIT-0050`)
**Task**: `.kit/tasks/4-in-review/KIT-0050-language-profiles.md`
**Status**: CI green (lint + tests), BugBot pass, CodeRabbit APPROVED,
0 unresolved threads. Core scripts 3.2.0 → 3.3.0.

## What this PR does

Unwinds the kit's founding presumption: the Python gauntlet stops
being imposed and becomes the seeded default behind one project-owned
hook.

1. **Dispatcher** — `ci-check.sh` runs `scripts/local/checks.sh
   --mode ci` when the hook exists; hook-absent behavior is
   byte-identical to before (characterization pinned BEFORE the change,
   `tests/test_ci_check.py`). Present-but-broken hooks error loudly.
2. **Contract** — `--mode ci|local`, exit 0/1, stdout, repo-root; a
   paragraph in TESTING-WORKFLOW.md + header template in both seeds.
3. **Seeds** — `bootstrap-consumer.sh --profile python|none`; python =
   gauntlet moved verbatim (output byte-equivalent, proven); none =
   loud no-op; planning forces none.
4. **Record/reader** — `kit-install` region gains `profile:`;
   `_doctor_install()` (extends KIT-0048's `_doctor_shape`) returns
   shape+profile with back-compat defaults and fail-loud malformed
   handling; `kit_markers.py` now seeds to single consumers too.
5. **Doctor scoping** — `40-version-skew.py` moves `# shapes: single`
   → `# profiles: python`; driver mechanism generalized
   (`_check_declared`), no if/else.
6. **CLAUDE.md** — kit's Project Rules marker-wrapped (content
   unchanged); consumer rules seeded per profile from that single
   source.

## Where to focus review

- **The trust story**: `tests/test_ci_check.py::TestCharacterization`
  goldens were captured against the pre-change script (commit
  `b4e3761` predates the dispatcher). Verify the dispatcher block in
  `scripts/core/ci-check.sh` sits entirely before the first output.
- **`_doctor_install()`** in `scripts/core/project` — the
  shape×profile default/error matrix, incl. the BugBot round fix:
  unreadable shape poisons the profile (never honor one without the
  other).
- **Bootstrap Step 1.5/2.5** — hook seeding, `append_region_if_absent`
  helper, `--no-kit` interaction (hook/record seed even on opt-out —
  deliberate: they're toolchain-level, not kit-workflow-level).

## Bot rounds (2, both single-finding)

- **BugBot** (real find): valid `profile:` line was honored under an
  unreadable shape, narrowing the promised full check set → fixed
  `ed05b88`, pinned by `test_malformed_shape_never_honors_valid_profile`.
- **CodeRabbit** (trivial): append-if-absent duplication → helper
  extracted `d469d90`.

## Evaluator trio (pre-PR)

fast-v2 CONCERNS · o3 FAIL · claude-code APPROVED. All four o3 bug
claims refuted empirically (first break in its 3/3 real-blocker
streak); its test gaps were real and are pinned. Full dispositions:
`.kit/context/reviews/KIT-0050-evaluator-review.md`.

## Flags for the planner

- **kit_markers.py sync dead-end** (fast-v2): seeded to consumers,
  rides no sync tier, so the record reader can drift from `project`.
  Pre-existing KIT-0048 design; consider a core/ move or manifest
  entry as a follow-up task.
- `ADVERSARIAL_UNATTENDED=1` now exists upstream and is REQUIRED in
  non-TTY contexts (the `echo y |` pipe no longer satisfies the
  guard) — memory/docs referencing the pipe are stale.
- Spec wording: "three toolchain checks" = one doctor.d file
  (`40-version-skew.py`) emitting two DOCTOR lines; profile-scoping
  the file covers the intent.

## Suggested merge

Squash-merge (repo convention). After merge: `project complete
KIT-0050`, remove worktree, delete branch, retro.
