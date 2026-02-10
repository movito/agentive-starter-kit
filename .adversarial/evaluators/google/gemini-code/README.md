# Gemini 3 Pro Code Review Evaluator

Code-focused security and quality review using Google's Gemini 3 Pro.

## Use Cases

- Security vulnerability detection
- Code quality analysis
- Script and automation review
- Configuration validation
- Multi-file codebase review
- Pull request reviews

## Performance

| Metric | Value |
| -------- | ----- |
| Typical response time | 20-45 seconds |
| Timeout setting | 180 seconds |
| Cost | ~$0.01-0.04 per evaluation |

## When to Use

**Best for:**
- Security-focused code review
- Finding injection vulnerabilities
- Code quality assessment
- Large context analysis (leverages Gemini's context window)

**Not ideal for:**
- Quick checks (use gemini-flash)
- Document review (use gemini-pro)
- Deep reasoning chains (use gemini-deep)

## Vulnerability Detection

This evaluator checks for:
- SQL injection
- Command injection
- Cross-site scripting (XSS)
- Path traversal
- Hardcoded secrets
- Authentication bypass
- Resource leaks

## Cognitive Diversity Note

This evaluator provides Google's perspective on code security. Combine with claude-code (Anthropic) or o1-code-review (OpenAI) for multi-provider coverage that catches different vulnerability patterns.

## Configuration

```yaml
api_key_env: GEMINI_API_KEY
model: gemini-3-pro-20260101
```

## Example Usage

```bash
adversarial evaluate --evaluator gemini-code src/api/handler.py
```

## Output Format

Findings use standardized severity labels:
- **CRITICAL**: Exploitable vulnerabilities, must fix immediately
- **HIGH**: Security issues requiring prompt attention
- **MEDIUM**: Code quality issues, should address
- **LOW**: Minor improvements and suggestions

Each finding includes file:line reference, issue description, and specific remediation.

## Related Evaluators

- `claude-code` - Anthropic code review
- `o1-code-review` - OpenAI deep reasoning code review
- `codestral-code` - Mistral code-focused review
- `gemini-flash` - Fast Google validation
