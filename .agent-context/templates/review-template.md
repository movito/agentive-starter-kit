# Review: ASK-XXXX - [Task Title]

**Reviewer**: code-reviewer
**Date**: YYYY-MM-DD
**Task File**: delegation/tasks/4-in-review/ASK-XXXX.md
**Verdict**: APPROVED | CHANGES_REQUESTED | ESCALATE_TO_HUMAN
**Round**: 1 | 2

## Summary

[2-3 sentence summary of what was implemented and your overall assessment. Be specific about what was done well and any concerns.]

## Acceptance Criteria Verification

Review each criterion from the task file:

- [x] **Criterion 1** - Verified in `path/to/file.py:42`
- [x] **Criterion 2** - Verified in `tests/test_feature.py`
- [ ] **Criterion 3** - NOT MET: [Explain why and what's missing]

## Code Quality Assessment

| Aspect | Rating | Notes |
|--------|--------|-------|
| Patterns | Good / Needs Work | [Does it follow existing project patterns?] |
| Testing | Good / Needs Work | [Are tests adequate and meaningful?] |
| Documentation | Good / Needs Work | [Are docstrings and comments present?] |
| Architecture | Good / Needs Work | [Does it follow relevant ADRs?] |

## Findings

List all issues found, categorized by severity:

### CRITICAL: [Finding Title]

**File**: `path/to/file.py:123`
**Issue**: [Clear description of the security vulnerability or critical bug]
**Suggestion**: [How to fix it]
**ADR Reference**: ADR-XXXX (if this violates an architectural decision)

### HIGH: [Finding Title]

**File**: `path/to/file.py:456`
**Issue**: [Description of missing requirement or broken functionality]
**Suggestion**: [How to fix it]

### MEDIUM: [Finding Title]

**File**: `path/to/file.py:789`
**Issue**: [Code quality or maintainability concern]
**Suggestion**: [How to improve]

### LOW: [Finding Title]

**File**: `path/to/file.py:101`
**Issue**: [Minor style issue or nice-to-have improvement]
**Suggestion**: [Optional improvement]

## Recommendations

[Optional improvements that don't block approval. These are nice-to-haves for future consideration.]

- Consider adding [X] for better [Y]
- Future improvement: [Z]

## Decision

**Verdict**: [APPROVED | CHANGES_REQUESTED | ESCALATE_TO_HUMAN]

**Rationale**: [Clear explanation of why this verdict was chosen]

---

### If CHANGES_REQUESTED:

**Required Changes** (must be addressed before re-review):

1. [ ] [Specific change 1 with file reference]
2. [ ] [Specific change 2 with file reference]
3. [ ] [Specific change 3 with file reference]

**Notes for Implementation Agent**:
[Any additional guidance for addressing the changes]

---

### If ESCALATE_TO_HUMAN:

**Reason for Escalation**: [Why human judgment is needed]

**Options for Human to Consider**:
1. [Option A with trade-offs]
2. [Option B with trade-offs]

**Reviewer Recommendation**: [Your recommendation if you have one]

---

### If APPROVED:

**Ready for**: Move task to `5-done`

**Commendations**: [What was done particularly well - optional but encouraged]

---

**Review completed**: YYYY-MM-DD HH:MM
**Next action**: [What happens next based on verdict]
