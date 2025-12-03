# Review Starter: [TASK-ID]

**Task**: [TASK-ID] - [Task Title]
**Task File**: `delegation/tasks/4-in-review/[TASK-ID]-*.md`
**Branch**: [feature-branch] → main
**PR**: [URL if applicable]

## Implementation Summary

[2-3 sentences describing what was built and the approach taken]

- [Key feature/change 1]
- [Key feature/change 2]
- [Key decision or tradeoff made]

## Files Changed

### New Files
- `path/to/new/file.py` - [brief description]

### Modified Files
- `path/to/modified/file.py` - [what changed]

### Deleted Files
- `path/to/deleted/file.py` - [why removed]

## Test Results

```
[Paste test output summary]
- X tests passing
- Y% coverage (if applicable)
```

## Areas for Review Focus

[Guide the reviewer to tricky or important areas]

1. **[Area 1]**: [Why it needs attention - e.g., "Complex async logic in X"]
2. **[Area 2]**: [Potential concern - e.g., "Edge case handling in Y"]
3. **[Area 3]**: [Architecture question - e.g., "Is this the right pattern for Z?"]

## Related Documentation

- **Task file**: `delegation/tasks/4-in-review/[TASK-ID]-*.md`
- **ADRs**: [List relevant ADR numbers, e.g., ADR-0001, ADR-0005]
- **Handoff**: `.agent-context/[TASK-ID]-HANDOFF-*.md` (if exists)

## Pre-Review Checklist (Implementation Agent)

Before requesting review, verify:

- [ ] All acceptance criteria from task file are implemented
- [ ] Tests written and passing
- [ ] CI passes (`/check-ci` or `./scripts/verify-ci.sh`)
- [ ] Task moved to `4-in-review/`
- [ ] No debug code or console.logs left behind
- [ ] Docstrings for public APIs

---

**Ready for code-reviewer agent in new tab**

To start review:
1. Open new Claude Code tab
2. Run: `agents/launch code-reviewer`
3. Reviewer will auto-detect this starter file
