# KIT-0103: Post-phase-4 residue — stale sync references + stale-project warning

**Status**: Backlog
**Priority**: low (rides the next plugin release train; nothing
urgent — the affected population is ~zero)
**Type**: Cleanup
**Estimated Effort**: 2-3 h
**Created**: 2026-08-12
**Source**: KIT-0102 PR #127 follow-ups (both operator-visible on the
PR threads / review starter)
**Evaluation**: skipped (planner) — enumerated cleanup, decisions made
below

## Sequencing (planner, 2026-08-13 — post KIT-ADR-0030 split)

- **R1 rides KIT-0105's release train**: 0105 already forces a plugin
  release (drift guard red-by-design until it ships). Land R1's canon
  fixes on the same train; do not cut a release for cleanup alone.
- **R2 waits for KIT-0104**: the door is being ported into the package
  (KIT-ADR-0030). Implementing detect-and-warn in the shell door now is
  work done twice; R2 becomes a small rider on or after 0104.

## R1 — release-train cleanup of stale sync references

Six rostered `.claude/` files still carry references to the retired
sync machinery (the KIT-0102 session enumerated them on the PR —
derive the list from there and re-grep). Fix in canon per the
grep-first sweep rule (the class grep's hit list IS the work list),
ship with the next plugin release; drift guard red-by-design between.

## R2 — stale pre-packaged project: detect-and-warn (DECIDED)

**Planner ruling (2026-08-12): detect-and-warn, NOT force-refresh.**
A pre-KIT-0102 consumer that re-bootstraps sees `❌ Sync engine
unavailable` because the door's never-overwrite invariant preserves
the old `project` script that imports the deleted engine. Force-refresh
would mutate preserved consumer files — breaking the invariant that
exists precisely to protect operator-owned state; the population is
effectively zero (one known instance: the operator's own `_old`
archive). Instead: the door detects the stale import and prints a
clear retirement notice — "this project predates the packaged era; its
copied scripts reference retired machinery — re-create via the door or
install agentive-kit and remove scripts/core" — instead of the raw
error. Portable shell; contract-string pin if the acceptance test
covers the tail.

## R3 — preflight gate hardening (from the KIT-0102 retro, accepted
by planner 2026-08-12)

Two silently-certify-unreviewed-PR failure modes, doc-fixed in
bot-triage the same day; this is their CODE half in `agentive
preflight`'s bot/review gates: (a) thread verification uses the
reviewThreads GraphQL count, never REST `pulls/comments` (REST
under-counted 3-of-10 on #127); (b) a bot approval only satisfies the
gate when its review's commit SHA matches the PR head AND the check
is not in a rate-limited state ("pass — Review rate limited" means
the head may be unreviewed). Falsify both once (stale-SHA approval →
gate FAILs; REST-vs-GraphQL divergence fixture).

## R4 — package hygiene riders (folded from archived KIT-0095, 2026-08-12)

Both verified still live at fold time: (a) remove the inert
`ADVERSARIAL_UNATTENDED=1` decoration from `review_input.py`'s printed
hints (the `echo y |` half does the work; verify against the installed
tool per self-review lesson #10's uv-path note); (b) the
worktree-hookpath doctor WARN (fires when a worktree's environment
gives git hooks no usable pytest; quiet when provisioned — break-once
both directions; cite the KIT-0092 incident).

## R3 addendum (from archived KIT-0074, 2026-08-12)

While hardening the preflight gates: consider Gate 1's at-cap
reporting under STACKED runs, and review-input auto-defaulting
`--base` to the PR's actual base (`gh pr view --json baseRefName`)
when unset — both thin remainders of KIT-0074, neither urgent.

## Acceptance Criteria

- [ ] R1: class grep opens the work, end grep proves it; ships in the
      next plugin release; drift guard green after
- [ ] R2: stale project produces the retirement notice, not the raw
      error (falsified once against the `_old` archive shape)
