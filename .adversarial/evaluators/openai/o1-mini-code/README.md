# o1-mini-code

Cost-effective reasoning-based code review using OpenAI o1-mini.

## Overview

This evaluator uses OpenAI's o1-mini model to provide thorough code review with step-by-step reasoning at a fraction of the cost of o1. It's ideal for regular PR reviews where you want more depth than GPT-4o but don't need full security audit capabilities.

## Use Cases

- **PR code reviews**: Systematic review of pull requests
- **Bug detection**: Finding logic errors and edge cases
- **Logic verification**: Ensuring code does what it claims
- **Test coverage analysis**: Identifying gaps in testing
- **Refactoring suggestions**: Spotting improvement opportunities

## Model

- **Model**: `o1-mini`
- **Provider**: OpenAI
- **Category**: code-review
- **Timeout**: 300s

## Cost Estimate

~$0.01-0.05 per review. Approximately 10x cheaper than o1.

Best balance of reasoning capability and cost for routine code review.

## Example Usage

```bash
# Review a PR's changed files
adversarial evaluate --evaluator o1-mini-code changed_files/

# Review a module
adversarial evaluate --evaluator o1-mini-code src/utils/

# Review specific file
adversarial evaluate --evaluator o1-mini-code api_handler.py
```

## Output

The evaluator produces:

1. **Code Understanding** summary
2. **Issues Found** with severity levels:
   - 🔴 CRITICAL: Security flaw or data loss risk
   - 🟠 HIGH: Bug that will cause failures
   - 🟡 MEDIUM: Bug in edge cases or code smell
   - 🟢 LOW: Style/maintainability suggestion
3. **Summary** with issue counts
4. **Verdict**: APPROVED, CHANGES_REQUESTED, or REJECT

## When to Use

| Scenario | Use o1-mini-code? |
|----------|-------------------|
| Regular PR reviews | ✅ Yes |
| Bug hunting | ✅ Yes |
| Logic verification | ✅ Yes |
| Security audit | ❌ Use o1-code-review |
| Quick sanity check | ❌ Use gpt4o-code |

## See Also

- [o1-code-review](../o1-code-review/) - Deep security analysis
- [gpt4o-code](../gpt4o-code/) - Fast general review
- [codestral-code](../../mistral/codestral-code/) - Mistral code review
