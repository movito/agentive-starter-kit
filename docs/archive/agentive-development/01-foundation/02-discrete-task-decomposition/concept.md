# Discrete Task Decomposition: Concept

**Layer:** Foundation
**Topic:** 1.2 Discrete Task Decomposition
**Estimated Reading Time:** 3-5 minutes

> **New to agentive development?** This guide teaches a methodology for working with AI assistants as specialized collaborators with defined roles. See the [Introduction to Agentive Development](../../00-introduction.md) for a complete overview. This document assumes basic familiarity with the approach.

---

## Key Terms

This guide uses these terms from **agentive development** (a methodology treating AI assistants as specialized collaborators, not mere code generators):

- **Task** - Discrete unit of work with clear acceptance criteria
- **Acceptance criteria** - Specific conditions that define task completion
- **Agent** - AI collaborator with a specific role and tool access
- **Coordinator** - Meta-agent that manages other agents and assigns tasks
- **Quality gate** - Objective pass/fail criteria before proceeding
- **Evaluation** - Adversarial review by external AI (GPT-4o) to catch design flaws
- **Delegation** - Assigning tasks to specialized agents with appropriate constraints
- **TDD (Test-Driven Development)** - Practice of writing tests before implementation (RED-GREEN-REFACTOR cycle)

See the [full glossary](../../../../.agent-context/agentive-development-glossary.md) for complete terminology reference.

---

## What is Discrete Task Decomposition?

In **agentive development**—a methodology that treats AI assistants as specialized collaborators with defined roles rather than mere code generators—discrete task decomposition is a foundational practice. It means breaking complex work into independent, testable **tasks**: discrete units of work with clear **acceptance criteria** (specific conditions that define completion). Each task has a single, clear responsibility, defined success criteria, and minimal dependencies on other work. This transforms overwhelming projects into manageable pieces that can be implemented, tested, and verified one at a time.

When you decompose discretely, you create tasks that are complete, coherent, and reversible. "Complete" means the task delivers working functionality, not a partial implementation. "Coherent" means the task addresses one concept, not scattered changes across multiple domains. "Reversible" means if the approach fails, you can revert cleanly without untangling changes from other work.

In agentive development, discrete tasks enable parallel work across multiple **agents** (AI collaborators with specific roles and tool access), clear ownership, and objective progress tracking. A **coordinator** (meta-agent managing other agents) can assign independent tasks to different specialized agents, verify each task individually through **quality gates** (objective pass/fail criteria), and compose them into larger features without coordination overhead.

## Why Does This Matter?

### Problems Solved

- **Scope creep from vague boundaries** - Large, fuzzy tasks expand unpredictably as new requirements surface during implementation
- **Unclear success criteria** - When tasks try to accomplish multiple goals, "done" becomes subjective and disputed
- **Difficult debugging across changes** - When a task modifies 20 files for 5 different purposes, isolating failures becomes archaeology
- **Context overload for reviewers** - Tasks spanning multiple domains require reviewers to understand everything simultaneously
- **Blocked dependencies** - Monolithic tasks create bottlenecks where nothing can proceed until everything completes

### Value Provided

Discrete decomposition creates predictable velocity. When tasks are sized consistently (2-6 hours), you can track progress objectively and identify blockers early. A task running 3x over estimate signals a problem immediately, not after weeks of drift.

This approach enables experimentation. Small, reversible tasks let you try an approach, validate it, and either continue or revert cleanly. Compare "Refactor entire architecture" (risky, irreversible) with "Extract timecode conversion to module" (testable, reversible).

Decomposition multiplies agent productivity. Independent tasks enable parallel work without conflicts. The coordinator assigns discrete tasks to specialized agents and integrates finished work without merge conflicts.

**Real-world example:** In the this project, implementing an API server was decomposed into four independent tasks (TASK-0078-A through D): database models, endpoint implementations, request validation, and comprehensive testing. Four different agents worked on these tasks simultaneously, completing in 2 days what would have taken 4 days sequentially—a 44% time savings (source: `delegation/tasks/active/TASK-0078-api-server-foundation.md`). Because tasks were discrete, each agent could validate their work independently, and integration required no conflict resolution.

## How It Fits in Agentive Development

Task decomposition multiplies every other practice. Structured collaboration requires well-defined tasks. **TDD (test-driven development)** works best with small, testable tasks—you can't write a focused test for "refactor entire system," but you can write one for "extract timecode validation to function." When a task is discrete, you know exactly what test to write first (the RED step), what behavior makes it pass (GREEN), and what to clean up afterward (REFACTOR). Git safety depends on atomic commits implementing complete units.

Consider how TDD and discrete tasks reinforce each other: If your task is "Add User model with password hashing," you write tests for password validation, hashing, and storage. Each test is focused because the task is focused. But if your task is "Add user authentication" (too broad), which test do you write first? Database schema? Password hashing? Session management? API endpoints? The vague task makes TDD unclear, which is a signal to decompose further.

Later layers depend on discrete tasks even more. External **evaluation** (adversarial review by GPT-4o) reviews task plans—large or interdependent tasks make evaluation vague. Agent **delegation** (assigning work to specialized agents) assigns one task per agent—monolithic tasks can't be completed independently. Multi-agent coordination parallelizes independent tasks—dependencies eliminate parallelization benefits.

Good decomposition enables agentive development. Poor decomposition bottlenecks it.

## Key Principles

### 1. Single Responsibility Per Task

Each task should change the system in exactly one way for exactly one reason. "Add user authentication" is multiple responsibilities (database schema, API endpoints, frontend forms, session management). "Add User model with password hashing" is a single responsibility. When tasks have multiple responsibilities, failures become ambiguous and testing becomes comprehensive instead of focused.

**Example:** "Improve performance" → "Add Redis caching for timecode lookups" (one specific improvement)

### 2. Testable in Isolation

You should be able to verify task completion without other tasks being finished. This requires clear inputs, outputs, and success criteria that don't depend on future work. If your task is "Add API endpoint for /users," you can test it immediately by calling the endpoint. If your task is "Add frontend for user management," but the API doesn't exist yet, the task isn't discrete—it's blocked.

**Example:** "Build user dashboard" → "Create UserStats API endpoint" + separate task "Create dashboard UI consuming UserStats"

### 3. Completable in One Session

Tasks should fit within a single focused work session (2-6 hours). Longer tasks accumulate context that must be preserved across sessions, increasing cognitive load and handoff friction. Shorter tasks may not be worth the overhead of task creation, testing, and documentation. The sweet spot enables focused implementation, comprehensive testing, and clean completion without requiring context recovery.

**Example:** Too small: "Add docstring to one function" | Good size: "Add docstrings to timecode module" | Too large: "Document entire codebase"

### 4. Clear Dependencies or None

When tasks have dependencies, make them explicit and minimal. "Task B depends on Task A" is clear. "Task D depends on tasks A, B, and C being partially complete" is coordination overhead that guarantees blocked work. Prefer dependency-free tasks that can start immediately. When dependencies are unavoidable, sequence them linearly (A→B→C) rather than creating complex webs (A+B→C, B+D→E).

**Example:** Linear: "Add User model" → "Add authentication endpoints" → "Add login UI" | Web: "Refactor auth + Add endpoints + Update tests + Fix frontend"

### 5. Reversible if Wrong Approach

Design tasks so failures can be reverted cleanly. This requires avoiding changes that can't be undone (database migrations in production, API changes that break clients) and maintaining clean git history (feature branches, atomic commits). When a task approach fails, you should be able to delete the feature branch and start over without collateral damage.

**Examples of reversible task design:**

- **Database changes:** "Migrate database schema in production" (irreversible) → "Add new table, dual-write to old and new, validate consistency" (reversible stages with rollback points)

- **API refactoring:** "Replace entire REST API with GraphQL" (breaks all clients) → "Add GraphQL endpoint, maintain REST, migrate one client at a time, deprecate REST when safe" (reversible, gradual)

- **Architecture experiments:** "Rewrite app in new framework" (months of work, hard to reverse) → "Build one feature in new framework as proof of concept, compare, decide" (reversible experiment)

- **Performance optimization:** "Rewrite core algorithm for speed" (risky, may break correctness) → "Add performance benchmark, implement new algorithm alongside old, A/B test, switch when validated" (reversible with safety net)

## What's Next

Ready to see this in action? Continue to:

1. **[Example: Discrete Task Decomposition](./example.md)** - See how TASK-0091 decomposed 30 tasks into 5 parallel groups
2. **[Practice Exercise](./practice.md)** - Apply these principles to decompose a feature yourself
3. **[Reflection Questions](./reflection.md)** - Deepen your understanding with guided questions
4. **[Pattern Template](./pattern.md)** - Get a reusable checklist for task decomposition

**Quick self-check:** Before moving on, can you explain the difference between "Add user authentication" (too broad) and "Add User model with password hashing" (discrete)? If not, review the "Single Responsibility Per Task" principle above.

---

**See also:**
- [Example: Discrete Task Decomposition](./example.md)
- [Practice Exercise](./practice.md)
- [1.1 Structured AI Collaboration](../01-structured-ai-collaboration/concept.md)
- [1.3 Test-Driven Development Basics](../03-test-driven-development-basics/concept.md)
- [4.1 Task Decomposition for Parallel Work](../../04-orchestration/01-task-decomposition-for-parallel-work/concept.md)
