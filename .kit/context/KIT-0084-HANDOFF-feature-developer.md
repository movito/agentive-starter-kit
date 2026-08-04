# KIT-0084: Working .env from day one — Implementation Handoff

**You are the feature-developer. Implement this task directly. Do not delegate or spawn other agents.**

**Date**: 2026-08-04
**From**: planner-f5
**To**: feature-developer
**Task**: `.kit/tasks/4-in-review/KIT-0084-working-env-from-day-one.md`
**Status**: Ready for implementation
**Evaluation**: arch-review-fast APPROVED (first pass) —
`.adversarial/logs/KIT-0084-working-env-from-day-one--arch-review-fast.md`

**Target Codebase**: This repo (agentive-starter-kit) — single-repo mode.

---

## Mission

A fresh `bootstrap --new` project must end with a working, safe `.env`:
present, mode 0600, gitignored, `PROJECT_NAME`/`TASK_PREFIX` not silently
wrong, and any key material moved only by the operator. Full requirements
F1–F5 in the task spec; this handoff maps them to code.

## Where each requirement lands (anchors verified 2026-08-04)

- **F1 (door seeds .env)** — `scripts/local/bootstrap:563` already defines
  `apply_env_source()`: preset-named source → target `.env`, refuses when
  `.env` is not gitignored (`:579-580`), `chmod 600` (`:589`), never
  prints contents. Extend the `--new` path so that when NO env-source is
  configured, the door falls back to seeding from the target's own
  `.env.template` with the same discipline (gitignore check, 0600, no
  printing). Reuse the function or factor a sibling — do not duplicate
  the safety checks. The call site / preset validation is around
  `:818-845` (`ENV_SOURCE=""`).
- **F2 (identity fields)** — after seeding, the door rewrites
  `PROJECT_NAME=` (target basename — it already validates/knows it) and
  `TASK_PREFIX=` (single shape: the `--prefix` answer; planning shape:
  no prefix exists at door time — write it EMPTY, never `TASK`).
  Template: `.env.template:78` (`PROJECT_NAME=`), `:81`
  (`TASK_PREFIX=TASK`). Change the template default to `TASK_PREFIX=`
  (empty). Doctor: extend `scripts/core/doctor.d/20-env-keys.py` (115
  lines; reads .env presence/keys today) to WARN when `TASK_PREFIX` is
  empty or `TASK` — actionable message telling the operator where it
  gets decided (intake Step 4a / project onboarding).
- **F3 (operator-consented carry-over)** — when no env-source preset
  exists: TTY runs may ask an explicit consent question naming the exact
  source path before any copy; non-TTY runs print the one-line copy
  command and continue (skip-with-notice, matching the door's existing
  offer pattern). Document the constraint that agents must never move
  key material (the permission classifier blocks it, correctly) in
  `docs/STARTING-A-PROJECT.md` and/or the door's help text.
- **F4 (first-session line)** — `scripts/local/engine-consumer.sh:921`
  seeds the `first-session` region (`FIRST_SESSION_BODY`). Add one
  sentence: verify `./scripts/core/project doctor` env-keys is green
  before the first evaluation. Note `:923` removes the region only if
  unmodified — changing the body text affects that comparison for
  EXISTING consumers on re-bootstrap; check `remove_region_if_unmodified`
  semantics and keep the upgrade path clean.
- **F5 (template honesty)** — fix `.env.template`'s comments around
  `:76-81`: describe the real mechanism (door-seeded; keys carried over
  by the operator or preset env-source), delete the claim that planner
  onboarding fills the fields.

## Data-shape verification

- Consumers of `TASK_PREFIX`/`PROJECT_NAME`: grep `scripts/core/` (the
  `project` CLI and linearsync read them) before changing defaults —
  confirm empty-string behavior degrades loudly, not weirdly.
- The preset parser (`load_preset`, `bootstrap:165+`) and
  `PRESET_KEYS` (`:133`) already include `env-source` — F1's fallback
  must not change preset semantics.

## Test approach

- New/updated tests in `tests/test_doctor.py` for the TASK_PREFIX WARN
  (follow the existing doctor test fixtures).
- Door behavior: extend whatever covers bootstrap (grep `tests/` for
  bootstrap/door harness; if none exists for the seeding path, add a
  minimal bats/pytest-subprocess case: `--new` into a tmpdir → assert
  `.env` exists, mode 0600, `PROJECT_NAME` filled, no secret echoed in
  captured output).
- **Known local red herring**: 8 `tests/test_doctor.py` cases fail on
  this machine's Apple git 2.30.1 (KIT-0080) — pre-existing, not yours.
  CI (newer git) is the gate; don't chase them, don't SKIP_TESTS your
  own new tests.
- `./scripts/core/ci-check.sh` before push; verify CI on GitHub after.

## Out of scope — do not touch

- Preset config-home resolution on Apple git (KIT-0080 S3)
- The adversarial CLI install (KIT-0083) and pin homes (#60/KIT-0079)
- `/setup-preset` skill internals
- No real key values anywhere: tests use dummy strings; never read the
  operator's actual `.env` into fixtures or output

## Evaluation summary

APPROVED first pass. No outstanding concerns. The evaluator's implicit
expectations worth honoring: keep the operator-consent boundary explicit
in help/docs (F3), and don't let the template default regress.

---

**Task File**: `.kit/tasks/4-in-review/KIT-0084-working-env-from-day-one.md`
**Evaluation Log**: `.adversarial/logs/KIT-0084-working-env-from-day-one--arch-review-fast.md`
**Source Issue**: movito/agentive-starter-kit#104 — comment there when the PR opens
