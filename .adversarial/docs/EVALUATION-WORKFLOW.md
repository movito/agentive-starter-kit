# Adversarial Evaluation Workflow

**Created**: 2025-11-01
**Updated**: 2026-02-01 (multi-evaluator architecture, provider-agnostic)
**Purpose**: Complete guide to using the adversarial evaluation workflow
**Audience**: All agents (especially Planner)
**Tool**: `adversarial` CLI (v0.7.0+)
**Evaluator**: External AI via adversarial-workflow (built-in or custom)

---

## Table of Contents

- [Overview](#overview)
- [Available Evaluators](#available-evaluators)
- [Three Modes: Evaluate, Proofread, Review](#three-modes-evaluate-proofread-review)
- [Discovering Evaluators](#discovering-evaluators)
- [Custom Evaluators](#custom-evaluators)
- [What It Is (and Isn't)](#what-it-is-and-isnt)
- [When to Use Each Mode](#when-to-use-each-mode)
- [Plan Evaluation Workflow](#plan-evaluation-workflow)
- [Proofreading Workflow](#proofreading-workflow)
- [Code Review Workflow](#code-review-workflow)
- [Evaluation Criteria (Code Plans)](#evaluation-criteria-code-plans)
- [Proofreading Criteria (Teaching Content)](#proofreading-criteria-teaching-content)
- [Code Review Criteria](#code-review-criteria)
- [Verdict Types](#verdict-types)
- [Cost Expectations](#cost-expectations)
- [Iteration Guidance](#iteration-guidance)
- [Known Issues](#known-issues)
- [Best Practices](#best-practices)
- [Example Output](#example-output)
- [Recent Usage](#recent-usage)
- [Documentation References](#documentation-references)

---

## Overview

The adversarial workflow provides independent quality assurance using **external AI** (via Aider CLI) for three types of content:

1. **Plan Evaluation** (`adversarial evaluate`) - Review implementation plans and architectural decisions
2. **Proofreading** (`adversarial proofread`) - Review teaching/documentation content quality
3. **Code Review** (`adversarial review`) - Review implemented code for quality and correctness

**Key Benefit**: Catch issues early—design flaws in plans, clarity problems in teaching content, or bugs in code—before they compound.

---

## Available Evaluators

As of adversarial-workflow v0.7.0, three built-in evaluators are available (require OPENAI_API_KEY):

| Command | Purpose | Best For |
|---------|---------|----------|
| `adversarial evaluate` | Plan evaluation | Task specs, architecture docs, implementation plans |
| `adversarial proofread` | Teaching content review | Concepts, guides, tutorials, documentation |
| `adversarial review` | Code review | Implemented code, PRs, refactoring validation |

**Discover evaluators:**
```bash
adversarial list-evaluators
```

---

## Three Modes: Evaluate, Proofread, Review

### `adversarial evaluate` - For Implementation Plans

**Use for:**
- Task specifications (TASK-*.md)
- Code architecture plans
- Implementation approaches
- Technical design decisions

**Evaluates:**
- Completeness, design quality, risk assessment
- Implementation clarity (file/function names)
- Error handling, test coverage
- Dependencies, edge cases

**Output:** `.adversarial/logs/TASK-*-PLAN-EVALUATION.md`

---

### `adversarial proofread` - For Teaching Content

**Use for:**
- Concept documents (teaching explanations)
- Examples (real-world applications)
- Practice exercises
- Documentation guides

**Evaluates:**
- Clarity, accuracy, engagement
- Pedagogical structure
- Examples quality
- Style guide/glossary consistency

**Output:** `.adversarial/logs/<doc-name>-PROOFREADING.md`

---

### `adversarial review` - For Implemented Code

**Use for:**
- Completed implementations before merge
- Pull request validation
- Refactoring verification
- Code quality audits

**Evaluates:**
- Code correctness and logic
- Error handling completeness
- Security considerations
- Performance implications
- Test coverage adequacy
- Code style and maintainability

**Output:** `.adversarial/logs/<identifier>-CODE-REVIEW.md`

---

### Quick Decision Guide

| Content Type | Command | Why |
|--------------|---------|-----|
| Task specification with implementation details | `evaluate` | Needs code-focused review |
| Architecture decision document | `evaluate` | Needs technical design review |
| Concept explanation (teaching) | `proofread` | Needs clarity/pedagogy review |
| Real-world example with code | `proofread` | Teaching content (even with code) |
| Practice exercise | `proofread` | Educational effectiveness |
| API documentation | `proofread` | User-facing clarity |
| README or guide | `proofread` | Teaching/explaining |
| Completed feature implementation | `review` | Needs code correctness review |
| Bug fix before merge | `review` | Verify fix is correct |
| Refactored code | `review` | Verify behavior preserved |
| Pull request changes | `review` | Pre-merge quality check |

**Rule of thumb:**
- **Planning code?** → `evaluate`
- **Teaching someone?** → `proofread`
- **Code already written?** → `review`

---

## Discovering Evaluators

Use the `list-evaluators` command to see all available evaluators:

```bash
adversarial list-evaluators
```

**Example output:**
```
Built-in Evaluators:
  evaluate       Plan evaluation (GPT-4o)
  proofread      Teaching content review (GPT-4o)
  review         Code review (GPT-4o)

Local Evaluators:
  security       Security-focused code review
  performance    Performance analysis

Create .adversarial/evaluators/*.yml to add custom evaluators.
```

This command shows:
- **Built-in evaluators**: Shipped with adversarial-workflow
- **Local evaluators**: Custom evaluators defined in your project

---

## Custom Evaluators

You can create project-specific evaluators by adding YAML files to `.adversarial/evaluators/`.

### Creating a Custom Evaluator

**1. Create the evaluator file:**
```bash
mkdir -p .adversarial/evaluators
```

**2. Define the evaluator (e.g., `.adversarial/evaluators/security.yml`):**
```yaml
name: security
description: Security-focused code review
model: gpt-4o  # Or: gemini/gemini-2.0-flash, mistral/mistral-large-latest, etc.
api_key_env: OPENAI_API_KEY  # Environment variable for API key

prompt: |
  You are a security expert reviewing code for vulnerabilities.
  
  Focus on:
  - OWASP Top 10 vulnerabilities
  - Input validation and sanitization
  - Authentication and authorization flaws
  - Secrets and credential exposure
  - Injection vulnerabilities (SQL, command, XSS)
  
  For each issue found, provide:
  - Severity (CRITICAL/HIGH/MEDIUM/LOW)
  - Location (file:line)
  - Description of the vulnerability
  - Recommended fix
  
  End with a verdict: APPROVED, NEEDS_REVISION, or REJECT

output_suffix: SECURITY-REVIEW
```

**3. Use the custom evaluator:**
```bash
adversarial security src/auth/login.py
```

### Custom Evaluator Schema

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Command name (lowercase, no spaces) |
| `description` | Yes | Short description shown in `list-evaluators` |
| `model` | No | AI model to use (see aider docs for formats) |
| `api_key_env` | No | Environment variable for API key |
| `prompt` | Yes | System prompt for the evaluator |
| `output_suffix` | No | Suffix for output files (default: EVALUATION) |

### Example Use Cases

- **Security review**: Focus on vulnerabilities and exploits
- **Performance review**: Analyze algorithmic complexity and bottlenecks
- **Accessibility review**: Check for WCAG compliance
- **API review**: Validate REST/GraphQL design patterns
- **Database review**: Check query efficiency and schema design

### Evaluator Library

Pre-built evaluators for multiple providers are available:

```bash
# Install evaluators from the evaluator library
./scripts/project install-evaluators

# See all available evaluators (built-in + custom + library)
adversarial list-evaluators
```

**Installed providers include:**
- OpenAI (gpt-4o, gpt-4o-mini, o3, gpt-5.2)
- Google (gemini-flash, gemini-pro, gemini-deep)
- Mistral (mistral-fast, mistral-content, codestral-code)

Each provider requires its own API key (set in `.env`):
- `OPENAI_API_KEY` for OpenAI evaluators
- `GOOGLE_API_KEY` for Gemini evaluators
- `MISTRAL_API_KEY` for Mistral evaluators

**Documentation**: `.adversarial/evaluators/README.md`
**Library**: https://github.com/movito/adversarial-evaluator-library

---

## What It Is (and Isn't)

### ✅ What It IS:

- **External AI evaluator** invoked via `adversarial evaluate` or `adversarial proofread` CLI commands
- Uses Aider to call external AI APIs (OpenAI, Google, Mistral, etc.)
- Saves output to `.adversarial/logs/` with different suffixes:
  - Evaluation: `TASK-*-PLAN-EVALUATION.md`
  - Proofreading: `<doc-name>-PROOFREADING.md`
- Independent critical review from a different AI model (external evaluator, not Claude)

### ❌ What It is NOT:

- **NOT** Claude in a new UI tab (that's for manual user review)
- **NOT** a Claude Code Task tool agent (those create phantom work that doesn't persist)
- **NOT** a Claude Code subagent (evaluators are external, via CLI)
- **NOT** a replacement for human review (it's a complement)

### 🔍 Critical Clarification:

The `.claude/CLAUDE.md` instruction "Always launch agents in new tabs" refers to opening **Claude Desktop UI tabs** for manual review by the user. This is **NOT** the same as the adversarial workflow, which is an external AI evaluator invoked via CLI.

**Confusion Prevention:**
- "Give this to Evaluator" = Run `adversarial evaluate` command (external AI via CLI)
- "Proofread this document" = Run `adversarial proofread` command (external AI via CLI)
- "Open in new tab for review" = User opens Claude Desktop tab for manual review
- They are completely different workflows!

---

## When to Use Each Mode

### Use `adversarial evaluate` for:

- ✅ **Before assigning implementation tasks** to specialized agents
- ✅ **Complex tasks** (>500 lines) with multiple phases
- ✅ **Critical dependencies or risks** that need validation
- ✅ **After creating/updating task specifications**
- ✅ **Architectural decision documents**

Skip `evaluate` for:
- ❌ Trivial tasks (<100 lines)
- ❌ Bug fixes with obvious solutions
- ❌ Teaching/documentation content (use `proofread` instead)

---

### Use `adversarial proofread` for:

- ✅ **Teaching content** (concepts, explanations)
- ✅ **Documentation guides** (READMEs, how-tos)
- ✅ **Real-world examples** with educational purpose
- ✅ **Practice exercises** and learning materials
- ✅ **API documentation** and user-facing content

Skip `proofread` for:
- ❌ Implementation plans (use `evaluate` instead)
- ❌ Code architecture documents (use `evaluate` instead)
- ❌ Technical specifications (use `evaluate` instead)

---

### Use `adversarial review` for:

- ✅ **Completed implementations** before merge
- ✅ **Bug fixes** to verify correctness
- ✅ **Refactored code** to ensure behavior preserved
- ✅ **Pull request changes** for pre-merge validation
- ✅ **Critical path code** requiring extra scrutiny

Skip `review` for:
- ❌ Planning documents (use `evaluate` instead)
- ❌ Teaching content (use `proofread` instead)
- ❌ Configuration files (usually not worth the cost)
- ❌ Trivial changes (<10 lines)

---

## Plan Evaluation Workflow

### Step-by-Step Process:

**1. Planner creates task specification**
```bash
# Create in delegation/tasks/2-todo/
delegation/tasks/2-todo/TASK-XXXX-description.md
```

**2. Planner runs evaluation directly via Bash tool**
```bash
# For files < 500 lines:
adversarial evaluate delegation/tasks/2-todo/TASK-XXXX-description.md

# For large files (>500 lines) requiring interactive confirmation:
echo y | adversarial evaluate delegation/tasks/2-todo/TASK-XXXX-description.md
```
- This invokes Aider with GPT-4o model
- GPT-4o analyzes plan using evaluation criteria
- Output saved to `.adversarial/logs/TASK-XXXX-PLAN-EVALUATION.md`

**3. Planner reads GPT-4o evaluation output**
```bash
# Read evaluation results
cat .adversarial/logs/TASK-XXXX-PLAN-EVALUATION.md
```

**4. Planner addresses CRITICAL and HIGH priority feedback**
- Fix design flaws identified by GPT-4o
- Add missing requirements
- Clarify ambiguous specifications
- Address risk concerns

**5. Planner updates task file based on recommendations**
- Edit task specification in `delegation/tasks/2-todo/`
- Incorporate GPT-4o's suggestions
- Improve clarity and completeness

**6. If NEEDS_REVISION: Repeat steps 2-5**
- Optimal: 2-3 evaluation rounds
- Diminishing returns after 3 rounds
- Use planner judgment

**7. If APPROVED (or planner override): Assign to specialized agent**
- Create handoff document
- Update agent-handoffs.json
- Begin implementation

---

## Proofreading Workflow

### Step-by-Step Process:

**1. Agent creates teaching/documentation content**
```bash
# Create in appropriate documentation directory
docs/agentive-development/01-foundation/01-structured-ai-collaboration/concept.md
```

**2. Agent or planner runs proofreading directly via Bash tool**
```bash
# For files < 500 lines:
adversarial proofread docs/agentive-development/01-foundation/01-structured-ai-collaboration/concept.md

# For large files (>500 lines) requiring interactive confirmation:
echo y | adversarial proofread docs/agentive-development/01-foundation/01-structured-ai-collaboration/concept.md
```
- This invokes Aider with GPT-4o model
- GPT-4o analyzes content using proofreading criteria
- Output saved to `.adversarial/logs/concept-PROOFREADING.md`

**3. Agent reads GPT-4o proofreading output**
```bash
# Read proofreading results
cat .adversarial/logs/concept-PROOFREADING.md
```

**4. Agent addresses CRITICAL and HIGH priority feedback**
- Fix inaccuracies or confusing explanations
- Add missing citations or sources
- Improve clarity and engagement
- Address style guide/glossary inconsistencies

**5. Agent updates document based on recommendations**
- Edit teaching content based on GPT-4o's suggestions
- Add better examples if needed
- Improve pedagogical flow
- Ensure terminology consistency

**6. If NEEDS_REVISION: Repeat steps 2-5**
- Optimal: 1-2 proofreading rounds (teaching content stabilizes faster)
- Diminishing returns after 2 rounds
- Use agent/planner judgment

**7. If APPROVED: Publish or commit document**
- Teaching content is ready for readers
- Commit to repository
- Share with learners

---

## Code Review Workflow

### Step-by-Step Process:

**1. Implementation is complete**
```bash
# Code is written and tests pass locally
pytest tests/ -v
```

**2. Run code review via Bash tool**
```bash
# Review specific files:
adversarial review src/feature/new_module.py

# Review multiple files:
adversarial review src/feature/

# Review with context from task spec:
adversarial review src/feature/ --context delegation/tasks/3-in-progress/TASK-0001.md
```
- This invokes Aider with GPT-4o model
- GPT-4o analyzes code using review criteria
- Output saved to `.adversarial/logs/<identifier>-CODE-REVIEW.md`

**3. Read GPT-4o code review output**
```bash
# Read review results
cat .adversarial/logs/new_module-CODE-REVIEW.md
```

**4. Address CRITICAL and HIGH priority findings**
- Fix bugs and logic errors
- Address security vulnerabilities
- Improve error handling
- Add missing edge case handling

**5. Update code based on recommendations**
- Implement suggested fixes
- Run tests to verify changes
- Ensure no regressions

**6. If NEEDS_REVISION: Repeat steps 2-5**
- Typical: 1-2 review rounds for code
- Code reviews often surface concrete bugs
- Focus on CRITICAL/HIGH issues

**7. If APPROVED: Proceed to merge**
- Code is ready for integration
- Create PR or merge to main
- Move task to done

---

## Evaluation Criteria (Code Plans)

GPT-4o evaluates plans using these criteria:

### 1. **Completeness Check**
- Does the plan address ALL requirements?
- Are all failing tests covered?
- Are edge cases identified?
- Is error handling specified?

### 2. **Design Quality**
- Is the approach sound?
- Are there simpler alternatives?
- Will this scale/maintain well?
- Are there hidden dependencies?

### 3. **Risk Assessment**
- What could go wrong?
- Are there breaking changes?
- Impact on existing code?
- Test coverage adequate?

### 4. **Implementation Clarity**
- Is the plan detailed enough to implement?
- Are file/function names specified?
- Is the sequence of changes clear?
- Are acceptance criteria defined?

### 5. **Missing Elements**
- What's not addressed in the plan?
- Are there unstated assumptions?
- Dependencies on other tasks?
- Documentation needs?

---

## Proofreading Criteria (Teaching Content)

GPT-4o proofreads teaching content using these criteria:

### 1. **Clarity**
- Are explanations clear and understandable?
- Are complex ideas broken down effectively?
- Is jargon explained when first used?
- Can a developer unfamiliar with the topic follow along?

### 2. **Accuracy**
- Are facts, metrics, and claims correct?
- Are sources cited (file paths, task references, ADRs)?
- Are code examples correct and runnable?
- Are claims verifiable?

### 3. **Engagement**
- Is the content interesting to read?
- Does it maintain an approachable, conversational tone?
- Are there concrete examples and stories?
- Does it avoid being too dry or academic?

### 4. **Pedagogical Structure**
- Does it teach effectively (concept → example → practice)?
- Is there a logical progression of ideas?
- Is the depth appropriate for the target audience?
- Are key takeaways clear?

### 5. **Completeness**
- Are all key concepts covered?
- Is important information missing?
- Is there too much or too little detail?
- Does it answer likely reader questions?

### 6. **Examples**
- Are examples real (not contrived/toy examples)?
- Do examples illustrate the concept effectively?
- Can examples be generalized to other contexts?
- Are code examples cited with file paths?

### 7. **Consistency**
- Voice: Second person, active voice, present tense?
- Terminology: Matches project glossary?
- Formatting: Consistent with style guide?
- Tone: Matches other teaching content?

**Style Guide Integration:**
- Automatically checks `.agent-context/documentation-style-guide.md` if present
- Automatically checks `.agent-context/agentive-development-glossary.md` if present
- Evaluates against these standards

**Does NOT evaluate for:**
- ❌ File/function names (teaching content, not code planning)
- ❌ Error handling in the document itself (unless evaluating code examples within)
- ❌ Implementation acceptance criteria (success criteria are learning outcomes)
- ❌ Technical architecture decisions

---

## Code Review Criteria

GPT-4o reviews implemented code using these criteria:

### 1. **Correctness**
- Does the code do what it's supposed to do?
- Are there logic errors or off-by-one bugs?
- Are edge cases handled correctly?
- Does it match the specification/requirements?

### 2. **Error Handling**
- Are errors caught and handled appropriately?
- Are error messages helpful for debugging?
- Is there proper cleanup on failure?
- Are exceptions used correctly (not for flow control)?

### 3. **Security**
- Are inputs validated and sanitized?
- Is there protection against injection attacks?
- Are secrets/credentials handled safely?
- Are permissions checked appropriately?

### 4. **Performance**
- Are there obvious inefficiencies (N+1 queries, unnecessary loops)?
- Is memory usage reasonable?
- Are there potential bottlenecks?
- Is caching used where appropriate?

### 5. **Maintainability**
- Is the code readable and well-structured?
- Are functions/methods appropriately sized?
- Is there unnecessary complexity?
- Are names descriptive and consistent?

### 6. **Test Coverage**
- Are critical paths tested?
- Are edge cases covered?
- Are tests meaningful (not just for coverage)?
- Are test failures informative?

---

## Verdict Types

GPT-4o will provide one of three verdicts (applies to both `evaluate` and `proofread`):

### ✅ APPROVED
- **Meaning**: Content is sound, proceed to next step
- **Action**:
  - **Evaluation:** Assign task to specialized agent
  - **Proofreading:** Publish or commit document
- **Note**: May include minor suggestions or "watch for X"

### ⚠️ NEEDS_REVISION
- **Meaning**: Significant issues that need fixing
- **Action**: Address feedback and re-run command
- **Common Issues**:
  - **Evaluation:** Missing error handling, unclear dependencies, incomplete requirements
  - **Proofreading:** Confusing explanations, missing citations, style inconsistencies

### ❌ REJECT
- **Meaning**: Fundamental problems, major rework needed
- **Action**:
  - **Evaluation:** Redesign approach from scratch
  - **Proofreading:** Rewrite content with different structure/examples
- **Rare**: Usually only for fundamentally broken content

---

## Cost Expectations

### Evaluation (`adversarial evaluate`)

**Per Evaluation:**
- $0.04-0.05 (GPT-4o via OpenAI API)

**Typical Workflow:**
- $0.10-0.15 (2-3 evaluation rounds)

**File Size Limit:**
- ~988 lines may hit rate limits on Tier 1 OpenAI accounts (30k TPM limit)
- Files >500 lines require interactive confirmation

---

### Proofreading (`adversarial proofread`)

**Per Proofreading:**
- $0.01-0.02 (GPT-4o via OpenAI API, typically smaller documents)

**Typical Workflow:**
- $0.02-0.04 (1-2 proofreading rounds, teaching content stabilizes faster)

**File Size Limit:**
- Same as evaluation: ~988 lines may hit rate limits
- Files >500 lines require interactive confirmation
- Most teaching documents are <300 lines, well within limits

---

### Code Review (`adversarial review`)

**Per Review:**
- $0.02-0.05 (GPT-4o via OpenAI API, depends on code size)

**Typical Workflow:**
- $0.04-0.10 (1-2 review rounds, code often has concrete fixes)

**File Size Limit:**
- Same as evaluation: ~988 lines may hit rate limits
- Review directories to batch related files
- Can provide task context for better review accuracy

---

## Iteration Guidance

### For Plan Evaluation: 2-3 Rounds Optimal

**When to Stop Iterating:**

1. ✅ All CRITICAL/HIGH concerns addressed
2. ✅ GPT-4o asking for implementation-level details (beyond planning scope)
3. ✅ Diminishing returns on planning detail
4. ✅ Manual planner review approves plan (planner override)

**Planner Override:**
The planner can approve NEEDS_REVISION plans when:
- Remaining issues are implementation-level details
- GPT-4o is requesting specifics that will be resolved during coding
- 2-3 rounds completed and plan is "good enough"
- User needs to start implementation for time-sensitive work

---

### For Proofreading: 1-2 Rounds Optimal

**When to Stop Iterating:**

1. ✅ All CRITICAL/HIGH concerns addressed
2. ✅ Content is clear and accurate
3. ✅ Diminishing returns on wording tweaks
4. ✅ Manual agent/planner review approves content

**Agent Override:**
Agents can approve NEEDS_REVISION content when:
- Remaining issues are minor style preferences
- GPT-4o is suggesting cosmetic changes
- 1-2 rounds completed and content teaches effectively
- Time-sensitive publication needed

**Note:** Teaching content typically stabilizes faster than code plans (fewer iterations needed).

---

## Known Issues

### 1. Wrapper Verdict Bug
**Issue**: CLI wrapper may report "✅ Evaluation approved!" even when GPT-4o verdict is NEEDS_REVISION
**Solution**: **Always check the log file** for the actual verdict
**File**: `.adversarial/logs/TASK-*-PLAN-EVALUATION.md`

### 2. Large Files & Rate Limiting
**Issue**: Files >500 lines may fail or trigger authentication issues on Tier 1 OpenAI accounts (30k TPM limit)
**Symptoms**:
- OpenRouter authentication window opens unexpectedly
- "Invalid authorization header" errors
- Aider falls back to alternative providers
**Root Cause**: When OpenAI rate limits are hit, Aider attempts to use OpenRouter as fallback
**Solution**:
- Break large tasks into smaller subtasks (recommended)
- Upgrade OpenAI account tier for higher rate limits
- Wait a few minutes and retry if transient rate limit hit
**Note**: If OpenRouter auth window appears, the issue is likely a large file triggering OpenAI rate limits, not an invalid API key

### 3. Interactive Mode
**Issue**: Command requires interactive confirmation for large files (>500 lines)
**Solution**: Use `echo y | adversarial evaluate <task-file>` to automatically confirm the evaluation

### 4. Git Warning
**Issue**: May show "Unable to list files in git repo: BadObject" warning
**Solution**: Ignore - non-critical, Aider still functions correctly
**Context**: Related to git history cleanup, doesn't affect evaluations

---

## Best Practices

### ✅ DO:

**For Plan Evaluation:**
- Use `evaluate` for **high-level plan validation** (not implementation details)
- Address **CRITICAL and HIGH priority feedback** first
- Focus on **GPT-4o's questions**, not just the verdict
- Manual **planner approval supersedes** GPT-4o verdict when appropriate

**For Proofreading:**
- Use `proofread` for **teaching content** (not code plans)
- Address **clarity and accuracy issues** first
- Focus on **pedagogical effectiveness**
- Manual **agent approval supersedes** GPT-4o verdict when appropriate

**For Both:**
- Always check `.adversarial/logs/` file for actual verdict (wrapper may lie)
- Choose the right mode: `evaluate` for code, `proofread` for teaching

### ⚠️ USE JUDGMENT:

- MEDIUM/LOW feedback may be minor preferences (not worth extensive revision)
- Don't iterate indefinitely - use judgment after optimal rounds
- Balance thoroughness with velocity
- Consider cost vs value for large documents

### ❌ DON'T:

- Don't use Task tool to invoke these commands (GPT-4o is external via CLI, not a Claude agent)
- Don't confuse "new tabs" instruction (for manual user review) with adversarial workflow (external GPT-4o)
- Don't use `evaluate` on teaching content (use `proofread`)
- Don't use `proofread` on code plans (use `evaluate`)
- Don't skip for complex/risky content
- Don't ignore CRITICAL concerns from GPT-4o

---

## Example Output

### Evaluation Example

**Location:** `.adversarial/logs/TASK-2025-0037-PLAN-EVALUATION.md`

**Verdict:** NEEDS_REVISION

**Sample Concerns:**
- **[CRITICAL]** Error handling - No strategy for IPC communication failures
- **[MEDIUM]** Testing strategies - Edge cases not specified
- **[LOW]** Dependency management - Version conflicts not documented

---

### Proofreading Example

**Location:** `.adversarial/logs/concept-PROOFREADING.md`

**Verdict:** NEEDS_REVISION

**Sample Concerns:**
- **[HIGH]** Lacks citations for claims (affects credibility)
- **[MEDIUM]** Could benefit from interactive elements (engagement)
- **[LOW]** Some sections could be more concise (readability)

**Questions:**
- What is the target audience's familiarity level?
- Are there specific real-world applications to include?

---

### Common Output Format (Both Modes)

Markdown with structured sections:
1. **Evaluation Summary** (Verdict, Confidence)
2. **Strengths** (What content does well)
3. **Concerns & Risks** (Prioritized: CRITICAL/HIGH/MEDIUM/LOW)
4. **Missing or Unclear** (Gaps in content)
5. **Specific Recommendations** (Actionable improvements)
6. **Questions for Author** (Clarifications needed)
7. **Approval Conditions** (What needs fixing for APPROVED)

---

## Recent Usage

### Plan Evaluations
- **2025-11-01**: TASK-2025-0037 evaluation (Electron scaffold) - NEEDS_REVISION (error handling, testing, dependencies)
- **2025-10-31**: Batch evaluation of 8 GUI tasks (Option C execution)
- **2025-10-30**: TASK-2025-0040, TASK-2025-0038 evaluations
- **2025-10-24**: TASK-2025-026 verification (3-round cycle testing)

### Proofreading
- **2025-11-14**: concept.md (structured AI collaboration) - NEEDS_REVISION (citations, engagement, conciseness) - $0.01
- **First proofreading**: Validated teaching-focused feedback vs code-focused (no file names, error handling mentioned)

---

## Documentation References

### Configuration:
- **Config file**: `.adversarial/config.yml` (evaluator_model: gpt-4o)
- **CLI location**: `/Library/Frameworks/Python.framework/Versions/3.11/bin/adversarial`

### Related Documentation:
- **Verification report**: `.agent-context/ADVERSARIAL-VERIFICATION.md` (280 lines)
- **Workflow verification**: `delegation/handoffs/EVALUATOR-WORKFLOW-VERIFICATION-2025-10-24.md` (293 lines)
- **Evaluation logs**: `.adversarial/logs/TASK-*-PLAN-EVALUATION.md` (all evaluations)
- **Proofreading logs**: `.adversarial/logs/*-PROOFREADING.md` (all proofreading)
- **Evaluation wrapper script**: `.adversarial/scripts/evaluate_plan.sh`
- **Proofreading wrapper script**: `.adversarial/scripts/proofread_content.sh`
- **Bugfix docs**: `.adversarial/docs/BUGFIX-OUTPUT-CAPTURE.md` (tee output capture fix)
- **ADR**: `docs/decisions/adr/ADR-0011-adversarial-workflow-integration.md`

### Quick Reference:
- **Procedural index**: `.agent-context/PROCEDURAL-KNOWLEDGE-INDEX.md` → Planner Procedures → Evaluation Workflow
- **Style guide**: `.agent-context/documentation-style-guide.md` (used by proofreader)
- **Glossary**: `.agent-context/agentive-development-glossary.md` (used by proofreader)

---

## Quick Command Reference

```bash
# Plan Evaluation (for code/architecture)
adversarial evaluate delegation/tasks/2-todo/TASK-FILE.md
cat .adversarial/logs/TASK-*-PLAN-EVALUATION.md

# Proofreading (for teaching content)
adversarial proofread docs/guide/concept.md
cat .adversarial/logs/concept-PROOFREADING.md

# Code Review (for implemented code)
adversarial review src/feature/module.py
adversarial review src/feature/ --context delegation/tasks/3-in-progress/TASK-0001.md
cat .adversarial/logs/module-CODE-REVIEW.md

# Discovery & Custom Evaluators
adversarial list-evaluators              # Show all available evaluators
# Custom evaluators: .adversarial/evaluators/*.yml

# System Commands
adversarial --version                    # Check CLI version
adversarial check                        # Validate setup and dependencies
adversarial evaluate --help              # Get evaluation help
adversarial proofread --help             # Get proofreading help
adversarial review --help                # Get code review help
```

---

**Last Updated**: 2025-01-27
**Maintained By**: Planner and feature-developer agents
**Questions?** See PROCEDURAL-KNOWLEDGE-INDEX.md or ask user
