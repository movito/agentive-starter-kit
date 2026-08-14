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

## R3 — Close the guard's blind half: roster ↔ published bodies
*(added 2026-08-14 from the KIT-0109 retro escalation, planner ruling)*

`check_drift()` hashes only the KIT source against
`roster.yaml:kit_sha256` — no code path opens
`plugins/agentive-workflow/**`. A release that bumps hashes but
forgets to copy bodies goes green with stale content published
(verified by the KIT-0109 session by reading the function).

**Ruling — the verification is in scope, but its home is the
MARKETPLACE repo**: plugin bodies legitimately differ from kit canon
(the KIT-ADR-0025 generalization the three-way merge preserves), so
kit-side comparison is impossible by design. Instead:

- roster.yaml gains a `plugin_sha256` column (hash of the shipped
  body);
- a marketplace-side CI check verifies recorded == actual for every
  rostered component — same repo, no network, fires on exactly the PR
  shape that produces the failure (bump-without-copy);
- the roster header's "intentionally differs" phrasing is rewritten
  to name what is verified where — its current wording reads as
  "unverifiable" and is why the gap stayed invisible;
- the kit-side guard's charter is UNCHANGED (kit ↔ roster) and its
  header comment states the division explicitly.

## R4 — Codify the resync tool: `scripts/local/plugin_resync.py`
*(added 2026-08-14 — third release running hand-rolled /tmp tooling;
the kit's own third-occurrence rule)*

The KIT-0109 method (delta from roster hashes; three-way merge with
base = kit blob at the previously-rostered hash; never plain copy)
becomes a script. It emits the merge work-list and performs the
mechanical merges, flagging conflicts for the human. Falsify once:
a synthetic divergent body + canon change → conflict surfaced, not
flattened.

## Acceptance Criteria

- [ ] Version-bump guard live and falsified once (unbumped change →
      fail)
- [ ] Every `first: N` completeness site in `.claude/` requests
      `hasNextPage` and fails closed (class grep quoted, before/after)
- [ ] `plugin_sha256` column + marketplace-side consistency check live;
      falsified once (bump-without-copy → red); roster header rewritten
- [ ] `plugin_resync.py` exists, used by the release this rides,
      conflict case falsified
- [ ] Rides a release: drift guard green after the train it ships on

## Notes

- The three-way-merge resync rule (KIT-0109 method note) applies if
  this lands near a release cut: base = previously-rostered blob.
- Do not patch plugin-side copies; canon only (KIT-0097 contract).
- **Release-spec budgeting note for the planner** (KIT-0109 retro):
  bot findings across releases run 42 → 12 → 3 — stop budgeting for
  KIT-0096-sized content rounds; one substantive round is the current
  baseline.
- Minor riders, fix only if touching those files: drift script's
  PyYAML error message should mention the kit ships a `.venv` with it;
  the Phase 5 review-input helper assumes `agentive` on PATH.
- Estimate revised with R3/R4: **4-6 h** (was 2-3 h).
