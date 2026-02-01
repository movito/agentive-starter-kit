# Mistral Fast Evaluator

Fast review evaluator using Mistral Small.

## Use Cases

- Fast review for larger documents
- When mistral-large times out
- Quick cognitive diversity check
- High-volume processing with Mistral perspective

## Performance

| Metric | Value |
|--------|-------|
| Typical response time | 30-60 seconds |
| Timeout setting | 300 seconds |
| Cost | ~$0.005-0.02 per evaluation |

## When to Use

**Best for:**
- Large documents that timeout with mistral-large
- Quick Mistral-perspective check
- Budget-conscious multi-model reviews

**Trade-offs:**
- Less detailed than mistral-content
- Better for structure than deep analysis

## Configuration

```yaml
api_key_env: MISTRAL_API_KEY
```

## Related Evaluators

- `mistral-content` - Full-featured Mistral review
- `gemini-flash` - Alternative fast evaluator
- `fast-check` - OpenAI fast evaluator
