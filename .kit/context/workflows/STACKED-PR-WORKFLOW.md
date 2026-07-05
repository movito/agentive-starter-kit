# Stacked PR Workflow

**Purpose**: Stack a second PR on an unmerged first PR, then reconcile cleanly
after the base PR merges — including the squash-merge case, which is not a
plain rebase
**Agents**: feature-developer (execution), planner (PR decomposition)
**Last Updated**: 2026-07-05
**Origin**: Derived live during KIT-0036 (PRs #63/#64); see
`.kit/context/retros/KIT-0036-retro.md`

---

## When to stack

Default is sequential PRs: PR 1 merges, then PR 2 branches from updated `main`
(see `PR-SIZE-WORKFLOW.md`). Stack only when **PR 2 depends on PR 1 code that
isn't merged yet** and waiting would serialize work that can proceed now
(KIT-0036: PR 2's wrapper needed PR 1's engine).

- Base PR 2's branch on **PR 1's branch**, not `main`:

  ```bash
  git checkout -b feature/TASK-pr2 feature/TASK-pr1
  gh pr create --base feature/TASK-pr1 ...
  ```

- **Know before you stack**: CodeRabbit skips PRs whose base isn't the default
  branch ("reviews are disabled for this base branch"). The stacked PR gets
  *no* CodeRabbit review until it is retargeted to `main` — and the review
  that then lands may surface a batch of fresh findings late (4 on KIT-0036
  PR #64). Budget a fix round after retargeting.

---

## Reconciling after PR 1 merges

How you reconcile depends on **how PR 1 landed**. Check before touching PR 2:

```bash
git fetch origin
gh pr view <PR1-num> --json mergedAt,mergeCommit
git log --oneline origin/main -5
```

### Case A: PR 1 was squash-merged (this repo's default)

`main` now contains one new squash commit; PR 1's *original* commits are
unreachable from `main` but still sit at the bottom of PR 2's branch. A naive
`git merge origin/main` replays both sides of the same changes from a common
pre-PR-1 base — conflicts (KIT-0036: both sides changed
`core_version`/`VERSION`) and a noisy diff.

The clean move is `rebase --onto`, which drops PR 1's now-squashed-away
originals and replays only PR 2's own commits:

```bash
git rebase --onto origin/main <PR1-branch-tip> <PR2-branch>
#   → drops PR1's now-squashed-away originals, replays only PR2's commits;
#     git auto-drops commits already upstream ("patch already upstream")
git push --force-with-lease origin <PR2-branch>
gh pr edit <PR2-num> --base main
```

`<PR1-branch-tip>` is the last commit of PR 1's branch as it exists at the
bottom of PR 2's history (`git log --oneline <PR2-branch>` and find the
boundary, or use `origin/<PR1-branch>` if it still exists). Anything PR 2
cherry-picked that landed verbatim in the squash is auto-dropped by git
("patch already upstream").

### Case B: PR 1 landed as a merge commit (or fast-forward)

PR 1's original commits are reachable from `main`, so no `--onto` surgery is
needed — a plain rebase (or merge) sees them as already upstream:

```bash
git rebase origin/main <PR2-branch>
git push --force-with-lease origin <PR2-branch>
gh pr edit <PR2-num> --base main
```

---

## Gotcha: retargeting the base does NOT trigger CI

`gh pr edit --base main` fires the `pull_request: edited` event. CI workflows
trigger on `synchronize` (new push), so the retargeted PR sits with **stale or
missing checks** — do not read that as green.

Two clean nudges (in preference order):

1. **Bundle the next real change into a push** — a fix from the
   post-retarget bot round usually exists anyway (KIT-0036 did exactly this).
   The push fires `synchronize` and CI runs naturally.
2. **Close and reopen the PR** — fires `reopened`, which standard
   `pull_request` triggers include.

Avoid `git commit --allow-empty` — it pollutes history for the same effect
nudge 1 gets with a real change.

---

## Gotcha: force-push may be permission-blocked

In agent sessions, `git push --force-with-lease` can be denied by the
permission layer (hit in the 2026-07-04 kit session). Don't fight it —
**branch replacement** is the supported fallback: create a fresh branch from
the rebased state, push it normally, open a new PR against `main`, and close
the old PR with a pointer to the new one.

---

## Quick Reference

| Situation | Action |
|-----------|--------|
| PR 2 needs unmerged PR 1 code | Branch PR 2 from PR 1's branch; expect no CodeRabbit until retarget |
| PR 1 squash-merged | `git rebase --onto origin/main <PR1-tip> <PR2-branch>` |
| PR 1 merge-committed | Plain `git rebase origin/main <PR2-branch>` |
| After either rebase | `git push --force-with-lease` + `gh pr edit <PR2-num> --base main` |
| Retargeted PR shows no fresh CI | Push the next real change, or close/reopen — `edited` ≠ `synchronize` |
| Force-push denied | Replace the branch: fresh branch + new PR, close the old one with a pointer |
