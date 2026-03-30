# Task Completion Protocol

**Purpose**: Standard process for completing implementation tasks
**Agent**: All agents that complete implementation tasks
**Last Updated**: 2025-11-01

---

## When to Use

- ✅ When all implementation work is complete
- ✅ Before handing off to coordinator or other agent
- ✅ Before marking task as COMPLETE in `.kit/tasks/`

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
- Before: XXX/350 tests passing (XX.X%)
- After: YYY/350 tests passing (YY.Y%)
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
6. **Stage and commit** handoff + agent-handoffs.json update
7. **Push to remote repository**
8. **Notify coordinator** (or wait for coordinator to pick up)

---

## Best Practices

### ✅ DO:
- Be thorough - don't skip checklist items
- Include test metrics in handoff (before/after pass rates)
- Document any known issues or limitations honestly
- Provide clear next steps for coordinator/user
- Update agent-handoffs.json status to "task_complete"

### ❌ DON'T:
- Don't mark task complete if tests are failing
- Don't skip handoff document (critical for coordination)
- Don't leave uncommitted changes
- Don't claim 100% completion if known issues exist

---

## Example Handoff Document

See existing handoffs for examples:
- `.kit/context/ASK-0043-HANDOFF-feature-developer.md`
- `.kit/context/ASK-0044-HANDOFF-feature-developer.md`

---

## Documentation

- **Quick Reference**: `.kit/context/PROCEDURAL-KNOWLEDGE-INDEX.md`
- **Full Protocol**: This document
- **Handoff Examples**: `.kit/context/*-HANDOFF-*.md`
- **Task Templates**: `.kit/templates/TASK-STARTER-TEMPLATE.md`

---

**Related Workflows**:
- [TESTING-WORKFLOW.md](./TESTING-WORKFLOW.md) - Verify tests before completion
- [COMMIT-PROTOCOL.md](./COMMIT-PROTOCOL.md) - Commit changes properly
- [Evaluation Workflow](../../adversarial/docs/EVALUATION-WORKFLOW.md) - For coordinators assigning tasks
