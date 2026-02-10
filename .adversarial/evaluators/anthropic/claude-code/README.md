# Claude 4 Sonnet Code Review Evaluator

Security-focused code analysis using Claude 4 Sonnet for balanced thoroughness and speed.

## Use Cases

- Security vulnerability detection
- Code quality review
- Best practices validation
- Architecture review
- Configuration file analysis
- Script and automation review

## Performance

| Metric | Value |
| -------- | ----- |
| Typical response time | 20-40 seconds |
| Timeout setting | 180 seconds |
| Cost | ~$0.01-0.04 per evaluation |

## When to Use

**Best for:**
- Security code review
- Finding vulnerabilities (injection, XSS, etc.)
- Code quality assessment
- Pre-deployment validation
- Pull request reviews

**Not ideal for:**
- Quick formatting checks (use claude-quick)
- Document review (use claude-adversarial)
- Very large codebases (consider splitting)

## Vulnerability Detection

This evaluator checks for common vulnerability classes:
- SQL injection
- Command injection
- Cross-site scripting (XSS)
- Path traversal
- Hardcoded secrets
- Insecure authentication patterns

## Cognitive Diversity Note

This evaluator provides Anthropic's perspective on code security. For comprehensive coverage, combine with o1-code-review (OpenAI) or codestral-code (Mistral) to catch different vulnerability patterns.

## Configuration

```yaml
api_key_env: ANTHROPIC_API_KEY
model: claude-4-sonnet-20260115
```

## Example Usage

```bash
adversarial evaluate --evaluator claude-code src/api/handler.py
```

## Output Format

Findings use standardized severity labels:
- **CRITICAL**: Exploitable vulnerabilities, must fix immediately
- **HIGH**: Security issues requiring prompt attention
- **MEDIUM**: Code quality issues, should address
- **LOW**: Minor improvements and suggestions

Each finding includes file:line reference, issue description, and specific remediation.

## Related Evaluators

- `o1-code-review` - OpenAI deep reasoning code review
- `codestral-code` - Mistral code-focused review
- `gpt4o-code` - Fast OpenAI code review
- `claude-quick` - Fast Anthropic validation
