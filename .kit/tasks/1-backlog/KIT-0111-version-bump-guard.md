# KIT-0111: Version-bump guard — changed component ⇒ same-commit `version:` bump

**Status**: Backlog
**Priority**: low (anytime filler — independent of every train)
**Type**: Infrastructure / CI guard
**Estimated Effort**: ~1 h
**Created**: 2026-08-14 (split from KIT-0110, operator-approved)
**Source**: KIT-0109 release follow-up F1
(`.kit/context/KIT-0109-KIT-FOLLOWUPS.md`)
**Evaluation**: skipped (planner) — remedy ruled at filing

## Requirement

**Planner ruling (2026-08-14): enforce the bump; do NOT retire
`kit_version` for the hash.** All 20 components shipped content
changes in the 2.0.4 release with zero `version:` frontmatter bumps —
one release after the discipline was established (KIT-0100,
`89aea3a`). A practice that lapses silently within one release needs a
guard, not retirement; and retiring the version column would orphan
the upgrader/README reconcile surface (KIT-ADR-0025). Automation
replaces sweeps (KIT-ADR-0034).

Implement a check — CI or pre-commit, implementer's call with a
one-line rationale — that any changed rostered `.claude/` component
carries a `version:` frontmatter bump in the same commit/PR.

- The rostered set is the scope (derive it from the roster/drift
  tooling, don't hand-list — grep-first rule).
- `last-updated:` staleness may ride along as a warning if cheap;
  not required.

## Acceptance Criteria

- [ ] Guard live; falsified once (component content change without a
      `version:` bump → fail, with a message naming the file and the
      rule)
- [ ] A legitimate bump-with-change passes
- [ ] Guard's scope derivation is dynamic (no hardcoded component
      list)

## Notes

- Independent of KIT-0110/0112 and of any release train — pure kit CI.
- Precedent commit for the discipline: `89aea3a` (KIT-0100).
