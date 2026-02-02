# Fast Check Evaluator

Quick validation for formatting and basic issues.

## Use Cases

- Quick formatting checks
- Basic consistency validation
- Link and reference verification
- Spelling and grammar review
- Pre-submission sanity check

## Performance

| Metric | Value |
|--------|-------|
| Typical response time | 10-15 seconds |
| Timeout setting | 180 seconds |
| Cost | ~$0.001-0.003 per evaluation |

## When to Use

**Best for:**
- First-pass before deeper review
- Catching obvious issues quickly
- High-volume document processing
- Gate before expensive evaluators

**Not ideal for:**
- Deep content analysis
- Logical verification
- Adversarial review

## Recommended Workflow

Use as first stage in multi-evaluator pipeline:
1. `fast-check` - Catch obvious issues
2. Fix any issues found
3. `gpt52-reasoning` or `gemini-deep` - Deep analysis

## Configuration

```yaml
api_key_env: OPENAI_API_KEY
```

## Related Evaluators

- `gemini-flash` - Alternative fast evaluator (Google)
- `gpt52-reasoning` - Deep review after fast-check passes
