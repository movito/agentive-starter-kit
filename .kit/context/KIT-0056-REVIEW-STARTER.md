# KIT-0056 Review Starter — Degraded Modes + Operator Presets

**Task**: `.kit/tasks/3-in-progress/KIT-0056-degraded-modes-and-presets.md`
**Branch**: `feature/KIT-0056-degraded-modes-presets`
**Scope**: KIT-ADR-0027 P5 (the floor) + P7 (the ceiling) — one
resolution mechanism read from opposite ends. After this, only P6
remains in the ADR arc.

## What to review

1. **The floor (P5)** — `scripts/core/preflight-check.sh` 1.3.0:
   Gates 2/3 SKIP-with-notice under a `bots:` declaration in the
   kit-install region (door `--bots` → engine writes → kit_markers
   reads). Absent line = both bots expected (N1: zero migration).
   Invalid/empty declarations fail closed with a NOTICE; doctor FAILs
   them loudly (`DOCTOR:bots-record:FAIL`).
2. **The ceiling (P7)** — `scripts/local/bootstrap`: the preset
   reader fills the KIT-0053 `resolve_setting` stub (CLI > preset >
   kit defaults > prompt; on adopt, an existing record short-circuits
   the preset). `--no-preset`, `env-source` (0600, never printed,
   gitignore-guarded), `docs/preset.example`,
   `project doctor --against-preset` (INFO-only PRESET: lines).
3. **Reader consistency** — the review theme that dominated
   evaluation: all three bots readers (door bash, project Python,
   preflight shell) share one tolerance rule (comma/space, any case,
   leading whitespace) so no declaration is valid to one reader and
   invalid to another.

## Verification trail

- Evaluator record (5 fast rounds + o3 + claude-code, run pre-PR,
  full disposition trail): `.kit/context/reviews/KIT-0056-evaluator-review.md`
- One-button demo (N4): transcript in the PR body — full preset →
  `bootstrap --new` under a real pty → zero prompts → record matches
  preset (`doctor --against-preset`: "record matches the preset on
  all 3 compared field(s)").
- `pytest`: 728 passed; `ci-check.sh` green. New coverage rides
  `tests/test_setup_door.py`, `tests/test_preflight_check.py`,
  `tests/test_doctor.py`.

## Notable calls a reviewer may want to weigh

- Record-beats-preset on adopt (silent by design; divergence surfaces
  via `doctor --against-preset` INFO, never a silent re-answer).
- Unknown preset keys WARN only in the door — the comparator
  deliberately does not duplicate the key vocabulary.
- `run_doctor_tail` verdict inversion fix (pre-existing KIT-0053 bug:
  doctor exit 1 was labeled WARNINGS, 2 labeled FAILURES).
- Engine's baked planning manifest bumped to 3.4.0 with core VERSION
  (the KIT-0050 precedent).
