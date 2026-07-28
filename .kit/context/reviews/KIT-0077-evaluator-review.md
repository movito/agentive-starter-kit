# KIT-0077 — Evaluator Review Record

**Task**: KIT-0077 (dedup cleanup — context archive, dispatch retirement,
doc archival)
**Branch**: `feature/KIT-0077-dedup-cleanup`
**Date**: 2026-07-28
**Evaluator**: `code-reviewer-fast` (gemini/gemini-2.5-flash) — **fast-only**
**Verdict**: CONCERNS
**Raw log**: `.adversarial/logs/KIT-0077-code-review-input--code-reviewer-fast.md`

## Why fast-only

Per the handoff: this is a mostly-moves diff (104 renames, ~270 reviewable
non-move lines). The deep evaluator's spend buys nothing on a relocation
sweep, and the planner's tree-grounded verification is the real merge gate.
Consistent with the prose-sweep precedent (KIT-0069 trio 0-for-7, KIT-0073
0-for-8).

**Input scoping note**: `prepare-review-input.sh --format full` produced a
910KB input because it inlined all 100 archived handoffs. The input was
rebuilt to cover only the 25 genuinely-modified files (336KB), with a
preamble stating what the moves are and which dispatch surfaces are
deliberately kept. Diff-only input on a move-heavy change is exactly the
setup that made evaluators reconstruct pre-fix state in KIT-0069/0073.

## Triage — 4 findings, 1 actioned

| # | Finding | Disposition |
|---|---------|-------------|
| 1 | `pyproject.toml` 0.9.0 vs `[Unreleased]` CHANGELOG = version mismatch | **REFUTED** |
| 2 | `setup-dev.sh` hard-errors on the removed `--with-dispatch` | **REJECTED (working as designed)** |
| 3 | `context/archive/` exclusion untested for non-task-ID files | **CONFIRMED → FIXED** |
| 4 | `/wrap-up` doesn't report `gh pr view` failure | **OUT OF SCOPE (pre-existing)** |

### 1 — REFUTED

The evaluator inferred that `[Unreleased]` sitting above `## [0.9.0]` means
the project version should already be bumped. That is Keep a Changelog
working as intended: `[Unreleased]` accumulates until a release task cuts
it. This repo's own history confirms the pattern — `21fbfc4`
(`release(KIT-0076): cut 0.9.0`) is what bumped `pyproject.toml` to 0.9.0.
Adding an `[Unreleased]` entry per task is a *required* step in
TASK-COMPLETION-PROTOCOL. No change.

### 2 — REJECTED (working as designed)

The unknown-argument error path is pre-existing; KIT-0077 only removed
`--with-dispatch` from the accepted set. Failing loudly on a removed flag is
the behavior this very script already encodes ("an explicit opt-in that
cannot be met is a failure, never a warning-that-reads-as-success" —
CodeRabbit, PR #98). Silently ignoring it would be the regression. Verified
that every invocation in the tree is flagless (`scripts/local/bootstrap`
:621, `engine-materials.sh`:175), so nothing in-repo breaks; the 2.0.0 bump
is the signal for anything out-of-repo. Manually confirmed:
`setup-dev.sh --with-dispatch` → exit 1 with a usage line.

### 3 — CONFIRMED → FIXED

Reproduced against the tree. `test_no_task_id_files_in_kit_dirs` matches
`^[A-Z]+-\d{4}` only, but `.kit/context/archive/` holds **9 non-task-ID
files** (`README.md`, six dated session records, `CI-CHECKER-FIX-…`,
`RELEASE-0.3.0-…`). Those would leak unnoticed if the wholesale exclude
regressed to a name pattern.

Fixed by `tests/test_engine_materials.py::test_context_archive_not_shipped`,
which pins the directory itself. The export path already had the symmetric
assertion in
`tests/test_setup_door.py::test_new_export_carries_no_planning_corpus`.

Both guards were sabotage-verified: each FAILS with its engine's exclude
removed and PASSES with it restored.

### 4 — OUT OF SCOPE

The `GH_TARGET pr view` step is pre-existing content that KIT-0077 only
renumbered (Step 4 → Step 3) when the dispatch emit step was removed. Real
but unrelated; not introduced here.

## Notes for the planner

- The trio was **not** run in full, by design (see above). Please treat the
  tree-grounded verification as the merge gate, with attention to:
  1. the archive membership rule (terminal folders incl. `8-archive`, plus
     the 8 dated one-offs — judgment calls listed in the PR body);
  2. the dispatch keep/remove line (shipped-and-guarded stays, local
     adoption goes);
  3. the two engine leak fixes.
- Pre-existing dangling doc references found during the link sweep and
  **deliberately not fixed** (out of scope, all absent on `main` too):
  `.kit/context/SERENA-TYPESCRIPT-VALIDATION.md`,
  `.kit/context/TASK-0102-HANDOFF-implementation-agent.md`,
  `.kit/context/workflows/API-TESTING-WORKFLOW.md`,
  `docs/EVALUATION-WORKFLOW.md`, `docs/LINEAR-SYNC-BEHAVIOR.md`,
  `docs/external/api-reference.md`. Worth a follow-up task.
