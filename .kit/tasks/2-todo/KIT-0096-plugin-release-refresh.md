# KIT-0096: Plugin release — refresh agentive-workflow from current kit content (2.0.0)

**Status**: Todo
**Priority**: high (blocks a meaningful new-project test — the plugin currently ships v6/v7-era agents and NO planner; in the packaged world the plugin is THE agent channel)
**Type**: Infrastructure / release
**Estimated Effort**: 0.5-1 day
**Created**: 2026-08-09
**Source**: pre-test readiness check 2026-08-09 (operator installing the
plugin surfaced the gap). This re-files archived KIT-0060, whose revive
condition — "plugin skill copies drift again" — has fired in the
strongest possible form.

## Verified state (2026-08-09)

`movito/agentive-skills` (public, last pushed 2026-06-18; installed
plugin reports 1.1.0): 25 files under `plugins/agentive-workflow/` —
**agents: ci-checker, code-reviewer, feature-developer-v6,
feature-developer-v7 only** (no planner, no f5 variants, two
generations behind); 13 commands; 5 skills. Meanwhile the kit's
canonical `.claude/` carries every contract shipped this arc:
verify-never-create Phase 1, Session-topology handoffs, Phase 9
reconciliation, the oscillation protocol, format-by-change-shape,
review-body triage, the launch conventions.

## Requirements

- **F1 — content refresh per KIT-ADR-0025 discipline.** Current kit
  agents, skills, and commands into the plugin layout — with
  project-agnostic bodies: the KIT-LOCAL region MECHANISM does not
  ship; each agent's project-context/stack-notes placeholder is
  replaced by an instruction to read the repo-owned context at runtime
  (CLAUDE.md, `.kit/context/`) — the ADR-0025 shape, reaffirmed by
  KIT-0093 F1 ("marker seeding retires with the copies"). Any
  kit-repo-specific text (kit footguns, ASK paths) is generalized or
  dropped; judgment calls recorded per file in the PR.
- **F2 — roster decisions, recorded AND machine-readable.** Retire
  feature-developer-v6/v7 (superseded); add feature-developer,
  feature-developer-f5, planner, planner-f5, project-intake(?),
  upgrader(?) — decide the consumer roster deliberately (KIT-0067
  function-enumeration law: name why each agent ships or stays
  kit-side). The roster lives as a small declarative file in the
  marketplace repo (name → source path → ships/kit-side + one-line
  why), not only as a PR table — it becomes F4's comparison input
  (evaluation finding, accepted in this half). A full templating
  system for body generalization is DECLINED as YAGNI at 8 files —
  the generalization is editorial judgment done once per release, and
  the drift guard makes staleness loud without generation machinery
  (same rationale family as KIT-0088's declined agent-DSL finding).
- **F3 — versioning.** plugin.json → 2.0.0 (breaking: agent renames),
  marketplace.json updated, a CHANGELOG in the marketplace repo noting
  the v6/v7 retirement and the rename path (the upgrader agent's
  docs/PLUGIN-UPGRADE-GUIDE flow is the consumer migration story).
- **F4 — drift guard: AUTOMATED, in CI — the checklist option is
  withdrawn** (evaluation finding, accepted: a checklist is a ritual,
  and this repo's own rule is that rituals lose to guards —
  KIT-0086/KIT-0088 precedent; the planner should not have offered
  it). A CI check compares kit `.claude/` content (via the F2 roster
  file's source paths — agent `version:` frontmatter and/or content
  hash) against the last published plugin release and FAILS when the
  kit is newer. Without this, the June-to-August drift recurs
  silently.
- **F5 — verify end-to-end.** After publishing: `claude plugin
  marketplace update agentive-skills` + `claude plugin update
  agentive-workflow`, then a fresh `--new` project shows the CURRENT
  contracts in its plugin agents (grep the verify-never-create
  sentinel — the same string `tests/test_agent_contracts.py` pins).

## Acceptance Criteria

- [ ] Plugin 2.0.0 live in the marketplace; installed plugin upgrades
      cleanly with the two consumer commands
- [ ] A fresh project's plugin agents carry the current Phase 1
      contract sentinel (verified by grep, not assumed)
- [ ] Roster decision table in the PR; no kit-specific text in shipped
      bodies
- [ ] AUTOMATED drift guard runs in CI and was falsified in a
      controlled scenario (kit content newer than release → check
      FAILS; in-sync → passes); no checklist-only enforcement
- [ ] KIT-0075's F4 question gets its evidence: note in the completion
      whether native plugin-agent invocation satisfies the operator's
      launch habit in the test project

## Evaluation record

arch-review-fast, 2 rounds (2026-08-09), final verdict
REVISION_SUGGESTED with all findings dispositioned — a legitimate
gate-pass per the Oscillation protocol (code-review-evaluator SKILL):

- Round 1 drift-guard-must-be-automated: ACCEPTED (F4 rewritten;
  checklist option withdrawn).
- Round 1 + round 2 automate-the-generalization: DECLINED as YAGNI at
  8 files, rationale recorded in F2; round 2 re-raised the declined
  finding without new evidence — cited, not re-litigated.
- Round 2 roster-schema formality: ACCEPTED minimally — the roster
  file documents its fields in its own header comment, and the F4 CI
  check is the enforcing consumer; no schema framework.

## Out of Scope

- Agent CONTENT changes beyond generalization (behavior stays as the
  kit repo defines it)
- The kit repo's own `.claude/` (remains canonical; kit is not a
  plugin consumer)
- Phase 3 consumer migration (separate; this only makes the channel
  current)
