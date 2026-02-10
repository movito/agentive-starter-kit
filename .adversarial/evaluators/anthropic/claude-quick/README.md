# Claude 4 Haiku Quick Check Evaluator

Fast validation using Claude 4 Haiku for rapid initial screening.

## Use Cases

- Quick formatting checks
- Basic code validation
- Pre-submission sanity check
- Rapid issue detection
- High-volume screening
- CI/CD pipeline validation

## Performance

| Metric | Value |
| -------- | ----- |
| Typical response time | 5-15 seconds |
| Timeout setting | 90 seconds |
| Cost | ~$0.001-0.005 per evaluation |

## When to Use

**Best for:**
- Initial screening before detailed review
- High-volume automated checks
- CI/CD integration
- Quick sanity checks
- Cost-sensitive validation

**Not ideal for:**
- Detailed security review (use claude-code)
- Adversarial analysis (use claude-adversarial)
- Complex logic verification (use o3-chain)

## Detection Capabilities

This evaluator catches obvious issues:
- Syntax errors and typos
- Hardcoded secrets
- Placeholder text
- Broken references
- Incomplete sections

For comprehensive security analysis, use claude-code or o1-code-review.

## Configuration

```yaml
api_key_env: ANTHROPIC_API_KEY
model: claude-4-haiku-20260115
```

## Example Usage

```bash
adversarial evaluate --evaluator claude-quick draft-document.md
```

## Output Format

Findings use standardized severity labels:
- **CRITICAL**: Blocking issues, must fix immediately
- **HIGH**: Significant issues to address
- **MEDIUM**: Should fix before proceeding
- **LOW**: Minor improvements

Optimized for quick scanning with brief, actionable feedback.

## Related Evaluators

- `fast-check` - OpenAI equivalent (GPT-4o-mini)
- `mistral-fast` - Mistral equivalent
- `gemini-flash` - Google equivalent
- `claude-code` - Detailed Anthropic code review
