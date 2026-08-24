# Review Starter: KIT-0116 — Automated review pipeline (multi-PR arc)

**Task**: `.kit/tasks/4-in-review/KIT-0116-automated-review-pipeline.md`
**Arc**: 3 phases, one PR each. Phase 1 MERGED (#148 → 8ddc214).
**Current**: **Phase 2 — PR #149** (`feature/KIT-0116-reviewer-delegation` @ `71438e9`), awaiting your verdict. Phase 3 awaits your go.

## Phase 2 — what shipped (PR #149)

| Surface | Change |
|---------|--------|
| `KIT-ADR-0036` (NEW, Proposed) | **Your merge IS the ratification.** Read-only reviewer delegation carve-out: every retained tool ruled (§3, iff-shaped); Bash removed from all reviewers, rejected outright by the drift test; findings return as final message, caller persists (§4 spawn contract + bounded completion + late-addendum rule); §5 records the ACTUAL verified boundary from two live smokes |
| `code-reviewer` 2.0.0 | Bash dropped; body reconciled end-to-end (report-return replaces KIT-ADR-0014 file-writing; CI = caller's concern; Serena "if available") |
| `architecture-reviewer` 1.0.0 (NEW) | Implementation-level ADR/pattern/boundary review; read-only from birth; `architecture` flag; **needs plugin rostering at arc-end release** |
| security-/document-reviewer 1.4.0 | Contract sections; WebSearch/WebFetch ruled in the ADR |
| fd 2.8.0/-f5 1.8.0, planner 2.3.0/-f5 1.3.0, powertest-runner | Tier-2 spawn contract (Phase 5b) + carve-out citations; powertest-runner had stated the OPPOSITE — reconciled + pinned |
| TASK-STARTER-TEMPLATE 2.3.0 | Handoff boilerplate "do not spawn" gains the carve-out (would have zeroed the Tier-2 metric) |
| engine-consumer.sh ×2 + pin test | architecture-reviewer rsync-excluded (builder-only); new test asserts every `*-reviewer.md` stays consumer-excluded |
| Contract tests | Toolset check = §3's iff allow-list (a declared `Task` fails CI); Phase-2 checks armed and green |

## The §5 verified boundary (recorded honestly)

- `code-reviewer` spawn: mechanics verified (~95k tok/4.8 min, zero prompts) — **roster caveat recorded**: session registry predated the toolset edit
- `architecture-reviewer` spawn (fresh roster, Read/Grep/Glob only): **the read-only verification** (~113k tok/6.1 min, zero prompts, no shell attempted) + FR-8 Should-Have — its findings were genuinely architectural and caught a CRITICAL (stale packaged-engine twin would have shipped the builder-only reviewer to consumers)

## Review ladder on this PR (dogfooded)

- Gate 5: `code-reviewer-fast` (prose-dominated → fast-only per axis 1, deep-skip recorded); Tier 1 `/code-review medium`; two Tier-2 smokes. **Ledger: 11+ fixed (1 CRITICAL, 3 HIGH), 0 deferred** → `.kit/context/reviews/KIT-0116-{evaluator-review,review-pass}.md` (Phase-2 appends)
- Bots: BugBot clean both rounds; CodeRabbit 7 threads over two rounds — 5 fixed, 1 acknowledged (roster/release), 1 declined with reasoning (inline-diff-always). All replied + resolved.

## Preflight @ 71438e9

Gates 2–8 PASS (Gate 8 via Step 1b). Gate 1: tests/lint/bots green; **only the plugin drift guard is red** — the ruled held-release shape (`plugin-drift.yml` expected-red window; release cut ONCE at arc end; architecture-reviewer rostering rides it).

## Areas for review focus

1. **KIT-ADR-0036 itself** — your merge ratifies it (Proposed → Accepted). §3's tool rulings and §4's bounded-completion are the load-bearing decisions.
2. **The Bash-outright-rejection choice** (test + ADR): re-ruling requires test+body+ADR in one PR. Third convergent finding class closed this way.
3. **code-reviewer 2.0.0's dual-mode body** — spawned (final-message) vs interactive (caller persists); check the reconciliation reads cleanly.

## Operator next steps

1. Review + merge PR #149 (all non-drift checks green at `71438e9`; drift red = ruled, per `.github/workflows/plugin-drift.yml` + the arc-end release ruling)
2. Say the word for **Phase 3** (Tier-3 deep-review workflow + formal escalation contract, ~0.5 day) — new branch from updated main, announced in-session
3. Or end the arc here — Phases 1+2 stand alone; the planner then decides release timing

---
*Phase-1 starter (PR #148, merged) superseded by this version; its content lives in the PR #148 description and git history.*
