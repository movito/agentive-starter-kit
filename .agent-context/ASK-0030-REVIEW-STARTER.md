# Review Starter: ASK-0030

**Task**: ASK-0030 - Python Version Ceiling Check
**Task File**: `delegation/tasks/5-done/ASK-0030-python-version-ceiling.md`
**Branch**: feature/ASK-0030-python-version-ceiling → main
**PR**: https://github.com/movito/agentive-starter-kit/pull/10

## Implementation Summary

Added Python version ceiling check (`>=3.10,<3.13`) to prevent cryptic pip errors when users run `./scripts/project setup` on Python 3.13+. The constraint comes from aider-chat dependency in adversarial-workflow.

This PR also includes:
- Task cleanup for ASK-0029, ASK-0031 (verified already implemented)
- Multi-evaluator configs from evaluator library
- BugBot/CodeRabbit feedback fixes

## Files Changed

### Core Changes (ASK-0030)
- `scripts/project` - Added version ceiling check in `cmd_setup()` with clear error messages
- `scripts/verify-setup.sh` - Updated to check `>=3.10,<3.13`
- `pyproject.toml` - Added `requires-python = ">=3.10,<3.13"`

### New Files (Evaluator Configs)
- `.adversarial/evaluators/anthropic/claude-adversarial/` - Anthropic evaluator
- `.adversarial/evaluators/google/{gemini-deep,gemini-flash,gemini-pro}/` - Google evaluators
- `.adversarial/evaluators/mistral/{codestral-code,mistral-content,mistral-fast}/` - Mistral evaluators
- `.adversarial/evaluators/openai/{fast-check,gpt52-reasoning,o3-chain}/` - OpenAI evaluators
- `.adversarial/evaluators/index.json` - Evaluator registry

### Modified Files
- `.claude/agents/onboarding.md` - Shell-aware venv activation, Python 3.10+ mention
- `docs/decisions/starter-kit-adr/KIT-ADR-0005-test-infrastructure-strategy.md` - Date fixes
- `tests/test_project_script.py` - New version check tests with proper mocking
- `tests/test_linear_sync.py` - Removed unused noqa directive

### Task Files Moved to Done
- `ASK-0028-venv-setup-command.md`
- `ASK-0029-multi-evaluator-architecture.md`
- `ASK-0030-python-version-ceiling.md`
- `ASK-0031-venv-activation-ux.md`

## Test Results

```
75 passed, 12 skipped in 1.25s

New tests added:
- TestPythonVersionCheck::test_python_too_old_error
- TestPythonVersionCheck::test_python_too_new_error
- TestPythonVersionCheck::test_python_future_version_error
- TestPythonVersionCheck::test_python_3_12_proceeds
- TestPythonVersionCheck::test_python_3_10_proceeds
```

## CI Status

- GitHub Actions: ✅ All passing
- BugBot: ✅ Issues addressed (removed duplicate evaluator configs)
- CodeRabbit: ✅ Major issues addressed (nitpicks remain)

## Areas for Review Focus

1. **Version check logic** (`scripts/project:297-323`): Verify the bounds are correct and error messages are helpful
2. **Test mocking** (`tests/test_project_script.py:376-420`): Ensure subprocess/Path mocks properly isolate tests
3. **Evaluator registry** (`.adversarial/evaluators/index.json`): Verify all providers and evaluators are correctly indexed

## Related Documentation

- **Task file**: `delegation/tasks/5-done/ASK-0030-python-version-ceiling.md`
- **Handoff**: `.agent-context/ASK-0030-HANDOFF-feature-developer.md`
- **Related tasks**: ASK-0028 (venv setup), ASK-0029 (multi-evaluator), ASK-0031 (activation UX)

## Pre-Review Checklist

- [x] All acceptance criteria from task file implemented
- [x] Tests written and passing (5 new tests)
- [x] CI passes
- [x] BugBot issues addressed
- [x] CodeRabbit major issues addressed
- [x] No debug code left behind

---

**Ready for code-reviewer agent in new tab**

To start review:
1. Open new Claude Code tab
2. Invoke the code-reviewer agent
3. Point to this starter file
