# KIT-0036 — Task-Spec Evaluator Review Trail

**Artifact**: `.kit/tasks/2-todo/KIT-0036-pull-based-consumer-sync.md`
**Input**: `.adversarial/inputs/KIT-0036-task-input.md` (spec + KIT-ADR-0026 + review-focus questions)
**Evaluator library**: v0.10.0
**Date**: 2026-07-03

| Round | Evaluator | Model | Verdict |
|-------|-----------|-------|---------|
| 1 | arch-review-fast-v2 | gemini-3-flash-preview | APPROVED (1:1 ADR coverage; sequencing sound; 3.0.0 call correct) |
| 1 | claude-arch | claude-opus-4-7 | REVISION_SUGGESTED (6 findings) |
| 2 | claude-arch | claude-opus-4-7 | REVISION_SUGGESTED (9 findings, all refinement-grade) |

## Disposition

**Round 1 (claude-arch)** — all six folded:
1. Dual-caller test straddles PRs → renamed to dual-*entrypoint* in PR 1; extension to `project sync` is an explicit PR 2 acceptance criterion.
2. Exit-1 conflation → documented rationale (both mean "human attention"); `--report-json`/`SyncReport.status` named as the finer-grained channel.
3. "Byte-identical" under-specified → file-tree-identical ignoring `synced_at`; PR body/commit asserted separately.
4. `--only` semantics → manifest entry key, not filesystem path.
5. **D7/D1 manifest-timing bug (real)** → new D2b: engine's manifest entry + 2.1.0→2.2.0 bump land in PR 1; PR 2 carries only the removal + 3.0.0.
6. Self-sync untested → explicit fixture test (source contains modified engine file).

**Round 2 (claude-arch)** — all folded:
1. Plan-resident-before-write invariant placement → already first-class in D1 (reviewer read an earlier placement); no change.
2. `--only` canonical form → "exactly as in manifest JSON" + both-slash-forms test.
3. `partial_sync` under `--dry-run` → `would_bump_core_version` / `would_set_partial_sync` in SyncReport.
4. Exit-1 wrapper UX → wrapper branches on `SyncReport.status`, never the exit code.
5. Stale-directory cleanup not named → explicit in D1 + directory-shrink edge case in D2.
6. Removal announcement mechanism → generalized `SyncReport.removed_entries` + wrapper "Removed from sync unit:" block; D6 uses it, no one-off logic.
7. `--no-branch` dirty-tree → refuses (exit 2) when touched paths are dirty.
8. "Well under 2 minutes" not checkable → local-fixture engine run < 5 s as the mechanical gate; network path recorded best-effort.
9. Engine-binds-to-manifest-schema invariant → added to KIT-ADR-0026 Risks (consumer's engine runs against source's manifest; schema change trips exit-3 loud-fail).

**Stopping rationale**: fast gate APPROVED round 1; claude-arch's round-2 findings were uniformly refinement-grade (field names, UX branching, measurable thresholds) with no structural objection — the round-1 structural finding (D2b timing) was confirmed fixed. All 15 findings across both rounds are folded. A third round was judged diminishing-returns; raw final logs in `.adversarial/logs/KIT-0036-task-input--*.md`.
