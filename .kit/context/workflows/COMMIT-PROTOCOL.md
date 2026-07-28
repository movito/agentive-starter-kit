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
7. **Run CI check**: `./scripts/core/ci-check.sh` (MANDATORY before push)
8. **Push to remote**: `git push` (only after ci-check passes)
9. **Verify CI/CD**: Monitor GitHub Actions until pass/fail (MANDATORY - see below)

---

## Commit Example

**Quoting rule (KIT-0048)**: commit messages containing shell
metacharacters — backticks, `$(…)`, `${…}` — must go through a
single-quoted heredoc (`<<'EOF'`, as below) or single quotes. In a
double-quoted `-m "..."`, `$(…)` executes locally before git ever sees
the message.

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
- ✅ isort: Import sorting
- ✅ flake8: Critical linting errors
- ✅ pattern-lint: Project-specific DK rules (DK001, DK003)

### Manual (you should do):
- ✅ Run pytest: Ensure tests pass
- ✅ **Pre-run Black on new/edited Python files before staging**
  (`black <files>`) — letting the hook reformat mid-commit aborts the
  commit and forces a re-stage cycle; running it first makes the hook
  a no-op (KIT-0053 retro)
- ✅ Check git status: Verify all intended files staged
- ✅ Review diff: Ensure no unintended changes
- ✅ **Verify HEAD moved after committing** (`git log --oneline -1`) whenever
  the staged set includes appended or generated markdown (review records,
  logs, retros). Pre-commit auto-fixers (trailing-whitespace,
  end-of-file-fixer) reformat such files and **abort the commit** — the
  long hook output can read as success while nothing was committed. If
  aborted: re-stage the hook's fixes and commit fresh (never `--amend`).
  (KIT-0035 retro #4 — happened twice in one session.)

---

## Before Push (MANDATORY)

**Always run CI check before pushing**:

```bash
./scripts/core/ci-check.sh
```

### What It Does

Runs the **SAME checks** as GitHub Actions:
- Full test suite (including slow tests)
- Coverage threshold check (`fail_under` gate in pyproject.toml, currently 80%)
- Pre-commit hooks (formatting, linting)
- Uncommitted changes verification

### Benefits

- **100% confidence CI will pass**
- **Catches failures locally** (no email alerts)
- **Faster feedback** than waiting for CI (15-30s vs minutes)

---

## After Push (MANDATORY)

**⚠️ CRITICAL: Do NOT end terminal session or mark task complete until CI passes**

After pushing to GitHub, you **MUST** verify that GitHub Actions CI/CD passes:

### Use verify-ci.sh Script (Recommended)

```bash
./scripts/core/verify-ci.sh [branch-name] [--wait] [--timeout seconds]

# Examples:
./scripts/core/verify-ci.sh                              # Current branch, report status
./scripts/core/verify-ci.sh --wait                        # Current branch, wait for completion
./scripts/core/verify-ci.sh feature/xyz --wait            # Specific branch, wait (default 300s timeout)
./scripts/core/verify-ci.sh feature/xyz --wait --timeout 600  # Custom timeout
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

1. **Report the failure** with a clear summary — failed workflow,
   failing test, error, and a brief analysis — then offer to fix it
2. **If the user says yes**: read the logs
   (`gh run view <run-id> --log-failed`), analyze the root cause,
   implement the fix, run `./scripts/core/ci-check.sh`, then commit
   and push the specific files and re-run CI verification (repeat
   until green)
3. **If the user says no**: document the failure in task notes, pause
   task completion, and await instructions

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
⏳ Waiting for CI verification... (verify-ci.sh --wait)

[Wait for verify-ci.sh to report back]

✅ CI/CD passed on GitHub
✅ Task complete!
```

**DO NOT** skip steps 4-6. CI verification is NOT optional.

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
- Don't mix planner artifacts (task specs, handoffs) with implementation code in the same PR (see `PR-SIZE-WORKFLOW.md`)
- Don't push planner artifacts to feature branches — every push restarts bot reviews. Planner commits go to main only (see planner agent Branch Isolation Policy)

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

- **Quick Reference**: `CLAUDE.md`
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
- After `./scripts/core/project linearsync` runs in CI

### How to Verify

```bash
./scripts/core/project sync-status
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

Run: ./scripts/core/project linearsync
```

### Handling Mismatches

1. **If local > Linear**: Run `./scripts/core/project linearsync` to sync missing tasks
2. **If Linear > local**: Normal if issues were created directly in Linear
3. **Persistent mismatch**: Check `.env` for `LINEAR_API_KEY` and `LINEAR_TEAM_ID`

### Integration with CI

The GitHub Actions workflow runs `./scripts/core/project linearsync` on push. After CI passes:

1. Wait ~30 seconds for Linear to update
2. Run `./scripts/core/project sync-status` to verify
3. If mismatch, investigate or re-run sync

---

**Related Workflows**:
- [TESTING-WORKFLOW.md](./TESTING-WORKFLOW.md) - Run tests before committing
- [TASK-COMPLETION-PROTOCOL.md](./TASK-COMPLETION-PROTOCOL.md) - Completing tasks with commits
