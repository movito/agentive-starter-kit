#!/bin/bash
# SCRIPT_VERSION: 0.9.8
# Phase 4: Test Validation - Evaluator validates implementation

# ANSI color codes
RED='\033[91m'
GREEN='\033[92m'
YELLOW='\033[93m'
BOLD='\033[1m'
RESET='\033[0m'

# Load environment variables from .env file
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
else
  echo -e "${RED}❌ ERROR: No .env file found${RESET}"
  echo ""
  echo -e "${BOLD}WHY:${RESET}"
  echo "   Workflow scripts need API keys to call AI models (GPT-4o, Claude, etc.)"
  echo "   These keys should be stored in a .env file in your project root."
  echo ""
  echo -e "${BOLD}FIX:${RESET}"
  echo "   Option 1 (RECOMMENDED): Run interactive setup"
  echo "     adversarial init --interactive"
  echo ""
  echo "   Option 2: Copy example and add your keys manually"
  echo "     cp .env.example .env"
  echo "     # Then edit .env and add your API keys"
  echo ""
  echo -e "${BOLD}GET API KEYS:${RESET}"
  echo "   • Anthropic (Claude): https://console.anthropic.com/settings/keys"
  echo "   • OpenAI (GPT-4o): https://platform.openai.com/api-keys"
  echo ""
  exit 1
fi

# Validate API keys are present
if [ -z "$OPENAI_API_KEY" ] && [ -z "$ANTHROPIC_API_KEY" ]; then
  echo -e "${RED}❌ ERROR: No API keys configured${RESET}"
  echo ""
  echo -e "${BOLD}WHY:${RESET}"
  echo "   Your .env file exists but contains no API keys."
  echo "   At least one API key is required: OPENAI_API_KEY or ANTHROPIC_API_KEY"
  echo ""
  echo -e "${BOLD}FIX:${RESET}"
  echo "   Edit .env and add at least one API key:"
  echo ""
  echo "     # For GPT-4o (OpenAI)"
  echo "     OPENAI_API_KEY=sk-proj-your-key-here"
  echo ""
  echo "     # For Claude 3.5 Sonnet (Anthropic)"
  echo "     ANTHROPIC_API_KEY=sk-ant-your-key-here"
  echo ""
  echo -e "${BOLD}GET API KEYS:${RESET}"
  echo "   • Anthropic: https://console.anthropic.com/settings/keys"
  echo "   • OpenAI: https://platform.openai.com/api-keys"
  echo ""
  echo -e "${BOLD}VERIFY:${RESET}"
  echo "   adversarial check"
  echo ""
  exit 1
fi

# Load configuration from .adversarial/config.yml
if [ ! -f .adversarial/config.yml ]; then
  echo "Error: Configuration file not found: .adversarial/config.yml"
  echo "Run 'adversarial init' first to initialize the workflow."
  exit 1
fi

# Parse config using grep/awk (simple YAML parsing)
# Note: evaluator_model is deprecated. Consider using 'adversarial evaluate' CLI instead.
EVALUATOR_MODEL=$(grep 'evaluator_model:' .adversarial/config.yml 2>/dev/null | awk '{print $2}')
EVALUATOR_MODEL=${EVALUATOR_MODEL:-gpt-4o}  # Default fallback if not configured
TASK_DIR=$(grep 'task_directory:' .adversarial/config.yml | awk '{print $2}')
LOG_DIR=$(grep 'log_directory:' .adversarial/config.yml | awk '{print $2}')
ARTIFACTS_DIR=$(grep 'artifacts_directory:' .adversarial/config.yml | awk '{print $2}')
TEST_CMD=$(grep 'test_command:' .adversarial/config.yml | sed 's/test_command: //')

TASK_FILE="$1"
TEST_COMMAND="${2:-$TEST_CMD}"

if [ -z "$TASK_FILE" ]; then
  echo "Usage: ./.adversarial/scripts/validate_tests.sh <task_file_path> [test_command]"
  echo ""
  echo "Example: ./.adversarial/scripts/validate_tests.sh ${TASK_DIR}TASK-2025-001.md"
  echo "Example: ./.adversarial/scripts/validate_tests.sh ${TASK_DIR}TASK-2025-001.md 'pytest tests/test_feature.py -v'"
  echo ""
  echo "Default test command from config: $TEST_CMD"
  exit 1
fi

if [ ! -f "$TASK_FILE" ]; then
  echo "Error: Task file not found: $TASK_FILE"
  exit 1
fi

# Extract task number from filename
TASK_NUM=$(basename "$TASK_FILE" | grep -oE 'TASK-[0-9]+-[0-9]+' || basename "$TASK_FILE" .md)

echo "╔════════════════════════════════════════════╗"
echo "║   PHASE 4: TEST VALIDATION                 ║"
echo "╚════════════════════════════════════════════╝"
echo ""
echo "Task: $TASK_NUM"
echo "Test Command: $TEST_COMMAND"
echo "Model: $EVALUATOR_MODEL"
echo ""

# Capture implementation state
echo "=== Capturing artifacts ==="
git diff > "${ARTIFACTS_DIR}${TASK_NUM}-final-implementation.diff"
git diff --stat > "${ARTIFACTS_DIR}${TASK_NUM}-final-changes.txt"

echo ""
echo "=== Running tests: $TEST_COMMAND ==="
echo ""

# Run tests and capture output
eval "$TEST_COMMAND" > "${ARTIFACTS_DIR}${TASK_NUM}-test-output.txt" 2>&1
TEST_EXIT_CODE=$?

# Display test output
cat "${ARTIFACTS_DIR}${TASK_NUM}-test-output.txt"

echo ""
if [ $TEST_EXIT_CODE -eq 0 ]; then
  echo "✓ Tests PASSED (exit code: 0)"
else
  echo "✗ Tests FAILED (exit code: $TEST_EXIT_CODE)"
fi
echo ""

# Parse test results for summary
TEST_SUMMARY=$(grep -E "passed|failed|error" "${ARTIFACTS_DIR}${TASK_NUM}-test-output.txt" | tail -1 || echo "Unable to parse test summary")

echo "Test Summary: $TEST_SUMMARY"
echo ""

echo "=== REVIEWER ($EVALUATOR_MODEL) ANALYZING TEST RESULTS ==="
echo ""

aider \
  --model "$EVALUATOR_MODEL" \
  --yes \
  --no-detect-urls \
  --no-gitignore \
  --read "$TASK_FILE" "${ARTIFACTS_DIR}${TASK_NUM}-final-implementation.diff" "${ARTIFACTS_DIR}${TASK_NUM}-test-output.txt" \
  --message "You are a REVIEWER performing test validation and analysis.

**Your Role:**
Analyze test results and validate that the implementation meets all requirements. You are the final checkpoint before code is approved for commit.

**Context:**
- Task: $TASK_NUM
- Task file: $TASK_FILE
- Test command: $TEST_COMMAND
- Test exit code: $TEST_EXIT_CODE
- Implementation diff: ${ARTIFACTS_DIR}${TASK_NUM}-final-implementation.diff
- Test output: ${ARTIFACTS_DIR}${TASK_NUM}-test-output.txt

**Your Validation Criteria:**

1. **Test Execution Status**
   - Did tests run successfully? (exit code 0 = pass)
   - Were all relevant tests executed?
   - Any tests skipped or xfailed that shouldn't be?

2. **Requirement Coverage**
   - Does task file specify which tests should pass?
   - Are those specific tests now passing?
   - Example: If task says '6 validation tests should pass', verify exactly those 6 pass

3. **Test Results Analysis**
   - Parse test output for pass/fail counts
   - Identify which specific tests failed (if any)
   - Analyze failure messages for root causes
   - Check for new test failures (regressions)

4. **Implementation-Test Alignment**
   - Do passing tests actually exercise the new code?
   - Are tests meaningful or just stubs?
   - Do test assertions validate the requirements?
   - Code coverage adequate for changes?

5. **Regression Analysis**
   - Compare to baseline: were there X passing tests before?
   - Are there NEW failures introduced?
   - Overall test pass rate acceptable?

6. **Performance & Quality**
   - Test execution time reasonable?
   - Any warnings or deprecations?
   - Test code quality (if new tests added)?

**Output Format:**

## Validation Summary
**Verdict:** [PASS / FAIL / CONDITIONAL_PASS]
**Test Status:** [ALL_PASS / PARTIAL_PASS / MULTIPLE_FAILURES]
**Exit Code:** $TEST_EXIT_CODE
**Regressions Detected:** [YES / NO]

## Test Results Breakdown
**Total Tests:** [number from output]
**Passed:** [number] ✓
**Failed:** [number] ✗
**Skipped:** [number] ⊘
**XFailed:** [number] (expected failures)

## Requirement Verification
[Check task file for specific test requirements]
- [ ] Requirement 1: [specific test or metric] → [PASS/FAIL]
- [ ] Requirement 2: [specific test or metric] → [PASS/FAIL]
- [ ] All specified tests passing: [YES/NO]

## Failed Tests Analysis (if any)
### Test: [test_name_1]
- **Location:** [file:line]
- **Error:** [error message]
- **Root Cause:** [analysis]
- **Fix Needed:** [specific action]

### Test: [test_name_2]
[repeat for each failure]

## Regression Analysis
- **Baseline pass rate:** [if known from task file]
- **Current pass rate:** [from test output]
- **Change:** [+/- X tests]
- **New failures:** [list any tests that used to pass]

## Code Coverage Assessment
- **Files modified:** [from diff]
- **Tests exercising changes:** [list relevant tests]
- **Coverage adequate:** [YES / NO / PARTIAL]
- **Missing test cases:** [scenarios not covered]

## Performance Metrics
- **Test execution time:** [from output]
- **Acceptable:** [YES / NO]
- **Slow tests:** [any tests >5s]

## Approval Decision

### If PASS:
✓ All requirements met
✓ Tests confirm implementation works
✓ No regressions detected
✓ Ready for commit

### If CONDITIONAL_PASS:
⚠️ Tests pass but with caveats:
- [List conditions/warnings]
- [Acceptable trade-offs]
Recommendation: [APPROVE with notes / NEEDS_MINOR_FIXES]

### If FAIL:
✗ Critical issues found:
- [Blocking test failures]
- [Regressions introduced]
- [Requirements not met]
Recommendation: RETURN TO IMPLEMENTATION (specific fixes listed above)

## Recommendations
1. [Specific action if needed]
2. [Follow-up testing suggested]
3. [Documentation updates needed]

---

Be precise with test counts and failure analysis.
If tests pass and requirements are met → PASS
If tests mostly pass with acceptable trade-offs → CONDITIONAL_PASS
If critical tests fail or regressions exist → FAIL" \
  --no-auto-commits

echo ""
echo "=== Test validation complete ==="
echo ""
echo "Next steps:"
echo ""
echo "If PASS or CONDITIONAL_PASS:"
echo "  → Review validation output above"
echo "  → Create final commit"
echo "  → Update project tracking"
echo ""
echo "If FAIL:"
echo "  → Address test failures"
echo "  → Run this script again after fixes"
echo ""
echo "Test artifacts saved:"
echo "  - ${ARTIFACTS_DIR}${TASK_NUM}-test-output.txt"
echo "  - ${ARTIFACTS_DIR}${TASK_NUM}-final-implementation.diff"
echo "  - ${ARTIFACTS_DIR}${TASK_NUM}-final-changes.txt"
echo ""
