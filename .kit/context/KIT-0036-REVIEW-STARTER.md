# Review Starter: KIT-0036 (PR 1 of 2)

**Task**: KIT-0036 — Pull-based consumer sync: engine extraction + `project sync`
**Task File**: `.kit/tasks/3-in-progress/KIT-0036-pull-based-consumer-sync.md`
(stays in-progress — this is PR 1 of 2; PR 2 adds the `project sync` wrapper)
**Branch**: `feature/KIT-0036-sync-engine` → `main`
**PR**: https://github.com/movito/agentive-starter-kit/pull/63

## Implementation Summary

Implements KIT-ADR-0026 (D1–D4): extracts Channel B's sync logic out of the
`sync-core-scripts.yml` bash heredoc into a single tested Python engine that
both the push Action and (in PR 2) a consumer-side `project sync` command
invoke — **one engine, two callers**, so the paths cannot drift.

- **Library-first engine** `sync(source, target, options) -> SyncReport`; thin
  argparse CLI maps `SyncReport.status` to a frozen exit-code contract (0–4).
- **Two-pass temp-then-commit** (KIT-0034 F3): the full plan (file bytes **and**
  permission bits) is read into memory before the first write, staged to a temp
  tree inside the target, then committed with moves only — safe self-overwrite,
  no half-updated targets, exec bits preserved.
- **Engine-computed completeness** (`partial_sync` marker) is entitlement-scoped,
  not caller-asserted.

## Files Changed

### New Files
- `scripts/core/sync_from_manifest.py` — the sync engine (D1).
- `tests/test_sync_from_manifest.py` — 52 tests (D2).
- `.kit/context/reviews/KIT-0036-evaluator-review.md` — Phase-7 triage.
- `.kit/context/reviews/KIT-0036-evaluator-{code-reviewer-fast,code-reviewer,claude-code}.md`
  — raw evaluator logs.

### Modified Files
- `scripts/.core-manifest.json` — add engine to `scripts_core`; `core_version`
  2.1.0 → 2.2.0 (D2b).
- `scripts/core/VERSION` — 2.1.0 → 2.2.0.
- `tests/test_core_manifest.py` — entry-count assertions 18 / 43 (D2b).
- `.github/workflows/sync-core-scripts.yml` — sync step is now a thin shell
  around the engine; per-repo `concurrency`; `workflow_dispatch` with a
  `validate-dispatch` guard job (D3, D4).
- `.kit/adr/KIT-ADR-0026-*.md` — status Proposed → Accepted.
- `.kit/context/KIT-0036-HANDOFF-*.md` — task-spec link repointed.

### Deleted Files
- None in PR 1. `check-sync.sh` retirement is PR 2 (D6).

## Test Results

```
52 engine tests passing (tests/test_sync_from_manifest.py)
96% coverage on scripts/core/sync_from_manifest.py
Full suite: 342 passed, 12 skipped
CI green on the PR (Lint + Tests); CodeRabbit approved; Cursor Bugbot clean.
```

## Areas for Review Focus

1. **Two-pass apply & self-overwrite** (`_apply`, `sync`): the engine's own file
   is in `scripts_core`, so a real sync overwrites the running module. Verified
   by an in-process test and a real-subprocess test. Confirm the staging-inside-
   target / move-only design reads correctly.
2. **Completeness semantics** (`SyncReport.complete`): defined as
   entitlement-scope (did the caller pull everything it's entitled to), **not**
   physical-file existence. An evaluator suggested the latter; the decline
   rationale (CI guarantees source entries exist; the change would create sticky
   `partial_sync`) is in the evaluator-review log — worth a sanity check.
3. **Workflow refactor** (`sync-core-scripts.yml`): the engine replaces ~110
   lines of heredoc; characterization tests are the behavior gate. Note the
   `validate-dispatch` job + `always()` guard on `sync`.

## Related Documentation

- **Task file**: `.kit/tasks/3-in-progress/KIT-0036-pull-based-consumer-sync.md`
- **ADR**: KIT-ADR-0026 (design authority), KIT-ADR-0022 (the push channel this
  complements), KIT-0034 F3 (temp-then-commit)
- **Handoff**: `.kit/context/KIT-0036-HANDOFF-2026-07-03.md`
- **Evaluator triage**: `.kit/context/reviews/KIT-0036-evaluator-review.md`

## Pre-Review Checklist (Implementation Agent)

- [x] All PR-1 acceptance criteria (D1–D4) implemented
- [x] Tests written and passing (52 engine tests, 96% coverage)
- [x] CI passes on the PR
- [x] No debug code / prints left behind
- [x] Docstrings for the public API (`sync`, `SyncReport`, CLI `--help`)
- [ ] Task moved to `4-in-review/` — **deferred**: two-PR task, completes after
      PR 2 (`project sync` wrapper, `check-sync.sh` retirement, 3.0.0, docs)

---

**PR 1 is ready for human review.** PR 2 (`feature/KIT-0036-project-sync`)
follows: the `project sync` pull wrapper (resolving the existing
`sync`→`linearsync` alias collision), `check-sync.sh` retirement, `core_version`
3.0.0, and the D8 docs.
