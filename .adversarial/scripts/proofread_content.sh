#!/bin/bash
# SCRIPT_VERSION: 0.9.8
# Proofreader: Teaching Content Quality Review

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
  echo "   Proofreader needs API keys to call AI models (GPT-4o, Claude, etc.)"
  echo "   These keys should be stored in a .env file in your project root."
  echo ""
  echo -e "${BOLD}FIX:${RESET}"
  echo "   Option 1 (RECOMMENDED): Run interactive setup"
  echo "     adversarial init --interactive"
  echo ""
  echo "   Option 2: Copy example and add your keys manually"
  echo "     cp .env.template .env"
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
LOG_DIR=$(grep 'log_directory:' .adversarial/config.yml | awk '{print $2}')

DOC_FILE="$1"

if [ -z "$DOC_FILE" ]; then
  echo "Usage: ./.adversarial/scripts/proofread_content.sh <document_file_path>"
  echo ""
  echo "Example: ./.adversarial/scripts/proofread_content.sh docs/agentive-development/01-foundation/01-structured-ai-collaboration/concept.md"
  exit 1
fi

if [ ! -f "$DOC_FILE" ]; then
  echo "Error: Document file not found: $DOC_FILE"
  exit 1
fi

# Extract document name from filename (without path and extension)
DOC_NAME=$(basename "$DOC_FILE" .md)

echo "╔════════════════════════════════════════════╗"
echo "║   PROOFREADER: TEACHING CONTENT REVIEW     ║"
echo "╚════════════════════════════════════════════╝"
echo ""
echo "Document: $DOC_FILE"
echo "Name: $DOC_NAME"
echo "Model: $EVALUATOR_MODEL"
echo ""

# Create proofreading output file
PROOFREAD_OUTPUT="${LOG_DIR}${DOC_NAME}-PROOFREADING.md"

echo "=== PROOFREADER ($EVALUATOR_MODEL) ANALYZING TEACHING CONTENT ==="
echo ""

# Ensure log directory exists
mkdir -p "$LOG_DIR"

# Check if style guide exists
STYLE_GUIDE_CONTEXT=""
if [ -f ".agent-context/documentation-style-guide.md" ]; then
  STYLE_GUIDE_CONTEXT="

**STYLE GUIDE REFERENCE:**
The project uses a documentation style guide at .agent-context/documentation-style-guide.md
Please consider these guidelines when evaluating consistency."
fi

# Check if glossary exists
GLOSSARY_CONTEXT=""
if [ -f ".agent-context/agentive-development-glossary.md" ]; then
  GLOSSARY_CONTEXT="

**GLOSSARY REFERENCE:**
The project maintains a glossary at .agent-context/agentive-development-glossary.md
Please check terminology consistency against this glossary."
fi

aider \
  --model "$EVALUATOR_MODEL" \
  --yes \
  --no-detect-urls \
  --no-git \
  --map-tokens 0 \
  --no-gitignore \
  --read "$DOC_FILE" \
  --message "You are a PROOFREADER performing quality review of teaching content.

**Your Role:**
You are reviewing educational documentation (concepts, examples, exercises) used to teach developers about best practices. Your job is to evaluate whether this content teaches effectively.

**Document File Provided:**
$DOC_FILE${STYLE_GUIDE_CONTEXT}${GLOSSARY_CONTEXT}

**IMPORTANT: This is TEACHING CONTENT, not code implementation plans.**
DO NOT evaluate for:
- File/function names (this is teaching prose, not code planning)
- Implementation details or technical architecture decisions
- Error handling in the plan itself (unless evaluating code examples within the doc)
- Code acceptance criteria (success criteria are learning outcomes)

**Your Evaluation Criteria:**

1. **CLARITY**
   - Are explanations clear and understandable?
   - Are complex ideas broken down effectively?
   - Is jargon explained when first used?
   - Can a developer unfamiliar with the topic follow along?

2. **ACCURACY**
   - Are facts, metrics, and claims correct?
   - Are sources cited (file paths, task references, ADRs)?
   - Are code examples correct and runnable?
   - Are claims verifiable?

3. **ENGAGEMENT**
   - Is the content interesting to read?
   - Does it maintain an approachable, conversational tone?
   - Are there concrete examples and stories?
   - Does it avoid being too dry or academic?

4. **PEDAGOGICAL STRUCTURE**
   - Does it teach effectively (concept → example → practice)?
   - Is there a logical progression of ideas?
   - Is the depth appropriate for the target audience?
   - Are key takeaways clear?

5. **COMPLETENESS**
   - Are all key concepts covered?
   - Is important information missing?
   - Is there too much or too little detail?
   - Does it answer likely reader questions?

6. **EXAMPLES**
   - Are examples real (not contrived/toy examples)?
   - Do examples illustrate the concept effectively?
   - Can examples be generalized to other contexts?
   - Are code examples cited with file paths?

7. **CONSISTENCY**
   - Voice: Second person, active voice, present tense?
   - Terminology: Matches project glossary?
   - Formatting: Consistent with style guide?
   - Tone: Matches other teaching content?

**Output Format:**

Please provide your evaluation in this EXACT format:

## Evaluation Summary
**Verdict:** [APPROVED / NEEDS_REVISION / REJECTED]
**Confidence:** [HIGH / MEDIUM / LOW]

## Strengths
- [What the document does well]
- [Clear, effective teaching moments]
- [Good examples or explanations]

## Concerns & Risks
- [CRITICAL] [Major issues that harm learning - inaccuracies, critical confusion]
- [HIGH] [Important improvements - clarity issues, missing key concepts]
- [MEDIUM] [Nice-to-have improvements - engagement, better examples]
- [LOW] [Minor polish - wording, formatting]

## Missing or Unclear
- [What needs clarification]
- [What concepts should be added]
- [What assumptions need explanation]

## Specific Recommendations
1. [Concrete, actionable improvement]
2. [Alternative explanations to consider]
3. [Additional examples needed]

## Questions for Author
1. [Question about teaching approach]
2. [Clarification needed on content]
3. [Target audience considerations]

## Approval Conditions
[If NEEDS_REVISION: List specific changes needed for approval]
[If APPROVED: Any suggestions for future improvements]

---

**FOCUS:** Will a learner understand this content and be able to apply these concepts in their work?

Be thorough and constructive. Your goal is to improve teaching effectiveness, not to block publication unnecessarily.

- If the content teaches well but has minor issues, mark as APPROVED with suggestions.
- If the content has clarity problems or missing key information, mark as NEEDS_REVISION with specific fixes.
- Only use REJECTED if the content is fundamentally confusing or inaccurate." \
  --no-auto-commits 2>&1 | tee "$PROOFREAD_OUTPUT"

echo ""
echo "=== Proofreading complete ==="
echo ""
echo "Proofreading saved to: $PROOFREAD_OUTPUT"
echo ""
echo "Next steps:"
echo "1. Review feedback above"
echo "2. Author addresses concerns and updates document"
echo "3. Run 'adversarial proofread' again if NEEDS_REVISION"
echo "4. Publish/share if APPROVED"
echo ""
