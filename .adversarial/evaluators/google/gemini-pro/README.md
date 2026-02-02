# Gemini Pro Knowledge Synthesis Evaluator

Large-context evaluator for synthesizing research across documents.

## Use Cases

- Synthesizing large document sets
- Cross-referencing multiple research outputs
- Knowledge gap identification
- Consistency checking across deliverables
- Research completeness verification

## Performance

| Metric | Value |
|--------|-------|
| Context window | 1M tokens |
| Typical response time | 45-120 seconds |
| Timeout setting | 400 seconds |
| Cost | ~$0.01-0.05 per evaluation |

## When to Use

**Best for:**
- Documents exceeding 50k tokens
- Multi-document synthesis
- Finding inconsistencies across large corpora
- Research quality validation

**Not ideal for:**
- Quick checks (use gemini-flash)
- Deep reasoning on small docs (use gemini-deep)
- Adversarial review (use gpt52-reasoning)

## Configuration

```yaml
api_key_env: GEMINI_API_KEY
```

## Example Usage

```bash
# Single large document
adversarial evaluate evaluators/google/gemini-pro/evaluator.yml large-doc.md

# Multiple documents (concatenate first)
cat docs/*.md > combined.md
adversarial evaluate evaluators/google/gemini-pro/evaluator.yml combined.md
```

## Related Evaluators

- `gemini-flash` - For quick preliminary checks
- `gemini-deep` - For extended reasoning on complex content
