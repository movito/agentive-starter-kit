# KIT-0099: Release plugin 2.0.1 — sync the KIT-0097+KIT-0098 canon, drift guard to green

**Status**: Todo
**Priority**: high (blocked by KIT-0098; until it ships, the drift
guard is red and consumer projects run 2.0.0 content)
**Type**: Release (mechanical)
**Estimated Effort**: 1-2 h
**Created**: 2026-08-10
**Source**: split from KIT-0098 S4 (arch-review-fast cohesion finding,
accepted — a fresh-eyes repair shouldn't carry release mechanics)
**Depends on**: KIT-0098 merged
**Evaluation**: skipped (planner) — mechanical release step; mechanics
are the KIT-0097 handoff's §"The 2.0.1 release step", already written

## Scope

Exactly the KIT-0097 handoff's release recipe, run against the
post-KIT-0098 canon:

1. Refresh the changed `.claude/` files into
   `~/Github/agentive-skills` `plugins/agentive-workflow/` (KIT-0096
   transforms are the precedent; KIT-LOCAL regions don't ship)
2. roster.yaml hashes updated; plugin.json → 2.0.1 (patch)
3. **R2 PII decision surfaced in the release PR** (author email:
   keep vs noreply — operator decides, inherited from KIT-0097)
4. Marketplace PR (CodeRabbit reviews there — verified on #4);
   operator merges
5. Verify: drift guard GREEN on kit main; `claude plugin marketplace
   update agentive-skills` + `claude plugin update
   agentive-workflow@agentive-skills` lands 2.0.1; closure noted on
   agentive-skills#4

## Acceptance Criteria

- [ ] 2.0.1 installed locally and verified (`claude plugin list`)
- [ ] Drift guard green on kit main
- [ ] PII decision recorded (either way) in the release PR
- [ ] agentive-skills#4 closure comment posted
