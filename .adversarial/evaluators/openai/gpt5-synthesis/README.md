# GPT-5 Turbo Knowledge Synthesis Evaluator

Cross-reference and completeness validation using GPT-5 Turbo for comprehensive knowledge synthesis.

## Use Cases

- Synthesizing information across documents
- Cross-referencing multiple sources
- Knowledge gap identification
- Consistency checking across deliverables
- Research completeness verification
- Multi-document coherence analysis

## Performance

| Metric | Value |
| -------- | ----- |
| Typical response time | 25-50 seconds |
| Timeout setting | 180 seconds |
| Cost | ~$0.02-0.06 per evaluation |

## When to Use

**Best for:**
- Multi-section document review
- Verifying internal consistency
- Finding coverage gaps
- Cross-referencing claims
- Research synthesis validation

**Not ideal for:**
- Very large documents (use gemini-pro for 1M context)
- Quick checks (use fast-check)
- Code review (use code-focused evaluators)

## Synthesis Capabilities

This evaluator identifies:
- Internal contradictions
- Coverage gaps
- Inconsistent terminology
- Missing cross-references
- Unsynthesized patterns

## Why GPT-5 for Synthesis?

GPT-5 Turbo provides strong analytical capabilities for synthesis tasks. For very large document sets requiring extended context, combine with gemini-pro which offers 1M token context.

## Configuration

```yaml
api_key_env: OPENAI_API_KEY
model: gpt-5-turbo-2025-11-01
```

## Example Usage

```bash
adversarial evaluate --evaluator gpt5-synthesis research-report.md
```

## Output Format

Findings use standardized severity labels:
- **CRITICAL**: Major inconsistency or critical gap
- **HIGH**: Significant coverage issue to address
- **MEDIUM**: Notable gap worth filling
- **LOW**: Minor synthesis opportunity

Each finding identifies the inconsistency or gap and how to address it.

## Related Evaluators

- `gemini-pro` - Google synthesis with 1M context window
- `gpt5-diversity` - Alternative perspective analysis (same provider)
- `mistral-content` - Content structure review
