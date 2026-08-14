# KIT-0110: Release tooling + verification — `plugin_resync.py` and the guard's blind half

**Status**: Backlog
**Priority**: medium-high — **sequence BEFORE the KIT-0105 release**,
so that train is the first release cut with real tooling instead of a
fourth hand-rolled resync
**Type**: Infrastructure / release tooling
**Estimated Effort**: 3-4 h (2 small PRs: kit tool → marketplace check)
**Created**: 2026-08-14 (split 2026-08-14, operator-approved: the
original bundle spanned two repos and three work-shapes — the
KIT-0102 mixed-shape profile; R1 → KIT-0111, R2 → KIT-0112)
**Source**: KIT-0109 release follow-ups + retro escalation
(`.kit/context/KIT-0109-KIT-FOLLOWUPS.md`, `retros/KIT-0109-retro.md`)
**Evaluation**: skipped (planner) — remedies ruled at filing; the two
halves below are one mechanism (the tool populates the column the
check verifies), which is why they stay one task

## R1 — `scripts/local/plugin_resync.py` (kit repo, PR 1)

Third release running hand-rolled `/tmp` tooling — the kit's own
third-occurrence rule. Codify the KIT-0109 method:

- Delta derived from roster hashes, never `git diff` (KIT-0099 rule).
- **Three-way merge, never copy**: base = the kit blob at the
  previously-rostered `kit_sha256`; a straight copy flattens the
  KIT-ADR-0025 generalization the plugin bodies legitimately carry.
- Emits the work-list, performs mechanical merges, surfaces conflicts
  for the human — and writes/updates the `plugin_sha256` column (R2's
  input).
- Falsify once: synthetic divergent body + canon change → conflict
  surfaced, not flattened.

## R2 — Close the guard's blind half (marketplace repo, PR 2)

**Planner ruling (2026-08-14)**: `check_drift()` reads only kit source
vs `roster.yaml:kit_sha256` — no code path opens
`plugins/agentive-workflow/**`; a bump-hashes-forget-bodies release
goes green with stale content published (KIT-0109 retro, verified by
reading the function). Verification is in scope but homed
MARKETPLACE-side (kit-side compare is impossible by design — the
bodies differ from canon per KIT-ADR-0025):

- `roster.yaml` gains `plugin_sha256` (hash of the shipped body);
- a marketplace-side CI check verifies recorded == actual for every
  rostered component — same repo, no network, fires on exactly the
  failure-shaped PR; falsify once (bump-without-copy → red);
- the roster header is rewritten to say what is verified WHERE —
  "intentionally differs" reads as "unverifiable" and is why the gap
  stayed invisible;
- the kit-side guard's charter is UNCHANGED (kit ↔ roster); its
  header comment states the division explicitly.

## Acceptance Criteria

- [ ] `plugin_resync.py` exists with tests; conflict case falsified
- [ ] `plugin_sha256` column populated for all rostered components;
      marketplace check live and falsified once
- [ ] Roster header + kit guard header state the verification division
- [ ] The next release (the KIT-0105 train) uses the tool and passes
      both checks — cited in that release's record

## Notes

- Do not patch plugin-side body content; canon only (KIT-0097).
- **Release-spec budgeting note for the planner** (KIT-0109 retro):
  bot findings across releases run 42 → 12 → 3 — one substantive
  round is the current baseline; stop budgeting for KIT-0096-sized
  content sieges.
- Minor riders, fix only if touching those files: drift script's
  PyYAML error message should mention the kit ships a `.venv` with it;
  the Phase 5 review-input helper assumes `agentive` on PATH.
