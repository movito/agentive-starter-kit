# Task Decomposition Worksheet

**Purpose:** Break a medium/large feature into 3-7 discrete, independent tasks
**Layer:** Foundation
**Topic:** 1.2 Discrete Task Decomposition
**Estimated Time to Complete:** 45-60 minutes

---


## Key Terms

This template uses these terms from **agentive development** (a methodology treating AI assistants as specialized collaborators, not mere code generators):

- **Task** - Discrete unit of work with clear acceptance criteria
- **Agent** - AI collaborator with a specific role and tool access
- **Template** - Reusable document structure with placeholders
- **Quality gate** - Objective pass/fail criteria before proceeding
- **TDD (Test-Driven Development)** - Practice of writing tests before implementation

See the [full glossary](../../../.agent-context/agentive-development-glossary.md) for complete terminology reference.

---

## When to Use This Template

Use this worksheet when:
- You need to implement a feature that feels too large for a single task (>6 hours)
- You want to enable parallel work by multiple agents or developers
- You need to break an EPIC into manageable subtasks
- You're planning a sprint and need to estimate work granularity
- You want to minimize dependencies and maximize independent progress

---

## Instructions

1. **Start with the feature overview** - Write 2-3 sentences describing what you're building and why
2. **Brainstorm task candidates** - List every possible subtask without filtering (aim for 8-15 initial ideas)
3. **Map dependencies** - Draw arrows showing which tasks depend on others
4. **Test independence** - For each task, ask: "Can this be completed without waiting for other tasks?"
5. **Check sizing** - Each task should be 2-6 hours. If larger, split further
6. **Write task stubs** - For each final task, write a brief specification
7. **Validate with checklist** - Ensure all criteria pass before proceeding

---

## The Template

```markdown
# Feature Decomposition: [FEATURE NAME]

**Date:** YYYY-MM-DD
**Decomposed by:** [Your name or agent name]
**Estimated total time:** [X hours or days]
**Target completion:** [Date or sprint]

---

## 1. Feature Overview

**What are we building?**
[2-3 sentences describing the feature]

**Why does it matter?**
[Business value or user impact]

**Success criteria for entire feature:**
- [ ] [Criterion 1 - measurable]
- [ ] [Criterion 2 - measurable]
- [ ] [Criterion 3 - measurable]

---

## 2. Task Candidate Brainstorm

<!-- List ALL potential subtasks without filtering. Aim for 8-15 ideas. -->

1. [Task idea 1]
2. [Task idea 2]
3. [Task idea 3]
4. [Task idea 4]
5. [Task idea 5]
6. [Task idea 6]
7. [Task idea 7]
8. [Task idea 8]
9. [Continue...]

---

## 3. Dependency Mapping

<!-- Show which tasks depend on others. Use arrows (→) or simple text. -->

**Example format:**
```
Task 1 (Foundation) → Task 3 (Uses Task 1's output)
Task 2 (Independent)
Task 4 (Depends on Task 1 + Task 3)
```

**Dependencies for this feature:**
[Your dependency map]

**Independent tasks** (can start immediately):
- [Task X]
- [Task Y]
- [Task Z]

**Dependent tasks** (need other tasks first):
- [Task A] → depends on [Task X]
- [Task B] → depends on [Task Y, Task Z]

---

## 4. Independence Test

<!-- For each task, verify it can be completed alone -->

| Task | Can start immediately? | Depends on | Can be done in parallel? |
|------|----------------------|------------|-------------------------|
| [Task 1] | ✅ Yes / ❌ No | [Dependencies or "None"] | ✅ Yes / ❌ No |
| [Task 2] | ✅ Yes / ❌ No | [Dependencies or "None"] | ✅ Yes / ❌ No |
| [Task 3] | ✅ Yes / ❌ No | [Dependencies or "None"] | ✅ Yes / ❌ No |
| [Continue...] | | | |

---

## 5. Size Estimation

<!-- Each task should be 2-6 hours. Split if larger. -->

| Task | Estimated Time | Too Large? | How to Split |
|------|---------------|-----------|--------------|
| [Task 1] | [X hours] | ✅ Yes / ❌ No | [Split strategy if yes] |
| [Task 2] | [X hours] | ✅ Yes / ❌ No | [Split strategy if yes] |
| [Task 3] | [X hours] | ✅ Yes / ❌ No | [Split strategy if yes] |
| [Continue...] | | | |

**Total estimated time:** [Sum of all tasks]
**Parallelization factor:** [If 3 tasks can run in parallel: "3x faster with 3 agents"]

---

## 6. Final Task List

<!-- After filtering and splitting, list your 3-7 final tasks -->

### Task 1: [TASK NAME]
- **Goal:** [What does this accomplish?]
- **Acceptance criteria:**
  - [ ] [Criterion 1]
  - [ ] [Criterion 2]
- **Dependencies:** [None or list tasks]
- **Estimated time:** [X hours]
- **Assigned to:** [Agent or person, or "TBD"]

### Task 2: [TASK NAME]
- **Goal:** [What does this accomplish?]
- **Acceptance criteria:**
  - [ ] [Criterion 1]
  - [ ] [Criterion 2]
- **Dependencies:** [None or list tasks]
- **Estimated time:** [X hours]
- **Assigned to:** [Agent or person, or "TBD"]

### Task 3: [TASK NAME]
- **Goal:** [What does this accomplish?]
- **Acceptance criteria:**
  - [ ] [Criterion 1]
  - [ ] [Criterion 2]
- **Dependencies:** [None or list tasks]
- **Estimated time:** [X hours]
- **Assigned to:** [Agent or person, or "TBD"]

<!-- Continue for all tasks (3-7 total) -->

---

## 7. Validation Checklist

Before proceeding with task creation, verify:

- [ ] Each task is testable independently (has clear acceptance criteria)
- [ ] Each task is 2-6 hours (not larger, not smaller)
- [ ] Dependencies are minimal (≤30% of tasks have dependencies)
- [ ] Tasks can mostly be done in different orders (flexible sequencing)
- [ ] Each task has clear acceptance criteria (objective pass/fail)
- [ ] Total effort matches feature estimate (±20%)
- [ ] At least 50% of tasks can start immediately (no dependencies)
- [ ] Each task delivers value on its own (not just scaffolding)

**If any item fails:** Revise the decomposition before creating task specifications.

---

```

---

## Usage Examples

This template was used for:

1. **[TASK-0091: TDD Enforcement Alignment](../../../delegation/tasks/completed/TASK-0091-align-tasks-with-tdd-enforcement.md)**
   - Feature: Update 30 active tasks with new TDD requirements
   - Decomposition: 5 groups (A, B, C, D, E) with 30 tasks total
   - Result: Enabled parallel updates, 6 tasks archived, 19 updated, 5 kept as-is
   - Time savings: Completed in 3.5 hours (estimated 4-5 hours)

2. **[TASK-2025-0078: API Server Foundation](../../../delegation/tasks/active/TASK-0078-api-server-foundation.md)**
   - Feature: Build FastAPI server with 2 endpoints + monitoring
   - Decomposition: 4 phases broken into 24 tasks (6 tasks/phase)
   - Result: Completed in 3 days (estimated 4.5 days, 33% time savings)
   - Parallelization: Testing and documentation done concurrently

3. **[EPIC-2025-TDD-ENFORCEMENT](../../../delegation/tasks/completed/EPIC-2025-TDD-ENFORCEMENT.md)**
   - Feature: Cultural shift to mandatory testing
   - Decomposition: 4 parallel tasks (fix tests, add hooks, update docs, setup monitoring)
   - Result: 100% completion in 8 hours (estimated 14-18 hours, 44% time savings)
   - Parallel execution: All 4 tasks ran simultaneously by different agents

---

## Tips

- **Tip 1: Start broad, then filter** - It's easier to combine small tasks than split large ones. Brainstorm 10-15 candidates, then consolidate to 3-7 final tasks.

- **Tip 2: Minimize dependencies** - Dependent tasks slow down parallel work. If >30% of tasks have dependencies, look for ways to invert or eliminate them.

- **Tip 3: Test independence with "can I start this today?"** - For each task, imagine you're starting work right now. If the answer is "I need to wait for X first," that's a dependency to document.

- **Tip 4: Use grouping for large features** - If you have >10 tasks, group them by theme (e.g., Group A: Testing, Group B: API, Group C: Features). See TASK-0091 for example.

- **Tip 5: Size tasks for TDD cycles** - A 2-6 hour task typically fits 2-4 RED-GREEN-REFACTOR cycles. This natural rhythm helps maintain momentum.

- **Tip 6: Validate with the "parallel test"** - Can 3 people start 3 different tasks at the same time? If not, you have too many dependencies.

- **Tip 7: Document "why not combined"** - If someone might ask "why didn't you combine Task 2 and Task 3?", document your reasoning in the decomposition notes.

---

**Related:**
- [Concept: Discrete Task Decomposition](../../01-foundation/02-discrete-task-decomposition/concept.md)
- [Example: F2 - Task Decomposition for API Server](../../examples/F2-task-decomposition-api-server.md)
- [Template: Task Specification](./task-specification.md) - Use after completing this worksheet
- [Pattern: Independence-First Decomposition](../../01-foundation/02-discrete-task-decomposition/pattern.md)
