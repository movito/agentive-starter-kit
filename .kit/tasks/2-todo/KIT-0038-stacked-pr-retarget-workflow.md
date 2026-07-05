# KIT-0038: Document the stacked-PR retarget-after-squash-merge workflow

**Status**: Todo
**Priority**: medium
**Assigned To**: unassigned
**Estimated Effort**: 1-2 hours
**Created**: 2026-07-04
**Target Completion**: TBD
**Linear ID**: (automatically backfilled after first sync)

## Related Tasks

**Parent Task**: KIT-0036 (Pull-based consumer sync) — surfaced in its retro
**Related**: `.kit/context/workflows/PR-SIZE-WORKFLOW.md` (sibling PR workflow)

## Overview

KIT-0036 shipped as two stacked PRs (#64 based on #63's branch, because PR 2
needed PR 1's engine before it merged). When #63 was **squash-merged**, PR 2's
branch still carried PR 1's original commits, and the naive "merge main in"
would have produced conflicts (both sides changed `core_version`/`VERSION` from
a common pre-PR1 base) and a noisy diff.

The clean resolution was non-obvious and was derived live:

```bash
git rebase --onto origin/main <PR1-branch-tip> <PR2-branch>
#   → drops PR1's now-squashed-away originals, replays only PR2's commits;
#     git auto-drops commits already upstream ("patch already upstream")
git push --force-with-lease origin <PR2-branch>
gh pr edit <PR2-num> --base main
git commit --allow-empty? NO — instead push the next real change, because a
#   base retarget fires `pull_request: edited`, which does NOT trigger a
#   `pull_request`-on-synchronize CI workflow. Bundle the next fix into a push,
#   or close+reopen the PR, to run CI.
```

## Goal

Add a short section to `.kit/context/workflows/PR-SIZE-WORKFLOW.md` (or a new
`STACKED-PR-WORKFLOW.md` next to it) covering:

1. When to stack (PR 2 depends on PR 1 code that isn't merged yet) — base PR 2
   on PR 1's branch, not `main`.
2. Reconciling after the base merges, **distinguishing squash-merge from merge
   commit** (rebase `--onto` for squash; plain rebase/retarget for a merge
   commit).
3. The retarget + force-push-with-lease + `gh pr edit --base main` steps.
4. The **base-retarget-doesn't-trigger-CI** gotcha (`edited` ≠ `synchronize`)
   and the two clean nudges (bundle a fix push; or close/reopen).

## Acceptance Criteria

- [ ] Workflow documented and linked from the workflow index
- [ ] Squash-merge vs merge-commit reconciliation both covered
- [ ] The CI-nudge gotcha called out explicitly

## References

- Retro: `.kit/context/retros/KIT-0036-retro.md` (What Should Change #3; What Worked #3-4)
