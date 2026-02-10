# Claude 4 Opus Adversarial Evaluator

Rigorous adversarial review using Claude 4 Opus for critical analysis and stress-testing.

## Use Cases

- Final document review before publication
- Critical argument stress-testing
- High-stakes deliverable validation
- Adversarial red-teaming
- Finding logical weaknesses and gaps

## Performance

| Metric | Value |
| -------- | ----- |
| Typical response time | 30-60 seconds |
| Timeout setting | 180 seconds |
| Cost | ~$0.03-0.10 per evaluation |

## When to Use

**Best for:**
- High-stakes final reviews
- Finding logical weaknesses
- Adversarial stress-testing
- Policy and strategy documents
- Validating critical decisions

**Not ideal for:**
- Quick checks (use claude-quick)
- Code-specific review (use claude-code)
- Very large documents (use gemini-pro)

## Cognitive Diversity Note

This evaluator provides Anthropic's perspective on adversarial analysis. Use alongside OpenAI's gpt52-reasoning for maximum blind-spot coverage through multi-provider review.

## Configuration

```yaml
api_key_env: ANTHROPIC_API_KEY
model: claude-4-opus-20260115
```

## Example Usage

```bash
adversarial evaluate --evaluator claude-adversarial policy-doc.md
```

## Output Format

Findings use standardized severity labels:
- **CRITICAL**: Must fix before proceeding
- **HIGH**: Significant issues requiring attention
- **MEDIUM**: Should address but not blocking
- **LOW**: Minor improvements

Each finding includes location, issue description, and remediation steps.

## Related Evaluators

- `gpt52-reasoning` - OpenAI alternative for adversarial review
- `claude-code` - Code-focused review (same provider)
- `o3-chain` - For step-by-step logical verification
