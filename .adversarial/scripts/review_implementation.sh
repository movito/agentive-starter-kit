#!/bin/bash
# SCRIPT_VERSION: 0.9.8
# Phase 3: Implementation Review - Evaluator analyzes actual code changes

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

TASK_FILE="$1"

if [ -z "$TASK_FILE" ]; then
  echo "Usage: ./.adversarial/scripts/review_implementation.sh <task_file_path>"
  echo ""
  echo "Example: ./.adversarial/scripts/review_implementation.sh ${TASK_DIR}TASK-2025-001.md"
  exit 1
fi

if [ ! -f "$TASK_FILE" ]; then
  echo "Error: Task file not found: $TASK_FILE"
  exit 1
fi

# Extract task number from filename
TASK_NUM=$(basename "$TASK_FILE" | grep -oE 'TASK-[0-9]+-[0-9]+' || basename "$TASK_FILE" .md)

echo "╔════════════════════════════════════════════╗"
echo "║   PHASE 3: IMPLEMENTATION REVIEW           ║"
echo "╚════════════════════════════════════════════╝"
echo ""
echo "Task: $TASK_NUM"
echo "Model: $EVALUATOR_MODEL"
echo ""

# Capture current implementation state
echo "=== Capturing implementation artifacts ==="
git diff > "${ARTIFACTS_DIR}${TASK_NUM}-implementation.diff"
git diff --stat > "${ARTIFACTS_DIR}${TASK_NUM}-change-summary.txt"
git status --short > "${ARTIFACTS_DIR}${TASK_NUM}-file-status.txt"

# Check if there are any changes
if [ ! -s "${ARTIFACTS_DIR}${TASK_NUM}-implementation.diff" ]; then
  echo ""
  echo "⚠️  WARNING: No changes detected in git diff!"
  echo "⚠️  This might indicate PHANTOM WORK - implementation claimed but not done."
  echo ""
  echo "Aborting review. Please ensure actual code changes have been made."
  exit 1
fi

# Count lines changed
LINES_CHANGED=$(git diff --stat | tail -1)

echo "✓ Changes captured:"
echo "  - Git diff: ${ARTIFACTS_DIR}${TASK_NUM}-implementation.diff"
echo "  - Statistics: $LINES_CHANGED"
echo ""

# Look for approved plan
PLAN_FILE="${LOG_DIR}${TASK_NUM}-PLAN-EVALUATION.md"
if [ -f "$PLAN_FILE" ]; then
  PLAN_AVAILABLE="yes"
  echo "✓ Found approved plan: $PLAN_FILE"
else
  PLAN_AVAILABLE="no"
  echo "⚠️  No approved plan found at: $PLAN_FILE"
  echo "   Review will proceed without plan comparison."
fi

echo ""
echo "=== REVIEWER ($EVALUATOR_MODEL) ANALYZING IMPLEMENTATION ==="
echo ""

# Build read files list
READ_FILES="${ARTIFACTS_DIR}${TASK_NUM}-implementation.diff ${ARTIFACTS_DIR}${TASK_NUM}-change-summary.txt ${ARTIFACTS_DIR}${TASK_NUM}-file-status.txt $TASK_FILE"
if [ "$PLAN_AVAILABLE" = "yes" ]; then
  READ_FILES="$READ_FILES $PLAN_FILE"
fi

aider \
  --model "$EVALUATOR_MODEL" \
  --yes \
  --no-detect-urls \
  --no-gitignore \
  --read $READ_FILES \
  --message "You are a REVIEWER performing critical code review.

**Your Role:**
Review the actual implementation changes. You are looking for real, working code and checking it against the original requirements.

**Files Provided:**
- Task requirements: $TASK_FILE
- Implementation diff: ${ARTIFACTS_DIR}${TASK_NUM}-implementation.diff (ACTUAL git changes)
- Change summary: ${ARTIFACTS_DIR}${TASK_NUM}-change-summary.txt
- File status: ${ARTIFACTS_DIR}${TASK_NUM}-file-status.txt
$(if [ "$PLAN_AVAILABLE" = "yes" ]; then echo "- Approved plan: $PLAN_FILE"; fi)

**Your Review Criteria:**

1. **Phantom Work Detection (CRITICAL)**
   - Is there REAL code, or just comments/TODOs?
   - Are changes substantive or superficial?
   - Look for placeholder text: 'TODO', 'FIXME', '// implement this'
   - Are claimed changes actually present in the diff?

2. **Plan Adherence** $(if [ "$PLAN_AVAILABLE" = "yes" ]; then echo "(compare to approved plan)"; fi)
   - Does implementation match the planned approach?
   - Are all planned changes present?
   - Are there unexpected deviations?
   - Are deviations justified and improvements?

3. **Completeness Check**
   - Does implementation address ALL requirements from task file?
   - Are all failing tests addressed?
   - Is error handling implemented (not just planned)?
   - Are edge cases handled?

4. **Code Quality**
   - Does code follow project conventions?
   - Are there obvious bugs or issues?
   - Is the implementation production-ready?
   - Good variable/function names?
   - Appropriate comments (not excessive)?

5. **Test Coverage**
   - Are there new or updated tests?
   - Do tests look meaningful or are they stubs?
   - Is test logic appropriate for changes?
   - Do tests actually exercise the new code?

6. **Breaking Changes & Risks**
   - Are there API changes?
   - Backward compatibility maintained?
   - Potential side effects on other code?
   - Performance implications?

**Output Format:**

## Review Summary
**Verdict:** [APPROVED / NEEDS_REVISION / REJECT]
**Implementation Quality:** [EXCELLENT / GOOD / ACCEPTABLE / POOR]
**Phantom Work Risk:** [NONE / LOW / MEDIUM / HIGH]
**Test Coverage:** [COMPLETE / ADEQUATE / INSUFFICIENT / MISSING]

## What Was Actually Implemented
[Describe the ACTUAL changes found in git diff - be specific about files, functions, logic]

## Verification Checklist
- [ ] Real code changes (not just comments/TODOs)
- [ ] All requirements addressed
- [ ] Plan followed (if plan existed)
- [ ] Tests added/updated
- [ ] Error handling present
- [ ] Edge cases covered
- [ ] No obvious bugs
- [ ] Production ready

## Strengths
- [What was done well]
- [Good implementation decisions]
- [Quality aspects]

## Issues Found
### CRITICAL (must fix before approval)
- [Blocking issues]

### MEDIUM (should fix)
- [Important improvements]

### LOW (nice to have)
- [Minor suggestions]

## Specific Improvements Needed
1. [Concrete change required in file X]
2. [Missing implementation in function Y]
3. [Test case needed for scenario Z]

## Plan Deviation Analysis
$(if [ "$PLAN_AVAILABLE" = "yes" ]; then echo "[Compare implementation to approved plan]
[List any deviations and whether they are justified]"; else echo "[No plan available for comparison]"; fi)

## Code Examples
[If suggesting changes, provide specific code examples]

## Approval Conditions
[If NEEDS_REVISION: specific changes needed]
[If APPROVED: any caveats or things to watch in testing]

---

Be thorough and critical. Phantom work is UNACCEPTABLE.
Real, working code is required. TODOs and comments are not implementation.

If code is fundamentally sound with minor issues → APPROVED with caveats
If code has significant gaps or bugs → NEEDS_REVISION with specific fixes
If code is mostly TODOs or doesn't address requirements → REJECT" \
  --no-auto-commits

echo ""
echo "=== Implementation review complete ==="
echo ""
echo "Next steps:"
echo "1. Review evaluation output above"
echo ""
echo "If APPROVED:"
echo "  → Proceed to test validation: ./.adversarial/scripts/validate_tests.sh $TASK_FILE"
echo ""
echo "If NEEDS_REVISION:"
echo "  → Address feedback and make changes"
echo "  → Run this script again after changes"
echo ""
echo "If REJECT:"
echo "  → Discard changes: git checkout ."
echo "  → Return to planning phase"
echo ""
