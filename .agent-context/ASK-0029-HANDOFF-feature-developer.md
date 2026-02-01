# ASK-0029 Handoff: Multi-Evaluator Architecture

**Task**: `delegation/tasks/2-todo/ASK-0029-multi-evaluator-architecture.md`
**Prepared by**: Planner
**Date**: 2026-02-01
**Evaluation Rounds**: 4 (GPT-4o x2, GPT-5.2 x2)

## Context

The adversarial-workflow package now supports custom evaluators via YAML files. This task updates the starter kit to:
1. Bump dependency to v0.7.0
2. Make documentation provider-agnostic
3. Add optional evaluator library installation

## Implementation Sequence

### Phase 1: Core Updates (Must Have)

1. **pyproject.toml** - Bump version:
   ```python
   "adversarial-workflow>=0.7.0",  # Multi-evaluator support, configurable timeouts
   ```

2. **`.adversarial/config.yml.template`** - Update to deprecate `evaluator_model`:
   - See task spec Section 2 for exact content
   - Remove any model-specific fields
   - Add comments about custom evaluators

3. **Create `.adversarial/evaluators/` directory**:
   ```bash
   mkdir -p .adversarial/evaluators
   touch .adversarial/evaluators/.gitkeep
   ```
   - Add README.md per task spec Section 3

### Phase 2: Install Command

4. **Add `install-evaluators` to `scripts/project`**:
   - Location: Add new function `cmd_install_evaluators(args)`
   - Use the implementation in task spec Section 4
   - Key features:
     - Pin to `EVALUATOR_LIBRARY_VERSION = "v0.2.2"`
     - Support `--ref <tag>` override
     - Record version + commit hash in `.installed-version`
     - Handle errors: no git, network timeout, clone failure

### Phase 3: Agent Updates

5. **Update `.claude/agents/planner.md`**:
   - Search for "GPT-4o" and replace with provider-agnostic language
   - Change "External GPT-4o via Aider" to "External AI via adversarial-workflow"
   - Update cost references to "Varies by evaluator"

6. **Update `.claude/agents/onboarding.md`**:
   - Add "Phase 7: Evaluator Setup (Optional)" per task spec Section 5

### Phase 4: Documentation

7. **Update `README.md`**:
   - Update adversarial section with multi-evaluator info
   - Add install-evaluators command
   - See task spec Section 7

8. **Update `.adversarial/docs/EVALUATION-WORKFLOW.md`**:
   - Add multi-evaluator guidance
   - Document custom evaluator creation

### Phase 5: Testing

9. **Add tests to `tests/test_project_script.py`**:
   - Mock subprocess.run for git operations
   - Test: git not found, already installed, --force, --ref
   - See task spec Testing section for stubs

## Files to Modify

| File | Change |
|------|--------|
| `pyproject.toml` | Bump adversarial-workflow to >=0.7.0 |
| `.adversarial/config.yml.template` | Deprecate evaluator_model, add comments |
| `.adversarial/evaluators/.gitkeep` | Create directory |
| `.adversarial/evaluators/README.md` | Create with usage guide |
| `scripts/project` | Add install-evaluators command |
| `.claude/agents/planner.md` | Remove GPT-4o references |
| `.claude/agents/onboarding.md` | Add evaluator setup phase |
| `README.md` | Update adversarial section |
| `.adversarial/docs/EVALUATION-WORKFLOW.md` | Add multi-evaluator guidance |
| `tests/test_project_script.py` | Add installer tests |

## Key Technical Details

### Version Pinning
- adversarial-workflow uses `>=0.7.0` (semver, allow patches)
- evaluator library uses tag pinning (more cautious, copies files directly)

### Installer Behavior
- Clones repo with `--depth 1 --branch <tag>`
- Copies `evaluators/` directory structure
- Records version + commit hash in `.installed-version`
- Idempotent: skips if already installed (use --force to override)

### Error Handling
Must handle:
- No git available
- Network timeout (60s)
- Clone failure (bad tag, network error)
- Already installed

## Evaluation Feedback Summary

The task was evaluated 4 times. Key concerns addressed:
1. Version citations: Added References section with release links
2. Reproducibility: Clarified >= vs tag pinning rationale
3. Built-in vs custom: Clarified OpenAI requirement for built-ins
4. Model-agnostic: Removed hard-coded model references

Deferred concerns (implementation details):
- SHA-based pinning for tags (tag + hash is sufficient)
- Overwrite behavior (can add --dry-run in implementation)
- Windows path handling (test coverage)

## Success Criteria

1. `pip install` succeeds with new dependency
2. `adversarial list-evaluators` shows installed evaluators
3. `./scripts/project install-evaluators` works:
   - Clones at pinned version
   - Records version in `.installed-version`
   - Handles errors gracefully
4. All tests pass
5. No GPT-4o/model-specific language in prompts/docs

## Commands to Run

```bash
# Start task lifecycle
./scripts/project start ASK-0029

# Development
pip install -e .
pip show adversarial-workflow | grep Version  # Verify 0.7.0+

# Testing
./scripts/project install-evaluators
adversarial list-evaluators
pytest tests/test_project_script.py -v

# CI verification
./scripts/ci-check.sh
```

---

Ready for implementation by feature-developer agent.
