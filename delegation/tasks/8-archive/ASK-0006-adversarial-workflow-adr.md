# ASK-0006: Adversarial Workflow Integration ADR

**Status**: Done
**Priority**: high
**Assigned To**: planner
**Estimated Effort**: 1-2 hours
**Created**: 2025-11-28
**Revised**: 2025-11-28 (scope clarification)

## Related Tasks

**Parent Task**: None (ADR Migration - Tier 1)
**Depends On**: None
**Blocks**: None
**Related**: ASK-0007 (Test Infrastructure)

## Overview

Create ADR-0004 documenting the **architectural decision** to adopt investigation-first development with adversarial evaluation. This ADR captures the "why" behind our approach to preventing phantom work in agentic systems.

**Source**: `thematic-cuts/docs/decisions/adr/ADR-0011-adversarial-workflow-integration.md`

**Why Essential**: This pattern has demonstrated 87% time savings in practice (3 hours vs 2-3 weeks on TASK-2025-017). It prevents agents from implementing features that don't match requirements.

## Scope Boundaries

### ADR-0004 Scope (This Task)

The ADR documents the **decision and rationale**:

| ADR Covers | Description |
|------------|-------------|
| Problem statement | Phantom work in agentic systems |
| Decision | Adopt investigation-first + external evaluation |
| Core principles | Why this approach works |
| Alternatives considered | Code-first (anti-pattern), manual review only |
| Consequences | Trade-offs, costs, benefits |
| Real-world metrics | 87% time savings, $0.04-0.08 per evaluation |

### Already Documented (DO NOT DUPLICATE)

The operational guide `.adversarial/docs/EVALUATION-WORKFLOW.md` (600+ lines) already covers:

| Existing Documentation | Location |
|----------------------|----------|
| Step-by-step workflows | EVALUATION-WORKFLOW.md §Plan Evaluation Workflow |
| When to use evaluate vs proofread | EVALUATION-WORKFLOW.md §Two Modes |
| Evaluation criteria | EVALUATION-WORKFLOW.md §Evaluation Criteria |
| Iteration guidance | EVALUATION-WORKFLOW.md §Iteration Guidance |
| Best practices | EVALUATION-WORKFLOW.md §Best Practices |
| Known issues | EVALUATION-WORKFLOW.md §Known Issues |

**Key Principle**: ADR-0004 should **reference** EVALUATION-WORKFLOW.md for operational details, not duplicate them.

## Key Concepts for ADR

### 1. The Phantom Work Problem

```
Traditional Approach (Code-First):
  Agent receives task → Implements immediately → Claims complete

  Problem: Agent may misunderstand requirements, implement wrong thing,
           or experience tool failures without realizing it.

  Example: TASK-2025-014 claimed "6 tests fixed" but git diff showed
           zero code changes. 4 hours wasted before discovery.
```

### 2. The Solution: Investigation-First Development

```
Investigation-First Approach:
  Phase 0: Investigation (understand before implementing)
     ↓
  Phase 1: Evaluator Review (external GPT-4o validation)
     ↓
  Phase 2+: Implementation (with validated understanding)
```

### 3. Core Principles

1. **Never implement without investigation** - Understand the codebase first
2. **External evaluation** - Use GPT-4o (different model) to validate plans
3. **Prevent phantom work** - Catch misunderstandings before coding
4. **Iterative refinement** - Max 2-3 evaluation rounds, then proceed

## Requirements

### Functional Requirements

1. Create ADR-0004 following project template (`docs/decisions/adr/TEMPLATE-FOR-ADR-FILES.md`)
2. Document the phantom work problem and investigation-first solution
3. Include alternatives considered (code-first anti-pattern)
4. Reference existing infrastructure (don't duplicate operational docs)
5. Include real-world metrics demonstrating value

### Non-Functional Requirements

- ADR follows project template structure
- Clear separation from operational documentation
- Links to `.adversarial/docs/EVALUATION-WORKFLOW.md` for operational details

## Acceptance Criteria

### Must Have

- [ ] ADR-0004 created at `docs/decisions/adr/ADR-0004-adversarial-workflow-integration.md`
- [ ] Follows project ADR template structure
- [ ] Documents phantom work problem with concrete example
- [ ] Explains investigation-first solution and core principles
- [ ] Lists alternatives considered (code-first anti-pattern)
- [ ] Documents consequences (positive, negative, neutral)
- [ ] References EVALUATION-WORKFLOW.md for operational details (no duplication)

### Should Have

- [ ] Real-world metrics (87% time savings, cost per evaluation)
- [ ] Guidance on when evaluation is worthwhile vs. skip (brief, reference operational docs)
- [ ] Related decisions section linking to other ADRs

### Should NOT Have

- [ ] ❌ Step-by-step workflow instructions (already in EVALUATION-WORKFLOW.md)
- [ ] ❌ Detailed evaluation criteria (already documented)
- [ ] ❌ Known issues and workarounds (already documented)

## Implementation Plan

### Step 1: Review Existing Materials (15 min)

1. Read thematic-cuts ADR-0011 (already reviewed, available at `~/Github/thematic-cuts/docs/decisions/adr/ADR-0011-adversarial-workflow-integration.md`)
2. Confirm scope boundaries with EVALUATION-WORKFLOW.md

### Step 2: Create ADR-0004 (45-60 min)

Create `docs/decisions/adr/ADR-0004-adversarial-workflow-integration.md` with:

**Context Section:**
- Problem: Phantom work in agentic systems
- Forces: Tool failures, misunderstandings, wasted implementation time
- Example: TASK-2025-014 phantom work incident

**Decision Section:**
- Adopt investigation-first development with external GPT-4o evaluation
- Core principles (4 principles listed above)
- Brief implementation overview (reference operational docs for details)

**Consequences Section:**
- Positive: 87% time savings, catches design flaws, prevents phantom work
- Negative: Upfront investigation time (1-2 hours), API cost ($0.04-0.08)
- Neutral: Requires discipline to follow process

**Alternatives Considered:**
- Code-first approach (rejected: phantom work risk)
- Manual review only (rejected: slower, no external perspective)
- Different evaluator model (considered: GPT-4o chosen for cost/quality balance)

**References Section:**
- Link to `.adversarial/docs/EVALUATION-WORKFLOW.md`
- Link to `.adversarial/` infrastructure
- Link to source thematic-cuts ADR-0011

### Step 3: Review and Finalize (15-30 min)

1. Verify no duplication with EVALUATION-WORKFLOW.md
2. Ensure all acceptance criteria met
3. Check ADR template compliance

## Success Metrics

### Quantitative

- ADR-0004 created and follows template
- < 200 lines (focused on decision, not operational details)
- All "Must Have" acceptance criteria met

### Qualitative

- Clear separation of concerns: ADR = decision, EVALUATION-WORKFLOW.md = operations
- Agents understand "why" from ADR, "how" from operational docs
- New projects can understand the decision rationale

## Time Estimate

| Phase | Time |
|-------|------|
| Review existing materials | 15 min |
| Create ADR-0004 | 45-60 min |
| Review and finalize | 15-30 min |
| **Total** | **1-2 hours** |

## References

- **Source ADR**: `~/Github/thematic-cuts/docs/decisions/adr/ADR-0011-adversarial-workflow-integration.md`
- **Operational Guide**: `.adversarial/docs/EVALUATION-WORKFLOW.md` (600+ lines)
- **ADR Template**: `docs/decisions/adr/TEMPLATE-FOR-ADR-FILES.md`
- **Existing Infrastructure**: `.adversarial/scripts/`, `.adversarial/config.yml.template`

## Notes

- This is a documentation task, not implementation
- The adversarial workflow infrastructure already exists in the starter-kit
- **Key Focus**: Document the decision rationale, not duplicate operational guidance
- Revised 2025-11-28 to clarify scope boundaries after review

### Evaluator Feedback Addressed (2025-11-28)

**Source of Truth Hierarchy:**
- ADR-0004 is authoritative for the *decision* (why we adopted this approach)
- EVALUATION-WORKFLOW.md is authoritative for *operations* (how to use it)
- If discrepancies arise, update the appropriate document based on this hierarchy

**Metrics Verification:**
- Real-world metrics (87% time savings, $0.04 cost) come from thematic-cuts ADR-0011
- These are production-validated metrics from actual task execution (TASK-2025-017)
- Source ADR available at: `~/Github/thematic-cuts/docs/decisions/adr/ADR-0011-adversarial-workflow-integration.md`

**File Path Specified:**
- Output: `docs/decisions/adr/ADR-0004-adversarial-workflow-integration.md`

---

**Template Version**: 1.0.0
**Created**: 2025-11-28
**Revised**: 2025-11-28
