# Code Review Workflow - Lessons Learned

**Date**: 2025-11-29
**Source**: ASK-0024 Learning Tests
**Purpose**: Document insights for continuous improvement

## Key Insights

### 1. Acceptance Criteria Are Critical

The task file's acceptance criteria provide the primary verification targets for review. Without clear, measurable criteria, review becomes subjective.

**Recommendation**: Ensure all tasks have explicit, verifiable acceptance criteria before implementation begins.

### 2. Severity Classification Works

The 4-level severity system (CRITICAL, HIGH, MEDIUM, LOW) effectively separates blocking issues from improvements:

| Level | Definition | Action |
|-------|------------|--------|
| CRITICAL | Security, data loss | Block immediately |
| HIGH | Missing requirements | Block, require fix |
| MEDIUM | Quality concerns | Note, don't block |
| LOW | Nice-to-haves | Suggest only |

**Recommendation**: Keep this classification. Consider adding examples to agent prompt.

### 3. File:Line References Are Essential

Findings without specific locations are not actionable. Every issue must reference:
- Exact file path
- Line number (or range)
- Suggested fix

**Recommendation**: Make this a hard requirement in review template.

### 4. Review Time Needs Monitoring

Test 1 took ~15 minutes vs 10-minute target. For simple implementations, this is acceptable, but larger reviews could become bottlenecks.

**Recommendation**:
- Add time-boxing guidance to agent prompt
- Consider tiered review depth based on change size

### 5. Automation Opportunities Exist

Several checks could be automated:
- Test count verification
- Coverage metrics
- Lint/style compliance
- ADR reference validation

**Recommendation**: Create tooling roadmap for review automation.

## Process Refinements

### Before Review

1. **Verify CI passes** - Don't review code that doesn't build
2. **Check handoff file exists** - Context matters
3. **Identify change scope** - Use git diff

### During Review

1. **Start with acceptance criteria** - Primary focus
2. **Check test coverage** - Adequate tests?
3. **Review code quality** - Patterns, style
4. **Verify documentation** - Docstrings, comments
5. **Scan for security** - Basic vulnerability check

### After Review

1. **Write structured report** - Use template
2. **Classify all findings** - Severity matters
3. **State clear verdict** - No ambiguity
4. **Provide next steps** - Actionable guidance

## Agent Prompt Improvements

Based on learning tests, these improvements should be applied to `.claude/agents/code-reviewer.md`:

### Add: Early Git Diff Step

```markdown
### Step 0: Identify Change Scope
```bash
git log --oneline -5  # Recent commits
git diff HEAD~N --stat  # Changed files and lines
```
Use this to focus review on changed code.
```

### Add: Time-Boxing Guidance

```markdown
## Time Management

Target review times by scope:
- Small (< 100 lines): 5-10 minutes
- Medium (100-500 lines): 10-20 minutes
- Large (> 500 lines): 20-30 minutes, consider splitting

If review exceeds target, note in report and continue.
```

### Add: Severity Examples

```markdown
## Finding Examples by Severity

**CRITICAL**:
- Hardcoded API key in source
- SQL injection vulnerability
- Unhandled exception causing data loss

**HIGH**:
- Acceptance criterion not met
- Test file missing for new feature
- Breaking change without migration

**MEDIUM**:
- Missing docstring on public function
- Code duplication (DRY violation)
- Inconsistent naming convention

**LOW**:
- Import order could be optimized
- Consider more descriptive variable name
- Optional: add type hints
```

## Future Calibration

### Quarterly Review

Every quarter, review the last 10-20 code reviews and assess:
- False positive rate (findings that weren't real issues)
- False negative rate (issues missed that were found later)
- Review time trends
- Common finding patterns

### Feedback Loop

1. Implementation agents can flag unclear feedback
2. Planner tracks review-to-fix time
3. Escalations to human are reviewed for patterns

## Metrics to Track

| Metric | How to Measure | Target |
|--------|----------------|--------|
| Review time | Timestamp diff | < 15 min average |
| False positive rate | Post-review feedback | < 20% |
| Rounds to approval | Review count per task | < 2 average |
| Escalation rate | ESCALATE_TO_HUMAN count | < 10% |

## Summary

The code review workflow is viable and adds value. Key success factors:
1. Clear acceptance criteria in task files
2. Structured review process with checklist
3. Severity-based finding classification
4. Actionable feedback with file:line references

Next phase: Apply agent prompt improvements and run full workflow test with real implementation.

---

**Document Version**: 1.0.0
**Created**: 2025-11-29
**Task Reference**: ASK-0024
