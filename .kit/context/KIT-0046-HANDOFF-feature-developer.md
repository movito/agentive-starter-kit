# KIT-0046 Handoff — feature-developer

**Task**: `.kit/tasks/2-todo/KIT-0046-project-doctor.md`
**Target Codebase**: This repo — NOT a target repo (single-repo mode)
**Prepared**: 2026-07-14 (planner-f5)
**Estimated effort**: 3–5 hours

You are the feature-developer. Implement this task directly — do not
delegate to another agent instance.

## ⚠️ LAUNCH

**Your repository root is
`/Users/broadcaster_three/Github/ask-worktrees/KIT-0046/`** — created by
`new-worktree.sh` (branch `feature/KIT-0046-project-doctor`, fully
provisioned: `.venv`, `.env`, `.adversarial/evaluators/`). Run
`git pull --ff-only` first — the worktree was cut just before the task
spec landed on main.

## Mission

Build `project doctor` — ADR-0027 P4, the first task of the accepted
transformation sequence. Every check maps to a documented incident from
the v0.8.0 arc (the requirements evidence is the incident table in
`KIT-ADR-0027`'s Context). You are turning the arc's whole failure
class from reactive debugging into a preventive check.

## Context you must not lose

- **The spec is complete and evaluated** — all eight v1 checks, the
  `DOCTOR:` line format with its three-colon field contract, the F3
  exit-code contract (self-review item 8 binds: never overload 0/1),
  the F4 lifecycle rule, and the F5 verify-setup shim are specified in
  the task file. Implement to it; the incident citations belong in each
  check's header comment.
- **N3 is load-bearing**: doctor is strictly read-only. It diagnoses
  the mutation class — it must never join it. No config writes, no env
  edits, no auto-fix.
- **N4**: resolve the primary clone via `git rev-parse
  --git-common-dir`, not cwd — you are running in a worktree yourself,
  which makes this self-testing (your own doctor run must find the
  primary's `core.bare`).
- **Driver seam**: leave `# TODO(P2): per-shape inclusion` where check
  selection happens — P2 will filter checks by the recorded shape, but
  shapes don't exist yet. Don't build them.

## Implementation guidance

- **Driver home**: a `cmd_doctor` in `scripts/core/project` (Python,
  follows `patterns.yml` CLI-layer conventions) iterating
  `scripts/core/doctor.d/*` executables; or a pure-shell driver if that
  composes better with the existing script family — your call, state it
  in the PR. Checks themselves are individually trivial; the value is
  the driver contract + coverage.
- **Skew check (F2.4)**: compare `.venv/bin/pip show <pkg>` vs the
  system `pip show <pkg>` (adversarial-workflow), and active
  `black --version` vs the `pyproject.toml` pin (parse, don't hardcode
  — the pin is exact `==`; remember isort's is a floor and is
  deliberately NOT checked, REVIEW-INSIGHTS has the note).
- **Plugin source check (F2.5)**: `claude plugin marketplace list` style
  detection was hardened in KIT-0035 F4 — reuse the resilient patterns
  from `docs/PLUGIN-UPGRADE-GUIDE.md`, don't re-derive greps (and test
  the rejection cases per TESTING-WORKFLOW.md).
- **Parked-channel check (F2.6)**: detect whether `on: push` exists in
  `sync-core-scripts.yml`; while absent, emit
  `DOCTOR:push-sync-token:SKIP:push channel parked — see KIT-0045`.
- **F4 lifecycle rule**: the retro skill/template lives in
  `.claude/commands/retro.md` (check for a template section) — add the
  closing requirement there; one sentence plus the three-way choice.
- **F5 shim**: `verify-setup.sh` becomes
  `exec ./scripts/core/project doctor` (or equivalent) with a
  deprecation comment; file the removal task as part of the PR
  (backlog task file in the same commit is fine).

## Test approach

- `tests/test_doctor.py`: driver behavior (no short-circuit, exit
  mapping, DOCTOR-line format incl. colons-in-detail), plus fixture
  coverage for skew / env-keys / core.bare per the spec's Test Plan.
  Follow the stub/tmp patterns from `test_preflight_check.py`; the
  suite-wide GIT_* isolation in conftest.py covers you — do not add
  per-module env handling.
- Run the real doctor from BOTH the worktree and the primary clone
  (N4); paste both outputs in the PR description.
- `pytest` directly; `./scripts/core/ci-check.sh` before pushing.
- Mixed script+doc task, code-dominated → normal phase order
  (evaluator trio after PR open is fine; Phase 7 as usual).
- **Post-evaluator rule**: `git status` after every evaluator run
  (code-review-evaluator skill Step 3).

## Evaluation summary

`arch-review-fast`: REVISION_SUGGESTED — one minor finding (detail-field
contract), accepted into F1. Design judged "robust, testable, ready for
growth". Disposition in the task file; log:
`.adversarial/logs/KIT-0046-project-doctor--arch-review-fast.md`.
No outstanding blockers.

## Out of scope

- Shapes/profiles (P2/P1 — seam only), the one door (P3), presets (P7)
- Fixing anything doctor finds (read-only, N3)
- KIT-0041 (stub-harness generalization)
- Downstream repos (their doctor arrives via sync after this merges)

## PR sizing

Single PR (< 450 lines: driver + 8 small checks + shim + tests + retro
rule): branch `feature/KIT-0046-project-doctor` (already created).
