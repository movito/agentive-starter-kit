# GPT-5.2 Deep Reasoning Evaluator

Primary adversarial evaluator for critical document review.

## Use Cases

- Final document review before publication
- Critical argument stress-testing
- High-stakes deliverable validation
- Complex multi-factor analysis
- Devils-advocate reviews

## Performance

| Metric | Value |
|--------|-------|
| Typical response time | 30-45 seconds |
| Timeout setting | 180 seconds |
| Cost | ~$0.02-0.08 per evaluation |

## When to Use

**Best for:**
- High-stakes final reviews
- Finding logical weaknesses
- Adversarial stress-testing
- Policy and strategy documents

**Not ideal for:**
- Quick checks (use fast-check)
- Numerical verification (use o3-chain)
- Very large documents (use gemini-pro)

## Cognitive Diversity Note

This evaluator provides a different perspective than Claude-based reviews. Use it alongside Claude analysis for maximum blind-spot coverage.

## Configuration

```yaml
api_key_env: OPENAI_API_KEY
```

## Example Usage

```bash
adversarial evaluate evaluators/openai/gpt52-reasoning/evaluator.yml policy-doc.md
```

## Related Evaluators

- `o3-chain` - For step-by-step logical verification
- `mistral-content` - Alternative perspective (European training)
- `gemini-deep` - Alternative deep reasoning (Google)
