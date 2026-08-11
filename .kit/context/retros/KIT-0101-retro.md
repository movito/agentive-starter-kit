# KIT-0101 — The cold-start UX contract (PRs #125 + #126, plugin 2.0.3)

**Date**: 2026-08-11
**Agent**: feature-developer-f5
**Mode**: single-repo (worktree `../ask-worktrees/KIT-0101`)
**Scorecard**: 14 threads (5 + 4 + 5 across kit #125, kit #126,
agentive-skills#8), 1 known-pattern regression (mutating-hook commit
abort, KIT-0057 class), 4 bot rounds (1 + 1 + 2), 12 commits
(3 + 5 + 2 kit-main + 3 release — squashed to `84e9286`, `5d55330`,
`c4be5f8`+`8a79b35`, `5e63707`). Released: agentive-workflow **2.0.3**.

## What Worked

1. **Trio-before-PR + fast-tier-only policy priced correctly** — both
   evaluator runs (diff format, ~$0.01 each) produced only findings
   that died against the tree; the bots' 14 findings were the real
   review. The KIT-0069/0073-derived policy the handoff mandated fit
   this prose-dominated task exactly.
2. **Canon-first release loop held under pressure** — all four
   release-round content findings (agentive-skills#8) were fixed as
   kit-main commits (`c4be5f8`, `8a79b35`) then re-synced with fresh
   roster hashes, never patched plugin-side. The KIT-0100 precedent
   made this mechanical.
3. **Stacked PR 2 during PR 1's bot wait** — building R5 on a stacked
   branch while #125's bots ran cost zero wall-clock and kept the two
   review surfaces cleanly under budget (394 + ~330 prose lines).
4. **Live door replays as R4 evidence** — running the door twice
   (PATH without `agentive`/`claude`, and full toolchain) produced
   verbatim tails for the PR body that no static grep could.

## What Was Surprising

1. **GitHub CLOSED the stacked PR instead of retargeting** when
   #125's squash-merge deleted its base branch — recovery needed the
   base branch recreated, reopen, retarget, delete again. The
   "GitHub retargets automatically" assumption in the PR-2 plan was
   wrong for this path.
2. **Force-push and `reset --hard` are permission-denied** in this
   profile — the rebase-after-squash cleanup had to become a
   double-merge (`origin/main` in, then old lineage in), acceptable
   only because squash-merge collapses history anyway.
3. **CodeRabbit reviewed the release repo copies against the kit
   contract** — it cited the kit's own COMMAND-UX-CONTRACT rules
   (learnings feature) when flagging incomplete Reads/Writes lines,
   effectively enforcing R1's truthfulness rule downstream. Two of
   its 14 findings were misreads of the dual-channel distribution
   (plugin vs script-manifest), fixed by clarifying the contract doc.
4. **pre-commit's pytest-fast hook runs the full not-slow suite
   (~3.5 min)** — the first commit attempt died at the Bash tool's
   3-minute default timeout with the commit NOT landed while the tail
   printed hook progress; `git log` verification (the KIT-0057
   reflex) caught it.

## What Should Change

1. **STACKED-PR-WORKFLOW.md now documents the base-deletion closure**
   (entry added with this retro): merge-the-base → stacked PR gets
   CLOSED, not retargeted; recovery recipe recorded (recreate base at
   old tip → reopen → retarget → delete; reconcile without force-push
   via double-merge when the profile denies it).
2. **Commit calls in this repo need an explicit 600 s timeout** — any
   `git commit` triggers the ~215 s hook suite; the tool default
   (120–180 s) kills mid-hook. Worth a Stack Notes line for the next
   session (planner may add it to the agent's kit-local block).
3. **F10 mock deviation needs an operator ruling** — the intake's
   closing command ships `claude --agent planner` (journey
   consistency) where the operator's mock wrote `planner-f5`. Flagged
   in the review record and both PR bodies; if the operator wants the
   mock verbatim, it is a one-line follow-up.

## Permission Prompts Hit

- `rm -rf /tmp/... && env ... bootstrap` chain — denied (~instant
  retry unchained); the `rm -rf` prefix was the trigger.
- `git push --force-with-lease` — denied twice; worked around with
  merge reconciliation (see Surprising #2).
- `git reset --hard` — denied; same workaround.
- None of these are allowlist candidates as-is (destructive class);
  no change requested.

## Process Actions Taken

- [x] STACKED-PR-WORKFLOW.md triage entry for the base-deletion
      closure (this commit)
- [ ] Stack Notes line: commit calls need timeout ≥ 600 s (planner)
- [ ] Operator ruling on `planner` vs `planner-f5` in the intake's
      F10 closing command (planner)

## Incident Closure

1. **Stacked PR closed by base deletion** → **triage-guide entry**:
   `.kit/context/workflows/STACKED-PR-WORKFLOW.md` §"When the base
   merges first" (added with this retro).
2. **Force-push/reset denied by permission profile** → covered by the
   same triage-guide entry (the no-force-push reconciliation recipe).
3. **Mutating-hook commit abort recurrence (KIT-0057 class)** →
   already closed historically (COMMIT-PROTOCOL guidance + the
   verify-after-hook reflex, which worked); no new artifact.
4. **CodeRabbit "Review rate limited" on the final round** →
   not-checkable note already exists for the bot-quota class
   (`scripts/core/doctor.d/80-bot-presence.sh`); proceeded on pass
   status + 0 unresolved threads, stated openly here.
