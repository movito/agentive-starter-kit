# ASK-0024: Code Review Learning Tests

**Status**: Done
**Priority**: medium
**Assigned To**: planner
**Estimated Effort**: 2-3 hours
**Created**: 2025-11-29

## Related Tasks

**Parent Task**: ASK-0023 (Code Reviewer Agent Implementation)
**Depends On**: ASK-0023 (agent must exist first)
**Blocks**: None
**Related**: ASK-0006 (Adversarial Workflow - similar learning phase)

## Overview

Run a series of controlled tests with the code-reviewer agent to validate the workflow, calibrate review quality, and document lessons learned. This learning phase ensures the review process is effective before full adoption.

**Why Valuable**: New agent workflows need calibration. Testing on known cases helps identify false positives, missed issues, and workflow friction before the process becomes standard.

## Test Strategy

### Test Categories

| Category | Purpose | Tasks to Review |
|----------|---------|-----------------|
| Known Good | Verify APPROVED verdict | ASK-0021 (already verified) |
| Known Issues | Verify findings detected | Synthetic test case |
| Edge Cases | Test verdict boundaries | Small/large changes |
| Workflow | Test full cycle | New task end-to-end |

### Test Cases

#### Test 1: Review Known-Good Implementation

**Target**: ASK-0021 (Logging Infrastructure)
**Expected Verdict**: APPROVED
**Purpose**: Baseline for good implementation

Questions to answer:
- Does the agent find the right files?
- Are acceptance criteria correctly verified?
- Is the report well-structured?

#### Test 2: Review with Intentional Issues

**Target**: Create synthetic task with known issues
**Expected Verdict**: CHANGES_REQUESTED
**Purpose**: Verify issue detection

Intentional issues to plant:
- Missing docstring
- Unused import
- Test without assertion
- Inconsistent naming

Questions to answer:
- Are issues correctly identified?
- Are suggestions actionable?
- Is severity appropriate?

#### Test 3: Edge Case - Trivial Change

**Target**: Documentation-only change (< 20 lines)
**Expected Verdict**: APPROVED (quick review)
**Purpose**: Verify lightweight review path

Questions to answer:
- Is review proportional to change size?
- Are skip conditions working?

#### Test 4: Edge Case - Large Change

**Target**: Multi-file implementation
**Expected Verdict**: Varies
**Purpose**: Test scalability

Questions to answer:
- Does agent handle large diffs?
- Is review time acceptable?
- Are cross-file issues detected?

#### Test 5: Full Workflow Cycle

**Target**: New small task, end-to-end
**Expected**: Complete workflow with revisions
**Purpose**: Test agent-to-agent handoff

Workflow to test:
1. Planner creates task
2. Feature-developer implements
3. CI passes
4. Code-reviewer reviews
5. If CHANGES_REQUESTED: developer revises
6. Re-review
7. APPROVED → done

Questions to answer:
- Is handoff file communication clear?
- Are revision instructions actionable?
- How many rounds needed?

## Metrics to Collect

### Quantitative

| Metric | Target | Notes |
|--------|--------|-------|
| Review time | < 10 min | Per review |
| False positive rate | < 20% | Findings that aren't issues |
| False negative rate | < 10% | Missed real issues |
| Rounds to approval | < 2 avg | For good implementations |

### Qualitative

- Report clarity and actionability
- Agent reasoning quality
- Workflow friction points
- Human intervention frequency

## Acceptance Criteria

### Must Have

- [ ] Test 1 (known good) completed and documented
- [ ] Test 2 (intentional issues) completed and documented
- [ ] Test 5 (full workflow) completed and documented
- [ ] Metrics collected for all tests
- [ ] Lessons learned documented

### Should Have

- [ ] Test 3 (trivial change) completed
- [ ] Test 4 (large change) completed
- [ ] Agent prompt improvements identified
- [ ] Workflow friction points documented

### Could Have

- [ ] Automated test harness for future validation
- [ ] Comparison with human review findings

## Deliverables

### 1. Test Results Document

`.agent-context/2025-XX-XX-code-review-test-results.md`:
- Each test case with results
- Metrics summary
- Pass/fail for each test

### 2. Lessons Learned

`.agent-context/2025-XX-XX-code-review-lessons-learned.md`:
- What worked well
- What needs improvement
- Agent prompt adjustments needed
- Workflow changes recommended

### 3. Agent Prompt Updates

Based on learnings, update `.claude/agents/code-reviewer.md`:
- Clarify ambiguous instructions
- Add missing checklist items
- Adjust severity thresholds
- Improve report format

### 4. ADR Amendment (if needed)

If significant workflow changes needed, amend ADR-0014.

## Implementation Plan

### Phase 1: Baseline Tests (45 min)

1. Run Test 1 (known good)
2. Document results
3. Verify report format

### Phase 2: Detection Tests (45 min)

1. Create synthetic task with issues
2. Run Test 2 (intentional issues)
3. Evaluate detection accuracy
4. Document false positives/negatives

### Phase 3: Edge Cases (30 min)

1. Run Test 3 (trivial)
2. Run Test 4 (large)
3. Document scalability findings

### Phase 4: Full Workflow (60 min)

1. Create small real task
2. Run complete workflow
3. Document handoff experience
4. Test revision cycle

### Phase 5: Analysis & Documentation (30 min)

1. Compile metrics
2. Write lessons learned
3. Propose improvements
4. Update agent prompt if needed

## Time Estimate

| Phase | Time |
|-------|------|
| Baseline tests | 45 min |
| Detection tests | 45 min |
| Edge cases | 30 min |
| Full workflow | 60 min |
| Analysis & documentation | 30 min |
| **Total** | **2-3 hours** |

## Success Criteria

The learning phase is successful if:

1. **Review accuracy**: > 80% of findings are valid issues
2. **Workflow viability**: Full cycle completes without human intervention
3. **Actionable feedback**: Developer can address findings without clarification
4. **Time efficiency**: Reviews complete in < 10 minutes
5. **Documentation**: Clear lessons learned for future improvement

## References

- ASK-0022: Code Review Workflow ADR
- ASK-0023: Code Reviewer Agent Implementation
- `.adversarial/docs/EVALUATION-WORKFLOW.md` (similar learning phase)

## Notes

- This is a calibration phase, not a gate
- Expect to iterate on agent prompt
- Document everything for future reference
- Consider making this a recurring process (quarterly calibration)

---

**Template Version**: 1.0.0
**Created**: 2025-11-29
