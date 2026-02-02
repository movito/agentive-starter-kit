# Review Starter: ASK-0029

**Task**: ASK-0029 - Multi-Evaluator Architecture
**Task File**: `delegation/tasks/4-in-review/ASK-0029-multi-evaluator-architecture.md`
**Branch**: feature/ask-0029-multi-evaluator-architecture → main
**PR**: https://github.com/movito/agentive-starter-kit/pull/9

## Implementation Summary

- Updated adversarial-workflow dependency to >=0.6.6 (v0.7.0 not yet published)
- Added `install-evaluators` command to scripts/project with version pinning
- Created .adversarial/evaluators/README.md with provider documentation
- Made agent prompts provider-agnostic (removed GPT-4o specificity from 11 agent files)
- Added evaluator setup phase to onboarding workflow
- Updated README.md and EVALUATION-WORKFLOW.md for multi-provider support

## Files Changed

**Core Changes:**
- `pyproject.toml` (modified) - Version bump
- `scripts/project` (modified) - New `install-evaluators` command (~100 lines)
- `.adversarial/config.yml.template` (modified) - Deprecated evaluator_model field
- `.adversarial/evaluators/README.md` (new) - Provider documentation

**Agent Prompts:**
- `.claude/agents/planner.md` (modified)
- `.claude/agents/tycho.md` (modified)
- `.claude/agents/feature-developer.md` (modified)
- `.claude/agents/test-runner.md` (modified)
- `.claude/agents/document-reviewer.md` (modified)
- `.claude/agents/security-reviewer.md` (modified)
- `.claude/agents/powertest-runner.md` (modified)
- `.claude/agents/agent-creator.md` (modified)
- `.claude/agents/AGENT-TEMPLATE.md` (modified)
- `.claude/agents/TASK-STARTER-TEMPLATE.md` (modified)
- `.claude/agents/onboarding.md` (modified) - New evaluator setup phase

**Documentation:**
- `README.md` (modified)
- `.adversarial/docs/EVALUATION-WORKFLOW.md` (modified)

**Tests:**
- `tests/test_project_script.py` (new) - 6 unit tests with mocked subprocess

## Test Results

- 63 tests passing, 12 skipped
- 92% coverage
- All 6 new tests for install-evaluators pass

## Areas for Review Focus

1. **install-evaluators command** - The main new functionality in scripts/project
2. **Version handling** - Using >=0.6.6 since v0.7.0 not published yet
3. **Agent prompt changes** - Ensure GPT-4o removal is consistent
4. **Onboarding flow** - New evaluator setup phase integration

## Related ADRs

- No new ADRs created (this is a feature addition, not architectural change)

---
**Ready for code-reviewer agent in new tab**
