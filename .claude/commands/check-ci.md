---
description: Verify GitHub Actions CI/CD status for a branch
version: 1.0.0
origin: dispatch-kit
origin-version: 0.3.2
last-updated: 2026-02-27
created-by: "@movito with planner2"
---

# Check CI/CD Status

Verify that GitHub Actions workflows have passed for a specific branch.

## Usage

```text
/check-ci [branch-name]
```

If no branch is specified, checks the current branch.

## Task

Run the verification script and report the results:

```bash
./scripts/verify-ci.sh $ARGUMENTS
```

The script will output a clear verdict:
- **PASS**: All workflows completed successfully
- **FAIL**: One or more workflows failed
- **IN PROGRESS**: Workflows still running (use `--wait` to block)
- **MIXED**: Some workflows passed, some skipped/cancelled

**If workflows are in progress**, you can wait for them:

```bash
./scripts/verify-ci.sh $ARGUMENTS --wait
```

Report the script output to the user. The script provides actionable next steps.

## Emit milestone event (optional, fire-and-forget — requires dispatch-kit)

```bash
dispatch emit ci_verified --agent feature-developer --task TASK_ID --payload '{"branch":"BRANCH_NAME","conclusion":"CONCLUSION"}' 2>/dev/null || true
```

Replace `TASK_ID` with the task ID from the branch name, `BRANCH_NAME` with the current branch, and `CONCLUSION` with `pass` or `fail` based on the script verdict.
