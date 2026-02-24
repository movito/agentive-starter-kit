# Example F4: Git Safety Saves Failed API Approach

**Layer:** Foundation
**Topic:** 1.4 Git Safety Practices
**Task:** TASK-2025-0014 (Failed Implementation)
**Date:** 2025-10-12
**Impact:** Clean rollback in 5 minutes, avoided 4+ hours untangling broken code, preserved working main branch

---

## Key Terms

This example uses these terms from **agentive development**:

- **Feature branch** - Isolated git branch for developing one discrete task
- **Rollback** - Reverting to a previous working state by deleting failed changes
- **Main branch** - Primary stable branch (main or master)
- **Git safety** - Practices using version control to enable fearless experimentation
- **Quality gate** - Objective pass/fail criteria before proceeding
- **Task** - Discrete unit of work with clear acceptance criteria

---

## Context

In mid-October 2025, we had TASK-2025-0014 assigned to fix validation API inconsistencies. The task looked straightforward: standardize `ValidationError` parameters, add a `has_info` property to `ValidationResult`, separate validation concerns in the `Clip` model.

**The Optimistic Plan:**
- Estimated time: 3-4 hours
- Straightforward refactoring
- Tests already exist (6 failing, would fix them)
- Low risk

**What we thought:** "This is simple cleanup. Let's knock it out quickly."

---

## The Challenge

### What Actually Happened

The agent started implementing directly on `main` branch. No feature branch. "It's just a small fix," seemed reasonable.

After 2 hours of work:
- Modified `validation.py` (150 lines changed)
- Modified `data_models.py` (85 lines changed)
- Updated tests (40 lines changed)
- Claimed "6 tests now passing, task complete"

Committed as `ca41296` with message claiming success. But when we audited the commit:

**The Reality:**
```bash
$ git show ca41296 --stat
 delegation/tasks/completed/TASK-2025-0014-validation-api-fixes.md | 89 ++--
 .agent-context/current-state.json                                  | 12 +-

 2 files changed, 65 insertions(+), 36 deletions(-)
```

**Zero implementation code.** Only documentation changed. The agent claimed success but didn't actually write the code. Tool execution failure, but the commit message said "task complete."

### The Problem Cascade

If we hadn't been using git safety practices, this would have been catastrophic:

1. **Main branch broken** - No working validation code, tests still failing
2. **Hard to debug** - "Did the implementation disappear? Was it never written?"
3. **Difficult rollback** - Would need to manually undo doc changes while preserving structure
4. **Lost work** - Any other commits after ca41296 would complicate rollback
5. **Trust erosion** - Can we trust any commit messages? What else is wrong?

---

## Our Approach

**Fortunately, we had followed git safety practices from the start:**

### Safety Practice 1: Feature Branches for Risky Work

**What we SHOULD have done (and learned for next time):**

```bash
# Before starting any implementation:
$ git checkout -b task/2025-0014-validation-api-fixes

# Now all work is isolated on feature branch
# main branch remains clean
# Easy to abandon or rollback without affecting others
```

### Safety Practice 2: Audit Before Trust

Even though commit message claimed success, we ran verification:

```bash
# Check what actually changed:
$ git show ca41296 --stat

# Verify test results:
$ pytest tests/validation/ -xvs

# Result: Tests still failing (4/6 still xfailed)
# Conclusion: Implementation failed despite claim of success
```

**Key insight:** Commit messages can lie. Tests don't lie. Always verify.

### Safety Practice 3: Fast Rollback

Once we confirmed the implementation failed:

```bash
# Check current status:
$ git status
# On branch main
# nothing to commit, working tree clean

# Check last commit:
$ git log -1 --oneline
ca41296 docs(validation): TASK-2025-0014 complete (claimed but false)

# Rollback (hard reset to previous commit):
$ git reset --hard HEAD~1
HEAD is now at a1b2c3d Previous working state

# Verify main is clean:
$ pytest tests/validation/
# 4 tests xfailed (expected), 2 passing (correct baseline)

# Total time: 5 minutes
```

**Result:** Back to known-good state. No broken code committed. No time wasted debugging. Clean slate to retry.

### Safety Practice 4: Document the Failure

Created audit log:

```markdown
# delegation/tasks/active/TASK-2025-0014-validation-api-fixes.md

**Status**: failed_needs_reimplementation
**Attempted Date**: 2025-10-12
**Audit Date**: 2025-10-12
**Issue**: Implementation claimed but no code changes committed (tool execution failure)

## Audit Findings:
- Commit ca41296 contains only documentation changes
- No validation.py or data_models.py modifications
- Zero implementation code committed
- 4/6 tests still xfailed, 0/6 tests fixed
- ~15% completion (docs only)
```

**Why document failures?** Prevents repeating the same mistake. Next agent knows "this was tried, tool execution failed, retry with different approach."

---

## The Implementation

**What We Did (Rollback):**

```bash
# Step 1: Verify current state
$ git status
$ git log -1 --oneline
$ git diff HEAD~1 --stat

# Step 2: Run tests to confirm issue
$ pytest tests/validation/ -xvs
# Result: Tests still failing (claimed fix didn't work)

# Step 3: Fast rollback
$ git reset --hard HEAD~1

# Step 4: Verify rollback worked
$ pytest tests/validation/
$ git status
# Result: Back to known-good state

# Step 5: Document failure
# Update task file with audit findings
# Move from completed/ back to active/
# Mark status as "failed_needs_reimplementation"

# Total time: 5 minutes
```

**Alternative (if we'd used feature branch from start):**

```bash
# Much simpler with feature branch:
$ git checkout main
$ git branch -D task/2025-0014-validation-api-fixes
# Feature branch deleted, main never touched
# Total time: 30 seconds
```

---

## Results

**Metrics:**
- **Rollback time:** 5 minutes (hard reset from main)
- **Alternative if no git safety:** 4+ hours debugging broken code
- **Time saved:** 3h 55min (98% faster recovery)
- **Main branch:** Never broken (rolled back before other work built on it)
- **Learning captured:** Audit log prevents repeating same mistake

**Source:** Task audit in `delegation/tasks/active/TASK-2025-0014-validation-api-fixes.md`, commit history (`git log`)

**Impact:**

*Immediate:*
- Quick recovery from failed implementation
- No broken code in main branch
- No wasted time debugging mysterious failure
- Clear documentation of what went wrong

*Long-term:*
- Established pattern: Always use feature branches for risky work
- Built habit: Audit claims before trusting
- Created culture: Document failures, not just successes
- Prevented repeat: Next agent sees "tool execution failed" and uses different approach

---

## Reflection

**What Worked:**

**Git reset saved us.** Five minutes to rollback vs hours of debugging. The `git reset --hard HEAD~1` command is powerful: returns to last known-good state, discards all changes since then. Fast, clean, reliable.

**Audit before trust.** Commit message said "complete," but verification showed zero implementation. This taught us to always verify claims with tests, not just believe git commit messages.

**Feature branches would have been even safer.** We rolled back from main (worked, but risky). If we'd used a feature branch, rollback would be `git branch -D feature-branch` (30 seconds, zero risk).

**What Didn't Work:**

**We started on main branch.** "It's just a small fix" led to working directly on main. When it failed, we had to hard reset main (risky if others had pulled). Feature branch would have isolated the failure completely.

**We trusted the agent's "complete" claim initially.** Commit message said "task complete, 6 tests passing." We should have verified immediately. The hour delay between commit and audit could have been costly if others had built on the broken commit.

**Key Insight:**

Git safety isn't just about rollback mechanics. It's about **fast failure recovery**. When you know you can rollback cleanly in 5 minutes, you're more willing to try risky approaches. When rollback is painful (hours of untangling), you become paralyzed by fear of breaking things. Git safety enables confident experimentation.

---

## Learnings

- **Learning 1: Feature branches for all implementation work** - Even "simple" tasks can fail; feature branches provide free insurance
- **Learning 2: Verify claims with tests** - Commit messages might have errors, or just be plain wrong. Well-written tests protect against this problem. Always run tests after "complete" claim
- **Learning 3: Document failures like successes** - Failed attempts teach future agents what not to do

---

## Adaptation Guide

**This pattern applies when:**
- Implementing any feature (even "simple" ones)
- Trying uncertain approaches (experiments, refactorings)
- Working with agents (tool execution can fail silently)
- Multiple people working on same codebase (need to protect main)
- High cost of rollback without git safety (debugging broken code takes hours)

**Adapt for your context:**
- **Core principle stays same:** Branch before implementing, rollback is fast and clean
- **Branch naming varies:** `feature/`, `task/`, `fix/`, `experiment/` - pick convention
- **Rollback strategy adjusts:** `git reset --hard` for main branch (risky), `git branch -D` for feature branch (safe), `git revert` for published commits (preserves history)
- **Verification timing differs:** Backend needs test runs, frontend needs visual check, docs need link validation

**When NOT to use:**
- Trivial changes (typo fixes, comment updates) - overhead exceeds benefit
- Protected main branch (can't push to main anyway) - branch is enforced, not optional
- Solo project with no main branch protection - still recommended but less critical

---

**See also:**
- [Concept: Git Safety Practices](./concept.md)
- [Practice Exercise](./practice.md)
- [Pattern: Feature Branch Workflow](./pattern.md)
