# KIT-0046: `project doctor` — incident-mapped environment verifier (ADR-0027 P4)

**Status**: In Progress
**Priority**: high
**Assigned To**: unassigned
**Estimated Effort**: 3-5 hours
**Created**: 2026-07-14
**Target Completion**: TBD
**Linear ID**: (automatically backfilled after first sync)

## Related Tasks

**Parent**: KIT-ADR-0027 P4 (Accepted 2026-07-14) — first task of the
transformation sequence P4→P2→P1→P3→P5+P7→P6
**Related**: KIT-0035 F1 (the Black drift warning this generalizes),
KIT-0040 (stub-`gh` harness pattern), KIT-0041 (harness generalization —
do not absorb)

## Overview

Turn the v0.8.0 arc's incident table (KIT-ADR-0027, Context §2) into a
standing preventive check: `./scripts/core/project doctor`. Every check
cites the incident that motivated it. The doctor is the
highest-value-per-line proposal of ADR-0027 and has no design
prerequisites — shapes/profiles (P2/P1) don't exist yet, so v1 assumes
today's single/python reality while keeping the check driver ready for
per-shape inclusion later.

## Requirements

### Functional Requirements

- **F1 — composable check driver**: checks live as small executable
  files in `scripts/core/doctor.d/` (one concern per file); a driver
  (`project doctor` subcommand) iterates them all, never stopping on a
  failing check (the fail-fast-masking lesson from the sync workflow).
  Each check emits one structured line —
  `DOCTOR:<name>:<PASS|WARN|FAIL|SKIP>:<detail>` — mirroring the
  preflight `GATE:` format so agents parse both the same way.
  **Field contract** *(from evaluation)*: `<name>` and the verdict are
  colon-free tokens; `<detail>` is everything after the third colon —
  one human-readable sentence, colons permitted (parsers split on the
  first three colons only, exactly as with `GATE:` lines). A
  `--format=json` mode is a noted future option, not v1 scope.
- **F2 — the incident-mapped checks** (v1 set; each check's header
  comment cites its incident):
  1. `gh` installed AND authenticated — backbone-first, inverting
     verify-setup.sh's "optional" (ADR-0027 Context).
  2. `.env` exists; required keys present AND uncommented
     (`ANTHROPIC_API_KEY` commented-out incident, KIT-0032). Never
     print key values — presence/comment-state only.
  3. Evaluator library installed: `.adversarial/evaluators/` non-empty
     ("invalid choice" incident, KIT-0043 worktree).
  4. **Venv-vs-system version skew** for packages where it bit us:
     `adversarial-workflow` (0.9.7 aider-era mutation incident,
     KIT-0044) and `black` vs the `pyproject.toml` pin (KIT-0032
     phantom failure; generalizes KIT-0035 F1 — the ci-check warning
     stays, doctor adds the standing check).
  5. Plugin marketplace source is github, not directory (KIT-0030
     gotcha: a directory source serves disk and defeats pins).
  6. Push-sync secrets — **only if** the push trigger is active in
     `sync-core-scripts.yml`; while parked, SKIP with a pointer to
     KIT-0045 (CROSS_REPO_TOKEN 22/22-failures incident).
  7. `git config core.bare` is `false` in the primary clone (GIT_DIR
     leak incident, KIT-0043).
  8. Bot presence — cheap detection only (e.g. bot check-runs/statuses
     on a recent PR); this is inherently unreliable pre-PR, so cap it
     at WARN/INFO, never FAIL (CodeRabbit quota incident is
     acknowledged as not cheaply checkable — record that in the check's
     comment per the lifecycle rule).
- **F3 — exit-code contract** (self-review item 8 binds): `0` all
  PASS/SKIP, `1` any FAIL, `2` warnings only, `3+` driver/usage errors.
  Document in the driver header; never overload `0`/`1` with
  driver-level failures.
- **F4 — the lifecycle rule** (ADR-0027 P4 refinement (b)): add to the
  retro skill/template a closing requirement — any retro incident must
  yield a doctor check, an explicit "not-checkable" note, or a
  triage-guide entry. This is what keeps doctor from decaying into a
  2026-07-14 snapshot.
- **F5 — `verify-setup.sh` becomes a shim**: it `exec`s `project
  doctor` with a deprecation note, and this PR files its removal task
  (the ADR's shims-with-filed-removal rule, applied early).

### Non-Functional Requirements

- **N1**: shell + `gh` + stdlib Python only; no new dependencies.
- **N2**: full doctor run completes in <10s locally (checks may not
  hit the network except `gh auth status` and the optional bot probe).
- **N3**: doctor is read-only — it never mutates config, env, or the
  working tree (it *diagnoses* the mutation class; it must not join it).
- **N4**: runnable from a worktree; checks that inspect the primary
  clone resolve it via `git rev-parse --git-common-dir`, not cwd
  assumptions.

## Acceptance Criteria

- [ ] `./scripts/core/project doctor` runs all `doctor.d/` checks,
      never short-circuits, emits `DOCTOR:` lines, honors the F3 exit
      contract
- [ ] All eight v1 checks implemented, each citing its incident in a
      header comment
- [ ] Version-skew check catches a deliberately downgraded venv package
      (test with a fixture, not a real downgrade)
- [ ] `verify-setup.sh` shims to doctor; removal task filed
- [ ] Retro skill/template carries the incident-closure lifecycle rule
- [ ] Test coverage via the stub-`gh`/tmp-fixture patterns
      (`tests/test_doctor.py`); driver + at least the skew, env-key,
      and core.bare checks covered
- [ ] Doctor run demonstrated green in the PR description (real run)

## Test Plan

- Unit: driver iteration (one failing check doesn't stop siblings),
  exit-code mapping, DOCTOR-line format.
- Fixtures: fake venv/system version pairs for skew; tmp `.env`
  variants (missing, commented, present); tmp git repo for core.bare.
- Manual: full doctor run in the primary clone AND in a worktree (N4).

## Notes

- Source: KIT-ADR-0027 P4 (Accepted) — the incident table in its
  Context section is the requirements evidence; the two evaluation
  refinements (doctor.d composability, lifecycle rule) are F1 and F4.
- Out of scope: shape/profile awareness (lands with P2/P3 — leave a
  `# TODO(P2): per-shape inclusion` seam in the driver), fixing
  anything doctor finds, generalizing the stub harness (KIT-0041).

## Evaluation (2026-07-14)

`arch-review-fast` (gemini-2.5-flash): **REVISION_SUGGESTED** — one
minor finding ("detail field contract unspecified"), accepted into F1
(three-colon split rule, human-readable sentence; `--format=json`
deferred). Design otherwise judged "robust, testable, and ready for
growth". Log: `.adversarial/logs/KIT-0046-project-doctor--arch-review-fast.md`.
Zero evaluator working-tree mutations.
