# o3 Chain-of-Thought Evaluator

Multi-step reasoning for complex logical and numerical analysis.

## Use Cases

- Complex calculations verification
- Multi-step scenario analysis
- Regulatory interpretation checking
- Numerical validation
- Logical argument step-by-step verification

## Performance

| Metric | Value |
|--------|-------|
| Typical response time | 30-40 seconds |
| Timeout setting | 180 seconds |
| Cost | ~$0.03-0.10 per evaluation |

## When to Use

**Best for:**
- Documents with calculations or numbers
- Multi-step logical arguments
- Financial or technical analysis
- Verifying "show your work" style content

**Not ideal for:**
- Narrative content without calculations
- Quick formatting checks (use fast-check)
- Large documents without numerical content

## Configuration

```yaml
api_key_env: OPENAI_API_KEY
```

## Related Evaluators

- `gpt52-reasoning` - For adversarial argument review
- `fast-check` - For quick validation
- `codestral-code` - For code/script verification
