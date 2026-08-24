# KIT-0116: Automated review pipeline — native review skills, background reviewer subagents, deep-review workflow

**Status**: In Review
**Priority**: high
**Assigned To**: feature-developer
**Estimated Effort**: 2-3 days (3 phases, independently shippable)
**Created**: 2026-08-18
**Target Completion**: —
**Linear ID**: (automatically backfilled after first sync)

## Related Tasks

**Parent Task**: —
**Depends On**: — (KIT-0114/KIT-0115 are independent; no ordering constraint)
**Blocks**: KIT-0117 (dispatch-kit archive — its salvage note references this spec as the landing site)
**Related**: KIT-0103 (agent-body canon changes ride the same release-train discipline)

## Status History

- **Todo** (from —) - 2026-08-18

## Overview

The kit's review coverage is strong at the ends of the pipeline and hollow in
the middle. Spec time gets cognitive diversity via adversarial evaluators
(arch-review-fast / arch-review / claude-arch). PR time gets BugBot +
CodeRabbit with a mature triage discipline. But the three dedicated reviewer
agents — `code-reviewer`, `security-reviewer`, `document-reviewer` — are
defined and **never invoked**, because invoking them has meant another
terminal tab and another pasted starter. Implementation-level architecture
review does not exist at all (evaluators only ever see the spec, not the
diff). Documentation is written opportunistically, not systematically.

This task wires the missing review dimensions into the existing gated
workflow using **native Claude Code features only** — built-in review skills,
background read-only subagents, and (opt-in, for risky tasks) a
multi-lens review Workflow. No new infrastructure, no new transport, no
polling. The operator stays the gate for verdicts; the operator stops being
the courier for review labor.

**Context**: This is the designed landing site for the salvaged dispatch-kit
concepts (see Appendix A). dispatch-kit (— `~/Github/dispatch-kit`, DSP
prefix, dormant since 2026-03) solved "human as router" with an event bus +
transition rules + gates on a tmux transport. The transport is obsolete
(native cross-session messaging, Agent tool background subagents, task
notifications), but three of its concepts survive here as configuration
shape, not code: declarative transitions (→ gate wiring in agent bodies),
trust modes (→ default-on / flag-triggered / opt-in tiers), and the bus
(→ harness task notifications). **No dispatch-kit code is reused.**

**Related Work**: KIT-0117 (archive chore); `.claude/skills/` (self-review,
code-review-evaluator, preflight); planner Phase 4 handoff contract;
sub-agent permission trap (Recurring Footguns, planner body).

## Requirements

### Functional Requirements

**Tier 1 — native review skills in the gate sequence (smallest, ship first)**

1. `feature-developer` (and `-f5`) preflight/pre-PR sequence invokes the
   harness-native `/code-review` skill on the branch diff after
   `code-review-evaluator` passes, before `review-handoff`. Findings are
   triaged inline (fix or explicitly defer with reason in the PR
   description).
2. `/security-review` runs in the same slot **when the task carries the
   `security` review flag** (see FR-7); never silently skipped — flagged
   tasks record the run and its outcome in the review starter.
3. The `preflight` skill's gate checklist grows one gate: "dedicated review
   pass done (code always; flagged dimensions as declared)". The gate
   count is a volatile value — surfaces that cite it do so by reference to
   the preflight skill/REVIEW-PIPELINE.md, and the drift greps verify
   consistency wherever a literal count survives.

**Tier 2 — background reviewer subagents (the tab-killer)**

4. After local tests pass, `feature-developer` MAY spawn the kit's reviewer
   agents (`code-reviewer`; plus `security-reviewer` / `document-reviewer`
   when flagged) as **background subagents via the Agent tool**, in
   parallel, and continue working (docs, changelog) until notified.
   Findings are triaged with the same fix-or-defer discipline as bot
   threads.
5. A new ADR codifies the **read-only carve-out** to the standing
   no-Task-delegation rule: delegation remains banned for *implementation*
   agents (permission-trap rationale unchanged); it is permitted for
   reviewer agents whose toolset is read-only (Read/Grep/Glob + read-only
   Bash). The planner body's "Sub-agent permission trap" footgun and the
   agent bodies that restate the rule are updated to cite the ADR.
6. Reviewer agent definitions are audited so their declared toolsets
   actually satisfy the carve-out. **Default remedy is REMOVAL of Bash**
   from reviewer agents (e.g. `code-reviewer` currently declares Bash).
   Bash may be retained only if a specific read-only invocation set is
   demonstrably necessary (e.g. `git diff`), in which case the exact
   permitted commands are enumerated in the agent body and the ADR;
   "documented read-only usage" without enumeration is not acceptable
   (evaluator finding, round 1).

**Flag system — planner-declared review scope**

7. Task specs and handoffs gain an optional `**Review Flags**:` field.
   The planner sets flags at spec/handoff time using trigger heuristics
   **defined once, in REVIEW-PIPELINE.md** (deep-evaluator finding: this
   spec is rationale, not the value authority — flag names and heuristics
   below are ILLUSTRATIVE; the authoritative list lives in
   REVIEW-PIPELINE.md from Phase 1 onward):
   - `architecture` (illustrative triggers: multi-module change, new
     pattern/abstraction, public API surface, cross-repo contract)
   - `security` (illustrative: auth, input handling, secrets, network
     calls, dependency changes)
   - `docs-audit` (illustrative: user-facing surface changed, or ≥ N
     sessions since last audit)
   Default (no flags) = code review only. Planner Phase 2/4 instructions
   **reference** the heuristics (cite, never restate);
   TASK-STARTER-TEMPLATE carries only the field shell.
8. **Architecture review of the implementation**: when the `architecture`
   flag is set, the pre-PR sequence includes an implementation-level
   architecture pass via a **new dedicated `architecture-reviewer` agent**
   (mirroring the security-reviewer / document-reviewer structure — one
   agent per flagged dimension, single responsibility; evaluator finding,
   round 1), or the Tier 3 workflow for high-risk tasks. This is a new
   dimension — today evaluators only see specs.

**Docs habit (explicitly NOT a per-task gate)**

9. `feature-developer` workflow gains a standing step before preflight:
   "update the docs your diff touches" (README/workflow docs/CHANGELOG as
   applicable). `document-reviewer` runs as a **periodic audit**
   (flag-triggered via `docs-audit`), not per task.

**Tier 3 — deep-review workflow (opt-in, risky tasks only)**

10. A saved workflow (`.claude/workflows/` or documented inline script)
    implements multi-lens diff review: parallel correctness / architecture
    / security lenses over the branch diff, each finding **adversarially
    verified** (refute-first) before surfacing — the same cognitive-
    diversity pattern the kit uses at spec time, applied to code. Invoked
    explicitly (operator or starter says so) for tasks flagged high-risk;
    never a default gate.
11. Workflow invocation honors the kit's explicit-opt-in rule: the starter
    or operator asks for it in words; fd never self-escalates to Tier 3.
12. **Tier 3 escalation contract is formal, not prose** (deep-evaluator
    finding): REVIEW-PIPELINE.md specifies the exact invocation (command /
    starter phrasing), who may invoke (operator, or planner via starter),
    and what evidence the run leaves behind — so escalation is neither
    accidental (token waste) nor a dead code path.

### Non-Functional Requirements

- [ ] **Proportionality**: default task cost grows by ONE code-review pass
      only. Arch/security/docs dimensions run solely when flagged. No
      always-on three-reviewer fan-out.
- [ ] **No new infrastructure**: native skills, Agent tool, Workflow tool,
      task notifications. No daemons, no polling loops, no tmux, no bus.
- [ ] **Operator sovereignty unchanged**: subagent findings inform; the
      human review verdict (planner Phase 7) remains the merge gate.
- [ ] **Maintainability**: every rule lands in exactly ONE authority file
      with cross-references (KIT-0101 R5: two authorities drift).
      Candidate single authority: a `REVIEW-PIPELINE.md` workflow doc that
      agent bodies and skills cite. It owns not only the review ladder but
      also the **governance of the Review Flags heuristics** — how trigger
      criteria are changed, reviewed, and propagated (evaluator finding,
      round 2); planner bodies cite, never redefine.

## Verification Approach (adapted TDD)

This is predominantly an instruction-surface task (agent bodies, skills,
templates, workflow docs) plus at most small script changes. Code-style TDD
applies only if scripts change (then: pytest, 80% new-code coverage,
pattern_lint). For the instruction surfaces:

1. **Red**: enumerate the gate sequence as a checklist per tier; write the
   drift-check greps (which files must mention the new gate, the flag
   field, the ADR) before editing.
2. **Green**: edit surfaces; run the greps; run a live smoke test — one
   scratch branch through Tier 1 (skill invocation) and one background
   `code-reviewer` spawn (Tier 2), transcript cited in the PR.
3. **Consistency**: `.claude/agents/` bodies, plugin-mirrored copies, and
   `agentive-skills` marketplace twins updated **by copy, not
   re-derivation** (patterns.yml: `harden_twins_by_copy_not_rederivation`).

### Test Requirements

- [ ] Drift greps pass: gate count, flag field name, and ADR number appear
      consistently across preflight skill, fd bodies (both variants),
      planner bodies (both variants), TASK-STARTER-TEMPLATE
- [ ] Drift greps include a **Bash-absence check** on reviewer agent
      frontmatter (deep-evaluator finding: enforce FR-6 mechanically in
      Phase 1 CI so Tier 2 cannot ship with wrong tool declarations)
- [ ] Live smoke: Tier 1 skill run + Tier 2 background reviewer run, each
      with transcript evidence
- [ ] If any Python script changes: pytest + pattern_lint + coverage per
      project standards

## Implementation Plan

### Phase 1 — Tier 1 + flag system (ship alone if needed)

Files to modify:

1. `.claude/skills/preflight/` — add the review gate; renumber/recount gates
2. `.claude/agents/feature-developer.md` + `feature-developer-f5.md` — gate
   sequence: code-review-evaluator → `/code-review` → (flagged)
   `/security-review` → review-handoff; docs-habit step
3. `.claude/agents/planner.md` + `planner-f5.md` — Phase 2/4: Review Flags
   field + trigger heuristics
4. `.kit/templates/TASK-STARTER-TEMPLATE.md` — carry Review Flags
5. New: `.kit/context/workflows/REVIEW-PIPELINE.md` — single authority for
   the full review ladder (what runs when, who triggers, cost tiers)

### Phase 2 — Tier 2 + ADR

6. New ADR `KIT-ADR-0036-readonly-reviewer-delegation.md` — the carve-out,
   its rationale, and the toolset condition (renumbered 2026-08-20:
   KIT-ADR-0035 was taken by the native-coordination decision ADR —
   re-verify at authoring time)
7. fd bodies — background-spawn instructions (spawn after tests pass,
   continue docs work, triage on notification, fix-or-defer discipline)
8. `.claude/agents/code-reviewer.md`, `security-reviewer.md`,
   `document-reviewer.md` — toolset audit for read-only compliance
   (Bash removed by default, per FR-6); prompt sharpening for diff-scoped
   review, including **explicit context inputs**: each specialist reviewer
   is instructed to read `patterns.yml`, `REVIEW-PIPELINE.md`, and the
   ADRs relevant to its dimension before reviewing, so findings are
   grounded in kit conventions rather than generic best practice
   (evaluator finding, round 2 — also the Risk 3 differentiation from
   bots)
8b. New: `.claude/agents/architecture-reviewer.md` — dedicated
   implementation-level architecture reviewer (FR-8), read-only toolset
   from birth
9. Planner bodies — footgun entry updated to cite the ADR

### Phase 3 — Tier 3 workflow

10. Deep-review workflow script (multi-lens fan-out + adversarial verify),
    saved + documented in REVIEW-PIPELINE.md with its opt-in contract

### PR Plan

Three PRs, one per phase — each independently valuable and mergeable.
Phase boundaries are also abort points: if Tier 2's live smoke exposes an
unresolvable permission-prompt issue, Phase 1 still stands.

## Acceptance Criteria

### Must Have ✅

- [ ] Default task path: exactly one added review pass (`/code-review`),
      triaged fix-or-defer, visible in review starter
- [ ] Flagged dimensions run when declared, never when not
- [ ] Review Flags field + heuristics in planner bodies and starter template
- [ ] ADR for read-only delegation carve-out; footgun text updated to match
- [ ] Docs-habit step in fd bodies; document-reviewer positioned as audit
- [ ] Deep-review workflow exists, documented, opt-in only
- [ ] Single-authority doc (REVIEW-PIPELINE.md); other surfaces cite it
- [ ] Drift greps green; live smoke transcripts for Tiers 1 and 2
- [ ] Twins (plugin/marketplace copies) updated by copy on the release train

### Should Have 🎯

- [ ] Drift greps wired into automation (`ci-check.sh` or pre-commit) so
      instruction-surface consistency is a mandatory gate, not a manual
      step (evaluator finding, round 1)
- [ ] `architecture-reviewer` produces implementation-level findings
      distinct from spec-time evaluator output (verified once on a
      real diff)
- [ ] Reviewer subagent cost noted in REVIEW-PIPELINE.md (tokens/time from
      the smoke runs) so flag decisions are informed

### Nice to Have 🌟

- [ ] `/simplify` positioned in the ladder as an optional post-review pass
- [ ] Review-findings → REVIEW-INSIGHTS.md extraction hook noted for
      planner Phase 7

## Success Metrics

### Quantitative
- Reviewer agents invoked ≥ 1× per applicable task (from 0 today)
- Default-path overhead: ≤ 1 additional review pass; flagged-path overhead
  declared up front in the starter
- Zero new daemons/processes/config systems

### Qualitative
- Operator no longer opens tabs to obtain review labor
- Findings arrive pre-PR (cheaper) instead of only at bot/human time
- Docs updated in the same PR as the change they describe

## Risks & Mitigations

### Risk 1: Reviewer subagents hit the permission trap despite read-only intent
**Likelihood**: Medium — `code-reviewer` declares Bash; `settings.json`
allow-patterns don't inherit into Task-spawned agents.
**Impact**: Medium (Tier 2 stalls; Tier 1 unaffected)
**Mitigation**: Phase 2 live smoke is the gate — verify before codifying;
reviewer toolsets default to Read/Grep/Glob with Bash removed (FR-6);
ADR records the verified boundary, not the hoped-for one.

### Risk 2: Review inflation — flags become always-on by social drift
**Likelihood**: Medium
**Impact**: Medium (token/time cost, finding fatigue, gate fatigue)
**Mitigation**: Heuristics are written criteria in the planner body, not
vibes; REVIEW-PIPELINE.md states the default is code-only; retro checks
flag usage occasionally.

### Risk 3: Redundancy with bots — subagent findings duplicate CodeRabbit/BugBot
**Likelihood**: Medium
**Impact**: Low-Medium (wasted triage)
**Mitigation**: Reviewer prompts scope to what bots don't do well
(cross-file reasoning, kit-convention adherence, patterns.yml compliance,
architecture); measured in the smoke run — if overlap dominates, narrow
the prompts before shipping Phase 2.

### Risk 4: Instruction-surface drift across twins and variants
**Likelihood**: High (three prior incidents)
**Impact**: Medium
**Mitigation**: Single-authority doc + drift greps in acceptance criteria +
copy-not-rederivation for twins; changes ride one release train.

## Rollback Plan

1. **Immediate**: each tier is a self-contained instruction change —
   revert the phase's PR; no data or state to unwind
2. **Verification**: drift greps against the reverted tree; one task run
   through the old gate sequence
3. **Root cause**: retro; findings to REVIEW-INSIGHTS.md
4. **Prevention**: tier boundaries are abort points by design

## Time Estimate

| Phase | Time | Status |
|-------|------|--------|
| Adversarial evaluation of this spec | 1-2 hours | [ ] |
| Phase 1: Tier 1 + flags | 4-6 hours | [ ] |
| Phase 2: Tier 2 + ADR (incl. live smoke) | 6-8 hours | [ ] |
| Phase 3: Tier 3 workflow | 4-6 hours | [ ] |
| Docs + twins + release train | 3-4 hours | [ ] |
| Review rounds | 2-4 hours | [ ] |
| **Total** | **20-30 hours (~2-3 days)** | [ ] |

## References

- **Salvage source**: `~/Github/dispatch-kit` — `docs/dispatch-kit-design.md`
  (concepts: Event/Bus/Gate/trust modes); archived per KIT-0117
- **Platform capability mapping** (deep-evaluator finding — the required
  capabilities, so a platform change means remapping this list, not
  re-architecting): (a) diff-scoped review skill invocable from a session
  (`/code-review`, `/security-review`); (b) read-only agent delegation
  with background completion notification (Agent tool); (c) deterministic
  parallel fan-out with verification stages (Workflow tool). VERIFIED
  present against code.claude.com docs 2026-08-18 by research agent
  (cross-session messaging v2.1.224+ default-on; Agent Teams experimental;
  Agent View); re-verify at implementation time. Vendor coupling is an
  accepted strategic choice (see Notes).
- **Harness-native skills present in this environment**: `code-review`
  (effort levels, `--comment`, `--fix`), `security-review`, `simplify`
- **Kit surfaces**: `.claude/skills/preflight/`, `self-review`,
  `code-review-evaluator`, `review-handoff`, `bot-triage`
- **Standing rules touched**: no-Task-delegation footgun (planner body);
  KIT-0101 R5 single-authority; patterns.yml
  `harden_twins_by_copy_not_rederivation`

## Notes

- Tier ordering is also a de-risking ladder: each tier is useful without
  the next; stop-loss at every phase boundary.
- Out of scope: reusing any dispatch-kit code; tmux in any form; changing
  the human-verdict merge gate; Agent Teams adoption (experimental —
  revisit when it leaves the flag); Windows support considerations.
- Accepted strategic dependency (evaluator round 2, acknowledged not
  fixed): the design is deliberately coupled to Claude Code native
  features. Feature availability is re-verified at implementation time;
  long-term platform coupling is revisited in ordinary architecture
  reviews, not hedged against here.
- **Design input (planner, 2026-08-24, from the KIT-0118 retro —
  binding on REVIEW-PIPELINE.md's tier heuristics)**: reviewer-tier
  selection has a third axis beyond the prose-vs-logic split.
  Measured on PR #147: the full evaluator trio, on full-file input,
  passed an argument-parsing seam that CodeRabbit flagged Major
  (`--evaluators=` skipping validation), and across four bot rounds
  the trio found nothing true the bots missed while its one FAIL was
  three-fifths false. Combined with KIT-0069/0073 (trio 0-for-17 vs
  bots 11-for-14 on deletion-heavy prose), the heuristic
  REVIEW-PIPELINE.md should encode: **argument-parsing and
  input-validation seams are bot-favourable and evaluator-hostile**
  — on flag-adding or argv-touching diffs, do not buy extra
  evaluator passes; spend the review budget on input-space
  enumeration (patterns.yml `flag_presence_is_not_flag_emptiness`)
  and on the bots. Full evidence: KIT-0118 retro (Surprising 2,
  Lesson 3) + REVIEW-INSIGHTS.md (KIT-0118 block).

---

## Appendix A: dispatch-kit concept mapping (salvage record)

| dispatch-kit concept | Fate | Where it lands here |
|---|---|---|
| Event bus (`bus.jsonl`) | Superseded | Harness task notifications (background agent completion) |
| Transition rules (when X → spawn Y) | **Salvaged as config shape** | Gate wiring in fd bodies: "tests pass → spawn reviewers" |
| Gates (human/CI/evaluator/compound) | Already lived in the kit | Preflight gates + human verdict (unchanged) |
| Trust modes (approve/notify/auto) | **Salvaged as tiering** | default-on (code) / flag-triggered (arch, security, docs) / opt-in (deep workflow) |
| Spawner (tmux send-keys) | Obsolete | Agent tool background subagents |
| Sessions (tmux attach/kill) | Obsolete | `/tasks`, Agent View, cross-session messaging |
| Starter (handoff context) | Already lived in the kit | TASK-STARTER-TEMPLATE (unchanged) |

---

**Template Version**: 1.0.0 (adapted for instruction-surface task)
**Created**: 2026-08-18
**Maintained By**: planner-f5
