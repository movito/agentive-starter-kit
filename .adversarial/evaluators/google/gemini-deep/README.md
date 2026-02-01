# Gemini Deep Think Evaluator

Extended reasoning evaluator for complex analysis and deep thinking.

## Use Cases

- Complex policy analysis requiring deep reasoning
- Multi-step logical evaluation
- Critical thinking and assumption testing
- Counter-argument development
- Second-order effect analysis

## Performance

| Metric | Value |
|--------|-------|
| Typical response time | 90-300 seconds |
| Timeout setting | 600 seconds |
| Cost | ~$0.01-0.03 per evaluation |

## When to Use

**Best for:**
- Complex arguments needing thorough analysis
- Finding hidden assumptions
- Developing counter-arguments
- Policy document stress-testing

**Not ideal for:**
- Quick checks (use gemini-flash)
- Very large documents (use gemini-pro)
- Factual verification (use o3-chain)

## Configuration

```yaml
api_key_env: GEMINI_API_KEY
```

## Related Evaluators

- `gpt52-reasoning` - Alternative deep reasoning (OpenAI)
- `o3-chain` - Chain-of-thought verification
- `gemini-flash` - Quick preliminary check
