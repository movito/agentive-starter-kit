# Git Safety Practices: Reusable Pattern

**Layer:** Foundation
**Topic:** 1.4 Git Safety Practices
**Type:** Template + Checklist

---

## Key Terms

This document uses these terms from **agentive development** (a methodology treating AI assistants as specialized collaborators, not mere code generators):

- **Agent** - AI collaborator with a specific role and tool access
- **Task** - Discrete unit of work with clear acceptance criteria
- **Quality gate** - Objective pass/fail criteria before proceeding
- **TDD (Test-Driven Development)** - Practice of writing tests before implementation
- **Template** - Reusable document structure with placeholders

See the [full glossary](../../../../.agent-context/agentive-development-glossary.md) for complete terminology reference.

---

## When to Use This Pattern

Use these git safety patterns when:
- Starting any new feature or bug fix work
- Experimenting with uncertain approaches
- Working on changes that might need to be rolled back
- Collaborating with others on shared repositories
- Creating changes that need clear history for review

## The Pattern

### Commit Message Format Template

```
[type]([scope]): [Brief summary - imperative mood, max 50 chars]

[Optional body: Detailed explanation of what and why, not how.
Wrap at 72 characters. Explain context, link to issues, note
any non-obvious decisions.]

[Optional footer: Breaking changes, issue references]
```

**Types:**
- `feat`: New feature or capability
- `fix`: Bug fix
- `refactor`: Code change that neither fixes bug nor adds feature
- `test`: Adding or updating tests
- `docs`: Documentation changes
- `chore`: Build, dependencies, tooling (no production code change)

**Examples:**

```
feat(api): Add user registration endpoint

Implements POST /api/register with email validation, password hashing
using bcrypt, and duplicate email detection. Returns 201 on success
with user ID, 400 on validation errors.

Resolves #47
```

```
fix(timecode): Prevent negative frame values in conversion

Added validation to reject negative frame counts before timecode
calculation. Previously would return invalid timecode strings like
"-00:00:01:15" which caused downstream parsing failures.

This fix prevents the bug reported in TASK-2025-0012.
```

```
refactor: Extract timecode utilities to separate module

No behavior changes. Moved 5 utility functions from core.py to new
timecode_utils.py for better organization and testability. All tests
still pass.
```

### Branch Naming Conventions

**Format:** `[type]/[brief-description]` or `[type]/[ticket-id]-[brief-description]`

**Types:**
- `feature/` - New features
- `fix/` - Bug fixes
- `refactor/` - Code refactoring
- `experiment/` - Uncertain approaches (safe to delete)
- `docs/` - Documentation work

**Examples:**
- `feature/user-authentication`
- `fix/timecode-negative-values`
- `refactor/extract-timecode-utils`
- `experiment/redis-caching`
- `feature/TASK-2025-0087-dashboard-optimization`

**Guidelines:**
- Keep names under 50 characters
- Use lowercase and hyphens (not underscores or spaces)
- Be descriptive but concise
- Include ticket ID when applicable
- Prefix `experiment/` for throwaway work you might delete

### Safe Experimentation Workflow Checklist

**Before Starting Work:**
- [ ] Confirm you're on main/master branch: `git branch --show-current`
- [ ] Pull latest changes: `git pull origin main`
- [ ] Create feature branch: `git checkout -b feature/your-work`
- [ ] Verify new branch created: `git status`

**During Work:**
- [ ] Make small, focused changes
- [ ] Commit after each logical step (not per file, per concept)
- [ ] Write descriptive commit messages using template above
- [ ] Run tests before each commit
- [ ] Push to remote regularly to backup work: `git push -u origin feature/your-work`

**If Approach Works:**
- [ ] Verify all tests pass
- [ ] Review your commit history: `git log --oneline`
- [ ] Squash commits if needed: `git rebase -i main` (optional)
- [ ] Merge to main via pull request or: `git checkout main && git merge feature/your-work`
- [ ] Delete feature branch: `git branch -d feature/your-work`

**If Approach Fails:**
- [ ] Switch back to main: `git checkout main`
- [ ] Delete failed branch: `git branch -D experiment/failed-approach`
- [ ] Verify main is unchanged: `git status`
- [ ] Start new branch with different approach

**Rollback Options:**
- **Undo last commit (keep changes):** `git reset --soft HEAD~1`
- **Undo last commit (discard changes):** `git reset --hard HEAD~1`
- **Undo specific file:** `git checkout HEAD -- path/to/file`
- **Revert pushed commit (safe):** `git revert [commit-hash]`

## Usage Example

**Scenario:** Experimenting with Redis caching - might not work.

```bash
# Start safely
git checkout main
git pull origin main
git checkout -b experiment/redis-caching

# Make first attempt
# ... edit files ...
git add src/cache.py tests/test_cache.py
git commit -m "experiment(cache): Add Redis connection setup

Testing connection pooling with 10 workers. Not sure if this
will handle our load yet - needs performance testing."

# Discover this approach is too slow
# ... more experimentation ...
git commit -m "experiment(cache): Try connection pool size of 50

Previous approach had 300ms latency. Trying larger pool."

# Still not good enough - abandon approach
git checkout main  # Switch back to safety
git branch -D experiment/redis-caching  # Delete experiment

# Try different approach
git checkout -b feature/memcached-caching  # Different strategy

# ... this works better ...
git add src/cache.py tests/test_cache.py
git commit -m "feat(cache): Add Memcached caching layer

Achieves <50ms latency with 70% cache hit rate in testing.
Simpler than Redis for our use case - no persistence needed.

Resolves TASK-2025-0087"

# Success - merge it
git checkout main
git merge feature/memcached-caching
git push origin main
git branch -d feature/memcached-caching
```

**Result:** Failed experiment was isolated and deleted cleanly. Successful approach has clear history.

## Customization Tips

**For different team workflows:**
- **Solo developer:** Can use simpler commit messages, less formal branch names
- **Small team:** Follow format strictly for clarity in code review
- **Large team:** Add required elements (ticket ID, reviewer tags, breaking change notes)

**For different project types:**
- **Open source:** Detailed messages help external contributors understand history
- **Internal tools:** Can be terser if team has context
- **Critical systems:** Require detailed rationale in every commit message

**Adjust granularity based on:**
- **Experimentation:** Commit very frequently - create many restore points
- **Well-understood work:** Commit after logical completion - cleaner history
- **Pair programming:** Commit when switching driver - captures collaboration
- **Before risky changes:** Always commit clean state before attempting risky refactors

---

## Key Terms

This document uses these terms from **agentive development** (a methodology treating AI assistants as specialized collaborators, not mere code generators):

- **Agent** - AI collaborator with a specific role and tool access
- **Task** - Discrete unit of work with clear acceptance criteria
- **Quality gate** - Objective pass/fail criteria before proceeding
- **TDD (Test-Driven Development)** - Practice of writing tests before implementation
- **Template** - Reusable document structure with placeholders

See the [full glossary](../../../../.agent-context/agentive-development-glossary.md) for complete terminology reference.

---

**See also:**
- [Concept: Git Safety Practices](./concept.md)
- [Example: Git Safety Practices](./example.md)
- [1.3 Test-Driven Development Basics](../03-test-driven-development-basics/concept.md)
