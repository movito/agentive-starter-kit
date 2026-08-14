# KIT-0112: Fail-closed thread counting — `reviewThreads` must not under-count silently

**Status**: Backlog
**Priority**: medium — certifies falsely when it fails; not currently
biting (PRs top out ~a dozen threads), which is exactly how it will
stay invisible until it certifies a false "clean"
**Type**: Canon fix (`.claude/` content)
**Estimated Effort**: ~1 h
**Created**: 2026-08-14 (split from KIT-0110, operator-approved)
**Source**: KIT-0109 release follow-up F2 — CodeRabbit Major on
agentive-skills#9 (thread `PRRT_kwDOSj0O5s6ZO02L`), planner concurred
**Rides**: the KIT-0105 release train (canon change; drift guard
red-by-design between merge and that release)
**Evaluation**: skipped (planner) — remedy ruled at filing

## Requirement

**Planner ruling (2026-08-14): fail closed, not full pagination.**
`.claude/commands/retro.md:97` queries `reviewThreads(first: 100)` and
counts with `[…nodes[]] | length` — past 100 threads the remainder is
silently dropped, and the count asserts triage completeness. The irony
is the point: the rule that made `reviewThreads` the mandatory truth
source BECAUSE REST under-counts (KIT-0102; bot-triage step 0) must
not itself under-count one order of magnitude up.

- Keep `first: 100`; request `pageInfo { hasNextPage }`; REFUSE to
  certify completeness when true, with a message telling the reader to
  paginate by hand.
- **Class, not site** (grep-first rule): `rg 'first: *[0-9]+' .claude/`
  — every paginated GitHub collection feeding a completeness assertion
  gets the same treatment. The grep hit list is the work list; quote
  it before/after in the PR.

## Acceptance Criteria

- [ ] Every completeness-asserting `first: N` site in `.claude/`
      requests `hasNextPage` and fails closed (class grep quoted,
      before/after)
- [ ] The refusal message is actionable (says what to do, not just
      that it stopped)
- [ ] Rides a release: drift guard green after the KIT-0105 train

## Notes

- Do not patch the plugin-side copies; canon only (KIT-0097). The
  packaged-twin mirror rule applies if any edited file has one
  (`test_door_data_sync.py`).
- Natural passenger on the KIT-0105 PR itself or a sibling canon PR on
  that train — implementer/planner sequencing call at assignment.
