# KIT-0123: ASK commodity audit — define lightweight ASK v2 scope

**Status**: In Progress
**Priority**: high
**Assigned To**: planner (analysis phases) + feature-developer (ADR drafting; no code expected)
**Estimated Effort**: 2-3 sessions
**Created**: 2026-09-24
**Target Completion**: —
**Linear ID**: (automatically backfilled after first sync)
**Review Flags**: architecture

## Related Tasks

**Parent Task**: — (opens the upgrade-architecture arc; session "2026-09-24 P5 Upgrade gestalt")
**Depends On**: — (FLEET-INVENTORY-2026-09-24.md is complete — see References)
**Blocks**: the distribution-architecture ADR (baseline + overlays + reconciler — to be filed as its own KIT task once this audit fixes the artifact surface it must distribute); any bulk fleet-upgrade work
**Related**: KIT-0111 (version-bump guard — release-train pain this may shrink or moot), KIT-0117 (dispatch salvage-and-archive — the disposal pattern this audit reuses), KIT-0114, KIT-0107/0108 (door consolidation — the audit may eat the channels too)

## Status History

- **Todo** (from —) - 2026-09-24

## Overview

Walk every artifact ASK ships — agents, skills, commands, workflow
docs, scripts, evaluators, door engines, distribution machinery
itself — and sort each into three bins with **dated evidence**:

- **differentiated** — process discipline and institutional knowledge no
  harness ships (hypothesis: task lifecycle, gated agent workflows,
  bot-triage's nine faces, marker-merge customization);
- **commodity** — reimplements what current Claude Code does natively
  (hypothesis: polling machinery, manual worktree protocol, parts of
  scripts/core);
- **superseded** — native does it *better*; retire via the KIT-ADR-0035
  salvage-then-archive pattern (hypothesis: parts of the adversarial
  evaluator trio — see evidence base below; COUNTER-EVIDENCE already on
  file: the newest projects, ixda-services-planning and DTL, carry
  `.adversarial/` and actively use it (operator-confirmed 2026-09-24) —
  the trio's verdict must weigh active current-gen usage, not just the
  recorded misses).

The output is the **keep-list that defines lightweight ASK v2**, plus a
draft KIT-ADR recording scope and rejected alternatives. This audit
deliberately runs BEFORE any distribution-architecture build: the size
of the sync problem is proportional to the size of ASK, and building
sync machinery for artifacts about to be deleted is waste.

**Context**: The fleet inventory (2026-09-24) found 27 ASK-family
projects of which only 3 are active consumers; the newest projects
(ixda-services pair) already run a de-facto lightweight ASK (user-level
plugin + thin `.kit/`, no local `.claude/`). Each project generation has
carried less ASK than the last — the fleet's revealed preference is
lightweight. Precedent: dispatch-kit was archived when native features
ate its niche (KIT-ADR-0035).

**Related Work**: `.kit/context/FLEET-INVENTORY-2026-09-24.md`;
KIT-ADR-0035; KIT-0116 (tiered native review pipeline — already
re-centered review on native `/code-review`).

## Requirements

### Functional Requirements

1. **Artifact census**: enumerate every shipped artifact (plugin roster
   28 components; scripts/core + scripts/optional; door engines;
   evaluator library integration; workflow docs; templates). No
   artifact unsorted.
2. **Per-artifact verdict with dated evidence**: each verdict cites the
   native Claude Code feature (from live docs, verified that day — never
   memory) and, for "superseded", a comparison test or recorded incident
   (e.g. trio 0-for-17 vs bots 11-for-14 on deletion-heavy input,
   KIT-0069/0073 prose-sweep shutouts). Verdicts without evidence are
   marked PREDICTED and excluded from action.
3. **Empirical cross-check**: diff the stratum-A projects' actual usage
   (ixda-services pair, DTL) against the shipped surface. Anything the
   newest projects never needed is a deletion candidate; anything they
   hand-rolled that we don't ship is a gap candidate.
4. **Keep-list**: the resulting "lightweight ASK v2" scope, stated as a
   list of artifacts with one-line purposes — each keep-list entry must
   name its single Jackson-style concept/purpose (an entry serving two
   purposes gets split or questioned).
5. **Draft KIT-ADR** ("ASK v2 scope") with: keep-list, retirement list
   (each with disposal route: archive / fold into docs / salvage), and
   rejected alternatives (hardened monolith, artifact registry,
   status-quo).
6. **Model-capability check**: for kept agent bodies, note where
   Opus-5.5/Fable-class models make prescriptive scaffolding removable
   (behavioral notes over procedure — the feature-developer-o55 preamble
   pattern). Trimming itself is follow-on work, not this task.

### Non-Functional Requirements

- [ ] Every "native does X" claim verified against live docs/changelog
      the day it is written, with date stamped (the environment lags —
      three recorded staleness incidents)
- [ ] No retirement executed in this task — this task DECIDES; disposal
      rides follow-on tasks (KIT-0117 pattern)
- [ ] Fleet-facing claims cite FLEET-INVENTORY-2026-09-24.md or a fresh
      scan, never memory

## TDD Workflow

Not applicable — analysis/decision task, no production code. The
"tests" here are the evidence requirements above (FR2) and the
adversarial evaluation gate below. Any small probe scripts written
during the audit are disposable and live in the session scratchpad,
not the repo.

## Approach

**Phase 1 — Census + native-feature baseline (planner or fd session).**
Build the artifact table (roster from the plugin manifest + scripts
dirs + door engines). Fetch and date-stamp the current Claude Code
native feature set relevant to each row. Output: census table with
evidence columns, PREDICTED rows marked.

**Phase 2 — Empirical cross-check (same session or second).**
Stratum-A usage diff (read-only scans of ixda pair + DTL: which
skills/commands/scripts are actually invoked or present). Interview
operator for the "used but invisible to scans" set.

**Phase 3 — Verdicts + keep-list + draft ADR.**
Sort every row; write the keep-list; draft KIT-ADR "ASK v2 scope"
(next free number at drafting time — verify; 0037+ per KIT-ADR-0036
being taken). Run the evaluation gate (arch-review-fast; escalate to
arch-review o3 given the `architecture` flag and the scope of the
decision). Present to operator for ruling.

## Acceptance Criteria

### Must Have ✅

- [ ] Census covers 100% of shipped artifacts (roster count reconciled
      against plugin manifest — currently 28 components — plus scripts,
      engines, evaluator integration, workflow docs)
- [ ] Every verdict evidenced-and-dated or marked PREDICTED
- [ ] Stratum-A empirical diff completed and cited in verdicts
- [ ] Keep-list published with per-entry single-purpose statement
- [ ] Draft KIT-ADR written with retirement + disposal routes and
      rejected alternatives
- [ ] Adversarial evaluation gate run (arch-review-fast minimum;
      arch-review for the contested calls); log persisted
- [ ] Operator ruling obtained on the keep-list before any follow-on
      retirement tasks are filed

### Should Have 🎯

- [ ] Follow-on task stubs drafted for each retirement cluster (ride
      KIT-0117's pattern) and for the distribution ADR
- [ ] Per-agent note on model-capability-driven trimming opportunities
      (FR6)

### Nice to Have 🌟

- [ ] Cost/effort estimate of the release train before/after (feeds
      KIT-0111 disposition)

## Success Metrics

### Quantitative
- 100% of artifacts sorted; 0 unevidenced non-PREDICTED verdicts
- Keep-list materially smaller than current surface (expectation, not
  requirement — "keep everything" is a valid audited outcome if the
  evidence says so)

### Qualitative
- The distribution-architecture ADR that follows can name its artifact
  surface in one table
- Operator can answer "what is ASK for?" in one sentence per kept
  concept

## Risks & Mitigations

### Risk 1: Audit drifts into redesign (scope creep into the distribution ADR)
**Likelihood**: Medium | **Impact**: Medium
**Mitigation**: This task's output is verdicts + keep-list + scope ADR
only. Distribution architecture (baseline/overlays/reconciler) is
explicitly a SEPARATE follow-on task; note ideas in the ADR's
Consequences, do not design them here.

### Risk 2: "Native does it" claims decay (docs move fast; env lags)
**Likelihood**: High | **Impact**: Medium
**Mitigation**: Date-stamp every claim; verify against live docs at
write time (recorded staleness incidents: model-ID class ×3). PREDICTED
rows carry no action.

### Risk 3: Deleting scaffolding that quietly still earns its keep
**Likelihood**: Medium | **Impact**: High
**Mitigation**: No retirement in this task; disposal tasks each re-verify
their own premise at execution time (retirement-sweeps-grep-internals
pattern); salvage-then-archive preserves recovery.

## Rollback Plan

Nothing to roll back in this task (no retirements executed). The draft
ADR remains Proposed until operator ruling; a rejected keep-list entry
is an edit, not a rollback.

## Time Estimate

| Phase | Time | Status |
|-------|------|--------|
| 1. Census + native baseline | 0.5-1 session | [ ] |
| 2. Empirical cross-check | 0.5 session | [ ] |
| 3. Verdicts + keep-list + draft ADR + eval gate | 1 session | [ ] |
| **Total** | **2-3 sessions** | [ ] |

## References

- `.kit/context/FLEET-INVENTORY-2026-09-24.md` (step 1 of this arc)
- `.kit/adr/KIT-ADR-0035-*` (dispatch-kit archive — precedent + pattern)
- `.kit/context/workflows/REVIEW-PIPELINE.md` (KIT-0116 outcome — native
  review re-centering already underway)
- `docs/PLUGIN-UPGRADE-GUIDE.md`, `docs/MANIFEST-UPGRADE-GUIDE.md`
  (current upgrade machinery under audit)
- Daniel Jackson, *The Essence of Software* — concepts/synchronizations
  framing used in the arc discussion (session 2026-09-24)

## Notes

- **Sequencing**: KIT-0116 Phase-1 remains the operator-ruled next
  implementation task; this audit is planner-led analysis and can
  interleave. Operator decides ordering.
- **The audit may eat the channels too**: PyPI door vs plugin-only
  distribution is in scope as an audit row (relates KIT-0107/0108), not
  a protected assumption.
- **Numbering**: filed as KIT-0123; NOTE a pre-existing backlog
  collision — two KIT-0120 files exist (`door-warn-on-empty-env-source`
  and `mechanize-preflight-gate-8`). Resolve separately; one needs
  renumbering (planner chore, do not renumber silently mid-audit).
