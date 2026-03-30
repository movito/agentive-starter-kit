# ASK-0022: Code Review Workflow ADR

**Status**: Done
**Priority**: high
**Assigned To**: planner
**Estimated Effort**: 2-3 hours
**Created**: 2025-11-29

## Related Tasks

**Parent Task**: None (New capability)
**Depends On**: None
**Blocks**: ASK-0023 (Code Reviewer Agent Implementation)
**Related**: ASK-0006 (Adversarial Workflow ADR)

## Overview

Document the Code Review Workflow architecture for the agentive-starter-kit. This ADR establishes a pattern for agent-based code review, enabling quality assurance between task completion and final acceptance.

**Why Valuable**: Currently, completed tasks go directly to done after CI passes. Adding an agent-based review step catches issues that tests miss: code style, architecture adherence, documentation gaps, and maintainability concerns.

## Key Concepts to Document

### Workflow States

```
2-todo
   ↓
3-in-progress (implementation)
   ↓
CI passes
   ↓
4-in-review (NEW: agent review)
   ↓
5-done (or back to 3-in-progress if issues)
```

### Agent-to-Agent Communication

Agents communicate asynchronously via files:

```
Implementation Agent          Review Agent
        │                          │
        ├──→ code + handoff        │
        │                          │
        │    ←── review report ────┤
        │                          │
        ├──→ revisions             │
        │                          │
        │    ←── APPROVED ─────────┤
```

### Review Report Structure

```markdown
# Review: ASK-XXXX

**Verdict**: APPROVED | CHANGES_REQUESTED | ESCALATE_TO_HUMAN

## Checklist
- [ ] Acceptance criteria met
- [ ] Tests adequate
- [ ] Follows project patterns
- [ ] ADR adherence
- [ ] Documentation complete

## Findings
### SEVERITY: Title
**File**: path:line
**Issue**: Description
**Suggestion**: Fix
```

### Review Verdicts

| Verdict | Action |
|---------|--------|
| APPROVED | Move to 5-done |
| CHANGES_REQUESTED | Back to 3-in-progress with feedback |
| ESCALATE_TO_HUMAN | Notify user, await decision |

### Iteration Limits

- Max 2 review rounds
- After 2 CHANGES_REQUESTED: escalate to human
- Prevents infinite back-and-forth

### Skip Conditions

Review can be skipped for:
- Trivial changes (< 50 lines, documentation only)
- Urgent hotfixes (with human approval)
- Tasks marked `skip-review: true`

## Acceptance Criteria

### Must Have

- [ ] ADR created following project template
- [ ] Documents workflow state transitions
- [ ] Defines agent communication protocol
- [ ] Specifies review report format
- [ ] Lists review verdicts and actions
- [ ] Documents iteration limits

### Should Have

- [ ] Skip conditions defined
- [ ] Integration with existing agents (ci-checker, test-runner)
- [ ] Escalation protocol
- [ ] Examples of review reports

### Could Have

- [ ] Metrics for review effectiveness
- [ ] Review categories (security, performance, style)

## Implementation Notes

### Files to Create

- `docs/decisions/adr/ADR-0014-code-review-workflow.md`

### Integration Points

- Planner coordinates review workflow
- ci-checker verifies CI before review
- Review reports in `.agent-context/reviews/`
- agent-handoffs.json tracks review status

### Comparison to Evaluation Workflow

| Aspect | Evaluation (Pre-impl) | Review (Post-impl) |
|--------|----------------------|-------------------|
| When | Before implementation | After implementation |
| What | Task specification | Actual code |
| Who | GPT-4o Evaluator | Code Reviewer Agent |
| Output | Plan feedback | Code feedback |

## References

- ADR-0006: Adversarial Workflow (evaluation pattern)
- `.adversarial/docs/EVALUATION-WORKFLOW.md`
- Existing: security-reviewer agent

## Notes

- This pattern mirrors human PR review workflows
- Agent review complements (doesn't replace) human review for critical changes
- Consider future: automated PR creation with review comments

---

**Template Version**: 1.0.0
**Created**: 2025-11-29
