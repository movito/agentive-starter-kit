# Example F1: Structured Task Alignment at Scale

**Layer:** Foundation
**Topic:** 1.1 Structured AI Collaboration
**Task:** TASK-0091
**Date:** 2025-11-02
**Impact:** 30 tasks aligned in 3.5 hours (30% faster than estimated), prevented quality drift across all agent work

---

## Key Terms

This example uses these terms from **agentive development**:

- **ADR (Architecture Decision Record)** - Document capturing key design decisions with context and rationale
- **Consumer-first testing** - API testing approach that writes tests from client perspective before implementation (ADR-0035)
- **TDD workflow** - RED-GREEN-REFACTOR cycle (write failing test, make it pass, improve code)
- **Quality gate** - Objective pass/fail criteria before proceeding
- **Agent** - AI collaborator with a specific role and tool access
- **Template** - Reusable document structure with placeholders

---

## Context

After completing EPIC-2025-TDD-ENFORCEMENT in early November 2025, we established mandatory testing requirements via pre-commit hooks and TDD workflows. This was a significant improvement to project quality standards. However, we immediately faced a problem: **30 active tasks predated these changes**.

**The Challenge:**

Every one of these 30 tasks lacked the new mandatory sections:
- **TDD workflow** requirements (RED-GREEN-REFACTOR cycle)
- Test coverage expectations
- API testing standards (**ADR-0035** - consumer-first testing approach)
- Pre-commit/pre-push validation requirements

Without updating these tasks, agents would implement features using outdated specifications that didn't require tests. The gap between "old tasks" and "new standards" would cause confusion, inconsistency, and quality regression.

**Why This Mattered:**

This wasn't just documentation cleanup - it was preventing quality drift. If agents picked up pre-TDD tasks, they'd deliver untested code that would bypass pre-commit hooks (using `SKIP_TESTS=1`) because the task didn't specify testing requirements. All the infrastructure we'd built for quality enforcement would be undermined by outdated task specifications.

---

## The Challenge

**Scale:** 30 tasks needed updates, but they weren't all the same. Some were API tasks requiring **consumer-first testing** (writing tests from client perspective before implementation, per ADR-0035). Some were feature tasks needing full TDD cycles. Some were documentation tasks requiring only pre-push validation. Some were obsolete documents that should be archived.

**Consistency:** Updates needed to be comprehensive but not copy-paste. Each task had unique context that should be preserved while adding standard sections.

**Time Pressure:** These were active tasks. Agents could pick them up at any time. We needed fast alignment to prevent quality issues.

**The Wrong Approach:**

Opening each task one-by-one, reading context, deciding what sections to add, updating, committing. For 30 tasks, this would take 5-8 hours and be error-prone. Some tasks would get different updates than others. Copy-paste errors would create inconsistencies.

---

## Our Approach

### Step 1: Update the Authoritative Template

**File:** `delegation/templates/TASK-TEMPLATE.md`

Before updating any tasks, we updated the template that defines what ALL future tasks should look like. Added four new sections:

```markdown
## TDD Workflow (Mandatory)
[Instructions for RED-GREEN-REFACTOR cycle]

## Test Coverage Requirements
[Line coverage targets, critical path coverage]

## API Testing Requirements (if applicable)
[ADR-0035 consumer-first testing standards]

## Pre-Commit/Pre-Push Requirements
[Git hooks, validation scripts]
```

**Why template-first:**
- Establishes single source of truth for "correct" task structure
- Future tasks automatically include these sections
- Provides authoritative reference when updating existing tasks
- Prevents "which version is right?" confusion

**Time:** 30 minutes

### Step 2: Classify Tasks into Groups

Instead of treating 30 tasks individually, we grouped them by type:

**Group A (4 tasks): Testing tasks** - Already aligned, no changes needed
**Group B (3 tasks): API tasks** - Need ADR-0035 consumer-first testing
**Group C (7 tasks): Feature tasks** - Need full TDD workflow
**Group D (4 tasks): Documentation tasks** - Need minimal pre-push validation
**Group E (11 tasks): Maintenance/meta tasks** - Review case-by-case, potentially archive

**Why classification works:**
- Similar tasks get similar updates (pattern-based efficiency)
- Different task types get appropriate requirements (not one-size-fits-all)
- Enables batch processing (Group B → Group C → Group D → Group E)
- Clear scope: 5 groups, not 30 individual tasks

**Key insight:** The classification revealed that Group E contained 6 obsolete documents (old handoffs, completed work summaries). These should be archived, not updated.

**Time:** 15 minutes

### Step 3: Batch Update Each Group

**Group A:** Verified alignment, marked ✅ complete

**Group B (API tasks):** Added ADR-0035 section:
```markdown
## API Testing Requirements (ADR-0035)
- [ ] Contract validation against OpenAPI spec
- [ ] Consumer-first testing (test from API user perspective)
- [ ] Quality metrics (no null pollution, minimal responses)
- [ ] Version compatibility tests
- [ ] Error response validation
```

**Group C (Feature tasks):** Added TDD workflow:
```markdown
## TDD Workflow (Mandatory)
1. **Before coding**: Copy `tests/test_template.py` → `tests/test_<feature>.py`
2. **Red**: Write failing tests for feature
3. **Green**: Implement until tests pass
4. **Refactor**: Improve code while keeping tests green
5. **Commit**: Pre-commit hook runs tests automatically
```

**Group D (Documentation tasks):** Added pre-push requirements:
```markdown
## Pre-Commit/Pre-Push Requirements
- [ ] Run `./scripts/ci-check.sh` before push (MANDATORY)
- [ ] All markdown files render correctly
- [ ] All links validate
- [ ] Code examples have correct syntax
```

**Group E (Maintenance):** Reviewed case-by-case:
- 6 archived to `delegation/tasks/completed/` (obsolete)
- 3 updated with appropriate requirements
- 2 kept as-is (reference documents, no action needed)

**Time:** 2.5 hours

### Step 4: Verification

- Ensured all updated tasks reference current workflows (TESTING-WORKFLOW.md, COMMIT-PROTOCOL.md)
- Verified consistent formatting across updates
- Confirmed no regressions (existing content preserved)
- Updated agent-handoffs.json with completion status

**Time:** 30 minutes

---

## The Implementation

**Code/Configuration:** `delegation/templates/TASK-TEMPLATE.md` (lines 45-95)

```markdown
## TDD Workflow (Mandatory)

**Before writing any code:**
1. Copy `tests/test_template.py` to `tests/test_<your_feature>.py`
2. Read the template examples to understand test patterns
3. Write test file before implementation

**RED-GREEN-REFACTOR cycle:**
1. **Red**: Write failing test that defines expected behavior
2. **Green**: Implement minimum code to make test pass
3. **Refactor**: Improve code quality while keeping tests green
4. **Commit**: Pre-commit hook runs tests automatically

## Test Coverage Requirements

**New code:**
- Line coverage: 80%+ for new code
- Branch coverage: 70%+ for new logic paths
- Critical paths: 100% coverage

**Overall project:**
- Maintain or improve baseline (currently 53%)
- No coverage regressions allowed
```

**Result structure:** 19 tasks updated with 1,100+ lines of requirements. Every implementation task now includes explicit testing expectations. Every agent knows what "done" means (tests passing, coverage maintained, pre-commit hooks pass).

---

## Results

**Metrics:**
- **Time:** 3.5 hours (vs 4-5 estimated, 30% faster)
- **Tasks updated:** 19 of 30 (remaining 11 either already aligned or archived)
- **Lines added:** ~1,100 lines of testing requirements
- **Quality:** Zero regressions (existing context preserved)
- **Consistency:** All tasks reference same workflows (TESTING-WORKFLOW.md)

**Source:** Task completion summary in `delegation/tasks/completed/TASK-0091-align-tasks-with-tdd-enforcement.md`

**Impact:**

*Immediate:*
- All active tasks now require tests (prevents untested code from shipping)
- Agents have clear expectations (no ambiguity about "done")
- Pre-commit hooks enforced project-wide (tests run on every commit)

*Long-term:*
- Template updates propagate to all new tasks automatically
- Consistent quality standards across all agent work
- Reduced CI failures (tests run locally before push)
- Better code quality through mandatory TDD workflow

---

## Reflection

**What Worked:**

Classification was the breakthrough. Breaking 30 tasks into 5 groups transformed "30 individual updates" into "5 pattern applications." Similar tasks got similar updates efficiently. Different task types got appropriate requirements (API tasks got ADR-0035, feature tasks got full TDD, documentation tasks got minimal validation).

Template-first approach established authority. Updating TASK-TEMPLATE.md before touching any tasks created a clear reference. All subsequent updates followed the template pattern. Future tasks automatically inherit the updated structure.

Archive decisions improved clarity. Group E review identified 6 obsolete documents. Moving them from `active/` to `completed/` reduced clutter and prevented agents from accidentally picking up outdated work.

**What Didn't Work:**

Group E took longer than expected. Initially estimated all groups as equal effort. Maintenance tasks required more judgment (archive vs update vs keep as-is). Should have allocated more time for review-heavy groups.

Some updates were more copy-paste than customized. Feature tasks (Group C) got nearly identical sections. Could have created single reference document (like TDD-REQUIREMENTS.md) and linked from tasks instead of duplicating content.

**Key Insight:**

Structured collaboration isn't just about individual tasks - it's about maintaining consistency at scale. When you have multiple tasks, multiple agents, and evolving standards, structure is what prevents chaos. Templates, classification, and batch processing turn "impossible to maintain" into "completed in an afternoon."

---

## Learnings

- **Learning 1: Templates are force multipliers** - 30 minutes updating one template file saved 2-3 hours of per-task customization
- **Learning 2: Classification before execution** - 15 minutes grouping tasks made 2.5 hours of updates flow smoothly
- **Learning 3: Archive decisions matter** - Removing 6 obsolete tasks improved clarity more than updating them would have

---

## Adaptation Guide

**This pattern applies when:**
- You need to standardize across 10+ existing resources (tasks, docs, configs)
- Resources can be meaningfully grouped by type or purpose
- Updates follow patterns (not all unique customization)
- You have a template or reference defining "correct" state
- Time investment is justified by scale and quality impact

**Adapt for your context:**
- **Core pattern stays same:** Template-first, classify, batch update, verify
- **Customize grouping:** Your groups will differ (by file type, by team, by priority)
- **Adjust batch size:** 30 tasks worked for us; scale up or down based on your resources
- **Automate verification:** Write scripts to check for required sections (we did manual spot-checking)

**When NOT to use:**
- Small scale (< 10 resources) - individual updates faster than classification overhead
- High uniqueness (resources share no patterns) - batch processing provides no efficiency
- Unclear standard (no template or reference) - premature to standardize without knowing target state

---

**See also:**
- [Concept: Structured AI Collaboration](./concept.md)
- [Practice Exercise](./practice.md)
- [Pattern: Task Template Evolution](./pattern.md)
