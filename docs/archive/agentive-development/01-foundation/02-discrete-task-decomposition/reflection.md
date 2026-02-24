# Discrete Task Decomposition: Reflection Questions

**Layer:** Foundation
**Topic:** 1.2 Discrete Task Decomposition
**Estimated Time:** 10-15 minutes

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

## Purpose

Reflection helps you develop intuition for task sizing and dependency management. These questions challenge you to think critically about when to split work, when to combine it, and how to balance independence with efficiency.

## Questions to Consider

### 1. How small is too small? How large is too large?

You've learned that tasks should be 2-6 hours, testable in isolation, and single-responsibility. But what happens at the extremes? A 30-minute task might not be worth the overhead of task creation, specification, and testing. A 12-hour task might be too complex to hold in working memory.

Reflect on your practice exercise. Did you split work too granularly (creating coordination overhead) or too coarsely (creating monolithic tasks)? What signals tell you the sizing is right?

### 2. What dependencies are acceptable versus problematic?

Some dependencies are clean: Task B requires Task A to be complete, period. Other dependencies are murky: Task C needs 70% of Task A and parts of Task B. Linear dependencies (A→B→C) are manageable. Dependency webs (A+B→C, B+C→D) create bottlenecks.

When is a dependency acceptable (clear, minimal) versus when does it signal poor decomposition? How do you recognize when you've created a dependency graph that will block parallelization?

### 3. When should you combine tasks instead of splitting them?

Discrete doesn't always mean separate. Sometimes two tasks are so tightly coupled that implementing them separately creates more work than implementing them together. Database schema and the first migration. API endpoint and its primary client. Model and its core validation logic.

How do you recognize when separation creates artificial boundaries versus when it enables independence? What's the difference between legitimate coupling and poor decomposition?

### 4. How do you handle emergent complexity during implementation?

You decomposed work upfront, but halfway through Task 2, you discover it's three times more complex than estimated. Do you stick with the original task, or stop and re-decompose? How do you balance planning discipline with adaptation to reality?

Think about your own projects. When did you discover complexity late? Would better decomposition have caught it earlier, or was it genuinely unforeseeable?

## Reflection Activity

Choose one of these methods to capture your reflections:

**Size guideline worksheet:** Create a personal reference for task sizing. Document 3-5 examples of well-sized tasks from your work. Note what made them right-sized. Use this as a calibration tool for future decomposition.

**Dependency map:** Take a recent multi-task feature. Draw the dependency graph (A→B, B→C). Identify where dependencies blocked progress. Could you have decomposed differently to reduce dependencies? Document your insights.

**Retrospective:** After completing a decomposed feature, write 3 sentences: What decomposition worked well? What would you split differently next time? What did you learn about your own sizing intuition?

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

**Next:** [Reusable Pattern](./pattern.md)
