# gpt4o-code

Fast, comprehensive code quality review using GPT-4o.

## Overview

This evaluator uses OpenAI's GPT-4o for quick but thorough code quality reviews. It's the go-to choice for everyday PR reviews where speed matters and you want comprehensive coverage of code quality, documentation, and basic security checks.

## Use Cases

- **Quick PR reviews**: Fast turnaround on code changes
- **Code style consistency**: Ensuring patterns are followed
- **Documentation completeness**: Checking docs and comments
- **Pattern adherence**: Verifying best practices
- **General quality checks**: Catching common issues

## Model

- **Model**: `gpt-4o`
- **Provider**: OpenAI
- **Category**: code-review
- **Timeout**: 180s

## Cost Estimate

~$0.01-0.03 per review. Fast and economical for routine reviews.

## Example Usage

```bash
# Quick review of a file
adversarial evaluate --evaluator gpt4o-code myfile.py

# Review multiple files
adversarial evaluate --evaluator gpt4o-code src/*.py

# Review before commit
adversarial evaluate --evaluator gpt4o-code $(git diff --name-only)
```

## Output

The evaluator produces:

1. **Issues** organized by severity:
   - 🔴 Critical
   - 🟠 Should Fix
   - 🟡 Consider
2. **What's Good** - positive observations
3. **Quick Stats** - files reviewed, issue counts
4. **Verdict**: APPROVED, CHANGES_REQUESTED, or REJECT

## Review Checklist

The evaluator checks:
- Code quality (SRP, naming, duplication)
- Error handling
- Documentation
- Testing
- Security basics
- Performance

## When to Use

| Scenario | Use gpt4o-code? |
|----------|-----------------|
| Quick PR review | ✅ Yes |
| Pre-commit check | ✅ Yes |
| Style/pattern review | ✅ Yes |
| Deep security audit | ❌ Use o1-code-review |
| Complex logic verification | ❌ Use o1-mini-code |

## See Also

- [o1-code-review](../o1-code-review/) - Deep security analysis
- [o1-mini-code](../o1-mini-code/) - Reasoning-based review
- [fast-check](../fast-check/) - Even faster basic checks
