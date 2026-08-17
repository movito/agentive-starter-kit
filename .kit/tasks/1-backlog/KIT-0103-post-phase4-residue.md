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

**R3 widening (KIT-0105 retro, 2026-08-15)**: the fail-closed
pagination contract (KIT-0112's canon fix) has three CODE siblings —
`review_input.py`, `check-bots.sh`, and `preflight.py` all verified
carrying bare `first: 100` counts (CodeRabbit on kit #134; fd
re-verified all three). Apply the same `hasNextPage` → refuse-to-
certify treatment in code; the canon query at retro.md:97 is the
reference implementation.

## R3 addendum (from archived KIT-0074, 2026-08-12)

While hardening the preflight gates: consider Gate 1's at-cap
reporting under STACKED runs, and review-input auto-defaulting
`--base` to the PR's actual base (`gh pr view --json baseRefName`)
when unset — both thin remainders of KIT-0074, neither urgent.

**+ review-input `--repo-root` / `--output` (KIT-0110 retro rider,
2026-08-14)**: the helper resolves the repo from CWD's CLAUDE.md and
writes CWD-relative, so marketplace-side reviews (KIT-0109 AND
KIT-0110 — two hand-assemblies now) can't use it. A flag pair makes
it serve any local checkout. Same surface as the `--base` item above.

## R5 — Thread ownership + holding-entry rules (canon, next train)
*(planner, 2026-08-15, from the KIT-0105 PR 2 holding incident —
operator deferred to "the next task")*

Two canon paragraphs:

- **bot-triage**: "Thread ownership follows the PR, not the finding's
  TOPIC. A finding about someone else's process (e.g. the planner's
  pending verification) is still yours to action — amend the record,
  request the input — never grounds to park the PR. Escalate the
  question, not the merge."
- **both fd agents** (holding/Phase 7): "Enter holding only after
  re-running the reviewThreads query AT THAT MOMENT — a preflight
  PASS ages the instant a bot re-reviews (KIT-0105 PR 2: a
  CHANGES_REQUESTED landed on the final head after preflight, and the
  session held on a stale gate table)."

Context for the implementer: the diagnosis (ownership seam + timing
race + tripwire accumulation) is in the planner session record
2026-08-15; the fix teaches judgment about WHERE caution applies, it
does not remove any STOP rule.

## R6 — Primary-clone ownership seam at task-end (canon, next train)
*(planner, 2026-08-17, from the KIT-0113 triple collision — fd wrap-up
and planner close-out interleaved in the primary clone: fd staged files
under the planner's feet, pre-commit's stash/rollback reverted the
planner's uncommitted edits TWICE, and the fd's own commit failed twice
on the mutating-hook pattern against the planner's concurrent writes.
All content survived because BOTH sides stopped and verified rather
than committing through it — but that was discipline, not structure.)*

Canon paragraphs, both fd agents (wrap-up) + both planners (Phase 7/8):

- **fd wrap-up**: "The wrap-up COMMIT is the ownership handover of the
  primary clone. Announce completion only after `git status` is clean
  and the commit is pushed; anything authored after that (follow-up
  task filings, addenda) is handed to the planner as content, not
  committed yourself. If a commit fails on the mutating-hook pattern
  and `git status` shows files you did not touch: STOP — another
  session owns the tree."
- **planner**: "Do not begin close-out bookkeeping in the primary
  clone until the fd's wrap-up commit is observed on main (`git log`,
  not the relay). After every Edit near a live session, re-verify the
  edit survived on disk immediately before `git add` — pre-commit
  stash/rollback from the other side can revert it silently."

## Acceptance Criteria

- [x] R1: DONE 2026-08-15 — rode the KIT-0105 train (kit PR #134 +
      release 2.1.0, agentive-skills#11 `3848b64`); class grep opened
      the work, planner tree grep at the gate caught + fixed two
      additional dangling-anchor instances (self-review items 8/9)
      under the improved class definition; drift guard green after
      the release
- [ ] R2: stale project produces the retirement notice, not the raw
      error (falsified once against the `_old` archive shape)
- [ ] R5: both paragraphs in canon, versions bumped, rides a release
- [ ] R6: ownership-seam paragraphs in all four agent bodies (fd,
      fd-f5, planner, planner-f5), versions bumped, rides a release
