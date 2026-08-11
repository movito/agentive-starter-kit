---
description: Verify GitHub Actions CI/CD status for a branch
version: 1.5.0
origin: dispatch-kit
origin-version: 0.3.2
last-updated: 2026-08-11
created-by: "@movito with planner2"
---

# Check CI/CD Status

Verify that GitHub Actions workflows have passed for a specific branch.

## Cross-repo mode (automatic)

`verify-ci.sh` auto-detects cross-repo mode from the
`## Target Repository` section of `CLAUDE.md`. When configured:

- `gh` CI queries target the configured repo instead of the
  planning-repo origin.
- The origin/gh default-repo consistency check is skipped (planning
  and target repos legitimately have different origins).
- Branch auto-detection reads from the target-repo working tree, so
  `/check-ci` without a branch argument finds the feature branch in
  `../target-repo`.

Override with `--repo owner/name` if needed.

## Usage

```text
/check-ci [branch-name] [--repo owner/name]
```

If no branch is specified, checks the current branch (in cross-repo
mode, the target-repo's current branch).

## Task

Run the verification script and report the results:

```bash
./scripts/core/verify-ci.sh $ARGUMENTS
```

The script will output a clear verdict:
- **PASS**: All workflows completed successfully
- **FAIL**: One or more workflows failed
- **IN PROGRESS**: Workflows still running (use `--wait` to block)
- **MIXED**: Some workflows passed, some skipped/cancelled

**If workflows are in progress**, you can wait for them:

```bash
./scripts/core/verify-ci.sh $ARGUMENTS --wait
```

Report the script output to the user. The script provides actionable next steps.

## If NO Tests run exists for an open PR's head

The `pull_request` event can silently fail to fire (observed on PR #105,
2026-08-04: bots ran, zero Tests runs on the head, while same-day PRs
triggered normally). The evidence-equivalent remedy is a manual dispatch
against the branch — the run attaches to the same head SHA.

**Resolve the workflow first — do not assume `test.yml`.** The file name
is project-owned, and in cross-repo mode the workflow lives in the
target repo, not the planning-repo origin. List what actually exists:

**Single-repo mode:**

```bash
gh workflow list
```

**Cross-repo mode** — `REPO` is the `- **GitHub**:` value from
`CLAUDE.md`'s `## Target Repository`. Both commands need it; a bare `gh`
here queries and dispatches the PLANNING repo's workflows:

```bash
gh workflow list --repo <target_github>
```

Pick the workflow that runs the tests, then dispatch it by the name or
filename that listing reported — single-repo first, cross-repo second:

```bash
gh workflow run <workflow-file-or-name> --ref <branch>
```

```bash
gh workflow run <workflow-file-or-name> --ref <branch> --repo <target_github>
```

Dispatch only works if the workflow declares `workflow_dispatch:` in its
`on:` triggers. If it does not, `gh workflow run` errors. In that case
re-trigger the `push`/`pull_request` events with an empty commit — **in
the TARGET repo's worktree**, since in split mode this command may be
running from the planning repo and a bare `git commit` there would
create the commit in the wrong repository and retrigger nothing:

**`--allow-empty` alone is not enough.** It *permits* an empty commit; it
does not *make* one. Anything already staged rides along, so a retrigger
run against a dirty index silently ships unrelated work inside a commit
labelled "chore: retrigger CI".

Add `--only`, which commits exactly the named paths — and with none
named, nothing at all. The commit is then structurally incapable of
carrying staged work, so there is no window between checking the index
and committing for a hook or a parallel process to stage something
(verified on git 2.55: with a file staged, `--allow-empty --only`
produces an empty commit and leaves that file still staged):

```bash
# Single-repo mode:
git commit --allow-empty --only -m "chore: retrigger CI" && git push
```

```bash
# Split mode — route every call, using the `- **Path**:` value from CLAUDE.md:
git -C "<target_path>" commit --allow-empty --only -m "chore: retrigger CI" && git -C "<target_path>" push
```

The push is chained with `&&` so a refused commit cannot still push: that
would re-send the previous state and report "retriggered" having done
nothing of the sort.

This is the `self-review` skill's **scoped staging in commit helpers**
rule (item 9) applied to a hand-run command: an automated commit must
carry only what it means to carry — and the strongest form of that is a
commit that *cannot* carry anything else, rather than one that checks
first and hopes nothing changes in between.

Or ask the operator to add the `workflow_dispatch:` trigger.

Then re-run the verification above. If this recurs on a second PR, treat
it as a repo-config incident (report to the planner), not a fluke.

## Emit milestone event (optional, fire-and-forget — requires dispatch-kit)

```bash
dispatch emit ci_verified --agent feature-developer --task TASK_ID --payload '{"branch":"BRANCH_NAME","conclusion":"CONCLUSION"}' 2>/dev/null || true
```

Replace `TASK_ID` with the task ID from the branch name, `BRANCH_NAME` with the current branch, and `CONCLUSION` with `pass` or `fail` based on the script verdict.
