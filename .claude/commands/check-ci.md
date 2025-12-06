---
description: Verify GitHub Actions CI/CD status for a branch
---

# Check CI/CD Status

Verify that GitHub Actions workflows have passed for a specific branch.

## Usage

```
/check-ci [branch-name]
```

If no branch is specified, checks the current branch.

## Task

Run the verification script and report the results:

```bash
./scripts/verify-ci.sh $ARGUMENTS
```

The script will output a clear verdict:
- ✅ **PASS**: All workflows completed successfully
- ❌ **FAIL**: One or more workflows failed
- ⏳ **IN PROGRESS**: Workflows still running (use `--wait` to block)
- ⚠️ **MIXED**: Some workflows passed, some skipped/cancelled

**If workflows are in progress**, you can wait for them:
```bash
./scripts/verify-ci.sh $ARGUMENTS --wait
```

Report the script output to the user. The script provides actionable next steps.
