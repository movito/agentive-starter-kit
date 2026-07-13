# KIT-0042 Handoff — feature-developer

**Task**: `.kit/tasks/2-todo/KIT-0042-preflight-bundle-support.md`
**Target Codebase**: This repo — NOT a target repo (single-repo mode)
**Prepared**: 2026-07-13 (planner-f5)
**Estimated effort**: 1–2 hours

You are the feature-developer. Implement this task directly — do not
delegate to another agent instance.

## Mission

Make preflight Gates 5/6 bundle-aware — or make the bundle convention
impossible to miss — so the next multi-task PR doesn't discover the
lead-task + pointer-files requirement by failing the gate. Plus F1.1
(non-negotiable in either route): the gates' FAIL output must name the
bundle convention.

## Verified current state (planner checked 2026-07-13, post-#72/#73)

- Gate 6 exact-name match: `preflight-check.sh:487` —
  `find .kit/context -maxdepth 1 -name "${TASK_ID}-REVIEW-STARTER.md"`.
  FAIL message at line 492 (`No review starter found for $TASK_ID`).
- Gate 5 evaluator-record check FAILs at line 481
  (`No evaluator review found for $TASK_ID`); read the resolution logic
  directly above line 479 for what filename shapes it accepts today.
- Reference pointer files from the KIT-0037/38/39 bundle exist:
  `.kit/context/KIT-0037-REVIEW-STARTER.md`, `KIT-0038-...`, `KIT-0039-...`
  (per-task starters pointing at the lead) and per-task
  `.kit/context/reviews/KIT-003{7,8,9}-evaluator-review.md`.
- The stub-`gh` harness for this script is `tests/test_preflight_check.py`
  (KIT-0040); Gates 5/6 are filesystem checks, so bundle scenarios need
  only tmp-dir fixtures, not new `gh` payloads.

## Implementation guidance

- **Decide (a) glob vs (b) convention first** and write the reasoning down
  before coding — it must address where bundle intelligence should live
  (gate code vs process/docs) if bundle shapes diversify. Planner's prior:
  (b) + F1.1 is likely the right cost/benefit — the gates stay strict, the
  convention is already proven (reference files above), and the failure
  message closes the discoverability gap. But it's your call; (a) is
  legitimate if the glob stays simple and false-positive-safe.
- **If (a)**: the check must find the task ID *within* combined starter
  names (e.g. `KIT-0037-38-39-REVIEW-STARTER.md` must satisfy KIT-0038).
  Prefix safety is the trap: `KIT-0004` must not match `KIT-0040-...`.
  Use a boundary-safe match (the `(?!-?\w)` name-terminator lesson from
  KIT-0040 — in shell/glob terms, require a non-alphanumeric boundary
  after the ID). Test both directions in the harness.
- **If (b)**: add the convention to `.kit/skills/review-handoff/SKILL.md`
  as an explicit "bundled PR?" step at the top (lead-task naming + one
  pointer starter and one pointer evaluator record per bundled task, named
  exactly `<TASK-ID>-REVIEW-STARTER.md` / `<TASK-ID>-evaluator-review.md`),
  citing the KIT-0037/38/39 files as the shape.
- **F1.1 (both routes)**: extend the FAIL echoes at lines 481 and 492 with
  the one-line pointer, e.g.
  `(bundled PR? each task needs its own pointer file — see review-handoff skill)`.
  Keep the `GATE:N:Name:FAIL:` prefix format intact — downstream parsing
  (and the KIT-0040 harness assertions) key on it.
- Self-review skill v1.2.0 has items 8–9 (exit codes, scoped staging) —
  irrelevant here except: don't renumber anything if you touch shared
  checklists.

## Test approach

- `pytest tests/test_preflight_check.py` — add: bundle scenario (pointer
  files present → Gates 5/6 PASS for a non-lead task), FAIL-message
  content assertion (names the convention), and if (a), the prefix
  false-positive case.
- `./scripts/core/ci-check.sh` before pushing.
- This is a small, code-adjacent task — per the new doc-dominated ordering
  rule this does NOT qualify for evaluator-before-PR (it's gate logic, not
  docs); normal Phase order applies.

## Evaluation summary

`arch-review-fast`: REVISION_SUGGESTED — both actionable findings accepted
into the spec (F1.1 actionable failure message; code-vs-process reasoning
requirement); `.bundle-manifest` idea declined as over-engineering.
Disposition in the task file; log:
`.adversarial/logs/KIT-0042-preflight-bundle-support--arch-review-fast.md`.
No outstanding blockers.

## Out of scope

- Other preflight gates (1–4, 7) — KIT-0034 landed those; don't touch
- Bundle manifest formats or multi-lead bundles (declined; revisit trigger
  is bundle shapes diversifying)
- KIT-0041 (harness generalization to other scripts)
- Downstream repos (operator deferral stands)

## PR sizing

Single PR, well under 200 lines either route:
`feature/KIT-0042-preflight-bundle-support`.
