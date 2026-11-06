# KIT-0116 — Review-Pass Record (Gate 8 artifact)

**Task**: KIT-0116 Phase 1 / PR 1 (branch `feature/KIT-0116-review-pipeline`)
**Date**: 2026-08-24
**Authority**: `.kit/context/workflows/REVIEW-PIPELINE.md`
**Note**: this task BUILT the Phase 5b gate; this record doubles as the
required Tier-1 live-smoke evidence (spec Test Requirements). The run
executed in the designed slot: after the Gate-5 evaluator passes, before
the PR opened.

## Passes that ran

| Pass | Tool / effort | Outcome |
|------|---------------|---------|
| Code review (always) | harness-native `/code-review`, **medium** | 8 verified findings |
| Security review | — **skipped** | no `security` flag declared (task spec carries no `**Review Flags**:` field → default = code only) |
| Other flagged dimensions | — none declared | — |

Smoke telemetry (recorded in REVIEW-PIPELINE.md's cost note): ~95k
subagent tokens, ~5.7 min, 15 tool uses; candidates verified against
the live tree by the skill's own verify pass before reporting.

## Findings and dispositions (fix-or-defer)

All 8 findings **FIXED** pre-PR:

1. **REVIEW-PIPELINE.md twin drift** (uncommitted edit diverged from the
   packaged door copy) — FIXED: twin re-mirrored same commit;
   `test_door_data_sync.py` pins it from merge onward.
2. **commit-push-pr Next Steps placed the native pass after PR open**,
   contradicting the pre-PR gate — FIXED: item reworded to verify the
   pass already ran pre-PR (Phase 5b), with recovery phrasing.
3. **commit-push-pr "gates 5-7 CAN be checked now" not updated for
   Gate 8** — FIXED: now gates 5-8, naming /preflight Step 1b and the
   CLI's 1-7-only emission.
4. **review-handoff bundled-PR pointer convention lacked a
   review-pass pointer** — FIXED: third pointer file added; Gates
   5/6/8 named; multi-PR spurious-FAIL note widened to 5-8; skill
   1.1.0 → 1.2.0.
5. **review-starter template checklist lacked the review-pass item** —
   FIXED: checklist gains the record + deferred-findings-surfaced item.
6. **preflight cross-repo mapping said "Gates 5-7" read planning** —
   FIXED: 5-8.
7. **Stale-7 drift grep missed the verdict idiom ("all 7 pass") and
   "7-gate"** — FIXED: pattern broadened.
8. **Phase-2 arming keyed on an exact ADR slug** (a "read-only" vs
   "readonly" spelling would silently disarm all Phase-2 checks) —
   FIXED: arms on `KIT-ADR-0036*.md` glob.

**Deferred**: none. **Refuted by the skill's own verify pass** (no
action): reviewer frontmatter parsing (already hardened), Gate-5 glob
collision with `-review-pass.md`, CHANGELOG placement,
REVIEW-PIPELINE.md version-bump-on-new-file.

## Smoke verdict

Tier 1 works as designed: the pass ran in-slot, produced findings
disjoint from the evaluator trio's (cross-file contract consistency —
exactly the dimension bots and single-file evaluators miss), and every
finding was triaged fix-or-defer before the PR opened. Transcript
evidence: this session (`KIT-0116 FDF5 review pipeline`), /code-review
agent `cccfa7`, 2026-08-24.

---

# Phase 2 append — PR 2 (`feature/KIT-0116-reviewer-delegation`)

**Date**: 2026-08-24 · **Authority**: REVIEW-PIPELINE.md 1.1.0

## Passes that ran

| Pass | Tool / effort | Outcome |
|------|---------------|---------|
| Code review (always) | `/code-review medium` (harness skill) | 8 verified findings, all FIXED |
| Tier 2 spawn smoke 1 | `code-reviewer` background subagent (Agent tool) | CHANGES_REQUESTED — 1 HIGH + 2 MEDIUM + 1 LOW, all FIXED. ~95k tokens / 4.8 min / 29 tool uses, zero permission prompts. Roster caveat: session registry predated the 2.0.0 toolset edit, so this run verified spawn mechanics, not the read-only toolset (recorded in KIT-ADR-0036 §5) |
| Tier 2 spawn smoke 2 | `architecture-reviewer` background subagent (fresh roster: Read/Grep/Glob only) | FINDINGS — 1 CRITICAL + 2 HIGH + 4 MEDIUM + 2 LOW, all FIXED. ~113k tokens / 6.1 min / 46 tool uses, zero permission prompts, no shell used or attempted. THE read-only §5 verification + FR-8 Should-Have (implementation-level findings distinct from spec-time evaluators) |
| Security review | skipped | no `security` flag declared |

## Fix-or-defer ledger (all FIXED, none deferred)

From /code-review: ADR §5 evidence honesty (rewritten to the actual
boundary); starter-template handoff boilerplate "do not spawn"
carve-out (2.3.0) — the finding that would have zeroed the Tier-2
metric; code-reviewer stale write/git/CI-precondition sections;
vacuous ADR-side enumeration check (heading-anchored regex);
powertest-runner stated opposite delegation law (reconciled + added to
citation-test roster); engine-consumer.sh consumer exclusion for
architecture-reviewer; REVIEW-PIPELINE 1.1.0 (+ twins).

From code-reviewer smoke: KIT-ADR-0014-era sections contradicting the
no-Write contract (Review Workflow I/O, Step 7, Reporting the
Verdict); Reference Documents omitted KIT-ADR-0036 and pointed at the
wrong ADR dir; fd bodies' ADR §4 restatement trimmed to citation.

From architecture-reviewer smoke: THREE stale door twins (packaged
engine-consumer.sh missing the exclusion — would have shipped the
builder-only reviewer to consumers; REVIEW-PIPELINE.md and
TASK-STARTER-TEMPLATE.md packaged copies at Phase-1 state); toolset
test inverted the ADR's iff (deny-list → per-agent allow-list; a
declared `Task` tool now fails CI); new roster-exclusion pin test
(two_homes_get_a_pin); KIT-ADR-0014 supersession annotated both sides;
Serena ruling reconciled (harness-inherited, "if available");
Tier-2 cost slot filled with measured numbers; architecture-reviewer
gained the sibling Evaluator-Workflow/Allowed-Operations sections;
about-kit-adr.md Last-Updated stamp.

## Smoke verdict

Tier 2 works end-to-end: background spawn, autonomous completion,
final-message report return, zero permission prompts on a genuinely
read-only toolset — and both spawns surfaced findings no other rung
of the ladder had (cross-surface contract contradictions, twin
drift). Transcript evidence: session "KIT-0116 FDF5 review pipeline",
2026-08-24.

---

# Phase 3 append — PR 3 (`feature/KIT-0116-deep-review`)

**Date**: 2026-09-30 · **Authority**: REVIEW-PIPELINE.md 1.2.0

## Passes that ran

| Pass | Tool / effort | Outcome |
|------|---------------|---------|
| Evaluator trio (Gate 5) | code-reviewer-fast / o3 / claude-code, 3 rounds | 9 FIXED, 8 rejected w/ reasons, 1 deferred — full dispositions in `KIT-0116-evaluator-review.md` (Phase 3 section) |
| Code review (always) | `/code-review origin/main..HEAD medium` (forked skill, background) | 8 deduped findings: 7 FIXED, 1 PARKED (below) |
| Security review | skipped | no `security` flag declared on spec, handoff, or resume starter |
| Tier 2 spawn | skipped (recorded decision) | no flags declared; diff already carried 3 evaluator rounds + Tier 1 — proportionality (NFR-1). Tier-2 mechanics were smoke-verified in Phase 2 |
| Tier 3 live run | **not run — by contract** | the resume starter contains no Tier-3 sentence; running our own deep-review workflow "as a test" would be self-escalation (FR-11). Ships parse-pinned + contract-pinned; first live run awaits a human ask |

## Fix-or-defer ledger — /code-review (7 fixed, 1 parked)

FIXED: (1) silent whole-lens death — lens identity now survives the
null path, the death is logged as PARTIAL evidence, and `lensesFailed`
rides the return; (2) `refutedCount` conflation — `noVerdict` added to
the RETURN (shape addition), contract text updated: dead verifier ≠
evidence-backed refutation; (3) budget pin now DERIVES 13 from the
real lens count (`key:` entries) + PER_LENS_CAP, so an added lens reds
the suite; (4) `f.file` label deref guarded (`|| 'unknown'`);
(5) StopIteration → `next(..., None)` + diagnostic asserts naming the
wrap anchor; (6) dead trailing `.filter(Boolean)` removed with a
shape comment; (7) resume-safety ban widened from three spellings to
the nondeterminism family regex (`Date(`, `performance.now`,
`randomUUID`, …).

PARKED: door/plugin consumers receive the escalation contract but not
`.claude/workflows/deep-review.js` (#142/#143 shipped-set drift
class) → honest **distribution note added to the contract** (both
twins) + filed `KIT-0124-deep-review-distribution-gap.md` (backlog),
routed to the distribution ADR successor rather than an ad-hoc copy.

## Deferred findings visible to the human reviewer

- o3: behavioural (execute-not-just-parse) test for the workflow —
  disproportionate to stub the runtime in pytest; first live Tier-3
  run is the behavioural check (and needs a human ask, FR-11).
- KIT-0124 (parked distribution gap, above) — rides the PR
  description too.
