# KIT-0100: Canon fixes round 2 — the 2.0.1 follow-ups + plugin 2.0.2

**Status**: Backlog
**Priority**: medium-high (six verified advisory defects, two
pair-rule-bound; promote as the next canon cycle — after the
operator's new-project test, or sooner if a defect bites)
**Type**: Content fixes + patch release
**Estimated Effort**: 0.5 day
**Created**: 2026-08-11
**Source**: `.kit/context/KIT-0099-KIT-FOLLOWUPS.md` — the finding
list IS the spec (six items, each verified against kit canon before
filing, with suggested fixes; CodeRabbit independently endorsed the
fix-here-then-release routing twice)
**Evaluation**: skipped (planner) — enumerated fixes with verified
anchors and suggested shapes; the KIT-0092/0099 precedent class

## Scope

- **F1–F6**: the six items in the follow-ups file, verbatim — stale
  Phase-6 refs (pair rule), `gh run watch` timeout wrapper, the
  `--allow-empty` dirty-index guard (cite the self-review scoped-
  staging rule), evaluator fallback tier containment, Step 2 snippet
  pointing at the tier rule (pair rule), wrap-up's unverified
  review-starter path. Re-verify each anchor before fixing (files
  have moved before).
- **Release 2.0.2**: the mechanical resync per the KIT-0099 recipe
  (drift guard red-by-design between kit merge and tag — the
  established rhythm). The follow-ups' "also noted" README item is
  ALREADY handled (agentive-skills#6, 2026-08-11).

## Ground rules (all now standing policy — cited, not restated)

Review-surface budget (small — this is well under); fast-tier-only +
`--format diff` (prose-shaped); circuit breaker; pair-identity test
enforces the pair rule mechanically; every fix's end state
grep-verified (the sweep-completeness class).

## Acceptance Criteria

- [ ] Six fixes landed in canon (or declined with rationale), pair
      test green, anchors re-verified in the PR body
- [ ] 2.0.2 live; drift guard green; `claude plugin list` shows 2.0.2
- [ ] Follow-ups file marked closed with pointers (it stays as the
      record)
