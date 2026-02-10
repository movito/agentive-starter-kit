# o1-code-review

Deep reasoning code review using OpenAI o1.

## Overview

This evaluator uses OpenAI's o1 model with extended reasoning capabilities to perform thorough security and correctness analysis of code. It excels at finding subtle issues that surface-level review would miss.

## Use Cases

- **Security audits**: Deep analysis of authentication, authorization, and data handling
- **Complex bug finding**: Reasoning through edge cases and race conditions
- **Architecture review**: Evaluating design decisions and patterns
- **Critical code paths**: Thorough review of payment, auth, or data processing code

## Model

- **Model**: `o1`
- **Provider**: OpenAI
- **Category**: code-review
- **Timeout**: 600s (extended for deep reasoning)

## Cost Estimate

~$0.15-0.50 per review depending on code size.

Use this evaluator for critical code where thoroughness matters more than speed.

## Example Usage

```bash
# Review critical authentication code
adversarial evaluate --evaluator o1-code-review src/auth/

# Review payment processing
adversarial evaluate --evaluator o1-code-review payment_handler.py
```

## Output

The evaluator produces:

1. **Critical Issues** table with attack vectors and impact
2. **High Priority Issues** with risk assessment
3. **Medium/Low Issues** list
4. **Positive Observations** on security measures done well
5. **Verdict**: APPROVED, CHANGES_REQUESTED, or REJECT

## When to Use

| Scenario | Use o1-code-review? |
|----------|---------------------|
| Security-critical code | ✅ Yes |
| Payment/financial logic | ✅ Yes |
| Authentication/authorization | ✅ Yes |
| Quick PR review | ❌ Use gpt4o-code |
| Large codebase scan | ❌ Use o1-mini-code |

## See Also

- [o1-mini-code](../o1-mini-code/) - Cost-effective alternative
- [gpt4o-code](../gpt4o-code/) - Fast general review
- [codestral-code](../../mistral/codestral-code/) - Mistral code review
