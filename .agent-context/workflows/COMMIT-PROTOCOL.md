# Git Commit Protocol

**Purpose**: Create high-quality git commits following project conventions
**Agent**: All agents that write code
**Last Updated**: 2025-11-01

---

## When to Use

- ✅ After implementing a feature or fix
- ✅ After tests pass successfully
- ✅ Before pushing to remote repository

---

## Commit Message Format

```
<type>: <description>

[optional body]

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

### Types:

- `feat`: New feature
- `fix`: Bug fix
- `refactor`: Code restructuring (no behavior change)
- `test`: Test additions or fixes
- `docs`: Documentation changes
- `chore`: Build, dependencies, tooling
- `perf`: Performance improvements

### Description Rules:

- Use imperative mood ("Add feature" not "Added feature")
- Start with lowercase (unless proper noun)
- No period at end
- Max 72 characters

---

## Workflow Steps

1. **Review changes**: `git status`, `git diff`
2. **Stage files**: `git add <files>`
3. **Run pre-commit hooks**: Automatic when you commit
4. **Write commit message** following format above
5. **Create commit**: Use HEREDOC format (see example below)
6. **Verify commit**: `git log -1 --format='%an %ae %s'`
7. **Run CI check**: `./scripts/ci-check.sh` (MANDATORY before push)
8. **Push to remote**: `git push` (only after ci-check passes)
9. **Verify CI/CD**: Monitor GitHub Actions until pass/fail (MANDATORY - see below)

---

## Commit Example

```bash
git commit -m "$(cat <<'EOF'
feat: Add semantic parser integration for natural language thematic lists

Implemented intent detection, fuzzy matching, and timecode parsing to allow
users to create thematic lists using natural language queries like
"interesting parts" or "between 5:30 and 10:15".

- Added SemanticParser class with confidence scoring
- Integrated with ClaudeOutputParser for query processing
- Added 20 tests covering intent detection and edge cases
- All tests passing (341/350 overall, 97.4% pass rate)

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

---

## Pre-commit Checks

### Automatic (via pre-commit hooks):
- ✅ trailing-whitespace: Remove trailing spaces
- ✅ end-of-file-fixer: Ensure newline at EOF
- ✅ check-yaml: Validate YAML syntax
- ✅ check-added-large-files: Prevent large file commits
- ✅ black: Python code formatting
- ✅ ruff: Python linting

### Manual (you should do):
- ✅ Run pytest: Ensure tests pass
- ✅ Check git status: Verify all intended files staged
- ✅ Review diff: Ensure no unintended changes

---

## Before Push (MANDATORY)

**Always run CI check before pushing**:

```bash
./scripts/ci-check.sh
```

### What It Does

Runs the **SAME checks** as GitHub Actions:
- Full test suite (including slow tests)
- Coverage threshold check (53%+)
- Pre-commit hooks (formatting, linting)
- Uncommitted changes verification

### Benefits

- **100% confidence CI will pass**
- **Catches failures locally** (no email alerts)
- **Faster feedback** than waiting for CI (15-30s vs minutes)

### Recommended Alias

Add to `~/.bashrc` or `~/.zshrc`:
```bash
alias gpush="./scripts/ci-check.sh && git push origin main"
```

Then use:
```bash
gpush  # Runs CI check + pushes if passes
```

---

## After Push (MANDATORY)

**⚠️ CRITICAL: Do NOT end terminal session or mark task complete until CI passes**

After pushing to GitHub, you **MUST** verify that GitHub Actions CI/CD passes:

### Option 1: Use ci-checker Agent (Recommended for Agents)

Agents should invoke the **ci-checker** sub-agent using the Task tool:

```
Use the Task tool with these parameters:
- subagent_type: "ci-checker"
- description: "Verify CI for branch <branch-name>"
- prompt: "Please verify CI status for branch '<branch-name>' after my recent push. Check the latest workflow runs and report PASS/FAIL/TIMEOUT status."
```

The ci-checker agent will:
- Monitor GitHub Actions workflows via `gh` CLI
- Report ✅ PASS / ❌ FAIL / ⏱️ TIMEOUT status
- Provide failure summaries if needed
- Take ~20s-10min depending on workflow duration

**Cost**: ~$0.001-0.003 per check (Haiku model)

### Option 2: Use verify-ci.sh Script (Manual or Agent)

```bash
./scripts/verify-ci.sh [branch-name] [timeout-seconds]

# Examples:
./scripts/verify-ci.sh                    # Current branch, 10min timeout
./scripts/verify-ci.sh feature/xyz 300    # Specific branch, 5min timeout
```

**What It Does**:
- Monitors GitHub Actions workflow runs
- Polls every 20 seconds
- Reports when workflows complete (pass/fail)
- Exits immediately on failure (no need to wait full timeout)

### Why This Is Critical

Even if `ci-check.sh` passes locally, CI can still fail due to:
- Environment differences (Python versions, dependencies)
- Race conditions not caught locally
- Caching issues
- GitHub Actions-specific configuration
- Network-dependent tests

**Real example**: "We've had weird CI failures for things I never thought would affect CI" - Project Owner

### Failure Handling (Proactive Fix Workflow)

**When CI fails, agents MUST offer to fix it automatically:**

1. ❌ **Report failure to user** with clear summary:
   ```markdown
   ❌ CI/CD failed on GitHub:

   Failed workflow: Tests (Python 3.11, 3.12, 3.13)
   Failure: tests/test_infrastructure_validation.py::test_task_management_structure
   Error: AssertionError: Missing task directory: active

   This appears to be [brief analysis: e.g., "a test expecting old folder structure"]

   Should I analyze the logs and implement a fix? (y/n)
   ```

2. **If user says YES:**
   - 📋 Read detailed logs: `gh run view <run-id> --log-failed`
   - 🔍 Analyze the failure (what broke, why, what needs to change)
   - 💡 Propose fix with explanation
   - 🔧 Implement the fix
   - ✅ Commit and push: `git add . && git commit -m "fix: ..." && git push`
   - 🔄 Re-run CI verification (recursive until pass)

3. **If user says NO:**
   - 📝 Document the failure in task notes
   - ⏸️ Pause task completion
   - 🤝 Await user instructions

**Example Interaction:**

```
Agent: ❌ CI failed with 1 test failure in test_infrastructure_validation.py
       The test expects folder "active" but we reorganized to numbered folders.

       Should I fix this test to check for the new folder structure? (y/n)

User: y

Agent: Analyzing logs... [reads gh run view output]

       Fix needed: Update test to check for "1-backlog", "2-todo", "3-in-progress"
       instead of "active", "completed", "templates"

       [Implements fix, commits, pushes]

       Verifying CI... ✅ All tests passing!
       Task complete.
```

**Soft Block Policy:**

If CI is still running after timeout:
- Check status manually: `gh run watch <run-id>`
- You may proceed if you're confident (soft block)
- Document decision in task completion notes

### Integration with Task Completion

**Before completing ANY task with code changes:**

```markdown
✅ Code implemented
✅ Tests pass locally
✅ ci-check.sh passed
✅ Pushed to GitHub
⏳ Waiting for CI verification... (ci-checker monitoring)

[Wait for ci-checker to report back]

✅ CI/CD passed on GitHub
✅ Task complete!
```

**DO NOT** skip steps 4-6. CI verification is NOT optional.

---

## Updated Git Workflow

### Before (old workflow)
```bash
git add .
git commit -m "message"  # Only formatting/linting
git push origin main     # Hope CI passes 🤞
```

### After (new workflow - MANDATORY)
```bash
git add .
git commit -m "message"      # Formatting + linting + fast tests ✅
./scripts/ci-check.sh        # MANDATORY pre-push verification ✅
git push origin main         # Push to GitHub ✅
./scripts/verify-ci.sh       # MANDATORY post-push CI verification ✅
# OR invoke ci-checker agent and wait for result
```

**Key changes**:
1. Pre-push verification is now **mandatory**, not optional
2. Post-push CI verification is **mandatory** before task completion
3. Agents must wait for CI pass before marking tasks complete

---

## Best Practices

### ✅ DO:
- One logical change per commit
- Descriptive commit message (explain WHY, not just WHAT)
- Run tests before committing
- Use HEREDOC format for multi-line messages
- Include Claude Code attribution and co-author

### ❌ DON'T:
- Don't commit secrets (.env files, credentials)
- Don't commit generated files (unless required)
- Don't use --no-verify (bypasses hooks) without good reason
- Don't make massive commits mixing unrelated changes

---

## Special Cases

### Amending Commits:
- Only amend commits that **haven't been pushed**
- Check authorship first: `git log -1 --format='%an %ae'`
- Use with caution: `git commit --amend`

### Pre-commit Hook Failures:
- If black/ruff auto-formats files, stage the changes and commit again
- If validation fails, fix the issues before committing
- Don't skip hooks unless absolutely necessary

---

## Documentation

- **Quick Reference**: `.agent-context/PROCEDURAL-KNOWLEDGE-INDEX.md`
- **Full Guide**: This document
- **Pre-commit Config**: `.pre-commit-config.yaml`
- **Git Setup**: See `README.md` → Development section

---

---

## Post-Push Linear Sync Verification

After pushing changes that affect task files (status changes, new tasks, completed tasks):

### When to Verify

- After completing tasks (moving to `5-done/`)
- After creating new tasks
- After any task status changes
- After `./scripts/project linearsync` runs in CI

### How to Verify

```bash
./scripts/project sync-status
```

**Expected Output (In Sync)**:
```
Linear Sync Status
==================
Team: Your Team
Local tasks:   26
Linear issues: 26

Status: ✅ In sync

Last sync: 2025-11-29 02:32:31 UTC
```

**Expected Output (Mismatch)**:
```
Linear Sync Status
==================
Team: Your Team
Local tasks:   26
Linear issues: 24

Status: ⚠️  Mismatch detected (2 missing in Linear)

Missing in Linear: ASK-0025, ASK-0026

Run: ./scripts/project linearsync
```

### Handling Mismatches

1. **If local > Linear**: Run `./scripts/project linearsync` to sync missing tasks
2. **If Linear > local**: Normal if issues were created directly in Linear
3. **Persistent mismatch**: Check `.env` for `LINEAR_API_KEY` and `LINEAR_TEAM_ID`

### Integration with CI

The GitHub Actions workflow runs `./scripts/project linearsync` on push. After CI passes:

1. Wait ~30 seconds for Linear to update
2. Run `./scripts/project sync-status` to verify
3. If mismatch, investigate or re-run sync

---

**Related Workflows**:
- [TESTING-WORKFLOW.md](./TESTING-WORKFLOW.md) - Run tests before committing
- [TASK-COMPLETION-PROTOCOL.md](./TASK-COMPLETION-PROTOCOL.md) - Completing tasks with commits
