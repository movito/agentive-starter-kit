# KIT-0110: Release-signal integrity — version-bump guard + fail-closed thread counting

**Status**: Backlog
**Priority**: medium — both findings certify falsely when they fail;
neither is currently biting
**Type**: Infrastructure / hardening
**Estimated Effort**: 2-3 h
**Created**: 2026-08-14
**Source**: KIT-0109 release follow-ups (F1 + F2 in
`.kit/context/KIT-0109-KIT-FOLLOWUPS.md`) — release-generated
findings, the KIT-ADR-0034 legitimate class
**Rides**: the KIT-0105 release train (canon fixes; drift guard
red-by-design between merge and that release)
**Evaluation**: skipped (planner) — both remedies ruled at filing
(below); enumerated hardening

## R1 — CI guard: changed component ⇒ same-commit `version:` bump

**Planner ruling (2026-08-14): enforce the bump; do NOT retire
`kit_version` for the hash.** The discipline existed (KIT-0100,
`89aea3a`) and lapsed silently within one release — all 20 components
shipped content changes in 2.0.4 with zero bumps. That is evidence it
needs a guard, not that the signal is useless; retiring it would also
orphan the upgrader/README version story (KIT-ADR-0025's reconcile
surface). Automation replaces sweeps (KIT-ADR-0034): a CI check (or
pre-commit, implementer's call with rationale) that any changed
rostered `.claude/` component carries a `version:` frontmatter bump in
the same commit. Falsify once: change a component without a bump →
check fails.

## R2 — `reviewThreads` counting fails CLOSED

**Planner ruling (2026-08-14): fail-closed, not full pagination.**
`.claude/commands/retro.md:97` (and any sibling the class grep finds):
keep `first: 100` but request `pageInfo { hasNextPage }` and REFUSE to
certify completeness when true, with a message telling the reader to
paginate by hand. The rule that made `reviewThreads` the mandatory
truth source because REST under-counts (KIT-0102, bot-triage step 0)
must not itself under-count silently one order of magnitude up
(CodeRabbit on agentive-skills#9, Major — concurred).

**Class, not site** (grep-first rule): `rg 'first: *[0-9]+' .claude/`
— every paginated GitHub collection feeding a completeness assertion
gets the same fail-closed treatment. The grep hit list is the work
list; quote it in the PR.

## Acceptance Criteria

- [ ] Version-bump guard live and falsified once (unbumped change →
      fail)
- [ ] Every `first: N` completeness site in `.claude/` requests
      `hasNextPage` and fails closed (class grep quoted, before/after)
- [ ] Rides a release: drift guard green after the train it ships on

## Notes

- The three-way-merge resync rule (KIT-0109 method note) applies if
  this lands near a release cut: base = previously-rostered blob.
- Do not patch plugin-side copies; canon only (KIT-0097 contract).
