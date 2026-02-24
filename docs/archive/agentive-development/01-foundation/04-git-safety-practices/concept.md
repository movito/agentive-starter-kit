# Git Safety Practices: Concept

**Layer:** Foundation
**Topic:** 1.4 Git Safety Practices
**Estimated Reading Time:** 3-5 minutes

> **New to agentive development?** This guide teaches a methodology for working with AI assistants as specialized collaborators with defined roles. See the [Introduction to Agentive Development](../../00-introduction.md) for a complete overview. This document assumes basic familiarity with the approach.

---

## Key Terms

This guide uses these terms from **agentive development** (a methodology treating AI assistants as specialized collaborators, not mere code generators):

- **Feature branch** - Isolated git branch for developing one discrete task
- **Quality gate** - Objective pass/fail criteria before proceeding (e.g., "tests pass")
- **Agent** - AI collaborator with a specific role and tool access
- **Coordinator** - Meta-agent that manages other agents and assigns tasks
- **Task** - Discrete unit of work with clear acceptance criteria
- **CI/CD (Continuous Integration/Continuous Deployment)** - Automated testing and deployment pipeline

See the [full glossary](../../../../.agent-context/agentive-development-glossary.md) for complete terminology reference.

---

## What Are Git Safety Practices?

Git safety practices are workflows that use version control to enable fearless experimentation. Instead of making changes directly to your main branch and hoping they work, you create isolated feature branches for each task, commit incrementally as you make progress, and maintain the ability to revert to any previous state without data loss. This transforms git from a backup tool into a time machine that makes mistakes reversible.

When you practice git safety, you never ask "what if this breaks everything?" because you can always roll back. You create branches for experiments, commit working states frequently, and merge only when tests pass. Failed experiments get deleted, successful work gets integrated, and your main branch stays stable.

In agentive development, git safety enables agent autonomy. Agents can experiment with implementations, knowing that failed approaches can be cleanly reverted. Coordinators can assign tasks to multiple agents in parallel, knowing that feature branches prevent conflicts until integration time.

## Why Does This Matter?

### Problems Solved

- **Lost work from accidental overwrites** - Without commits, a mistaken delete or failed merge loses hours of work permanently
- **Broken main branch blocks all work** - When experiments happen directly on main, failures prevent anyone from deploying or building on stable code
- **Unclear history makes debugging impossible** - When changes lack context ("fixed stuff"), identifying when bugs were introduced becomes archaeology
- **Fear of refactoring prevents improvement** - Without safe rollback, improving code structure feels too risky to attempt

### Value Provided

Git safety enables confident experimentation. When you can revert any change in seconds, you become willing to try alternative approaches, refactor aggressively, and optimize without fear. The cost of failure drops from "lost days" to "delete branch and restart."

This workflow provides automatic documentation of decisions. Commit messages explain what changed and why. Branch history shows approaches tried and abandoned. Six months later, `git log` answers "why this way?" without human archeology.

Git safety makes code review effective. When branches contain coherent changes for a single task, reviewers can understand the entire change in context. Compare reviewing a 500-line commit message "misc fixes" versus five 100-line commits with descriptive messages for discrete changes.

## How It Fits in Agentive Development

Git safety is the foundation for parallel agent work. When multiple agents implement independent tasks on separate branches, they don't block each other or create merge conflicts. The coordinator assigns tasks, agents create branches, work proceeds in parallel, and integration happens when tasks complete successfully.

Git safety also enables quality gates. A task isn't complete when code is written—it's complete when tests pass on the feature branch. The merge to main happens only after validation. This prevents broken code from polluting the stable branch and creating cascading failures.

Later layers build on git safety. External evaluation reviews plans before implementation, reducing failed branches. Specialized agents work on independent branches without coordination overhead. CI/CD runs tests on every branch to catch problems before merge. All of this assumes git safety practices provide isolation and reversibility.

## Key Principles

### 1. Branch Before Experimenting

Create a new branch before starting any task, even small ones. `git checkout -b feature/timecode-precision` isolates your changes from main. If the experiment fails, you delete the branch. If it succeeds, you merge it. Main branch stays stable throughout. Never commit experimental code directly to main.

**Example:** `git checkout -b fix/api-timeout` → experiment with timeout values → if successful, merge; if failed, delete branch

### 2. Commit Early, Commit Often

Make small, incremental commits as you reach working states. Don't wait until a feature is "done" to commit—commit when tests pass, when a function works, when a refactoring completes. Small commits make history useful and rollback surgical. Large commits make debugging painful and rollback risky.

**Example:** Commit sequence: "Add User model" → "Add authentication helper" → "Add login endpoint" → "Add authentication tests" (4 reversible steps, not 1 monolithic change)

### 3. Meaningful Commit Messages

Write commit messages that explain what changed and why, not just what files were touched. "Fix bug" is useless six months later. "Fix timecode rounding to use Fraction instead of float, preventing 86-frame drift" explains the change and the motivation. Good messages make `git log` valuable for understanding history.

**Example:** Instead of "Update tests," write "Add precision tests for 2.5-hour timecode calculations (TASK-2025-0012)"

### 4. Easy Rollback When Wrong

Structure commits so reverting is clean. One commit per logical change means reverting one change doesn't undo others. Avoid commits that mix unrelated changes—if you need to revert the bug fix but keep the refactoring, they must be separate commits. Make rollback a routine operation, not an emergency procedure.

**Example:** If a performance optimization causes bugs, `git revert abc123` removes just that commit, leaving other work intact

### 5. Never Force Push to Main

Force pushing (`git push --force`) rewrites history, potentially deleting other people's work and breaking their local repositories. On main or shared branches, force push is catastrophic. On your personal feature branches, it's occasionally useful but still risky. Default to never force pushing. When you must, understand exactly what you're destroying.

**Example:** Rebasing feature branches is fine, but once pushed to shared branches or main, history is permanent

## What's Next

Ready to see git safety in practice? Continue to:

1. **[Example: Git Safety Practices](./example.md)** - See how feature branch workflow saved hours when reverting failed implementation
2. **[Practice Exercise](./practice.md)** - Practice the branch-commit-merge workflow yourself
3. **[Reflection Questions](./reflection.md)** - Understand when and why these practices matter
4. **[Pattern Template](./pattern.md)** - Get a reusable git workflow checklist

**Quick self-check:** Before moving on, can you explain why committing to a feature branch before experimenting is safer than committing directly to main? If not, review principle #1 above.

---

**See also:**
- [Example: Git Safety Practices](./example.md)
- [Practice Exercise](./practice.md)
- [1.2 Discrete Task Decomposition](../02-discrete-task-decomposition/concept.md)
- [1.3 Test-Driven Development Basics](../03-test-driven-development-basics/concept.md)
- [3.4 Single-Agent Task Assignment](../../03-delegation/04-single-agent-task-assignment/concept.md)
