# ADR-0014: Code Review Workflow

**Status**: Accepted

**Date**: 2025-11-29

**Deciders**: planner, User

## Context

### Problem Statement

Currently, completed tasks move directly from implementation to done after CI passes. While TDD and CI/CD catch functional issues, they don't verify:
- Code style and pattern consistency
- Architecture adherence (ADR compliance)
- Documentation completeness
- Maintainability concerns
- Non-functional requirements

```
CURRENT WORKFLOW (gap identified):
  Task → Implementation → CI passes → Done
                                ↑
                          No quality review here
```

Human code review is valuable but doesn't scale with agent-based development. We need an automated first-pass review that catches common issues before human attention is required.

### Forces at Play

**Technical Requirements:**
- Agents are stateless (no persistent conversation)
- Reviews must be structured and actionable
- Workflow must integrate with existing task management
- Review findings must reference specific code locations

**Constraints:**
- Agents cannot directly communicate (async only)
- Reviews must complete in reasonable time (< 10 minutes)
- False positives reduce trust in the system
- Cannot block all changes on review (need escape hatches)

**Assumptions:**
- CI has already verified tests pass
- Task specifications include acceptance criteria
- Code is accessible via semantic navigation (Serena)
- Most implementations are good-faith efforts by capable agents

## Decision

We will adopt **agent-based code review** with async file-based communication between implementation and review agents.

### Core Principles

1. **Complement, don't replace**: Agent review is first-pass; critical changes still need human review
2. **Actionable feedback**: Every finding must include file location and suggested fix
3. **Bounded iteration**: Maximum 2 review rounds to prevent infinite loops
4. **Proportional effort**: Simple changes get lightweight review

### Implementation Details

**The Review Workflow:**

```
                    ┌─────────────────────────────────────┐
                    │                                     │
                    ▼                                     │
┌──────────┐   ┌──────────────┐   ┌──────────────┐   ┌────┴─────┐
│ 2-todo   │ → │ 3-in-progress│ → │ 4-in-review  │ → │ 5-done   │
└──────────┘   └──────────────┘   └──────────────┘   └──────────┘
                      │                   │
                      │                   │ If CHANGES_REQUESTED
                      │                   │ (max 2 rounds)
                      └───────────────────┘
```

**Workflow State Transitions:**

| From | To | Trigger |
|------|-----|---------|
| 3-in-progress | 4-in-review | CI passes |
| 4-in-review | 5-done | Verdict: APPROVED |
| 4-in-review | 3-in-progress | Verdict: CHANGES_REQUESTED |
| 4-in-review | (user notified) | Verdict: ESCALATE_TO_HUMAN |

**Agent-to-Agent Communication Protocol:**

Since agents are stateless, they communicate via structured files:

```
Implementation Agent                    Review Agent
        │                                     │
        ├──→ Writes code                      │
        ├──→ Creates/updates handoff file     │
        │    (.agent-context/TASK-HANDOFF.md) │
        │                                     │
        │         ←── Reads code + handoff ───┤
        │         ←── Writes review report ───┤
        │             (.agent-context/reviews/ASK-XXXX-review.md)
        │                                     │
        │    (if CHANGES_REQUESTED)           │
        │                                     │
        ├──← Reads review feedback            │
        ├──→ Makes revisions                  │
        ├──→ Updates handoff (revision notes) │
        │                                     │
        │         ←── Re-reviews ─────────────┤
        │         ←── Updates report ─────────┤
```

**Handoff File Format:**

```markdown
# Task Handoff: ASK-XXXX

## Implementation Summary
[What was implemented and key decisions made]

## Files Changed
- `path/to/file.py` - [description]

## Testing Notes
- [How to verify the implementation]

## Revision History
- 2025-XX-XX: Initial implementation
- 2025-XX-XX: Addressed review feedback (round 1)
```

**Review Report Format:**

```markdown
# Review: ASK-XXXX - [Task Title]

**Reviewer**: code-reviewer
**Date**: YYYY-MM-DD
**Task File**: delegation/tasks/[folder]/ASK-XXXX.md
**Verdict**: APPROVED | CHANGES_REQUESTED | ESCALATE_TO_HUMAN
**Round**: 1 (of max 2)

## Summary
[2-3 sentence summary of the review]

## Acceptance Criteria Verification
- [x] Criterion 1 - verified in `file.py:42`
- [x] Criterion 2 - verified in tests
- [ ] Criterion 3 - NOT MET: [explanation]

## Findings

### [CRITICAL|HIGH|MEDIUM|LOW]: Finding Title
**File**: `path/to/file.py:123`
**Issue**: Description of the problem
**Suggestion**: How to fix it
**ADR Reference**: ADR-XXXX (if applicable)

[Additional findings...]

## Recommendations
[Optional improvements that don't block approval]

## Decision
APPROVED: [Rationale]
- OR -
CHANGES_REQUESTED: [What must be fixed]
- OR -
ESCALATE_TO_HUMAN: [Why human judgment needed]
```

**Review Verdict Criteria:**

| Verdict | Criteria |
|---------|----------|
| APPROVED | All acceptance criteria met, no CRITICAL/HIGH findings |
| CHANGES_REQUESTED | CRITICAL/HIGH findings, or acceptance criteria not met |
| ESCALATE_TO_HUMAN | Architectural concerns, security issues, or round 2 still has issues |

**Finding Severity Levels:**

| Severity | Definition | Blocks Approval |
|----------|------------|-----------------|
| CRITICAL | Security vulnerability, data loss risk | Yes |
| HIGH | Broken functionality, missing requirements | Yes |
| MEDIUM | Code quality, maintainability issues | No |
| LOW | Style, documentation, minor improvements | No |

**Iteration Limits:**

```
Round 1: Initial review
    ↓ (if CHANGES_REQUESTED)
Round 2: Re-review after revisions
    ↓ (if still issues)
ESCALATE_TO_HUMAN (no round 3)
```

Rationale: Prevents infinite back-and-forth. If implementation and reviewer can't agree after 2 rounds, human judgment is needed.

**Skip Conditions:**

Review may be skipped for:

| Condition | Justification |
|-----------|---------------|
| Documentation-only changes | Low risk, high overhead ratio |
| Changes < 20 lines | Trivial scope |
| Task marked `skip-review: true` | Explicit opt-out |
| Urgent hotfix (with human approval) | Time-sensitive |

### Integration with Existing Agents

| Agent | Role in Review Workflow |
|-------|------------------------|
| **planner** | Coordinates workflow, moves tasks between folders |
| **ci-checker** | Verifies CI passed (prerequisite to review) |
| **code-reviewer** | Performs the review, writes report |
| **feature-developer** | Reads feedback, makes revisions |
| **security-reviewer** | Deep security review (optional, for sensitive changes) |

### File Locations

```
.agent-context/
├── reviews/
│   ├── ASK-0021-review.md
│   ├── ASK-0022-review.md
│   └── ...
├── templates/
│   └── review-template.md
└── [TASK-ID]-HANDOFF-[agent].md
```

## Consequences

### Positive

- ✅ **Consistent quality**: Every task gets reviewed before completion
- ✅ **Faster feedback**: Issues caught before human review
- ✅ **Documented decisions**: Review reports create audit trail
- ✅ **Pattern enforcement**: ADR adherence verified systematically
- ✅ **Scalable**: Agents can review many tasks without fatigue

### Negative

- ⚠️ **Workflow overhead**: Additional step between implementation and done
- ⚠️ **False positives**: Risk of flagging non-issues, eroding trust
- ⚠️ **Iteration cost**: CHANGES_REQUESTED triggers another implementation round
- ⚠️ **Agent prompt maintenance**: Review agent needs calibration over time

### Neutral

- 📊 **New artifact type**: Review reports accumulate in repository
- 📊 **Coordination complexity**: Planner must track review state
- 📊 **Learning curve**: Team must understand when to escalate vs iterate

## Alternatives Considered

### Alternative 1: Human-Only Review

**Description**: All code reviewed by humans, no agent involvement

**Rejected because**:
- ❌ Doesn't scale with agent-generated code volume
- ❌ Humans are slow for repetitive checks (style, patterns)
- ❌ Inconsistent application of standards
- ❌ Review bottleneck in development flow

### Alternative 2: Post-Merge Review

**Description**: Review happens after merge to main, fix issues later

**Rejected because**:
- ❌ Technical debt accumulates
- ❌ Harder to fix issues once merged
- ❌ No gate before completion
- ❌ Contradicts "shift-left" quality principles

### Alternative 3: Inline Review During Implementation

**Description**: Review agent comments on code as it's being written

**Rejected because**:
- ❌ Agents are stateless - can't maintain review context
- ❌ Interrupts implementation flow
- ❌ Complex coordination between agents
- ❌ Partial code harder to review than complete implementation

### Alternative 4: Automated Linting Only

**Description**: Use static analysis tools (ruff, mypy) instead of agent review

**Rejected because**:
- ❌ Linting catches syntax/style, not semantic issues
- ❌ Can't verify acceptance criteria
- ❌ No ADR adherence checking
- ❌ Missing documentation review
- ✅ (But: linting should complement agent review, not replace it)

## Real-World Results

*To be updated after ASK-0024 (Learning Tests) is completed*

**Before this pattern:**
- Tasks moved directly to done after CI
- Quality issues discovered later by humans
- Inconsistent adherence to ADRs
- No documentation of review decisions

**After this pattern:**
- [Results pending]

## Related Decisions

- ADR-0006: Agent Session Initialization (agent startup pattern)
- ADR-0006: Adversarial Workflow (similar evaluation pattern, pre-implementation)
- ADR-0009: Logging & Observability (review may check logging adherence)

## References

- Task file: `delegation/tasks/2-todo/ASK-0022-code-review-workflow-adr.md`
- Implementation task: `delegation/tasks/1-backlog/ASK-0023-code-reviewer-agent-implementation.md`
- Learning tests: `delegation/tasks/1-backlog/ASK-0024-code-review-learning-tests.md`
- Existing agent: `.claude/agents/security-reviewer.md` (similar pattern)

## Revision History

- 2025-11-29: Initial decision (Accepted)
  - Documented agent-based review workflow
  - Defined communication protocol and report format
  - Established iteration limits and skip conditions

---

**Template Version**: 1.1.0
**Last Updated**: 2025-11-29
**Project**: agentive-starter-kit
