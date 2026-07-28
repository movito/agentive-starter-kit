# Review Starter: KIT-0033

**Task**: KIT-0033 — Make planner + feature-developer truly portable downstream
**Task File**: `.kit/tasks/4-in-review/KIT-0033-portable-agents-downstream.md`
**Branch**: feature/KIT-0033-portable-agents-downstream → main
**PR**: https://github.com/movito/agentive-starter-kit/pull/58

## Implementation Summary

Makes the consolidated V2 **planner** and **feature-developer** agents portable to
consumer projects bootstrapped via `bootstrap-consumer.sh`. Resolves the four
PR #57 bot threads on under-scaffolded downstream bootstrap.

- **Markers (N2)**: the consumer-customizable sections — Project Context (both
  agents) and Stack Notes (feature-developer) — are wrapped in stable
  `<!-- BEGIN/END KIT-LOCAL: <region> -->` markers. ASK's own filled content is
  byte-unchanged; the diff is purely additive (N1).
- **`scripts/local/kit_markers.py`** (stdlib-only) merges marker regions:
  - *Fresh bootstrap* → regions seeded with consumer-neutral placeholders derived
    from the project name (no kit identity, no KIT-NNNN, no kit-only paths).
  - *Re-bootstrap* → consumer's filled regions preserved **byte-for-byte** while
    structure *outside* the markers refreshes from upstream. Without markers,
    `--ignore-existing` is the only safe rsync mode and consumers get stuck on
    whatever agent version they first bootstrapped (the gap #3 root cause).
  - *Markerless pre-consolidation agent* → reseeds from placeholders, never
    inheriting kit identity. *Malformed marker* (BEGIN without END) → fails fast
    with `ValueError` rather than clobbering trapped content. *CRLF endings* →
    parsed and preserved.
- **`.kit/` skeleton (F1)**: bootstrap provisions `tasks/1-backlog … 7-blocked`,
  `context/`, and `templates/TASK-STARTER-TEMPLATE.md`; the shipped
  `./scripts/core/project` makes the lifecycle work on day one.
- **`--no-kit` opt-out (F3)**: skips the `.kit/` scaffold and drops planner /
  feature-developer, with a one-line skip summary. Self-target guard refuses to
  bootstrap into the kit source repo itself.

## Files Changed

- `.claude/agents/feature-developer.md` — KIT-LOCAL markers around Project Context
  + Stack Notes (additive only)
- `.claude/agents/planner.md` — KIT-LOCAL markers around Project Context (additive)
- `scripts/local/kit_markers.py` (new) — stdlib marker merge helper + CLI
- `scripts/local/bootstrap-consumer.sh` — `.kit/` skeleton, marker-merge of the two
  agents, `--no-kit` flag, self-target guard, stale-test sweep
- `tests/test_kit_markers.py` (new) — 35 tests over merge logic, re-bootstrap
  byte-preservation, edge cases, and the CLI surface
- `CHANGELOG.md` — Unreleased → Added entry
- `.kit/context/reviews/KIT-0033-evaluator-review.md` (new) — Phase-7 evaluator trail
- `.kit/tasks/{1-backlog → 3-in-progress}/KIT-0033-*.md` (moved)

## Verification

All acceptance criteria exercised end-to-end against scratch consumer dirs:

- ✅ `.kit/` skeleton created; `project start` then `project complete` move a stub
  task `2-todo → 3-in-progress → 5-done` and update `**Status**`
- ✅ Fresh bootstrap identity-clean (no KIT-NNNN / kit paths in customizable regions)
- ✅ Re-bootstrap: both regions byte-identical preserved; outside-marker structure
  refreshed from upstream (stale heading replaced)
- ✅ Opt-out: no `.kit/`, no planner/feature-developer, clean summary; other agents
  still ship
- ✅ Markerless pre-consolidation agent reseeds to placeholders (no identity leak)
- ✅ Stale orphan `tests/test_kit_markers.py` swept on re-bootstrap
- ✅ N1: ASK agent diff purely additive (markers + mechanism note)
- Full suite: 290 passed, 12 skipped; coverage 89.8% (`kit_markers.py` 100%);
  black / isort / flake8 / pattern-lint clean; CI green on PR #58

## Review History

**Evaluator** (Phase 7, code-reviewer-fast / Gemini): FAIL → all findings fixed
(self-bootstrap guard, duplicate-region handling, blank-name fallback) + CLI tests
added. Trail: `.kit/context/reviews/KIT-0033-evaluator-review.md`.

**Bots** (PR #58): 7 threads across 4 rounds — all valid, all fixed and resolved:
1. Consumer pytest import failure (test shipped, helper not) → exclude from sync +
   module-skip guard + stale-orphan `rm -f` sweep
2. Fail-fast on malformed consumer marker → `merge()` raises `ValueError`
3. CLI handler/`main()` coverage → `TestCLI` class (restored 80% gate)
4. CRLF line endings broke marker parsing → `\r?\n`-tolerant pattern

## Areas for Review Focus

1. **Marker scheme robustness** — confirm the `\r?\n` region pattern and the
   fail-fast-on-malformed behavior are the right trade-offs; that the body is
   preserved byte-for-byte across re-bootstrap regardless of line endings.
2. **N1 (no ASK regression)** — that the agent diffs are purely additive and ASK's
   filled Project Context / Stack Notes are unchanged.
3. **Placeholder content** — that the seeded placeholders are genuinely
   consumer-neutral (no kit identity) and useful as a fill-in starting point.
4. **Bootstrap orchestration** — the merge branch (fresh vs. re-bootstrap), the
   `--no-kit` path, and the self-target / stale-test guards.

## Related Tasks

- Resolves the four PR #57 threads (r3484524391, r3484524395, r3484592020,
  r3484585878). Coordinate with **KIT-0026** (peer-repo agent/skill sync — different
  mechanism, different target). No new ADR.

---
**Ready for human / code-reviewer review.**
