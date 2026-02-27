---
description: Commit all changes, push to remote, and open a pull request
argument-hint: "[optional commit message override]"
version: 1.0.0
origin: dispatch-kit
origin-version: 0.3.2
last-updated: 2026-02-27
created-by: "@movito with planner2"
---

# Commit, Push, and Open PR

## Step 1: Gather context

Run these commands to understand what needs to be committed:

```bash
# Current branch
git branch --show-current
```

```bash
# Git status
git status --short
```

```bash
# Diff summary
git diff --stat HEAD
```

```bash
# Staged diff summary
git diff --cached --stat
```

```bash
# Recent commits (for message style)
git log --oneline -5
```

```bash
# Remote tracking status
git rev-parse --abbrev-ref --symbolic-full-name @{u} 2>&1 || echo "No upstream branch"
```

## Step 2: Stage & Commit

- Review the status and diffs from Step 1
- Stage all relevant changed files (be specific — avoid `git add -A`)
- Do NOT stage files containing secrets (.env, credentials, etc.)
- Extract the task ID from the branch name (e.g., `feature/TASK-0010-foo` -> `TASK-0010`)
- Write a concise commit message: `[type]: [description]` where type is feat/fix/chore/docs/test/refactor
- If `$ARGUMENTS` is provided, use it as the commit message instead
- Include `Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>` trailer
- Use a HEREDOC for the message to preserve formatting

## Step 3: Push

- Push to origin with `-u` flag to set upstream tracking
- If push fails due to no upstream: first run `git branch --show-current` to get the branch name, then run `git push -u origin <branch-name>` as a separate command. **Never use `$()` subshells** — they trigger permission prompts.

## Step 4: Create PR

- Use `gh pr create` with:
  - Title: `[TASK-ID]: Brief description` (under 70 chars)
  - Body using this template:

Use a HEREDOC to pass the body (no `$()` subshells):

```bash
gh pr create --title "[TASK-ID]: Brief description" --body "$(cat <<'EOF'
## Summary
- [Key change 1]
- [Key change 2]
- [Key change 3]

## Test Plan
- [ ] All existing tests pass
- [ ] [Specific verification steps]

Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

> **Note**: The `$(cat <<'EOF'...)` heredoc pattern is the ONE exception to the
> no-`$()` rule — it's required for multi-line `--body` arguments and is
> auto-approved because the command starts with `gh`.

- If a PR already exists for this branch, skip creation and report the existing PR URL

## Step 5: Emit milestone event (optional, fire-and-forget — requires dispatch-kit)

After the PR is created (or if one already exists), emit:

```bash
dispatch emit pr_created --agent feature-developer --task TASK_ID --payload '{"pr_number":PR_NUMBER,"pr_url":"PR_URL","branch":"BRANCH_NAME"}' 2>/dev/null || true
```

Replace `TASK_ID`, `PR_NUMBER`, `PR_URL`, and `BRANCH_NAME` with the actual values from steps 2-4.

## Step 6: Preflight gate (MANDATORY)

Run preflight to see which completion gates are satisfied:

```bash
./scripts/preflight-check.sh --pr PR_NUMBER --task TASK_ID
```

Parse the `GATE:` lines and present the PASS/FAIL table (same format as `/preflight`).

**This step is informational, not blocking** — gates 1-4 (CI, bots, threads) are expected
to fail immediately after PR creation since bots need 2-6 minutes. But gates 5-7 (evaluator
persisted, review starter, task folder) CAN be checked now.

After presenting results, output the **Next Steps** checklist:

```text
## Next Steps (do NOT skip — review handoff requires all 7 gates)

1. Wait for bots: `/check-bots` (CodeRabbit ~1-2 min, BugBot ~4-6 min)
2. Triage bot findings: `/triage-threads`
3. Run code-review evaluator (skill: code-review-evaluator)
4. Create review starter (skill: review-handoff)
5. Re-run preflight: `/preflight --pr PR_NUMBER --task TASK_ID`
6. When all 7 gates pass -> hand off for human review
```

> **Why this exists**: Post-mortem analysis found that agents skip evaluator and
> preflight phases when they're not mechanically enforced. This checklist ensures
> visibility into remaining work immediately after PR creation.

## Step 7: Report

Output the PR URL and a brief summary of what was committed.
