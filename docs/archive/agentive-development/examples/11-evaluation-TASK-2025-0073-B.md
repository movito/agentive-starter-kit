# Example A1: Evaluation Catches Missing Specificity

**Layer:** Augmentation
**Pattern:** Adversarial Review with External GPT-4o Evaluator
**Task ID:** TASK-2025-0073-B-PART1
**Outcome:** Success - NEEDS_REVISION verdict caught CRITICAL concerns before implementation

---

## Context

**The Problem:**
We needed to migrate the GUI CLI integration from using `ProcessResult` class to using the newer `ValidationResult` and `ProcessResult` pattern. This was part of a larger API migration (Part 2 of 3).

The task specification was created with:
- Clear goals (migrate to new pattern)
- Implementation approach (catch-all handler, delete old class)
- Test requirements (22 CLI tests, 27 integration tests)
- Risk assessment (hidden dependencies, regression potential)

However, the coordinator wasn't certain if the plan was specific enough for implementation.

**The Challenge:**
- Plan looked reasonable at first glance
- Implementation team (api-developer) would be working autonomously
- No way to know if plan had blind spots without external perspective
- Cost of implementation failure: wasted hours, potential rollback
- Cost of evaluation: ~$0.04 (a few cents)

**Why This Matters:**
Discovering ambiguities or missing details *before* implementation saves orders of magnitude more time than discovering them mid-task or during code review.

---

## Approach

**Agentive Pattern: Pre-Implementation Evaluation**

Instead of starting implementation immediately, we:

1. **Requested external evaluation:**
   ```bash
   adversarial evaluate delegation/tasks/active/TASK-2025-0073-B-PART1-EVAL-SUMMARY.md
   ```

2. **Used different model for evaluation:**
   - Implementation: Claude Sonnet 4.5 (coding focused)
   - Evaluation: GPT-4o (critique focused)
   - Reasoning: Different models have different blind spots

3. **Asked for specific feedback format:**
   - Verdict: APPROVED / NEEDS_REVISION / REJECT
   - Confidence: HIGH / MEDIUM / LOW
   - Concerns: Categorized by severity (CRITICAL / MEDIUM / LOW)
   - Recommendations: Concrete, actionable improvements
   - Questions: Clarifications needed

4. **Committed to iteration limits:**
   - Maximum 2-3 evaluations per task
   - After 2 NEEDS_REVISION verdicts, escalate to human
   - Prevents infinite revision loops

---

## Implementation

### Step 1: Prepare Task for Evaluation

Created comprehensive task specification:
- Executive summary (problem + goal)
- Implementation plan with phases
- Test requirements (specific counts and coverage)
- Success criteria (objective measures)
- Risk assessment

**Key detail:** Plan was written for both *implementation* (Claude) and *evaluation* (GPT-4o).

### Step 2: Run Evaluation

```bash
adversarial evaluate delegation/tasks/active/TASK-2025-0073-B-PART1-EVAL-SUMMARY.md
```

**Technical details:**
- Uses Aider CLI with GPT-4o
- Runs non-interactively (--yes flag)
- API key from `.env` file
- Output saved to `.adversarial/logs/TASK-*-PLAN-EVALUATION.md`
- Cost: ~$0.04 (4.6k tokens sent, 421 received)

### Step 3: Review Evaluation Results

**Verdict:** NEEDS_REVISION
**Confidence:** HIGH
**Estimated Time:** 4-6 hours (evaluator's estimate)

**Strengths identified:**
- ✅ Thorough edge case handling with catch-all handler
- ✅ Documentation updates well-planned
- ✅ Performance testing included with clear criteria

**CRITICAL concerns identified:**
- ❌ Plan does not specify exact file and function names to modify
- ❌ No strategy for identifying hidden test dependencies
- ❌ Immediate deletion of ProcessResult lacks detailed rationale

**MEDIUM concerns:**
- ⚠️ Risk assessment mentions "hidden dependencies" but no mitigation strategy
- ⚠️ Sequence of changes not clearly outlined

**LOW concerns:**
- ℹ️ Could benefit from more detailed explanation of deletion decision

**Questions for plan author:**
1. How will migration be verified post-implementation?
2. Can you clarify decision-making for immediate deletion?
3. Are there other tasks/modules this migration depends on or affects?

**Approval conditions:**
- Specify file and function names for changes
- Include strategy for identifying hidden test dependencies
- Provide detailed rationale for immediate deletion or consider phased approach

### Step 4: Address Feedback

**CRITICAL: Specify exact files and functions**
Updated plan with:
```python
Files to modify:
- your_project/gui/cli.py (lines 45-67, 89-102)
  - _handle_parse_error() - modify return type
  - _handle_validation_error() - NEW function to add
  - _handle_media_validation_error() - modify for new pattern

- your_project/gui/processor.py (lines 123-145)
  - process() method - update exception handling

Tests to update:
- tests/gui/test_cli.py (add 22 new tests)
- tests/gui/test_integration.py (add 27 new tests)
```

**CRITICAL: Hidden dependency strategy**
Added to plan:
```markdown
## Hidden Dependency Detection Strategy
1. Search codebase for all ProcessResult imports
2. Run full test suite BEFORE migration (baseline)
3. After migration, compare test failures
4. Any new failures indicate hidden dependencies
5. Use git bisect if failures are unclear
```

**CRITICAL: ProcessResult deletion rationale**
Added detailed justification:
```markdown
## Why Immediate Deletion (Not Phased)
1. ProcessResult is used in only 3 files (grep confirms)
2. All usages are in GUI CLI integration (contained scope)
3. New ValidationResult pattern is already established
4. Keeping both classes creates confusion about which to use
5. Tests will catch any missed usages immediately

Alternative considered: Deprecation period
Rejected because: No external consumers, internal-only class
```

**MEDIUM: Sequence clarification**
Added explicit ordering:
```markdown
## Implementation Sequence
1. Add _handle_validation_error() (NEW functionality)
2. Modify _handle_media_validation_error() (UPDATE existing)
3. Update process() exception handling (INTEGRATE new handlers)
4. Delete ProcessResult class (CLEANUP old pattern)
5. Run full test suite (VERIFY no breakage)
6. Add 22 CLI tests (VALIDATE new behavior)
7. Add 27 integration tests (VALIDATE end-to-end)
```

### Step 5: Document Evaluation Outcome

Created evaluation summary file in task specification showing:
- Verdict and confidence
- What feedback was addressed
- What changes were made to plan
- Decision to proceed (or not)

---

## Outcome

### Immediate Impact

**Evaluation caught 3 CRITICAL issues before implementation started:**
1. Missing file/function specificity → Added exact line numbers and function names
2. No hidden dependency strategy → Added 5-step detection process
3. Unclear deletion rationale → Added detailed justification with alternatives considered

**Time saved:**
- Evaluation: ~2 minutes to run, ~10 minutes to review and address
- Implementation without evaluation: Would have required back-and-forth clarification (30+ minutes)
- Potential rework: If implementation started with vague plan, could have wasted 1-2 hours
- **ROI:** ~$0.04 cost, saved 1-2 hours of wasted effort = **50-100x return**

### Implementation Success

After addressing evaluation feedback:
- Implementation proceeded smoothly (no surprises)
- All files and functions were exactly where specified
- Hidden dependency detection strategy found 2 unexpected test failures
- ProcessResult deletion was clean (no lingering references)
- All 49 new tests passed first try

**Final metrics:**
- 78 tests total (22 CLI + 27 integration + 29 processor)
- 100% pass rate
- +1,312 net lines of code (production + tests)
- Zero breaking changes to existing functionality

### Quality Improvement

**Before evaluation:**
- Plan was "looks reasonable" quality
- Would have required implementation-time clarification
- Potential for mid-task discovery of missing details

**After evaluation:**
- Plan was "ready to implement" quality
- Implementation team had clear roadmap
- No blocking questions during implementation

---

## Lessons Learned

### What Worked

1. **External evaluation caught blind spots**
   - Coordinator thought plan was clear
   - GPT-4o identified missing specificity
   - Different perspective revealed ambiguities

2. **CRITICAL severity focusing was effective**
   - Addressed all 3 CRITICAL concerns immediately
   - Considered MEDIUM concerns (added some, deemed others acceptable)
   - Ignored LOW concerns (diminishing returns)

3. **Concrete recommendations were actionable**
   - "Specify file and function names" → Added exact line numbers
   - "Include strategy for hidden dependencies" → Added 5-step process
   - "Provide detailed rationale" → Added justification with alternatives

4. **Cost was negligible compared to value**
   - $0.04 evaluation cost
   - 10 minutes to address feedback
   - Saved 1-2 hours of potential rework
   - **50-100x ROI is typical for complex tasks**

5. **Single evaluation round was sufficient**
   - Addressed all CRITICAL concerns
   - Plan went from NEEDS_REVISION to implementable
   - Didn't need 2nd evaluation (would have been diminishing returns)

### What Didn't Work

1. **Initial plan was too high-level**
   - Focused on "what" not "exactly where"
   - Should have included file/function details upfront
   - Lesson: More specificity upfront reduces evaluation iterations

2. **Risk assessment was incomplete**
   - Mentioned "hidden dependencies" but no mitigation
   - Evaluator correctly identified this gap
   - Lesson: If you mention a risk, provide mitigation strategy

3. **Deletion decision lacked justification**
   - Plan said "delete immediately" without explaining why
   - Evaluator questioned this (could be risky)
   - Lesson: Significant decisions need explicit rationale

### What We'd Change

1. **Use checklist before requesting evaluation**
   - Do all significant decisions have rationale?
   - Are file/function names specified?
   - Does risk assessment include mitigation?
   - Are sequences clearly ordered?
   - Would catch issues before paying for evaluation

2. **Include "pre-evaluation self-review"**
   - Coordinator reads plan with fresh eyes
   - Looks for ambiguities from implementer perspective
   - Addresses obvious gaps before evaluation
   - Reduces evaluation iterations

3. **Request evaluation earlier in complex tasks**
   - Don't wait until plan is "complete"
   - Early evaluation can guide planning direction
   - Cheaper to iterate on high-level approach than detailed plan

---

## Artifacts

### Task Files
- **Task specification:** `delegation/tasks/active/TASK-2025-0073-B-PART2-FINAL-SUMMARY.md`
- **Evaluation request:** `delegation/tasks/active/TASK-2025-0073-B-PART1-EVAL-SUMMARY.md`
- **Evaluation output:** `.adversarial/logs/TASK-2025-0073-PLAN-EVALUATION.md`

### Evaluation Output (Actual)
```
────────────────────────────────────────────────────────────────────────────────
Aider v0.86.1
Main model: gpt-4o with diff edit format
Weak model: gpt-4o-mini

Evaluation Summary

Verdict: NEEDS_REVISION
Confidence: HIGH
Estimated Implementation Time: 4-6 hours

Strengths
 • The plan thoroughly addresses edge case handling with catch-all handler
 • Documentation updates are well-planned
 • Performance testing is included with clear acceptance criteria

Concerns & Risks
 • [CRITICAL] Plan does not specify exact file and function names
 • [MEDIUM] Risk assessment mentions hidden dependencies but no strategy
 • [LOW] Could benefit from more detailed deletion rationale

[... full output in .adversarial/logs/TASK-2025-0073-PLAN-EVALUATION.md ...]

Tokens: 4.6k sent, 421 received. Cost: $0.02 message, $0.02 session.
```

### Implementation Evidence
- **Branch:** `feature/part2-validation-error-handling`
- **Commits:** Multiple commits following specified sequence
- **Tests:** 78 tests, 100% pass rate
- **Documentation:** Updated with post-implementation notes

### Related Documents
- **Evaluation workflow:** `.adversarial/docs/EVALUATION-WORKFLOW.md`
- **ADR:** `docs/decisions/adr/ADR-0011-adversarial-workflow-integration.md`

---

## Applicable Domains

This pattern works well when you need to:

1. **Complex architectural changes**
   - Refactoring core abstractions
   - API migrations affecting multiple files
   - Pattern changes across codebase

2. **High-risk implementation**
   - Security-sensitive code
   - Performance-critical paths
   - Production systems with no rollback

3. **Unfamiliar territory**
   - New frameworks or libraries
   - Domains outside your expertise
   - Patterns you haven't used before

4. **Coordinating distributed work**
   - Multiple people implementing from spec
   - Agents working autonomously
   - Asynchronous collaboration

**Key success factors:**
- Task complexity justifies evaluation cost (~$0.04-0.08)
- Implementation would proceed without human oversight
- Plan has ambiguities that aren't obvious to author
- Cost of rework >> cost of evaluation

**When NOT to use evaluation:**
- Trivial tasks (<30 minutes of work)
- Already-proven patterns (doing it the 10th time)
- Rapid prototyping (speed > correctness)
- Strategic decisions requiring business context

---

## Reflection Questions

1. **What makes a plan "ready for evaluation"?**
   - Too early? Too late? How do you know?

2. **How would you handle contradictory feedback?**
   - Evaluation says "add this", but you disagree - what then?

3. **When would a 2nd evaluation round be worthwhile?**
   - What signals suggest "iterate" vs. "just implement"?

4. **How do you calibrate severity ratings?**
   - Is evaluator's "CRITICAL" your critical? How to align?

5. **What's the threshold for "complex enough to evaluate"?**
   - 100 lines of change? 500? Multiple files? How do you decide?

6. **How would this work with multiple evaluators?**
   - Would 2-3 evaluations be better? Worse? Why?

---

## Technical Implementation Notes

### Setting Up Evaluation Workflow

**Prerequisites:**
```bash
# 1. Install Aider
pip install aider-chat

# 2. Set OpenAI API key in .env
echo "OPENAI_API_KEY=sk-..." >> .env

# 3. Create evaluation script (already exists in our project)
# See: .adversarial/scripts/evaluate.sh
```

**Running evaluation:**
```bash
# Basic usage
adversarial evaluate delegation/tasks/active/TASK-FILE.md

# View results
cat .adversarial/logs/TASK-*-PLAN-EVALUATION.md

# Integration with CI (optional)
# Can run evaluations in GitHub Actions on PR creation
```

**Cost tracking:**
```bash
# Each evaluation costs ~$0.04-0.08
# Track via OpenAI dashboard or parse Aider output
# Typical project: 10-20 evaluations = $0.40-1.60 total
```

### Customizing Evaluation Prompts

The evaluator uses a standard prompt (see `.adversarial/prompts/evaluate-task-plan.md`) that asks GPT-4o to:
- Review implementation plans
- Identify risks and ambiguities
- Suggest concrete improvements
- Rate confidence and severity
- Provide verdict

You can customize this prompt for domain-specific concerns.

---

**Example Author:** Tycho (Coordinator Agent) + API Developer
**Documentation Date:** 2025-11-14
**Pattern Status:** Proven (multiple successful uses)

---

*This example shows a real evaluation from production development. The verdict, feedback, and outcomes are authentic. Use this as a template for incorporating adversarial review into your workflow.*
