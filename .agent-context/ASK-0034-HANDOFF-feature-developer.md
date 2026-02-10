# Handoff: ASK-0034 - PR #12 Review Fixes

**From**: planner
**To**: feature-developer
**Date**: 2026-02-09
**Task File**: `delegation/tasks/2-todo/ASK-0034-pr12-review-fixes.md`

## Context

PR #12 (ASK-0033 Agent creation automation) received 28 review comments from CodeRabbit and Cursor BugBot. CI is green, but the feedback identifies real bugs that need fixing before merge.

**PR**: https://github.com/movito/agentive-starter-kit/pull/12
**Branch**: `feature/ASK-0033-agent-creation-automation`

## Quick Start

```bash
# 1. Switch to the branch
git checkout feature/ASK-0033-agent-creation-automation
git pull origin feature/ASK-0033-agent-creation-automation

# 2. Start the task
./scripts/project start ASK-0034

# 3. Review the PR comments
gh pr view 12 --comments
```

## Priority 1: HIGH Severity Bugs (Fix First)

### Bug 1: Sed Escaping Failure

**File**: `scripts/create-agent.sh` around line 414
**Problem**: Descriptions containing `/`, `&`, or `\` break sed substitution.

**Current code** (broken):
```bash
sed -i '' "s/\[description\]/$DESCRIPTION/g" "$AGENT_FILE"
```

**Fix approach**:
```bash
# Escape sed special characters in the value
escape_sed() {
    printf '%s\n' "$1" | sed 's/[&/\]/\\&/g'
}

ESCAPED_DESC=$(escape_sed "$DESCRIPTION")
sed -i '' "s/\[description\]/$ESCAPED_DESC/g" "$AGENT_FILE"
```

**Test to add**:
```python
def test_description_with_special_chars(self, tmp_path):
    """Descriptions with /, &, \\ should be handled correctly."""
    setup_temp_project(tmp_path)
    result = run_create_agent(
        "--name", "test-agent",
        "--description", "Handles I/O & file\\path operations",
        cwd=tmp_path
    )
    assert result.returncode == 0
    content = (tmp_path / ".claude/agents/test-agent.md").read_text()
    assert "Handles I/O & file\\path operations" in content
```

### Bug 2: Icon Glob Pattern Quoting

**File**: `scripts/create-agent.sh` (look for icon mapping generation)
**Problem**: Pattern matching never works because asterisks are inside quotes.

**Current code** (broken):
```bash
[[ "$name" == "*agent-name*" ]]  # Literal comparison, not glob!
```

**Fix**:
```bash
[[ "$name" == *"agent-name"* ]]  # Asterisks outside quotes for glob
```

**Search for**: The code that generates icon case statements and fix the quoting.

## Priority 2: MAJOR Severity Issues

### Bug 3: `--force` Creates Duplicate Entries

**File**: `scripts/create-agent.sh` around line 554 (`update_launcher` function)
**Problem**: When overwriting, entries are appended without checking if they exist.

**Fix approach**: Before appending, check if the agent name already exists in the array:
```bash
# In update_launcher, before adding to agent_order:
if ! grep -q "\"$AGENT_NAME\"" "$LAUNCHER_FILE"; then
    # Only add if not already present
    awk '...' # existing append logic
fi
```

### Bug 4: Stale Lock Detection

**File**: `scripts/create-agent.sh` around line 337 (file-based lock fallback)
**Problem**: If process crashes, lock file remains forever.

**Fix approach**: Check if PID in lock file is still alive:
```bash
if [[ -f "$LOCK_FILE" ]]; then
    lock_pid=$(cat "$LOCK_FILE" 2>/dev/null)
    if [[ -n "$lock_pid" ]] && ! kill -0 "$lock_pid" 2>/dev/null; then
        log "Removing stale lock from dead PID $lock_pid"
        rm -f "$LOCK_FILE"
    fi
fi
```

### Bug 5: Fix Concurrency Test

**File**: `tests/integration/test_concurrent_agent_creation.py` lines 43 and 127
**Problem**: `run_create_agent` deletes lock file before each call, defeating locking.

**Fix**: Remove the lock file deletion from `run_create_agent`, only do it once in test setup.

### Bug 6: TOCTOU Race in Lock Fallback

**File**: `scripts/create-agent.sh` around line 338
**Problem**: Race between check and create.

**Fix approach**: Use atomic directory creation:
```bash
# Instead of checking then creating file, use mkdir (atomic)
LOCK_DIR="${LOCK_FILE}.d"
if mkdir "$LOCK_DIR" 2>/dev/null; then
    echo $$ > "${LOCK_DIR}/pid"
    # Got lock
else
    # Failed to get lock, wait and retry
fi
```

## Priority 3: Minor Issues

See task file for complete list. Key ones:

1. **`--position` flag**: Either implement it or remove it entirely
2. **JSON escaping in logs**: Use `jq` or escape quotes
3. **Test assertions**: Strengthen weak assertions
4. **Bash syntax in conftest.py**: Remove `local` from top level

## Files You'll Modify

1. `scripts/create-agent.sh` - Main fixes (sed, glob, locking, duplicates)
2. `tests/integration/test_concurrent_agent_creation.py` - Fix test helpers
3. `tests/test_create_agent.py` - Add new tests, fix assertions
4. `tests/conftest.py` - Fix launcher template syntax

## Testing Strategy

```bash
# Run all create-agent tests
pytest tests/test_create_agent.py tests/integration/test_concurrent_agent_creation.py -v

# Test specific scenarios
pytest -k "special_char" -v  # After adding new test
pytest -k "concurrent" -v    # Concurrency tests

# Verify script syntax
bash -n scripts/create-agent.sh

# Run full CI check
./scripts/ci-check.sh
```

## Commit Strategy

Suggest multiple focused commits:

1. `fix(ASK-0034): Escape sed special characters in agent descriptions`
2. `fix(ASK-0034): Fix glob pattern quoting in icon mapping`
3. `fix(ASK-0034): Prevent duplicate launcher entries with --force`
4. `fix(ASK-0034): Add stale lock detection and recovery`
5. `fix(ASK-0034): Fix concurrency test to not delete lock file`
6. `chore(ASK-0034): Address minor review feedback`

## Success Criteria

- [ ] All HIGH severity issues fixed (2)
- [ ] All MAJOR severity issues fixed (4)
- [ ] Tests pass locally
- [ ] CI passes
- [ ] No new HIGH/MAJOR CodeRabbit comments after push

## Questions?

If you hit blockers or need clarification on any fix approach, check the PR comments for detailed context or ask the planner.

---

**Ready for implementation. Good luck!**
