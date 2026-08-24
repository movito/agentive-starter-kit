# KIT-0120: Mechanize preflight Gate 8 (review pass) in the agentive CLI

**Status**: Backlog
**Priority**: low
**Assigned To**: unassigned
**Estimated Effort**: 0.5-1 day
**Created**: 2026-08-24

## Related Tasks

**Parent Task**: KIT-0116 (Phase 1 created the gate)
**Related**: KIT-0114 (same extraction direction: executable gate logic
out of markdown, into the CLI)

## Overview

KIT-0116 Phase 1 added completion Gate 8 — "review pass done", a
non-empty `.kit/context/reviews/<TASK-ID>-review-pass.md` — to the
`/preflight` command as a **session-checked** gate. The `agentive
preflight` engine still emits mechanical gates 1–7 only.

The gate was deliberately NOT added to the engine in Phase 1:

1. **Version skew**: the engine ships via PyPI (`agentive-kit`), the
   command markdown via the plugin release train. A markdown that
   required `GATE:8` from the CLI would break every consumer whose
   `agentive-kit` install lags the plugin. The session-checked layer is
   forward- and backward-compatible.
2. **Matrix cost**: `tests/test_preflight_check.py` is a 1174-line
   behavior matrix pinning the 7-gate contract; growing it belongs in a
   dedicated change, not as a rider on an instruction-surface phase.

But a session-checked gate is exactly the fail-open shape KIT-0113
measured and KIT-0114 exists to eliminate — an agent can skip a
markdown step; it cannot skip an exit code. Once consumers are
routinely on a door-era `agentive-kit`, move the check into the engine.

## Requirements

1. `agentive preflight` gains Gate 8: PASS on a non-empty
   `.kit/context/reviews/<TASK-ID>-review-pass.md`, FAIL otherwise
   (existence + non-empty, mirroring Gates 5/6 — content stays
   agent/human discipline). While mechanizing, EVALUATE whether a
   minimal structure check (e.g. a passes-ran table and at least one
   disposition line) is worth the brittleness — CodeRabbit (PR #148)
   argued a placeholder file can satisfy a pure non-empty check; the
   KIT-0042 counter-doctrine is that gates stay strict-but-simple and
   content intelligence lives in process. Decide with evidence, not
   by default.
2. Behavior matrix extended; all "all 7"/"7-gate" literals inside the
   engine (`preflight.py` docstring, `_HELP`, dispatch summary,
   `cli.py`) move to 8.
3. `.claude/commands/preflight.md` Step 1b collapses to "parse GATE:8
   like the others" — with a compatibility note for engines that
   predate the gate (treat a missing GATE:8 line as "check manually",
   not PASS).
4. Coordinate the `agentive-kit` version bump/release with the planner
   (minor bump: new gate is a behavior change for consumers).

## Acceptance Criteria

- [ ] Gate 8 emitted by the engine, matrix-pinned
- [ ] Once the engine emits Gate 8, no stale 7-gate literal remains in
      package or command surfaces (post-change state — extend
      `tests/test_review_pipeline_contracts.py`; until this task lands,
      the engine's 7-gate literals are correct and intentional)
- [ ] Compatibility note for lagging engines in the command markdown

## Notes

Value authority for the gate's semantics:
`.kit/context/workflows/REVIEW-PIPELINE.md` (KIT-0116). This task
changes WHERE the check runs, never what it checks.
