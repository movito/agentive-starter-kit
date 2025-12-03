# Task Starter Message Template

**Version**: 1.0.0
**Last Updated**: 2025-11-16
**Purpose**: Standardized format for handing off tasks to implementation agents
**Used By**: Coordinators (tycho, coordinator) when assigning tasks

---

## When to Create a Task Starter

Create a task starter message when:
- Assigning a task to an implementation agent
- Task has been evaluated and revised (if applicable)
- Ready for agent to begin work
- User needs to invoke the agent in a new tab

---

## Task Starter Message Format

### Header Section

```markdown
## Task Assignment: [TASK-ID] - [Task Title]

**Task File**: `delegation/tasks/[folder]/[TASK-ID]-[slug].md`
**Handoff File**: `.agent-context/[TASK-ID]-HANDOFF-[agent-type].md`
```

### Overview Section

```markdown
### Overview

[2-3 sentence summary of what needs to be done and why]

[Brief context about the problem being solved or opportunity being addressed]

Your mission: [Clear, action-oriented statement of the agent's goal]
```

### Acceptance Criteria Section

```markdown
### Acceptance Criteria (Must Have)

- [ ] **[Category 1]**: [Specific, measurable criterion]
- [ ] **[Category 2]**: [Specific, measurable criterion]
- [ ] **[Category 3]**: [Specific, measurable criterion]
- [ ] **[Category 4]**: [Specific, measurable criterion]
- [ ] **[Category 5]**: [Specific, measurable criterion]
- [ ] **[Category 6]**: [Specific, measurable criterion]

[Include 5-8 checkboxes covering the most critical deliverables]
```

### Success Metrics Section

```markdown
### Success Metrics

**Quantitative**:
- [Metric 1]: [Target value] (baseline: [current value])
- [Metric 2]: [Target value] (baseline: [current value])
- [Metric 3]: [Target value] (baseline: [current value])
- [Metric 4]: [Target value] (baseline: [current value])

**Qualitative**:
- [Quality attribute 1] ([how this will be verified])
- [Quality attribute 2] ([how this will be verified])
- [Quality attribute 3] ([how this will be verified])
```

### Time Estimate Section

```markdown
### Time Estimate

[Total range] total:
- [Phase 1]: [time range]
- [Phase 2]: [time range]
- [Phase 3]: [time range]
- [Phase 4]: [time range]

[OR for simpler tasks:]

**Estimated**: [X-Y] hours
- [Breakdown by major component if helpful]
```

### Notes Section

```markdown
### Notes

[Include important context that doesn't fit elsewhere:]
- Evaluation status (if applicable)
- Dependencies or blockers
- Related work or reference implementations
- Key decisions or constraints
- Starting point suggestions

[If task was evaluated, mention it:]
- This spec has been evaluated by GPT-4o and revised (cost: $X.XX)
- All [CRITICAL/HIGH/etc.] feedback addressed
- See handoff file for detailed implementation guidance

**⚠️ FIRST ACTION**: Run `./scripts/project start [TASK-ID]` to move task to `3-in-progress/`
```

### Footer

```markdown
---

**Ready to assign to `[agent-name]` agent when you are.**

[OR if specific agent:]

**Recommended agent**: `[agent-name]` ([reason - e.g., "TDD expertise required"])
```

---

## Example Task Starter

Here's a complete example following the template:

```markdown
## Task Assignment: TASK-0102 - Linear Task Sync TDD Rebuild

**Task File**: `delegation/tasks/2-todo/TASK-0102-linear-task-sync-tdd-rebuild.md`
**Handoff File**: `.agent-context/TASK-0102-HANDOFF-implementation-agent.md`

### Overview

Rebuild our Linear task folder synchronization system using proper Test-Driven Development. The current sync was built without tests and shows 12+ legacy mapping warnings per sync. Two sync scripts exist with unclear responsibilities, and zero tests cover the core sync functionality.

Your mission: Follow the RED-GREEN-REFACTOR TDD cycle to create a properly tested, single sync implementation that eliminates legacy warnings and syncs all 178 tasks correctly to Linear.

### Acceptance Criteria (Must Have)

- [ ] **RED Phase**: 30+ failing tests written defining sync behavior
- [ ] **GREEN Phase**: All tests pass, sync works correctly
- [ ] **REFACTOR Phase**: Single sync implementation, legacy code removed
- [ ] **Test Coverage**: ≥80% for sync logic (measured via pytest-cov)
- [ ] **No Legacy Warnings**: Zero "Legacy mapping used" messages
- [ ] **Real Sync Verification**: All 178 tasks show correct Linear status
- [ ] **Documentation**: 6 files created/updated with examples

### Success Metrics

**Quantitative**:
- 30+ tests covering sync scenarios (all passing)
- 80%+ test coverage for sync logic
- 100% sync accuracy (178/178 tasks in correct Linear status)
- 0 legacy warnings (down from 12+)
- 1 sync script (down from 2)

**Qualitative**:
- Tests serve as documentation (clear, descriptive names)
- Safe to refactor (tests provide safety net)
- "Done" means "working" (objective test verification)

### Time Estimate

7-10.5 hours total:
- Phase 1 (RED - Tests): 2-3 hours
- Phase 2 (GREEN - Implementation): 2.5-3.5 hours
- Phase 3 (REFACTOR - Cleanup): 1-2 hours
- Phase 4 (Documentation): 1.5-2 hours

### Notes

- This spec has been evaluated by GPT-4o and revised (cost: $0.03)
- All critical feedback addressed (rate limiting, dependencies, documentation)
- See handoff file for starting point and implementation details
- Follow `tests/test_linear_comments.py` as TDD example pattern

**⚠️ FIRST ACTION**: Run `./scripts/project start TASK-0102` to move task to `3-in-progress/`

---

**Ready to assign to `test-runner` or `powertest-runner` agent when you are.**
```

---

## Complementary Handoff File

The task starter references a handoff file that contains:
- Detailed implementation guidance
- Critical technical details
- Starting point code examples
- Resources and references
- Evaluation history
- Success criteria

See template structure below for creating handoff files.

### Handoff File Structure

```markdown
# [TASK-ID]: [Task Title] - Implementation Handoff

**Date**: YYYY-MM-DD
**From**: [Coordinator Name]
**To**: [Agent Type] ([specific agent if known])
**Task**: delegation/tasks/[folder]/[TASK-ID]-[slug].md
**Status**: Ready for implementation
**Evaluation**: [Status - e.g., "✅ REVISED", "N/A", etc.]

---

## Task Summary
[Detailed task summary - can be longer than task starter]

## Current Situation
[Context about why this task exists]

## Your Mission
[Detailed breakdown of what the agent needs to do]
- Phase 1: [Details]
- Phase 2: [Details]
- Phase 3: [Details]

## Acceptance Criteria (Must Have)
[Same as task starter but can include additional detail]

## Success Metrics
[Same as task starter]

## Critical Implementation Details
[Technical details, code examples, gotchas]

### 1. [Detail Category 1]
[Detailed explanation with code examples]

### 2. [Detail Category 2]
[Detailed explanation]

## Resources for Implementation
[Links to reference code, docs, ADRs, etc.]

## Time Estimate
[Same as task starter]

## Starting Point
[Concrete first steps - what to create, what to run]

## Questions for [Coordinator]
[How agent should communicate if blocked]

## Evaluation History
[If task was evaluated, include summary]

## Success Looks Like
[Concrete end state description]

## Notes
[Additional context]

---

**Task File**: `delegation/tasks/[folder]/[TASK-ID]-[slug].md`
**Evaluation Log**: `.adversarial/logs/[TASK-ID]-PLAN-EVALUATION.md` (if applicable)
**Handoff Date**: YYYY-MM-DD
**Coordinator**: [Name]
```

---

## Best Practices

### DO:
- ✅ Keep task starter concise (fit in user's viewport)
- ✅ Put detailed guidance in handoff file
- ✅ Use checkboxes for acceptance criteria (visual progress)
- ✅ Include both quantitative and qualitative metrics
- ✅ Mention evaluation status if task was evaluated
- ✅ Provide time estimates to set expectations
- ✅ Make success criteria objective and measurable
- ✅ Link to both task file and handoff file

### DON'T:
- ❌ Include full task specification in starter (too long)
- ❌ Skip acceptance criteria (agent needs clear goals)
- ❌ Use vague success metrics ("make it better")
- ❌ Forget to mention evaluation cost/status
- ❌ Omit time estimates (user needs to know scope)
- ❌ Create starter without companion handoff file
- ❌ Use jargon without explanation

---

## Checklist for Creating Task Starter

Before sending task starter to user:

- [ ] Task specification file exists and is complete
- [ ] Handoff file created with detailed guidance
- [ ] Task starter includes all required sections
- [ ] Acceptance criteria are specific and measurable
- [ ] Success metrics include both quantitative and qualitative
- [ ] Time estimate is realistic and broken down by phase
- [ ] Evaluation status mentioned (if applicable)
- [ ] Both task file and handoff file links included
- [ ] **FIRST ACTION reminder included** (`./scripts/project start <TASK-ID>`)
- [ ] Recommended agent type specified
- [ ] agent-handoffs.json updated with task assignment
- [ ] Message is concise enough to fit in viewport

---

## Integration with Agent Workflows

### For Coordinators (Tycho)

After creating task specification and addressing evaluation feedback:

1. Create handoff file: `.agent-context/[TASK-ID]-HANDOFF-[agent-type].md`
2. Update `agent-handoffs.json` with task assignment
3. Create task starter message using this template
4. Send task starter to user
5. User invokes agent in new tab with task starter

### For Implementation Agents

When receiving task starter:
1. **Run `./scripts/project start <TASK-ID>`** to move task to `3-in-progress/` and update status
2. Read task file for full specification
3. Read handoff file for implementation guidance
4. Update `agent-handoffs.json` status to "in_progress"
5. Begin work following acceptance criteria
6. Report progress back through handoff updates

---

**Template Version**: 1.0.0
**Created**: 2025-11-16
**Maintained By**: Coordinators (tycho, coordinator)
**Related**: AGENT-TEMPLATE.md, OPERATIONAL-RULES.md
