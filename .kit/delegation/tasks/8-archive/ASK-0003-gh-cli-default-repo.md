# ASK-0003: Fix GitHub CLI Default Repository Issue

**Status**: Done
**Priority**: High
**Assigned To**: feature-developer
**Estimated Effort**: 1 hour
**Created**: 2025-11-28
**Source**: AL2 ADR-0001 (Problem #8)

## Problem Statement

After cloning from the starter kit and creating a new GitHub repository, the `gh` CLI defaults to the **upstream** (starter kit) repository instead of the new project's origin. This causes:

1. `gh run list` shows starter kit's CI runs, not the new project's
2. `gh pr create` attempts to create PRs on the wrong repo
3. **ci-checker agent fails** because it can't find workflows for the actual project

## Root Cause

When a repo is cloned, `gh` CLI determines the "default" repository based on various factors. After removing the old origin and adding a new one, `gh` may still reference the original upstream.

## Requirements

### Must Have

- [ ] Add `gh repo set-default` to onboarding process (Phase 7: GitHub Setup)
- [ ] Update ci-checker agent to verify correct default repo
- [ ] Document the issue and fix in README

### Should Have

- [ ] Add verification step in onboarding that confirms `gh` is pointed at correct repo
- [ ] Update `/check-ci` slash command to handle this gracefully

## Implementation

### 1. Update Onboarding Agent (`.claude/agents/onboarding.md`)

In Phase 7 (GitHub Repository Setup), after creating the repo, add:

```markdown
**After creating repo, set it as default for gh CLI:**
```bash
# Set the new repo as default for gh commands
gh repo set-default

# Verify it's set correctly
gh repo view --json nameWithOwner -q .nameWithOwner
```

This ensures `gh run list`, `gh pr create`, and ci-checker work correctly.
```

### 2. Update ci-checker Agent

Add a pre-flight check to `.claude/agents/ci-checker.md`:

```markdown
## Pre-flight Check

Before checking CI status, verify `gh` is configured for this repo:

```bash
# Check default repo matches current directory
EXPECTED_REPO=$(git remote get-url origin | sed 's/.*github.com[:/]//' | sed 's/.git$//')
ACTUAL_REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner 2>/dev/null)

if [ "$EXPECTED_REPO" != "$ACTUAL_REPO" ]; then
    echo "Warning: gh CLI default repo mismatch"
    echo "Expected: $EXPECTED_REPO"
    echo "Actual: $ACTUAL_REPO"
    echo "Run: gh repo set-default"
fi
```
```

### 3. Update README.md

Add to Quick Start or Troubleshooting section:

```markdown
### GitHub CLI Configuration

After creating your GitHub repository, set it as the default for `gh` commands:

```bash
gh repo set-default
```

This is required for `gh run list`, `gh pr create`, and the ci-checker agent to work correctly. The onboarding process does this automatically, but if you set up the repo manually, run this command.

**Verify configuration:**
```bash
gh repo view --json nameWithOwner -q .nameWithOwner
# Should show: your-username/your-project-name
```
```

### 4. Update `/check-ci` Slash Command

If `.claude/commands/check-ci.md` exists, add error handling:

```markdown
## Pre-check

First verify gh CLI is configured for this repo:
- Run `gh repo view` and confirm it shows YOUR repo, not the starter kit
- If wrong, run `gh repo set-default` first
```

## Acceptance Criteria

1. After onboarding completes, `gh repo view` shows the correct repo
2. ci-checker agent successfully lists workflows for the new project
3. `gh run list` shows the correct project's CI runs
4. Documentation explains the issue and fix

## Testing

```bash
# Simulate the problem
git clone agentive-starter-kit my-project
cd my-project
git remote remove origin
gh repo create my-project --private --source=. --push

# Before fix: gh defaults to upstream
gh repo view  # Might show movito/agentive-starter-kit (wrong!)

# After fix:
gh repo set-default
gh repo view  # Shows your-username/my-project (correct!)
gh run list   # Shows YOUR CI runs
```

## Related

- ci-checker agent (`.claude/agents/ci-checker.md`)
- Onboarding agent (`.claude/agents/onboarding.md`)
- `/check-ci` slash command
- AL2 ADR-0001 (source of requirements)
