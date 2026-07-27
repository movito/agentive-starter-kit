# KIT-0069 / PR #95 — Tree-Grounded Verification Record

**Run**: 2026-07-27, planner-f5 orchestrated workflow (8 agents:
6 fixed-row verifiers + special-dispositions auditor + completeness
checker), against merged main at `1bdceac`. ~989k tokens, 252 tool
uses, ~7 min.

**Why this replaced the evaluator trio**: the trio went 0-for-7 on
this PR — diff-only input invites a model to reconstruct the
unchanged side from assumption, and it reconstructs the PRE-fix
state (fd diagnosis, PR body). These verifiers worked from the
merged tree with `grep -Rn` only (`rg` banned per self-review item
16), citing file:line for every verdict.

## Result

| Metric | Value |
|---|---|
| Verdicts | 57 |
| Confirmed | 54 |
| Broken (all minor, same-class residuals) | 3 |
| Uncertain | 0 |
| Completeness | **COMPLETE** — all 54 owned A-numbers dispositioned |

**Completeness detail**: owned set recomputed independently from the
spec's ownership rule (54 = 92 confirmed − 17 KIT-0068 − 7 KIT-0065
− 14 KIT-0067); every owned number present (50 fixed + A56/A82
already-fixed + A74 refuted + A75 deferred). A41/A45 appear as
informational deferred rows matching their spec-assigned owner —
legitimate. One cosmetic inconsistency: the PR body's "Fixed (47)"
header undercounts its own 50-row table (headline "54 owned" is
arithmetically correct).

**Special dispositions**: A74's refutation re-measured independently
(evaluator verdict-vocabulary split confirmed); already-fixed rows
verified against current main; deferred rows traced to covering
owner-task requirements.

## The 3 broken — fixed by planner same-day (behavior-neutral)

1. **A06 residual**: `scripts/core/validate_task_status.py:9`
   docstring still gave the pre-v0.4.0 invocation path → fixed to
   `scripts/core/`.
2. **A79 residual**: `tests/test_linear_sync.py:139` false
   "Import will fail until implementation exists" comment (the exact
   class A78 removed elsewhere) → removed.
3. **A20 residual**: `engine-materials.sh` new comment claimed a
   "testing guide" deleted in ASK-0044; dead excludes for
   `docs/TESTING.md` and `docs/proposals/` (neither exists) →
   comment corrected, dead excludes dropped
   (`tests/test_engine_materials.py` 5/5 after).

## Pattern note

All three breaks are the sibling-instance class (self-review item
15/16 territory) — the fixes named in the rows were correct; the
residuals were adjacent lines. The verification design (per-row
three-part check: old token gone / new claim true / sibling grep)
caught exactly what diff-reading could not.
