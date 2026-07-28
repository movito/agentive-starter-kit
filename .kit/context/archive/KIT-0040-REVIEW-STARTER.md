# KIT-0040 Review Starter — KIT-0034 Retro Follow-ups

**PR**: https://github.com/movito/agentive-starter-kit/pull/70
**Branch**: `feature/KIT-0040-kit-0034-retro-followups`
**Task**: `.kit/tasks/4-in-review/KIT-0040-kit-0034-retro-followups.md`
**Handoff**: `.kit/context/KIT-0040-HANDOFF-feature-developer.md`
**Date**: 2026-07-05

## What shipped

Three retro follow-ups from KIT-0034, F3 first per the planner's
sequencing decision (all three landed in one PR — nothing dragged):

- **F3 — `kit_markers.py` fixes** (`scripts/local/kit_markers.py`): the
  two BugBot findings open on merged PR #58 since KIT-0033. Prose
  mentions of a BEGIN marker no longer abort re-bootstrap (line-anchored
  malformed check); whitespace-drifted markers now parse and preserve
  customized consumer content instead of silently clobbering it with
  placeholders; drift beyond tolerance fails fast. Byte-preserving
  round-trip retained. Both PR #58 threads replied to and resolved with
  pointers to PR #70.
- **F1 — stub-`gh` preflight harness** (`tests/test_preflight_check.py`):
  the real `preflight-check.sh` runs against canned `gh` payloads across
  the KIT-0034 8-state matrix + baseline all-pass (10 tests, ~1.8 s,
  hermetic temp dirs, mutation-verified). Ships to consumers (targets
  `scripts/core/` only).
- **F2 — decision: tooling fix** (stated choice; the COMMIT-PROTOCOL.md
  documentation fallback was not needed): `project move|start|complete|
  block` rewrites the moved task's numbered-folder path in
  `agent-handoffs.json` + `HANDOFF-*.md` files. Conservative (exact file
  name, numbered folders only), warn-never-block, re-run = repair.

## Review trail

- **Bots**: CodeRabbit round 1 → 1 finding (UnicodeDecodeError not
  caught by `except OSError`) — fixed in `5addbdf` with regression test;
  latest CodeRabbit review APPROVED. BugBot → 1 finding (`\b` prefix
  collision in the malformed-marker detector) — fixed in `dca46c8`;
  thread auto-resolved, reply added. 3 threads total on PR #70 (2 + the
  courtesy reply), 0 unresolved.
- **Evaluators** (`.kit/context/reviews/KIT-0040-evaluator-review.md`):
  fast-v2 CONCERNS (1 real → fixed in `dca46c8`; 3 declined with
  reasoning), o3 CONCERNS (2 claims verified false empirically, 1
  documented fail-fast trade-off), claude-code APPROVED.
- **CI**: green on every push (Lint + Tests + BugBot + CodeRabbit).

## Suggested review focus

1. `scripts/local/kit_markers.py` — the three regexes (`BEGIN_RE`,
   `_region_pattern`, `_begin_marker_line_re`) and the consistency
   argument: everything parseable is preserved byte-for-byte; everything
   marker-shaped but unparseable fails fast; nothing falls between.
2. `scripts/core/project::_sync_coordination_metadata` — conservative
   rewrite scope (is `[0-9]+-[a-z-]+` + exact file name the right
   boundary?).
3. Known accepted limitation: a literal BEGIN-marker line inside a
   fenced code sample (region otherwise absent) still fail-fast aborts —
   deliberate (loud abort beats silent clobber), same behavior as before
   the fix, noted by both evaluators and declined.

## Verification commands

```bash
pytest tests/test_kit_markers.py tests/test_preflight_check.py tests/test_project_script.py -q
./scripts/core/ci-check.sh
./scripts/core/preflight-check.sh --pr 70
```
