# ASK-0023: Code Reviewer Agent Implementation

**Status**: Done
**Priority**: high
**Assigned To**: planner
**Estimated Effort**: 3-4 hours
**Created**: 2025-11-29

## Related Tasks

**Parent Task**: ASK-0022 (Code Review Workflow ADR)
**Depends On**: ADR-0014 (Code Review Workflow)
**Blocks**: ASK-0024 (Code Review Learning Tests)
**Related**: security-reviewer agent, test-runner agent

## Overview

Implement the code-reviewer agent and supporting infrastructure as documented in ADR-0014. This agent reviews completed implementations for quality, consistency, and adherence to project standards.

**Why Valuable**: Automates the first pass of code review, catching common issues before human review. Ensures consistent review quality and documents review decisions.

## Requirements

### Functional Requirements

1. Create `.claude/agents/code-reviewer.md` agent definition
2. Create review report template in `.agent-context/templates/`
3. Create reviews directory `.agent-context/reviews/`
4. Update planner agent to coordinate review workflow
5. Document review invocation in agent instructions

### Non-Functional Requirements

- Review should complete in < 10 minutes for typical tasks
- No new dependencies required
- Agent should use Serena for semantic code navigation
- Reviews should be deterministic (same code = same findings)

## Agent Definition

```yaml
---
name: code-reviewer
description: Reviews completed implementations for quality and standards adherence
model: claude-sonnet-4-20250514  # Fast, good for review
tools:
  - Read
  - Glob
  - Grep
  - Bash (git diff, git log only)
  - mcp__serena__* (semantic navigation)
  - TodoWrite
---
```

## Review Checklist

The agent should verify:

| Category | Checks |
|----------|--------|
| Acceptance Criteria | All criteria from task file met |
| Tests | Adequate coverage, meaningful assertions |
| Code Style | Consistent with project patterns |
| Architecture | Follows relevant ADRs |
| Documentation | Docstrings, comments where needed |
| Security | No obvious vulnerabilities |
| Performance | No obvious inefficiencies |

## Review Report Format

```markdown
# Review: ASK-XXXX - [Task Title]

**Reviewer**: code-reviewer
**Date**: YYYY-MM-DD
**Task File**: delegation/tasks/[folder]/ASK-XXXX.md
**Verdict**: APPROVED | CHANGES_REQUESTED | ESCALATE_TO_HUMAN

## Summary
[2-3 sentence summary of the review]

## Acceptance Criteria Verification
- [x] Criterion 1 - verified in file:line
- [x] Criterion 2 - verified in tests
- [ ] Criterion 3 - NOT MET: explanation

## Findings

### [CRITICAL|HIGH|MEDIUM|LOW]: Finding Title
**File**: `path/to/file.py:123`
**Issue**: Description of the problem
**Suggestion**: How to fix it
**ADR Reference**: ADR-XXXX (if applicable)

## Recommendations
[Optional improvements that don't block approval]

## Decision
[Explanation of verdict]
```

## Acceptance Criteria

### Must Have

- [ ] `.claude/agents/code-reviewer.md` created
- [ ] Agent can read task file and extract acceptance criteria
- [ ] Agent produces structured review report
- [ ] Agent uses Serena for code navigation
- [ ] Review verdicts: APPROVED, CHANGES_REQUESTED, ESCALATE_TO_HUMAN
- [ ] Reviews saved to `.agent-context/reviews/ASK-XXXX-review.md`

### Should Have

- [ ] Review template in `.agent-context/templates/review-template.md`
- [ ] Planner documentation updated for review workflow
- [ ] Finding severity levels (CRITICAL, HIGH, MEDIUM, LOW)
- [ ] Git diff analysis for changed files

### Could Have

- [ ] Automated review triggering (future)
- [ ] Review metrics collection
- [ ] Integration with GitHub PR comments (future)

## Implementation Plan

### Step 1: Create Agent Definition (45 min)

Create `.claude/agents/code-reviewer.md` with:
- Serena activation instructions
- Review checklist
- Report format template
- Verdict decision criteria

### Step 2: Create Review Infrastructure (30 min)

- Create `.agent-context/reviews/` directory
- Create `.agent-context/templates/review-template.md`
- Add `.gitkeep` to reviews directory

### Step 3: Update Planner (30 min)

Update `.claude/agents/planner.md` to document:
- When to invoke code-reviewer
- How to handle review verdicts
- Iteration limits (max 2 rounds)

### Step 4: Create Example Review (30 min)

- Document a sample review for reference
- Show each verdict type
- Demonstrate finding format

### Step 5: Test the Agent (60 min)

- Review a recently completed task
- Verify report format
- Test verdict logic

## Success Metrics

### Quantitative

- Agent completes review in < 10 minutes
- Report follows template 100%
- All acceptance criteria verifiable

### Qualitative

- Findings are actionable
- Verdicts are appropriate
- Integration with planner is smooth

## Time Estimate

| Phase | Time |
|-------|------|
| Create agent definition | 45 min |
| Create review infrastructure | 30 min |
| Update planner | 30 min |
| Create example review | 30 min |
| Test the agent | 60 min |
| Documentation | 15 min |
| **Total** | **3-4 hours** |

## References

- ADR-0014: Code Review Workflow (when created)
- `.claude/agents/security-reviewer.md` (similar pattern)
- `.claude/agents/test-runner.md` (similar pattern)

## Notes

- Start with conservative review (fewer false positives)
- Agent should explain reasoning for verdicts
- Consider caching review results by commit hash (future)

---

**Template Version**: 1.0.0
**Created**: 2025-11-29
