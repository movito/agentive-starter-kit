# Session Handoff Template

**Purpose:** Document session state for resumption by another agent or in a future session
**Layer:** Foundation
**Topics:** 1.4 Git Safety Practices + 1.5 Context Management Basics
**Estimated Time to Complete:** 10-20 minutes (short form) or 30-45 minutes (detailed form)

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

Use this template when:
- Ending a work session and want to document progress for later resumption
- Handing off partially completed work to another agent or developer
- Reaching a natural stopping point but task isn't complete
- Encountering a blocker that requires external input or decisions
- Creating a completion report for a finished task (expanded detail version)
- Documenting decisions made during implementation for future reference

---

## Instructions

1. **Choose your format** - Short (100-200 words), Standard (200-400 words), or Detailed (400-600 words)
2. **Fill in session metadata** - Date, agent, task reference, branch name
3. **Document current status** - What's done, what's in progress, what's not started
4. **Capture decisions made** - Technical choices, trade-offs, rejected approaches
5. **List blockers** - Anything preventing forward progress
6. **Specify next steps** - Priority-ordered list of what should happen next
7. **Check git state** - Ensure everything is committed or document uncommitted changes
8. **Update agent-handoffs.json** - Keep brief_note in sync with this handoff document
9. **Save handoff file** - Location: `.agent-context/YYYY-MM-DD-TASK-XXXX-HANDOFF.md`

---

## Template Formats

### Short Form (100-200 words)

Use for: Simple tasks, daily standups, quick status updates

```markdown
# Session Handoff: [TASK-ID] [Task Name]

**Date:** YYYY-MM-DD HH:MM
**Agent:** [Agent name or developer name]
**Task:** [TASK-ID or TASK-ID]
**Branch:** [branch-name or "main"]
**Status:** [In Progress | Blocked | Ready for Review]

---

## Progress

**Completed:**
- [Item 1]
- [Item 2]

**In progress:**
- [Item currently being worked on]

**Not started:**
- [Item 1]
- [Item 2]

---

## Next Steps

1. [Priority 1 action]
2. [Priority 2 action]
3. [Priority 3 action]

**Assigned to:** [Agent/person or "TBD"]
**Estimated time to complete:** [X hours]

---

## Git State

- Current branch: `[branch-name]`
- Commits this session: [N commits]
- Uncommitted changes: [None | List files]
- Ready to push: ✅ Yes | ❌ No - [reason]
```

---

### Standard Form (200-400 words)

Use for: Medium tasks, inter-agent handoffs, multi-session work

```markdown
# Session Handoff: [TASK-ID] [Task Name]

**Date:** YYYY-MM-DD HH:MM
**Agent:** [Agent name or developer name]
**Task:** [Link to task file - e.g., delegation/tasks/active/TASK-XXXX.md]
**Branch:** [branch-name or "main"]
**Session duration:** [X hours]
**Progress:** [Percentage complete - e.g., "60% complete (3/5 subtasks)"]

---

## Executive Summary

[2-3 sentences summarizing what was accomplished this session and current state]

---

## Status

### Completed This Session ✅
1. [Item 1 with brief detail]
2. [Item 2 with brief detail]
3. [Item 3 with brief detail]

### In Progress 🔄
- **[Item name]** - [What's done, what remains]
  - Files modified: [list]
  - Tests: [passing/failing count]
  - Blocker: [if any]

### Not Started Yet ⏸️
1. [Item 1]
2. [Item 2]
3. [Item 3]

---

## Decisions Made

### Decision 1: [Decision Title]
- **Context:** [Why this decision was needed]
- **Options considered:** [Option A, Option B, Option C]
- **Decision:** [What was chosen]
- **Rationale:** [Why this option was best]
- **Trade-offs:** [What we're accepting as consequence]

### Decision 2: [Decision Title]
[Same structure]

---

## Blockers

### Blocker 1: [Blocker Title]
- **Description:** [What's blocking progress]
- **Impact:** [How this affects the task]
- **Who can unblock:** [Person/agent/team]
- **Required by:** [Date or "ASAP"]

### Blocker 2: [Blocker Title]
[Same structure if applicable, or delete if no blockers]

---

## Next Steps

**Priority order:**
1. [Highest priority action - who should do it]
2. [Next action - who should do it]
3. [Third action - who should do it]

**Recommended assignee:** [Agent/person or "TBD"]
**Estimated time to complete:** [X hours for remaining work]

---

## Context for Resumption

### Files Modified
- `[file_path]` - [what was changed]
- `[file_path]` - [what was changed]
- `[file_path]` - [what was changed]

### Tests Added/Updated
- `tests/[test_file]` - [N tests added, M tests updated]
- Test status: [X/Y passing]

### Documentation Updated
- [Document name] - [what was updated]

### Key Code Locations
- [Feature implementation]: `[file:line]`
- [Test coverage]: `tests/[file]`
- [Related code]: `[file:line]`

---

## Git State

- **Current branch:** `[branch-name]`
- **Commits this session:**
  - `[commit-hash]` - [commit message]
  - `[commit-hash]` - [commit message]
  - [Continue for all commits]
- **Uncommitted changes:** [None | List files with brief description]
- **Ready to push:** ✅ Yes | ❌ No
  - If No: [Reason - e.g., "Waiting for test fixes" or "WIP commit needs completion"]
- **Needs merge from main:** ✅ Yes | ❌ No

### Git Commands for Resumption
```bash
# To resume work on this branch:
git checkout [branch-name]
git pull origin [branch-name]

# To merge latest main (if needed):
git fetch origin
git merge origin/main
```

---

## agent-handoffs.json Update

Update the entry for [agent-name]:
```json
{
  "[agent-name]": {
    "status": "in_progress",
    "current_task": "[TASK-ID]",
    "task_started": "YYYY-MM-DD",
    "brief_note": "[One sentence status]",
    "details_link": ".agent-context/YYYY-MM-DD-TASK-XXXX-HANDOFF.md"
  }
}
```
```

---

### Detailed Form (400-600 words)

Use for: Complex tasks, completion reports, major milestones, critical handoffs

```markdown
# [Session Handoff | Completion Report]: [TASK-ID] [Task Name]

**Date:** YYYY-MM-DD HH:MM
**Agent:** [Agent name or developer name]
**Task:** [Link to task file]
**Branch:** [branch-name or "main"]
**Session duration:** [X hours]
**Status:** [In Progress | Completed | Blocked | Ready for Review]
**Progress:** [Percentage complete with breakdown]

---

## Executive Summary

[3-5 sentences providing high-level overview of session work and outcomes]

---

## Session Objectives

**What we planned to accomplish:**
1. [Objective 1]
2. [Objective 2]
3. [Objective 3]

**What we actually accomplished:**
1. ✅ [Objective 1 - completed]
2. 🔄 [Objective 2 - in progress, 60% done]
3. ❌ [Objective 3 - blocked by X]

**Variance from plan:**
[Explanation of why actual differed from planned]

---

## Detailed Status

### Completed This Session ✅

#### 1. [Feature/Task Name]
- **What:** [Description of what was completed]
- **Files changed:** [list with line counts]
- **Tests added:** [N tests, all passing]
- **Time spent:** [X minutes/hours]
- **Commits:**
  - `[hash]` - [message]

#### 2. [Feature/Task Name]
[Same structure]

### In Progress 🔄

#### [Feature/Task Name] (60% complete)
- **What's done:**
  - [Item 1]
  - [Item 2]
- **What remains:**
  - [Item 1 - estimated X hours]
  - [Item 2 - estimated Y hours]
- **Files modified:** [list]
- **Current blocker:** [if any]
- **Tests:** [X passing, Y failing]
  - Failing tests: [list with brief reason]

### Not Started Yet ⏸️
1. [Item 1 - estimated X hours]
2. [Item 2 - estimated Y hours]
3. [Item 3 - estimated Z hours]

**Total remaining work:** [Sum of estimates]

---

## Technical Decisions Made

### Decision 1: [Decision Title]
- **Context:** [Detailed background - why was this decision needed?]
- **Options considered:**
  1. **Option A:** [description] - Pros: [list], Cons: [list]
  2. **Option B:** [description] - Pros: [list], Cons: [list]
  3. **Option C:** [description] - Pros: [list], Cons: [list]
- **Decision:** [What we chose and why]
- **Rationale:** [Detailed reasoning with metrics if available]
- **Trade-offs accepted:**
  - [Trade-off 1]
  - [Trade-off 2]
- **Alternatives rejected:** [Why other options weren't chosen]
- **Documented in:** [ADR reference if applicable, or "This handoff only"]

### Approaches Tried and Rejected

#### Attempt 1: [Approach Name]
- **What we tried:** [Description]
- **Why it didn't work:** [Technical reason]
- **What we learned:** [Key insight for future work]
- **Time spent:** [X hours]

#### Attempt 2: [Approach Name]
[Same structure]

---

## Blockers and Issues

### Critical Blockers 🚨
These prevent any forward progress:

#### Blocker 1: [Title]
- **Description:** [Detailed explanation]
- **Impact:** [How this affects task and timeline]
- **Root cause:** [What's causing the blocker]
- **Who can unblock:** [Specific person/agent/team]
- **Required by:** [Date or "ASAP"]
- **Workaround:** [Temporary solution if available, or "None"]

### Non-Blocking Issues ⚠️
Work can continue, but these need attention:

#### Issue 1: [Title]
- **Description:** [What's the problem]
- **Workaround:** [How we're working around it]
- **Should be fixed because:** [Why it matters long-term]
- **Assignee:** [Who should fix it]

---

## Next Steps

**Immediate next steps** (priority order):
1. [Action 1 - who, estimated time, dependencies]
2. [Action 2 - who, estimated time, dependencies]
3. [Action 3 - who, estimated time, dependencies]

**Subsequent steps:**
4. [Action 4]
5. [Action 5]

**Recommended assignee for next session:** [Agent/person or "TBD"]
**Estimated time to completion:** [X hours for remaining work]

**Prerequisites for next session:**
- [Prerequisite 1 - e.g., "Need design approval"]
- [Prerequisite 2 - e.g., "Blocker must be resolved"]

---

## Context for Resumption

### Implementation Details

**Key code locations:**
- Main implementation: `[file:line-range]`
- Tests: `tests/[file:line-range]`
- Configuration: `[file:line-range]`
- Related utilities: `[file:line-range]`

**Code patterns used:**
- [Pattern 1 - e.g., "Factory pattern for format handlers"]
- [Pattern 2 - e.g., "AAA pattern for all tests"]

**Important functions/classes:**
- `[function_name]` in `[file]` - [what it does]
- `[class_name]` in `[file]` - [what it does]

### Files Changed

| File | Lines Changed | Purpose |
|------|--------------|---------|
| `[file_path]` | +X -Y | [what changed] |
| `[file_path]` | +X -Y | [what changed] |
| `[file_path]` | +X -Y | [what changed] |

**Total:** +[X] lines, -[Y] lines

### Tests

**Tests added:** [N tests]
**Tests updated:** [M tests]
**Current test status:** [X/Y passing (Z%)]

**Test files:**
- `tests/[file]` - [N tests, all passing/X failing]
  - Failing: [test names with brief failure reason]

**Coverage:**
- Module coverage: [X%]
- Lines covered: [X/Y]
- Missing coverage: [files or line ranges]

### Documentation

**Documentation updated:**
- [Document name] - [what sections were updated]
- [Document name] - [what was added]

**Documentation needed:**
- [What still needs documenting]
- [Why it matters]

---

## Testing & Quality

### Test Results
```bash
# Latest test run
pytest tests/[module]/ -v
# Result: X passed, Y failed, Z skipped

[Paste test output if relevant]
```

### Coverage Report
```bash
# Coverage check
pytest tests/[module]/ --cov=[module] --cov-report=term
# Result: X% coverage

[Paste coverage output]
```

### Quality Checks
- [ ] Code formatted: `black [files]` ✅ | ❌
- [ ] Imports sorted: `isort [files]` ✅ | ❌
- [ ] Linting clean: `flake8 [files]` ✅ | ❌
- [ ] Type hints added: ✅ | ❌
- [ ] Tests passing: ✅ | ❌ | ⚠️ Partial
- [ ] Coverage target met (80%+): ✅ | ❌
- [ ] Pre-commit hook passes: ✅ | ❌

---

## Git State

### Branch Information
- **Current branch:** `[branch-name]`
- **Parent branch:** `[main/develop/feature-branch]`
- **Divergence:** [X commits ahead, Y commits behind]
- **Branch age:** [Created N days ago]

### Commits This Session

1. `[full-commit-hash]` - `[commit message]`
   - Files: [N files changed]
   - Lines: +[X] -[Y]
   - Tests: [status]

2. `[full-commit-hash]` - `[commit message]`
   - Files: [N files changed]
   - Lines: +[X] -[Y]
   - Tests: [status]

[Continue for all commits]

**Total commits:** [N]
**Total changes:** +[X] lines, -[Y] lines across [Z] files

### Working Tree Status
```bash
git status
# Output:
[Paste git status output]
```

**Uncommitted changes:**
- [file] - [brief description of changes]
- [file] - [brief description of changes]

**Untracked files:**
- [file] - [what it is]

### Push Status
- **Ready to push:** ✅ Yes | ❌ No
- **If No:** [Reason]
- **Push command:**
  ```bash
  git push origin [branch-name]
  ```

### Merge Status
- **Needs merge from main:** ✅ Yes | ❌ No
- **Conflicts expected:** ✅ Yes (in [files]) | ❌ No
- **Last merged from main:** [Date or "Never"]

### Git Commands for Resumption
```bash
# Resume work on this branch
git checkout [branch-name]
git pull origin [branch-name]

# Sync with main (if needed)
git fetch origin
git merge origin/main
# or: git rebase origin/main

# View recent changes
git log --oneline -5

# View file changes
git diff origin/main...HEAD
```

---

## agent-handoffs.json Update

**Current entry for [agent-name]:**
```json
{
  "[agent-name]": {
    "status": "[in_progress|idle|blocked]",
    "current_task": "[TASK-ID]",
    "task_started": "YYYY-MM-DD",
    "brief_note": "[One sentence summary of current state]",
    "details_link": ".agent-context/YYYY-MM-DD-TASK-XXXX-[HANDOFF|COMPLETION].md",
    "status_report": "[path to this file]"
  }
}
```

**Recommended status:** [in_progress | blocked | ready_for_review]
**Update brief_note to:** "[One sentence capturing current state]"

---

## Lessons Learned

### What Went Well ✅
1. [Thing 1 that worked well]
2. [Thing 2 that worked well]
3. [Thing 3 that worked well]

### What Could Be Improved 🔄
1. [Thing 1 to improve next time]
2. [Thing 2 to improve next time]

### Key Insights 💡
1. [Insight 1 - technical or process learning]
2. [Insight 2 - something we discovered]
3. [Insight 3 - pattern that emerged]

---

## Related Documents

- **Task specification:** [path to task file]
- **Related tasks:** [links to dependent or related tasks]
- **ADRs:** [links to relevant architecture decision records]
- **Previous handoffs:** [links to prior session handoffs for this task]
- **References:** [links to documentation, articles, or resources used]

---

**Next reviewer:** [Who should review this handoff]
**Review by:** [Date if time-sensitive]
```

---

## Usage Examples

This template was used for:

1. **[TASK-2025-0083 Completion Report](.agent-context/2025-11-12-TASK-2025-0083-COMPLETION-REPORT.md)**
   - Format: Detailed form (395 lines)
   - Purpose: Document completion of API test bug fixes
   - Content: 11 bugs fixed, 17 tests passing, design decisions, lessons learned
   - Result: Clear completion handoff with all context for future reference

2. **[agent-handoffs.json](../../../.agent-context/agent-handoffs.json)**
   - Format: Short form (embedded in JSON)
   - Purpose: Track current agent status across all agents
   - Pattern: `brief_note` provides 1-sentence status, `details_link` points to full handoff
   - Update frequency: After every significant status change

3. **[TASK-0091 Multi-Agent Coordination](../../../delegation/tasks/completed/TASK-0091-align-tasks-with-tdd-enforcement.md)**
   - Format: Standard form with frequent status updates
   - Purpose: Track progress across 30 tasks in 5 groups
   - Pattern: Updated "Progress Summary" section at top as work progressed
   - Result: Clear visibility into 100% task completion across multiple sessions

---

## Tips

- **Tip 1: Choose the right format** - Short for daily updates, Standard for inter-agent handoffs, Detailed for completions or complex state.

- **Tip 2: Write for your future self** - You'll forget details in 2 weeks. Document enough that you (or another agent) can resume without re-learning.

- **Tip 3: Capture decisions immediately** - Don't wait until end of session. Write down technical decisions as you make them while context is fresh.

- **Tip 4: Keep agent-handoffs.json in sync** - The JSON should have a brief summary, with details_link pointing to full handoff document.

- **Tip 5: Document what didn't work** - Rejected approaches save future time. "We tried X, it failed because Y" prevents repeating mistakes.

- **Tip 6: Git state is critical** - Always document uncommitted changes, unpushed commits, and merge status. Git issues block resumption.

- **Tip 7: Prioritize next steps** - List in priority order, not random order. The next person should know exactly what to do first.

- **Tip 8: Blockers need action items** - Don't just say "blocked by X". Say "who can unblock this" and "by when".

- **Tip 9: Use templates consistently** - Don't invent new formats. Consistency helps readers quickly find information.

- **Tip 10: Link liberally** - Reference task files, ADRs, prior handoffs, test files. Make it easy to navigate to related context.

---

**Related:**
- [Concept: Context Management Basics](../../01-foundation/05-context-management-basics/concept.md)
- [Concept: Git Safety Practices](../../01-foundation/04-git-safety-practices/concept.md)
- [Example: Session Handoff for Multi-Session Task](../../examples/F5-session-handoff-multi-session.md)
- [Pattern: Handoff-Driven Development](../../01-foundation/05-context-management-basics/pattern.md)
- [Workflow: COMMIT-PROTOCOL.md](../../../.agent-context/workflows/COMMIT-PROTOCOL.md)
