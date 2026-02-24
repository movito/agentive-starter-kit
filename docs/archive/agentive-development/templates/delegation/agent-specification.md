# Agent Specification: [Agent Name]

<!-- INSTRUCTION: This is a high-level specification for designing a new agent.
     Fill this out BEFORE writing the detailed agent instruction prompt.
     Use this to think through the agent's role and boundaries. -->

**Agent ID**: `[agent-identifier]` (lowercase-with-hyphens, e.g., `api-developer-davinci`)
**Version**: 1.0.0
**Status**: [Proposed | Active | Deprecated]
**Created**: YYYY-MM-DD
**Last Updated**: YYYY-MM-DD

---

## Agent Identity

**Name**: [Agent Name]
**Role**: [One sentence description]
**Emoji**: [Emoji for identity header, e.g., 🔌 for API developer, 🧪 for test runner]

**Example Identity Header:**
```
[EMOJI] **[AGENT-NAME-UPPERCASE]** | Task: [current task description]
```

---

## Purpose and Scope

<!-- INSTRUCTION: Clearly define what this agent does and doesn't do.
     Narrow scope enables deep expertise. -->

**Primary Purpose:**
[What problem does this agent solve? What value does it provide?]

**In Scope:**
- [Responsibility 1 - be specific]
- [Responsibility 2 - be specific]
- [Responsibility 3 - be specific]

**Out of Scope:**
- [What this agent should NOT do - equally important]
- [Responsibility that belongs to another agent]
- [Task type this agent should decline]

**Boundaries:**
[How does this agent know when to hand off to another agent?]

---

## Core Responsibilities

<!-- INSTRUCTION: List 4-6 core responsibilities.
     Focus on WHAT outcomes, not HOW implementation. -->

1. **[Responsibility 1]**
   - [Specific task or outcome]
   - [Success measure]

2. **[Responsibility 2]**
   - [Specific task or outcome]
   - [Success measure]

3. **[Responsibility 3]**
   - [Specific task or outcome]
   - [Success measure]

4. **[Responsibility 4]**
   - [Specific task or outcome]
   - [Success measure]

5. **[Responsibility 5 - optional]**
   - [Specific task or outcome]
   - [Success measure]

---

## Expertise and Knowledge

<!-- INSTRUCTION: What specialized knowledge does this agent need?
     What domain expertise should it demonstrate? -->

**Domain Expertise:**
- [Area 1 - e.g., "Python testing frameworks (pytest, unittest)"]
- [Area 2 - e.g., "Test coverage analysis and improvement strategies"]
- [Area 3 - e.g., "Performance testing and benchmarking"]

**Technical Skills:**
- [Skill 1 - e.g., "Writing test fixtures and mocks"]
- [Skill 2 - e.g., "Interpreting test failure messages"]
- [Skill 3 - e.g., "Debugging flaky tests"]

**Project-Specific Knowledge:**
- [Knowledge 1 - e.g., "Project testing standards and conventions"]
- [Knowledge 2 - e.g., "Known test infrastructure quirks"]
- [Knowledge 3 - e.g., "Integration testing requirements"]

---

## Tool Access and Permissions

<!-- INSTRUCTION: What tools does this agent need?
     Grant minimum necessary permissions (principle of least privilege). -->

**Required Tools:**
- [Tool 1 - e.g., "Read (all project files)"]
- [Tool 2 - e.g., "Write (test files only)"]
- [Tool 3 - e.g., "Bash (run tests, no destructive commands)"]
- [Tool 4 - e.g., "Glob (find test files)"]
- [Tool 5 - e.g., "Grep (search test code)"]
- [Tool 6 - e.g., "TodoWrite (track test development progress)"]

**Restricted Tools:**
- [Tool + Restriction - e.g., "Edit (read-only mode, cannot modify production code)"]
- [Tool + Restriction - e.g., "Bash (cannot run git push, coordinator only)"]

**File Access:**
- **Read access:** [All files | Specific paths]
- **Write access:** [Specific paths only - e.g., `tests/`, `docs/test-reports/`]
- **No access:** [Restricted paths - e.g., `.env`, `secrets/`]

---

## Agent Model Selection

<!-- INSTRUCTION: Which Claude model should this agent use?
     Trade-off: Capability vs. cost vs. speed -->

**Recommended Model:** `[Model ID]`

**Model Options:**
- `claude-sonnet-4-5-20250929` - Most capable, best for complex tasks
- `claude-3-5-haiku-20241022` - Faster and cheaper, good for routine tasks
- `claude-opus-4-20250514` - Highest capability, use for critical/complex work

**Rationale for Selection:**
[Why is this model appropriate for this agent's tasks?]

---

## Quality Gates and Standards

<!-- INSTRUCTION: How do we know if this agent's work is acceptable?
     Define objective, measurable criteria. -->

**Output Quality Standards:**
- [Standard 1 - e.g., "All tests use AAA pattern (Arrange-Act-Assert)"]
- [Standard 2 - e.g., "Test coverage increases by ≥80% for new code"]
- [Standard 3 - e.g., "No flaky tests introduced"]

**Acceptance Criteria for Tasks:**
- [Criterion 1 - e.g., "All tests pass locally before commit"]
- [Criterion 2 - e.g., "Test execution time <5s for fast tests"]
- [Criterion 3 - e.g., "Test descriptions clearly explain what's being tested"]

**Mandatory Workflows:**
- [Workflow 1 - e.g., "Must run full test suite before marking task complete"]
- [Workflow 2 - e.g., "Must update test documentation for new test types"]
- [Workflow 3 - e.g., "Must follow pre-commit/pre-push protocols"]

---

## Coordination and Handoffs

<!-- INSTRUCTION: How does this agent interact with other agents?
     Define handoff protocols and communication patterns. -->

**Receives Work From:**
- [Agent 1 - e.g., "coordinator (task assignments)"]
- [Agent 2 - e.g., "feature-developer (requests for test coverage)"]

**Hands Off Work To:**
- [Agent 1 - e.g., "coordinator (completion reports)"]
- [Agent 2 - e.g., "feature-developer (if bugs found during testing)"]

**Communication Channels:**
- [Channel 1 - e.g., "agent-handoffs.json (status updates)"]
- [Channel 2 - e.g., "Task files in delegation/tasks/ (detailed work specs)"]
- [Channel 3 - e.g., "Test reports in docs/test-reports/ (results documentation)"]

**Status Signaling:**
- `idle` - Available for new work
- `in_progress` - Actively working on task
- `blocked` - Waiting on dependency or clarification
- `completed` - Task finished, results available

---

## Evaluation Workflow Integration

<!-- INSTRUCTION: Should this agent use adversarial evaluation?
     When and how should it request external review? -->

**Evaluation Usage:** [Always | Frequently | Rarely | Never]

**When to Request Evaluation:**
- [Scenario 1 - e.g., "Designing new test strategy for complex feature"]
- [Scenario 2 - e.g., "Unclear acceptance criteria for test coverage"]
- [Scenario 3 - e.g., "Proposed refactoring of test infrastructure"]

**Evaluation Command:**
```bash
adversarial evaluate delegation/tasks/active/TASK-FILE.md
```

**Iteration Limits:**
- Maximum 2-3 evaluations per task
- Escalate to coordinator after 2 NEEDS_REVISION verdicts
- Use judgment: contradictory feedback → ask human, not AI

---

## Example Tasks for This Agent

<!-- INSTRUCTION: Provide 3-5 concrete examples of tasks this agent would handle.
     Helps clarify agent scope and boundaries. -->

### Example 1: [Task Title]
**Description:** [What needs to be done]
**Scope:** [What's included]
**Deliverable:** [What the agent produces]
**Success metric:** [How we know it's done well]

### Example 2: [Task Title]
**Description:** [What needs to be done]
**Scope:** [What's included]
**Deliverable:** [What the agent produces]
**Success metric:** [How we know it's done well]

### Example 3: [Task Title]
**Description:** [What needs to be done]
**Scope:** [What's included]
**Deliverable:** [What the agent produces]
**Success metric:** [How we know it's done well]

---

## Counter-Examples (What This Agent Won't Do)

<!-- INSTRUCTION: Provide 2-3 examples of tasks that seem related but are OUT OF SCOPE.
     Helps define boundaries clearly. -->

### Counter-Example 1: [Task Title]
**Why out of scope:** [Explain why this belongs to another agent or role]
**Better alternative:** [Which agent should handle this instead?]

### Counter-Example 2: [Task Title]
**Why out of scope:** [Explain why this belongs to another agent or role]
**Better alternative:** [Which agent should handle this instead?]

---

## Constraints and Restrictions

<!-- INSTRUCTION: Explicit limits on what this agent can do.
     Important for safety and clarity. -->

**Operational Constraints:**
- [Constraint 1 - e.g., "Cannot modify production code, only test code"]
- [Constraint 2 - e.g., "Cannot deploy or release changes"]
- [Constraint 3 - e.g., "Cannot skip test execution for speed"]

**Technical Constraints:**
- [Constraint 1 - e.g., "Test suite must complete in <2 minutes for fast tests"]
- [Constraint 2 - e.g., "Must use existing test infrastructure (no new frameworks)"]
- [Constraint 3 - e.g., "All tests must be deterministic (no flaky tests)"]

**Process Constraints:**
- [Constraint 1 - e.g., "Must follow TDD workflow (test-first development)"]
- [Constraint 2 - e.g., "Must update test documentation for new patterns"]
- [Constraint 3 - e.g., "Cannot skip pre-commit/pre-push checks"]

---

## Success Metrics for This Agent

<!-- INSTRUCTION: How do we measure if this agent is effective?
     Should be observable and measurable over time. -->

**Quality Metrics:**
- [Metric 1 - e.g., "Test coverage maintained ≥80% for new code"]
- [Metric 2 - e.g., "Zero flaky tests introduced"]
- [Metric 3 - e.g., "95%+ test pass rate maintained"]

**Velocity Metrics:**
- [Metric 1 - e.g., "Test development completes within estimated time 80%+ of tasks"]
- [Metric 2 - e.g., "Bugs caught in testing (not production) >90%"]
- [Metric 3 - e.g., "Test execution time remains <5s for fast tests"]

**Collaboration Metrics:**
- [Metric 1 - e.g., "Clear handoff documentation in >95% of completed tasks"]
- [Metric 2 - e.g., "Blockers escalated within 1 hour of identification"]
- [Metric 3 - e.g., "Task rework <10% (good acceptance criteria)"]

---

## Related Documents

<!-- INSTRUCTION: Link to relevant context for this agent. -->

- **Detailed Instruction Prompt:** `[path-to-agent-instruction.md]`
- **Procedural Knowledge:** `.agent-context/PROCEDURAL-KNOWLEDGE-INDEX.md`
- **Testing Workflow:** `.agent-context/workflows/TESTING-WORKFLOW.md`
- **Agent Coordination:** `.agent-context/agent-handoffs.json`
- **Example Tasks:** [Links to completed tasks this agent handled]

---

## Revision History

<!-- INSTRUCTION: Track changes to agent specification over time. -->

### Version 1.0.0 (YYYY-MM-DD)
- Initial agent specification created
- [Other notable decisions or changes]

### Version 1.1.0 (YYYY-MM-DD)
- [Changes made and why]
- [Impact of changes]

---

## Next Steps (Implementation Checklist)

<!-- INSTRUCTION: Steps to go from specification to operational agent. -->

- [ ] Agent specification reviewed and approved
- [ ] Detailed instruction prompt written (see `agent-instruction.md` template)
- [ ] Agent deployed in system (`.claude/agents/[agent-name].md`)
- [ ] Agent added to coordination system (`agent-handoffs.json`)
- [ ] Agent tested with 2-3 sample tasks
- [ ] Documentation updated (procedural knowledge index)
- [ ] Success metrics baseline established
- [ ] Evaluation workflow configured (if applicable)

---

**Template Version:** 1.0.0
**Last Updated:** 2025-11-14
**Adapted From:** this project agent design patterns

<!-- INSTRUCTION: Remove this comment block before using the template -->
