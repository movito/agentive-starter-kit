# Task Completion Protocol

**Purpose**: Standard process for completing implementation tasks
**Agent**: All agents that complete implementation tasks
**Last Updated**: 2025-11-01

---

## When to Use

- ✅ When all implementation work is complete
- ✅ Before handing off for review
- ✅ Before marking task as COMPLETE in `.kit/tasks/`

> **Enforced path**: the PR-readiness gates (CI, bots, threads,
> evaluator, review starter, task folder) are checked mechanically by
> `/preflight`, and `/wrap-up` finalizes the session. This protocol
> covers what those gates don't: deliverables, documentation, no
> regressions, and the handoff document.

---

## Completion Checklist

1. ✅ **All deliverables implemented** as specified in task file
2. ✅ **All tests passing** (or properly xfailed with justification)
3. ✅ **Code committed to git** with descriptive message
4. ✅ **No regressions introduced** (overall pass rate maintained or improved)
5. ✅ **Documentation updated** (README, CHANGELOG, ADRs if applicable)
6. ✅ **CI/CD passing** (GitHub Actions green)
7. ✅ **Handoff document created** (`.kit/context/<TASK-ID>-HANDOFF-*.md`)

---

## Handoff Document Format

### Filename:
```
.kit/context/<TASK-ID>-HANDOFF-<agent-type>.md
```

### Required Sections:

```markdown
## Task Summary
Brief description of the task and its purpose

## What Was Implemented
Detailed description of what you actually built/fixed

## Deliverables
- ✅ Deliverable 1 (with status/location)
- ✅ Deliverable 2
- ✅ Deliverable 3

## Test Results
- Before: [passing/total from the baseline run]
- After: [passing/total after your changes]
- New tests added: Z
- Regressions: None / List any

## Files Modified/Created
- path/to/file1.py (description)
- path/to/file2.py (description)
- tests/test_new_feature.py (NEW - Z tests)

## Commits
- abc1234 - feat: Add new feature
- def5678 - test: Add comprehensive tests
- ghi9012 - docs: Update README

## Technical Notes
Any important implementation details, design decisions, or caveats

## Known Issues (if any)
List any issues you discovered but didn't fix

## Next Steps (for receiving agent)
What should the next agent do with this?
```

---

## Workflow Steps

1. **Verify all deliverables complete** (check task file)
2. **Run full test suite**: `pytest tests/ -v`
3. **Review git status**: Ensure all changes committed
4. **Create handoff document** in `.kit/context/`
5. **Update `.kit/context/agent-handoffs.json`** with task completion
   — **on `main` only**: the planner is the file's single writer
   (KIT-0086); branch sessions never edit it, and `project move`
   skips it automatically off-main since KIT-0090 PR 1
6. **Stage and commit** the handoff (+ the JSON update when on main)
7. **Push to remote repository**
8. **Notify the user** (or the planner) with the PR link and status

---

## Best Practices

### ✅ DO:
- Be thorough - don't skip checklist items
- Include test metrics in handoff (before/after pass rates)
- Document any known issues or limitations honestly
- Provide clear next steps for the user or reviewing agent
- Update agent-handoffs.json status to "task_complete" (planner, on main — KIT-0086)

### ❌ DON'T:
- Don't mark task complete if tests are failing
- Don't skip handoff document (critical for coordination)
- Don't leave uncommitted changes
- Don't claim 100% completion if known issues exist

---

## Example Handoff Document

See existing handoffs for examples (finished tasks' handoffs live under
`.kit/context/archive/`; write new ones to the flat `.kit/context/`):
- `.kit/context/archive/ASK-0043-HANDOFF-feature-developer.md`
- `.kit/context/archive/ASK-0044-HANDOFF-feature-developer.md`

---

## Documentation

- **Quick Reference**: `CLAUDE.md`
- **Full Protocol**: This document
- **Handoff Examples**: `.kit/context/archive/*-HANDOFF-*.md`
- **Task Templates**: `.kit/templates/TASK-STARTER-TEMPLATE.md`

---

**Related Workflows**:
- [TESTING-WORKFLOW.md](./TESTING-WORKFLOW.md) - Verify tests before completion
- [COMMIT-PROTOCOL.md](./COMMIT-PROTOCOL.md) - Commit changes properly
- [Evaluation guidance](../../../.claude/skills/code-review-evaluator/SKILL.md) - For planners assigning tasks

## CHANGELOG discipline (KIT-0076 retro)

Any task whose PR changes user-visible behavior (features, removals,
CLI/output changes, doc restructures) adds its `[Unreleased]`
CHANGELOG entry **in the same PR**. At the 0.9.0 cut, seven merged
tasks had no entry and the release notes had to be reconstructed from
memory records — a release cut should be a rename of `[Unreleased]`,
not an archaeology session. Reviewers (bots and planner verification)
may treat a missing entry on a user-visible PR as a finding.
