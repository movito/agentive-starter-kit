---
description: Verify GitHub Actions CI/CD status for a branch
version: 1.3.0
origin: dispatch-kit
origin-version: 0.3.2
last-updated: 2026-08-09
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
`on:` triggers. If it does not, `gh workflow run` errors — in that case
push an empty commit to the branch (`git commit --allow-empty`) to
re-trigger the `push`/`pull_request` events instead, or ask the operator
to add the trigger.

Then re-run the verification above. If this recurs on a second PR, treat
it as a repo-config incident (report to the planner), not a fluke.

## Emit milestone event (optional, fire-and-forget — requires dispatch-kit)

```bash
dispatch emit ci_verified --agent feature-developer --task TASK_ID --payload '{"branch":"BRANCH_NAME","conclusion":"CONCLUSION"}' 2>/dev/null || true
```

Replace `TASK_ID` with the task ID from the branch name, `BRANCH_NAME` with the current branch, and `CONCLUSION` with `pass` or `fail` based on the script verdict.
