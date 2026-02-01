# Claude Adversarial Evaluator

Critical review and stress-testing evaluator using Claude Sonnet for high-stakes documents.

## Use Cases

- Final document review before publication
- Critical argument stress-testing
- Policy and strategy validation
- Adversarial red-team reviews
- High-stakes deliverable assessment

## Performance

| Metric | Value |
|--------|-------|
| Typical response time | 30-60 seconds |
| Timeout setting | 180 seconds |
| Cost | ~$0.02-0.06 per evaluation |

## When to Use

**Best for:**
- High-stakes final reviews
- Finding logical weaknesses
- Adversarial stress-testing
- Policy and strategy documents
- Validating critical decisions

**Not ideal for:**
- Quick preliminary checks (use claude-quick)
- Code-specific reviews (use claude-code)
- Very large documents >50k tokens (consider chunking)

## Cognitive Diversity Note

This evaluator provides an Anthropic perspective on adversarial review. For maximum blind-spot coverage, use alongside:
- `gpt52-reasoning` (OpenAI adversarial)
- `gemini-deep` (Google deep reasoning)

## Configuration

```yaml
api_key_env: ANTHROPIC_API_KEY
```

Get your API key at: https://console.anthropic.com/settings/keys

## Example Usage

```bash
# Review a task specification
adversarial claude-adversarial delegation/tasks/2-todo/my-task.md

# Review a design document
adversarial claude-adversarial docs/architecture.md
```

## Related Evaluators

- `gpt52-reasoning` - OpenAI adversarial (alternative perspective)
- `claude-code` - Code-focused Anthropic review
- `claude-quick` - Fast Anthropic assessment
- `gemini-deep` - Google deep reasoning
