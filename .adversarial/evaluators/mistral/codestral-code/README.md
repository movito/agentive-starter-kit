# Codestral Code Review Evaluator

Code-focused review using Mistral's code-specialized model.

## Use Cases

- Script and automation review
- Data processing pipeline validation
- Configuration file analysis
- Calculation and formula verification
- Security review for code

## Performance

| Metric | Value |
|--------|-------|
| Typical response time | 30-60 seconds |
| Timeout setting | 300 seconds |
| Cost | ~$0.01-0.03 per evaluation |

## When to Use

**Best for:**
- Python, JavaScript, shell scripts
- Configuration files (YAML, JSON, TOML)
- Data processing code
- Financial calculations in code

**Not ideal for:**
- Prose documents (use mistral-content)
- Very large codebases (review file-by-file)

## Configuration

```yaml
api_key_env: MISTRAL_API_KEY
```

## Related Evaluators

- `o3-chain` - For numerical verification in docs
- `mistral-content` - For non-code documents
- `fast-check` - For quick formatting checks
