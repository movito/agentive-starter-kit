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
| Commands: check-ci, preflight, triage-threads, retro, check-spec, wrap-up | Agent/doc-cited gate machinery — retiring any of these dangles live references (citation table with counts and file lists: worksheet Phase 2b, dated 2026-09-28) |
| Skills: bot-triage, pre-implementation, self-review, review-handoff | Institutional knowledge, cheap prose, evidence-derived |
| Skill: code-review-evaluator + adversarial trio | KEPT under R1 for logic-shaped diffs, alongside native /code-review as the default gate; tier selection per REVIEW-PIPELINE; evaluator-channel hygiene rides KIT-0119/0121 |
| Task lifecycle: spec folders, status flow, `agentive` CLI | Process state machine. CONVERGENCE: CLI is canonical (DTL pattern); vendored `scripts/core/project` becomes a shim then retires (kills the #142/#143 drift class) |
| Workflow canon (REVIEW-PIPELINE first among equals) + templates (TASK-STARTER authority, AGENT-TEMPLATE, task template) | Written process; per-doc trim pass for native-superseded mechanics |
| KIT-LOCAL marker-merge | Consumer-customization concept (unchanged) |
| roster.yaml pattern (`ships/retired/why` + hashes) | Per-artifact decision record; EXTEND for overlays/provenance rather than inventing parallel state |

### Retirement candidates (each rides its own follow-on task)

| Artifact | Route | Gate |
|---|---|---|
| status, babysit-pr, start-task, commit-push-pr commands | Uncited in any kit surface (evidence: worksheet Phase 2b grep, 2026-09-28) — retire clean after ablation | Ablation test (R2) MUST pass first — protocol: worksheet Phase 2b; /status also carries dead dispatch steps (KIT-0117 overlap); /start-task superseded by planner authoring-time branch rule |
| check-bots, wait-for-bots commands (+ their .sh scripts) | Retire after retargeting their few remaining citations (list: worksheet Phase 2b) | Ablation test (R2, protocol: worksheet Phase 2b) + citation retarget |
| ci-checker agent | Absorb into fd Phase 7 + verify-ci.sh | Citation sweep |
| test-runner agent | Contested — TDD is a project rule but current models run suites unaided; decide with operator | Operator ruling; FALLBACK: if unruled by the time the distribution ADR lands, default KEEP (R1 strictness bias — never retire a gate-adjacent artifact by timeout) |
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

- **Execution surface is roster.yaml, not this document**: the
  keep-list table above is rationale; the machine-readable state that
  tooling and guards consume is roster.yaml's `ships`/`retired`/`why`
  fields (extended for overlays by the successor ADR). Every keep or
  retire verdict lands as a roster edit in the release that executes
  it — no parallel keep-list file is created.
- Smaller sync surface → the distribution ADR gets cheaper.
- Trims touch plugin-rostered bodies → changes ride release trains
  (KIT-0111 guard priority rises).
- **Riding native is an explicit dependency, managed by re-audit, not
  by a compatibility shim** (eval-gate finding, 2026-09-28): native
  harness contracts change under us — the cache-TTL divergence this
  audit found is the live example. The mechanism: keep-list verdicts
  and the worksheet's native-baseline carry dates; a model rollout or
  observed harness-contract change triggers a re-audit pass (the
  upgrader agent's pin-refresh duty extends to this). No standing
  adapter layer is built — that would recreate the workaround stratum
  this ADR retires.
- **roster.yaml extension discipline** (eval-gate finding,
  2026-09-28): the successor distribution ADR must define the roster's
  schema evolution explicitly and may split overlay/provenance state
  into a sibling artifact rather than overload one file — "extend the
  pattern" constrains the concept, not the file count.
- Retirements are individually reversible (salvage-then-archive);
  the keep-list is re-auditable — verdicts carry dates, and native
  capability keeps moving.

## Appendix — premise snapshot (qualitative; primary sources cited)

One-line summaries of the load-bearing external premises, so this ADR
reads standalone; the cited documents remain authoritative and any
conflict resolves in their favor.

- **KIT-ADR-0035**: precedent — a whole subsystem (dispatch-kit) was
  retired when native Claude Code coordination superseded it, via
  salvage-then-archive; this ADR reuses that disposal pattern.
- **KIT-ADR-0036**: the ruled exception letting implementation
  sessions spawn read-only reviewer agents as background subagents —
  the delegation shape that keeps the reviewer agents differentiated.
- **Fleet inventory (2026-09-24)**: 27 ASK-family projects, 3 active
  consumers; plugin enabled at user level (machine-wide agents);
  newest projects run a thin `.kit/` with no local `.claude/`;
  the adversarial layer is actively used by current-gen projects.
- **Audit worksheet (2026-09-24/28)**: census, dated native-baseline,
  command-citation tables, ablation protocol (Phase 2b), and the
  operator rulings R1/R2 quoted in Context above.
