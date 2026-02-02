# Gemini Flash Evaluator

Fast, cost-effective evaluator for quick document assessment.

## Use Cases

- Quick document reviews and assessments
- Fast preliminary evaluations
- Cost-effective bulk processing
- Initial quality checks before deep review

## Performance

| Metric | Value |
|--------|-------|
| Typical response time | 6-15 seconds |
| Timeout setting | 180 seconds |
| Cost | ~$0.001-0.005 per evaluation |

## When to Use

**Best for:**
- First-pass review of any document
- High-volume processing where cost matters
- Quick sanity checks before submission

**Not ideal for:**
- Deep reasoning or complex analysis
- Adversarial review (use gpt52-reasoning)
- Large documents (use gemini-pro)

## Configuration

```yaml
api_key_env: GEMINI_API_KEY
```

Requires Google AI API key. Set in environment:
```bash
export GEMINI_API_KEY="your-key-here"
```

## Example Usage

```bash
adversarial evaluate evaluators/google/gemini-flash/evaluator.yml document.md
```

## Related Evaluators

- `gemini-pro` - For larger documents and knowledge synthesis
- `gemini-deep` - For extended reasoning tasks
- `fast-check` (OpenAI) - Alternative fast evaluator
