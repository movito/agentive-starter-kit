# KIT-ADR-0037: ASK v2 scope — the lightweight keep-list

**Status**: Proposed (DRAFT — pending KIT-0123 evaluation gate and
operator ruling; number verified free 2026-09-28)
**Date**: 2026-09-28
**Task**: KIT-0123
**Deciders**: operator (@movito) + planner-f5
**Evidence**: `.kit/context/FLEET-INVENTORY-2026-09-24.md`,
`.kit/context/KIT-0123-audit-worksheet.md` (census, native baseline
dated 2026-09-24/28, stratum-A cross-check, operator interview)

## Context

ASK accreted three layers with different fates: (1) process discipline
and institutional knowledge (no harness equivalent), (2) harness
workarounds (native Claude Code now ships the mechanism, sometimes
with contracts that contradict ours), (3) distribution machinery
(two channels + vendored scripts, with a recorded drift class).
The fleet inventory shows consumers shedding weight generation over
generation, ending at the ixda-services pattern: user-level plugin +
thin `.kit/` + one lifecycle script. Precedent for retiring a whole
subsystem to native: dispatch-kit (KIT-ADR-0035).

Two operator rulings bind this decision (2026-09-28):

- **R1 — strict gates**: CI + BugBot + CodeRabbit are load-bearing;
  architectural morass is a live risk. Mechanisms may consolidate;
  the gate ladder never weakens.
- **R2 — commands**: agents demonstrably self-handle polling/status;
  retirement of the operator-convenience commands requires the
  ablation test (worksheet Phase 2b protocol), not inference.

## Decision

ASK v2 is a **process-discipline layer riding the native harness**,
distributed as (a) the agentive-workflow plugin for agents/commands/
skills and (b) the `agentive` CLI for lifecycle + door. Everything
below not on the keep-list is retired via salvage-then-archive
(KIT-ADR-0035 pattern), each retirement as its own task that
re-verifies its premise at execution time.

### Keep-list (each entry: one concept, one purpose)

| Artifact | Concept / purpose |
|---|---|
| planner, feature-developer (+ model-pin variants f5, o55) | Gated implementation/coordination process — the moat. MANDATED TRIM: harness-workaround content out (stale cache-TTL pacing, polling mechanics now native, `$()`-era scaffolds re-examined per model generation) |
| code-, security-, document-, architecture-reviewer | Strict review dimensions as spawnable read-only reviewers (KIT-ADR-0036 delegation shape) — R1 |
| project-intake | Prototype graduation through the door |
| upgrader | Project-to-baseline mover; grows into the reconciler (baseline capture, prune-shadowing, overlay recording) |
| Commands: check-ci, preflight, triage-threads, retro, check-spec, wrap-up | Agent/doc-cited gate machinery (grep 2026-09-28: check-ci alone is cited by 8 agents — retiring it would dangle 14 references) |
| Skills: bot-triage, pre-implementation, self-review, review-handoff | Institutional knowledge, cheap prose, evidence-derived |
| Skill: code-review-evaluator + adversarial trio | KEPT under R1 for logic-shaped diffs, alongside native /code-review as the default gate; tier selection per REVIEW-PIPELINE; evaluator-channel hygiene rides KIT-0119/0121 |
| Task lifecycle: spec folders, status flow, `agentive` CLI | Process state machine. CONVERGENCE: CLI is canonical (DTL pattern); vendored `scripts/core/project` becomes a shim then retires (kills the #142/#143 drift class) |
| Workflow canon (REVIEW-PIPELINE first among equals) + templates (TASK-STARTER authority, AGENT-TEMPLATE, task template) | Written process; per-doc trim pass for native-superseded mechanics |
| KIT-LOCAL marker-merge | Consumer-customization concept (unchanged) |
| roster.yaml pattern (`ships/retired/why` + hashes) | Per-artifact decision record; EXTEND for overlays/provenance rather than inventing parallel state |

### Retirement candidates (each rides its own follow-on task)

| Artifact | Route | Gate |
|---|---|---|
| status, babysit-pr, start-task, commit-push-pr commands | UNCITED anywhere (grep 2026-09-28) — retire clean after ablation | Ablation test (R2) MUST pass first; /status also carries dead dispatch steps (KIT-0117 overlap); /start-task superseded by planner authoring-time branch rule |
| check-bots, wait-for-bots commands (+ their .sh scripts) | Retire with 2 citation fixes (bot-triage line, WORKFLOW-FREEZE) | Ablation test (R2) + citation retarget |
| ci-checker agent | Absorb into fd Phase 7 + verify-ci.sh | Citation sweep |
| test-runner agent | Contested — TDD is a project rule but current models run suites unaided; decide with operator | Operator ruling |
| powertest-runner, bootstrap, agent-creator agents | Already `ships: false`; archive kit-side (keep AGENT-TEMPLATE) | Low risk |
| WORKTREE-WORKFLOW mechanics | Native EnterWorktree/isolation; KEEP the ordering rule (project start on main → worktree) inside task protocols | Doc trim, not deletion |
| Per-consumer scripts/core copies (beyond hook-wired hygiene: ci-check, pattern_lint, validate_task_status) | Migrate lifecycle to CLI; hygiene scripts stay project-side | Distribution ADR (successor task) |

### Explicitly NOT decided here

Distribution architecture (baseline + overlays + reconciler) — the
successor ADR, now sized to this keep-list. Channel consolidation
(plugin vs PyPI door) — audit row stays open into that ADR
(KIT-0107/0108 related).

## Alternatives considered

- **Hardened monolith** (faster releases, keep everything): fails
  partial adoption; keeps paying the vigilance tax on redundant
  channels. Rejected.
- **Artifact registry** (per-artifact versions, consumer-resolved
  compatibility): moves compatibility burden onto a one-operator
  fleet; prose-cites-prose coupling makes per-artifact attestation
  weak. Rejected.
- **Status quo**: worksheet documents shipped guidance that now
  contradicts the live harness (cache-TTL pacing). Rejected on
  evidence.

## Consequences

- Smaller sync surface → the distribution ADR gets cheaper.
- Trims touch plugin-rostered bodies → changes ride release trains
  (KIT-0111 guard priority rises).
- Retirements are individually reversible (salvage-then-archive);
  the keep-list is re-auditable — verdicts carry dates, and native
  capability keeps moving.
