# AEL-0005 Handoff: Phase 1 Evaluator Implementation

**Task**: `delegation/tasks/3-in-progress/AEL-0005-phase1-evaluator-implementation.md`
**Prepared by**: Planner
**Date**: 2026-02-01

## Context

Phase 1 of the multi-evaluator expansion adds 6 new evaluators to achieve full provider coverage. This follows ASK-0029 which established the infrastructure.

## Implementation Sequence

### Phase 1: Anthropic Provider (3 evaluators)

Create `anthropic/` provider directory with:

1. **claude-adversarial** - Category: adversarial
   - Model: `anthropic/claude-sonnet-4-20250514`
   - Purpose: Critical document review, stress-testing arguments
   - Complements: gpt52-reasoning (OpenAI alternative)

2. **claude-code** - Category: code-review
   - Model: `anthropic/claude-sonnet-4-20250514`
   - Purpose: Code and configuration analysis
   - Complements: codestral-code (Mistral alternative)

3. **claude-quick** - Category: quick-check
   - Model: `anthropic/claude-3-5-haiku-20241022`
   - Purpose: Fast, cost-effective preliminary checks
   - Complements: fast-check, gemini-flash, mistral-fast

### Phase 2: Google Expansion (1 evaluator)

4. **gemini-code** - Category: code-review
   - Model: `gemini/gemini-2.5-flash`
   - Purpose: Code review with multimodal capability
   - Unique: Can analyze code alongside screenshots/diagrams

### Phase 3: OpenAI Expansion (2 evaluators)

5. **gpt5-diversity** - Category: cognitive-diversity
   - Model: `gpt-5.2`
   - Purpose: Alternative perspective, reduce blind spots
   - Complements: mistral-content

6. **gpt5-synthesis** - Category: knowledge-synthesis
   - Model: `gpt-5.2`
   - Purpose: Cross-reference verification, knowledge synthesis
   - Complements: gemini-pro (large context)

### Phase 4: Index Update

Update `index.json` to include all 6 new evaluators with correct:
- name, provider, path, model, category, description

Add `anthropic` to providers section with `api_key_env: ANTHROPIC_API_KEY`

## File Templates

### evaluator.yml Template

```yaml
# [Evaluator Name]
# [Brief description]
#
# Provider: [provider]
# Use cases:
#   - [Use case 1]
#   - [Use case 2]

name: [evaluator-name]
description: [One-line description]
model: [provider/model-id or model-id]
api_key_env: [PROVIDER]_API_KEY
output_suffix: -[evaluator-name].md
timeout: [seconds]

prompt: |
  [System prompt with {content} placeholder]
```

### README.md Template

```markdown
# [Evaluator Name]

[Brief description]

## Use Cases

- [Use case 1]
- [Use case 2]

## Performance

| Metric | Value |
|--------|-------|
| Typical response time | [X] seconds |
| Timeout setting | [Y] seconds |
| Cost | ~$[X]-[Y] per evaluation |

## When to Use

**Best for:**
- [Scenario 1]

**Not ideal for:**
- [Scenario 1]

## Configuration

\`\`\`yaml
api_key_env: [PROVIDER]_API_KEY
\`\`\`

## Example Usage

\`\`\`bash
adversarial [evaluator-name] document.md
\`\`\`

## Related Evaluators

- [Related evaluator 1]
```

## Prompt Design Guidelines

### Adversarial Evaluators
- Challenge every claim
- Demand evidence for assertions
- Look for logical weaknesses
- Provide specific improvement suggestions
- End with APPROVED / NEEDS_REVISION / REJECT verdict

### Code Review Evaluators
- Check for security vulnerabilities
- Verify error handling
- Assess maintainability
- Look for edge cases
- Suggest concrete improvements

### Quick Check Evaluators
- Focus on obvious issues
- Keep responses concise
- Prioritize actionable feedback
- Don't over-analyze

### Diversity Evaluators
- Provide alternative perspectives
- Challenge assumptions
- Consider different stakeholder viewpoints
- Avoid groupthink

### Synthesis Evaluators
- Cross-reference related content
- Verify consistency
- Identify gaps in coverage
- Suggest integrations

## Success Criteria

1. All 6 evaluator directories created with correct structure
2. All YAML files parse without error
3. index.json updated with all 6 entries
4. Each README.md provides clear usage guidance
5. `adversarial list-evaluators` shows 15+ evaluators

## Commands to Run

```bash
# Start task
./scripts/project start AEL-0005

# Verify YAML syntax
for f in .adversarial/evaluators/anthropic/*/evaluator.yml; do
  python -c "import yaml; yaml.safe_load(open('$f'))" && echo "✓ $f"
done

# List evaluators
adversarial list-evaluators

# Run tests
pytest tests/ -v
./scripts/ci-check.sh
```

---

Ready for implementation by feature-developer agent.
