# Review Starter: KIT-0116 — Automated review pipeline (multi-PR arc)

**Task**: `.kit/tasks/4-in-review/KIT-0116-automated-review-pipeline.md`
**Arc**: 3 phases, one PR each. Phase 1 MERGED (#148 → 8ddc214).
Phase 2 MERGED (#149 → 4c7af31, KIT-ADR-0036 ratified).
**Current**: **Phase 3 — PR #152** (`feature/KIT-0116-deep-review` @
`79c4017`), awaiting your verdict. **This PR closes the arc.**

## Phase 3 — what shipped (PR #152)

| Surface | Change |
|---------|--------|
| `.claude/workflows/deep-review.js` (NEW) | Tier-3 saved workflow (FR-10): scope agent → 3 lenses (correctness / kit-convention architecture / security) → one **refute-first** verifier per finding → synthesis. Budget derived + capped at 13 agents; dead lenses, dead verifiers, capped drops all logged AND returned (`lensesFailed`, `noVerdict`) — never silent. Resume-safe; `args {taskId, base}` shape-validated |
| REVIEW-PIPELINE.md 1.2.0 (+ door twin, byte-synced) | **Formal escalation contract** (FR-12): who may invoke (operator in words, or planner via explicit starter sentence — a Review Flag is NOT enough), exact invocation, evidence incl. requested-but-could-not-run and partial-coverage honesty; FR-11 never-self-escalate; Tier-2 toolset distinction; distribution note (door/plugin consumers lack the file → KIT-0124) |
| Contract tests | Workflow existence, opt-in metadata, `meta.name` stability, nondeterminism-family resume ban, budget derived from the real lens count, contract wording + evidence section, `node --check` under runtime wrapping |
| `KIT-0124` (NEW, backlog) | Parked distribution gap — routed to the distribution-ADR successor, not ad-hoc copy |

## Resume-protocol note (this session)

Prior fd-f5 session ended unpushed at `6d53db2` + a 4-file refinement.
Judged on content, **adopted in full** + one hygiene fix; rebased onto
main (planner bookkeeping only). Call recorded in the PR description.

## Review ladder on this PR (dogfooded)

- Gate 5 trio, 3 rounds (fast CONCERNS / o3 FAIL / claude-code
  CHANGES_REQUESTED): **9 fixed, 8 rejected with recorded reasoning,
  1 deferred** → `KIT-0116-evaluator-review.md` (Phase 3 section)
- Tier 1 `/code-review medium` (forked): 8 findings — **7 fixed, 1
  parked (KIT-0124)** → `KIT-0116-review-pass.md` (Phase 3 append)
- Tier 2: skipped, recorded (no flags; proportionality NFR-1)
- **Tier 3 live run: NOT run, by its own contract** — no Tier-3
  sentence in the starter; a "test run" would be self-escalation
  (FR-11). First live run awaits your words.
- Bots: BugBot clean; CodeRabbit 2 threads, both accepted + fixed
  (`79c4017`), replied, resolved → **re-review APPROVED**.

## Preflight @ 79c4017

Gates 2–8 PASS. Gate 1: tests/lint/bots green; **only the plugin
drift guard is red** — red on `main` itself since 2026-09-14 (10
rostered components newer than the published plugin + 2 unrostered
agents incl. `feature-developer-o55`, none from this PR). This is the
ruled held-release shape: release cut ONCE at arc end.

## Areas for review focus

1. **The escalation contract** (REVIEW-PIPELINE.md §Escalation) — the
   two invocation paths and the "a Review Flag is NOT enough" line
   are the load-bearing policy; the workflow file is just mechanism.
2. **Partial-evidence semantics** — `refutedCount` = evidence-backed
   only; `noVerdict`/`lensesFailed` make degraded runs visible in the
   record. Check the contract text and return shape agree.
3. **KIT-0124 parking** — distribution note honest enough until the
   distribution ADR lands?

## Operator next steps

1. Review + merge PR #152 (all non-drift checks green at `79c4017`;
   CodeRabbit APPROVED; drift red = ruled held-release)
2. **Arc ends at merge** → the planner decides the arc-end release
   train and its riders (KIT-0115 / KIT-0103 R6 / KIT-0117 stripping /
   KIT-0108, KIT-0111; architecture-reviewer + o55 rostering). This
   session stops before any release mechanics, per ruling.
3. First live Tier-3 run: whenever you ask for it in words, on a
   genuinely high-risk diff.

---
*Phase-2 starter content superseded (PR #149 merged); it lives in the
PR #149 description and git history.*
