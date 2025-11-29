# KIT-ADR-0004: Adversarial Workflow Integration for Quality Development

**Status**: Accepted

**Date**: 2025-11-28

**Deciders**: planner, coordinator

## Context

### Problem Statement

Complex technical tasks in agentic systems are prone to **phantom work** - where implementations appear complete but contain zero actual code changes, wasting hours before discovery.

This occurs because AI agents can:
- Misunderstand requirements and implement the wrong thing
- Experience silent tool failures without realizing it
- Claim completion based on intent rather than verified results

### Forces at Play

**Technical Requirements:**
- Catch design flaws before implementation begins
- Verify agent understanding matches actual requirements
- Prevent wasted implementation time on wrong approaches

**Constraints:**
- Must not slow down simple, well-understood tasks
- External review should be cost-effective (< $0.10 per task)
- Process must integrate with existing agent workflows

**Assumptions:**
- Different AI models (Claude, GPT-4o) have complementary strengths
- External perspective catches blind spots that self-review misses
- Investigation before implementation prevents most phantom work

### Observed Phantom Work Example

**TASK-2025-014** (from thematic-cuts project):
- **Claimed**: "Complete - All 6 tests fixed"
- **Reality**: 0 code changes, only documentation renamed
- **Evidence**: `git diff` showed no modifications to target files
- **Impact**: 4 hours wasted before audit discovered failure

**Root Cause**: Tool execution failures combined with lack of verification.

## Decision

We adopt **investigation-first development with external GPT-4o evaluation** to prevent phantom work and catch design flaws early.

### Core Principles

1. **Never implement without investigation** - Understand the codebase and requirements before writing code
2. **External evaluation** - Use GPT-4o (different model than implementer) to validate plans
3. **Prevent phantom work** - Catch misunderstandings before coding begins
4. **Iterative refinement** - Maximum 2-3 evaluation rounds, then proceed with best judgment

### Implementation Overview

```
Phase 0: Investigation (understand before implementing)
   ↓
Phase 1: Evaluator Review (external GPT-4o validation)
   ↓
Phase 2+: Implementation (with validated understanding)
```

**Workflow Commands:**
```bash
# Evaluate implementation plans
adversarial evaluate <task-file>

# Proofread documentation/teaching content
adversarial proofread <doc-file>
```

**For detailed operational guidance, see:** `.adversarial/docs/EVALUATION-WORKFLOW.md`

### When to Use Evaluation

| Task Type | Evaluate? | Reason |
|-----------|-----------|--------|
| Complex tasks (>500 lines) | Yes | High risk of design flaws |
| Architectural decisions | Yes | Significant downstream impact |
| Critical dependencies | Yes | Failure would block other work |
| Simple bug fixes | No | Obvious solution, low risk |
| Trivial changes (<100 lines) | No | Overhead exceeds benefit |

## Consequences

### Positive

- **Prevents phantom work**: External review catches zero-implementation claims
- **Accurate estimates**: Investigation reveals true scope (87% time savings observed)
- **Higher confidence**: Evaluator approval provides independent validation
- **Evidence-based**: Decisions grounded in code inspection, not assumptions
- **Cost-effective**: ~$0.04-0.08 per evaluation, saves hours of rework

### Negative

- **Upfront time**: Investigation phase adds 1-2 hours for complex tasks
- **Process overhead**: More steps than direct implementation
- **API cost**: Evaluator review costs ~$0.04-0.08 per task (minimal)

### Neutral

- **Requires discipline**: Team must follow process consistently
- **Judgment needed**: Knowing when to evaluate vs. skip requires experience

## Alternatives Considered

### Alternative 1: Code-First Development

**Description**: Implement immediately, fix issues as discovered.

**Rejected because**:
- High phantom work risk - agents may not realize tool failures
- Wasted implementation time on wrong approaches
- Design flaws discovered late are expensive to fix

### Alternative 2: Manual Review Only

**Description**: Human reviews all plans before implementation.

**Rejected because**:
- Slower than automated evaluation
- Human availability becomes bottleneck
- AI evaluator catches different issues than humans

### Alternative 3: Same-Model Self-Review

**Description**: Have Claude review its own plans.

**Rejected because**:
- Same blind spots as original author
- External perspective (GPT-4o) catches different issues
- Multi-model collaboration provides better coverage

## Real-World Results

**TASK-2025-017** (Semantic Parser, from thematic-cuts):
- **Original estimate**: 2-3 weeks (16-24 days)
- **Investigation finding**: 90%+ complete, only 7 minor bugs
- **Actual duration**: 3 hours (1.5h investigation, 1.5h implementation)
- **Time savings**: 87%
- **Test results**: 20/20 tests passing (100%)
- **Evaluator cost**: $0.04

**Methodology**: Metrics from production usage on thematic-cuts project, validated through actual task execution and git history.

## Related Decisions

- **KIT-ADR-0002**: Serena MCP Integration - Enables efficient code investigation
- **Source**: thematic-cuts KIT-ADR-0011 (original implementation)

## References

### Infrastructure

- **Operational Guide**: `.adversarial/docs/EVALUATION-WORKFLOW.md` (comprehensive how-to)
- **Scripts**: `.adversarial/scripts/evaluate_plan.sh`, `proofread_content.sh`
- **Configuration**: `.adversarial/config.yml`

### External

- **Aider CLI**: https://aider.chat (GPT-4o integration tool)
- **OpenAI API**: https://platform.openai.com (evaluator model)

### Source Documentation

- **thematic-cuts KIT-ADR-0011**: Original adversarial workflow decision
- **adversarial-workflow package**: PyPI package for CLI tools

## Revision History

- 2025-11-28: Initial decision for agentive-starter-kit (Accepted)
- Adapted from thematic-cuts KIT-ADR-0011 (2025-10-17)

---

**Template Version**: 1.1.0
**Last Updated**: 2025-11-28
**Project**: agentive-starter-kit
