# KIT-0099: Release plugin 2.0.1 — sync the KIT-0097+KIT-0098 canon, drift guard to green

**Status**: Done
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

- [x] 2.0.1 installed locally and verified (`claude plugin list`) —
      `claude plugin update agentive-workflow@agentive-skills` reported
      "updated from 2.0.0 to 2.0.1"; `claude plugin list` shows
      `Version: 2.0.1`, `Status: ✔ enabled`
- [x] Drift guard green on kit main — CI run
      https://github.com/movito/agentive-starter-kit/actions/runs/31464384207
      (conclusion `success`; job log: "in sync: 27 shipped components
      match the published roster.")
- [x] PII decision recorded (either way) in the release PR — operator
      decided **KEEP** (public visibility known and accepted);
      recorded on agentive-skills#5
- [x] agentive-skills#4 closure comment posted —
      https://github.com/movito/agentive-skills/pull/4#issuecomment-5249792416

## Outcome

Release PR: movito/agentive-skills#5, merged `05eec45` (squash).
17 components resynced; roster membership byte-identical to 2.0.0;
all four version fields at 2.0.1.

Bot rounds: 12 threads across Cursor Bugbot + CodeRabbit (2 rounds), all
resolved with a reasoned reply. Two fixed on the branch — the duplicate
`Cross-Repo Mode` heading my three-way merge introduced (`5d9f01c`), and
explicit empty CHANGELOG categories, which matter because the `upgrader`
agent fetches that file to compute the reconcile diff (`1a188ec`).

Six kit-canonical defects filed rather than patched plugin-side (a
plugin-only edit re-opens drift and turns the guard red — KIT-ADR-0028):
`.kit/context/KIT-0099-KIT-FOLLOWUPS.md`. CodeRabbit independently
reached the same routing conclusion, twice writing "Apply the fix in
agentive-starter-kit first, then resync this plugin copy."

Method note worth keeping: the delta was derived from roster.yaml's
recorded 2.0.0 hashes, not `git diff`. The guard found 17 stale
components where git showed 15 — `planner`/`planner-f5` changed after
the 2.0.0 hashes were cut. Git-only derivation would have shipped two
stale agents and left the guard red.
