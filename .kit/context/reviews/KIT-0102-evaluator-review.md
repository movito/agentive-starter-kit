# KIT-0102 — Evaluator review record (Gate 5)

**Date**: 2026-08-11
**Input**: `.adversarial/inputs/KIT-0102-code-review-input.md` (`--format diff`)
**Run before the PR opened** (KIT-0035 / KIT-0046 ordering rule).

## Tier decision

Ran **`code-reviewer-fast` only**. The deep tier (`code-reviewer`,
`claude-code`) was **skipped deliberately**:

- The diff is ~3,800 net deletions plus prose (docs, ADR headers). Under
  the prose-sweep guidance the deep tier's spend buys little on a
  deletion-shaped change, and `--format diff` was chosen over `full` so
  evaluators would not review whole unchanged modules and return
  findings about code this PR never touched (the KIT-0092 noise class).
- The genuine risk on this task is *enumeration* (did something still
  call the deleted code?), which greps + the full suite answer more
  reliably than an LLM reading a diff. Those ran and are recorded in
  `KIT-0102-enumeration.md`.

## Result: CONCERNS → all three findings dispositioned

Log: `.adversarial/logs/KIT-0102-code-review-input--code-reviewer-fast.md`

### 1. Retired `project sync` lacks tests — VALID, FIXED

New behavior (retirement message + exit 2) shipped with no assertion.
Added to `tests/test_project_script.py`:

- `test_sync_reports_retirement_not_unknown_command` — exit 2, names its
  retirement, points at BOTH replacements (plugin, `linearsync`), and
  never falls through to "Unknown command".
- `test_sync_retirement_ignores_extra_args` — old flags (`--dry-run`,
  `--tier`) don't change the outcome.

**Falsified**: with the `sync` branch removed from `main()`, both tests
fail on the real regression (`assert 1 == 2`, stdout
`❌ Unknown command: sync`); restored, both pass.

### 2. Inconsistent cleanup on consumer re-bootstrap — VALID, FIXED

The strongest finding, and correct. I had swept the retired *workflow*
with `rm -f` but not the engine/manifest/doctor-check. Verified the
mechanism rather than taking the claim on faith:

- `RSYNC_BASE` is `rsync -a --ignore-existing …` — it can never delete.
- The planning-shape `cp` loop is guarded by `[ ! -e ]` — same.

So a consumer bootstrapped before KIT-0102 would keep a dead
`sync_from_manifest.py` and a `.core-manifest.json` pointing at it,
forever. Fixed in `scripts/local/engine-consumer.sh`: both shapes now
sweep `sync_from_manifest.py`, `.core-manifest.json` and
`doctor.d/60-push-sync-token.sh`, matching the existing
`plugin-drift.yml` idiom.

Covered by `test_rebootstrap_sweeps_retired_sync_machinery`, which
plants all four retired files in a bootstrapped consumer and asserts a
re-bootstrap removes them (runs the real door).

### 3. `evaluator_library_version` drift unguarded — ACKNOWLEDGED, no action

Correct but not introduced here: the guard
(`test_library_pin_mirrors_agree`) was deleted in KIT-0079/KIT-0090;
this PR removed its host file. The two pins currently agree (`v0.10.0`),
and the reader move is KIT-0079's scope. This PR replaced the stale
comment (which pointed at a now-deleted test) with an explicit
⚠️ UNGUARDED note naming the manual invariant.

## Verification after fixes

- Full suite: **1088 passed, 13 skipped, 0 failed** (was 1085 — three
  new tests).
- Scaffold acceptance: 26 passed. Plugin drift guard: 17 passed, and the
  live guard reports *"in sync: 27 shipped components match the
  published roster"* — `.claude/` deliberately untouched.
- `project doctor`: 13 pass / 1 warn (pre-existing TASK_PREFIX) / 0 fail.
