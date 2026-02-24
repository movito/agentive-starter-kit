# Discrete Task Decomposition: Practice Exercise

**Layer:** Foundation
**Topic:** 1.2 Discrete Task Decomposition
**Estimated Time:** 35-45 minutes
**Difficulty:** Beginner

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

## Objective

You will learn to decompose a medium-sized feature into discrete, independent tasks. By the end of this exercise, you'll understand how to identify task boundaries, verify independence, and ensure each task delivers testable value.

## Prerequisites

- Understanding of discrete task decomposition (read [concept.md](./concept.md))
- Familiarity with task specifications from [1.1 Structured AI Collaboration](../01-structured-ai-collaboration/concept.md)
- Text editor for documenting tasks

## The Exercise

### Scenario

You've been asked to add user authentication to an existing web application that currently has no login system. The application has a React frontend, Express backend, and PostgreSQL database. Users should be able to register, log in, log out, and access protected routes.

This is too large to implement as a single task. Your job is to decompose it into 3-5 discrete tasks that can be completed independently.

### Your Task

Break down the authentication feature following these steps:

1. **List all required components** - Brain dump everything needed: database tables, API endpoints, frontend forms, password handling, session management, error handling, tests, documentation. Don't organize yet, just capture.

2. **Group by single responsibility** - Cluster related components that change for the same reason. Database schema changes together. API endpoint logic together. Frontend UI together. Each group becomes a candidate task.

3. **Define task boundaries** - For each candidate task, write one sentence describing what it accomplishes. If you need "and" in the description, split it into multiple tasks. "Add User model and authentication endpoints" becomes two tasks.

4. **Verify independence** - Can each task be completed and tested without others being finished? Can they be done in any order? If Task B requires Task A to be complete, document the dependency explicitly.

5. **Size check** - Estimate each task in hours. Target 2-6 hours. Tasks under 2 hours might be too granular. Tasks over 6 hours need further decomposition. Re-split or combine as needed.

### Success Criteria

You've completed this exercise successfully when:

- [ ] You have 3-5 discrete tasks documented
- [ ] Each task has a single, clear responsibility stated in one sentence
- [ ] Each task can be tested independently (describe how)
- [ ] Dependencies are explicit and minimal (linear chain, not complex web)
- [ ] Time estimates fall within 2-6 hours per task
- [ ] Tasks could be assigned to different developers without coordination

## Alternative: Apply to Your Project

Choose a real medium-sized feature from your backlog - something that feels too big for one session but not large enough to be an epic. Authentication, reporting dashboard, file upload system, notification service - any feature with multiple components.

Apply the five steps above to decompose it. Focus on finding natural boundaries where responsibilities separate cleanly. Pay attention to testing - if you can't test a task without other tasks being complete, the decomposition isn't discrete enough.

## What You Learned

Discrete decomposition is how you make complex work tractable. By identifying single responsibilities, minimizing dependencies, and ensuring testability, you create tasks that can be implemented confidently, verified objectively, and parallelized effectively.

This skill compounds. The better you decompose, the faster you deliver, because each task becomes a small, manageable problem rather than part of an overwhelming whole. Agents execute discrete tasks efficiently. Monolithic tasks bog them down.

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

**Next:** [Reflection Questions](./reflection.md)
