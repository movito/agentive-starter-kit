# Discrete Task Decomposition: Reusable Pattern

**Layer:** Foundation
**Topic:** 1.2 Discrete Task Decomposition
**Type:** Checklist

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

Use this task decomposition checklist when:
- Breaking down a medium-to-large feature into implementable units
- Evaluating whether existing tasks are properly scoped
- Planning parallel work across multiple developers or agents
- Identifying why a task feels overwhelming or blocked
- Reviewing task specifications before assignment

## The Pattern

### Task Sizing Checklist

For each candidate task, verify:

**Single Responsibility:**
- [ ] Task description fits in one sentence without "and"
- [ ] Task changes the system for exactly one reason
- [ ] All modifications relate to the same concept or component
- [ ] If you split this task, each piece would feel incomplete alone

**Testable in Isolation:**
- [ ] Task can be verified without other incomplete tasks
- [ ] Success criteria are objective and measurable now
- [ ] Required dependencies already exist or are documented
- [ ] Tests can run immediately upon task completion

**Appropriate Size:**
- [ ] Estimated effort is 2-6 hours
- [ ] Can be completed in a single focused work session
- [ ] Not so small that task overhead exceeds implementation time
- [ ] Not so large that it requires mental context across multiple days

**Clear Dependencies:**
- [ ] Dependencies are explicit (documented) or absent
- [ ] No circular dependencies (A depends on B depends on A)
- [ ] Dependency chain is linear (A→B→C) not web-like
- [ ] Task can start immediately or after specified prerequisite completes

**Reversible if Wrong:**
- [ ] Changes are contained to feature branch
- [ ] Can be reverted without affecting other work
- [ ] No irreversible operations (production schema changes, published APIs)
- [ ] Failure mode is well understood

### Single Responsibility Test

If the task fails the single responsibility check, try this decomposition:

1. **List all file changes** - Which files will this task modify?
2. **Group by reason for change** - Cluster files that change for the same reason
3. **Name each group** - Each group becomes a candidate subtask
4. **Verify independence** - Can groups be implemented separately?

### Dependency Mapping Template

```markdown
## Task Dependencies

**Task:** [TASK-ID] [Task name]

**Depends on:** [List prerequisite tasks that must complete first]
- [TASK-ID-1]: [Why this dependency exists]
- [TASK-ID-2]: [Why this dependency exists]

**Blocks:** [List tasks that cannot start until this completes]
- [TASK-ID-3]: [What they're waiting for]
- [TASK-ID-4]: [What they're waiting for]

**Can run in parallel with:** [List tasks with no interdependency]
- [TASK-ID-5], [TASK-ID-6], [TASK-ID-7]
```

## Usage Example

**Scenario:** Breaking down "Add user authentication" into discrete tasks.

**Original (too large):**
```
TASK: Add user authentication
- Add User model
- Create registration endpoint
- Create login endpoint
- Add frontend login form
- Add session management
- Write tests
```
This is 12+ hours, multiple responsibilities, difficult to test incrementally.

**Decomposed (discrete tasks):**

```markdown
TASK-2025-0090: Add User model with password hashing
Dependencies: None
Size: 3 hours
Single responsibility: Database layer only
Tests: Model validation, password hashing/verification

TASK-2025-0091: Add POST /api/register endpoint
Dependencies: TASK-2025-0090
Size: 2 hours
Single responsibility: Registration logic only
Tests: Valid registration, duplicate email handling, validation errors

TASK-2025-0092: Add POST /api/login endpoint
Dependencies: TASK-2025-0090
Size: 2 hours
Single responsibility: Authentication logic only
Tests: Valid login, invalid credentials, session creation

TASK-2025-0093: Add frontend login form
Dependencies: TASK-2025-0092
Size: 3 hours
Single responsibility: UI layer only
Tests: Form validation, API integration, error display

TASK-2025-0094: Add frontend registration form
Dependencies: TASK-2025-0091
Size: 3 hours
Single responsibility: UI layer only
Tests: Form validation, API integration, success redirect
```

**Benefits of decomposition:**
- Tasks 2091 and 2092 can run in parallel (both depend only on 2090)
- Tasks 2093 and 2094 can run in parallel (independent UI work)
- Each task is testable immediately upon completion
- Each task can be assigned to different developers/agents
- Failures are isolated (broken login doesn't block registration)

## Customization Tips

**For different work types:**
- **New features:** Emphasize independence and parallelization
- **Bug fixes:** Often naturally atomic - less decomposition needed
- **Refactoring:** Break by component/module, verify tests pass at each step
- **Infrastructure:** Decompose by deployment stage (dev → staging → production)

**For different team structures:**
- **Solo work:** Can tolerate some dependencies - you control sequencing
- **Small team (2-3):** Minimize dependencies to enable parallel work
- **Multi-agent:** Require strict independence - no coordination overhead

**Adjust granularity based on:**
- **Experimentation:** Smaller tasks enable faster failure/iteration
- **Well-understood work:** Can use larger tasks with confidence
- **Critical path:** Break critical work smaller to reduce risk
- **Low priority:** Larger tasks acceptable - less overhead matters more

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
- [Concept: Discrete Task Decomposition](./concept.md)
- [Example: Discrete Task Decomposition](./example.md)
- [1.1 Structured AI Collaboration](../01-structured-ai-collaboration/concept.md)
