# Review Starter: ASK-0033

**Task**: ASK-0033 - Agent Creation Automation Script
**Task File**: `delegation/tasks/4-in-review/ASK-0033-agent-creation-automation.md`
**Branch**: feature/ASK-0033-v2-agent-creation → main
**PR**: https://github.com/movito/agentive-starter-kit/pull/13
**Commits**: 7 (099f1cc..58ed0ed)

## Implementation Summary

Clean reimplementation of the agent creation automation script after the original PR #12 accumulated 25 review rounds with 18 bugs. The v2 uses TDD: tests written first by two parallel feature-developer agents (32 unit + 9 integration), then the script implemented to pass all tests. Two rounds of CodeRabbit automated review addressed 12 findings; 18 items triaged as false positives or external library design choices.

- `scripts/create-agent.sh` (~578 lines): Creates Claude Code agents from AGENT-TEMPLATE.md and registers them in `agents/launch`
- mkdir-based atomic locking with PID/timestamp/token metadata for concurrent safety
- AWK-based scoped launcher modification (agent_order, serena_agents, get_agent_icon)
- Per-project lock directory derived from PROJECT_ROOT md5 hash (avoids cross-repo collisions)
- Post-lock TOCTOU re-check for duplicate agents
- Lock held through launcher validation (`bash -n`)

## Files Changed

### New Files
- `scripts/create-agent.sh` - Main script: locking, template processing, launcher integration, JSON logging
- `tests/test_create_agent.py` - 32 unit tests across 9 classes (CLI, validation, template, launcher, exit codes, logging, dry-run)
- `tests/integration/__init__.py` - Empty init for integration test package
- `tests/integration/test_concurrent_agent_creation.py` - 9 integration tests across 4 classes (sequential, concurrent, lock recovery, e2e)

### Modified Files
- `scripts/project` - Added `create-agent` subcommand with help text, cwd parameter
- `tests/conftest.py` - Added `setup_temp_project()` fixture, `MINIMAL_LAUNCHER`, `MINIMAL_TEMPLATE`, shared `run_create_agent_script()` helper

### Also in diff (not part of this feature)
- `.adversarial/evaluators/**` - Evaluator library v0.4.0 installed via `./scripts/project install-evaluators` (50+ files). Minor fixes applied to grammar and README model name mismatches. These are external library files.

## Test Results

```
144 tests collected, 143 passed, 1 skipped
- 32 unit tests (tests/test_create_agent.py)
- 9 integration tests (tests/integration/test_concurrent_agent_creation.py, @pytest.mark.slow)
- 103 existing tests (no regressions)
```

CI: Lint & Format Check pass, Run Tests pass (all 3 push commits verified).

## Commit History

| Commit | Description |
|--------|-------------|
| 099f1cc | Set up v2 branch with evaluator library v0.4.0 |
| ab89827 | Add setup_temp_project() test fixture to conftest.py |
| b124285 | Add unit tests for create-agent.sh (32 tests, TDD Red Phase) |
| 9562e07 | Add integration tests for concurrent agent creation (9 tests) |
| 9dec8a6 | Implement create-agent.sh with concurrent-safe locking (Green Phase) |
| 50d7b7c | Address CodeRabbit round 1: per-project lock, TOCTOU re-check, lock held through validation |
| 58ed0ed | Address CodeRabbit round 2: python3 duration calc, sed newline safety, extract shared helper |

## Areas for Review Focus

1. **Locking correctness** (`scripts/create-agent.sh` ~lines 100-165):
   - `is_lock_stale()`: Missing owner file treated as NOT stale (TOCTOU fix). A just-created lock dir without an owner file yet means another process is in the race window between `mkdir` and writing metadata, not an orphaned lock.
   - `acquire_lock()`: Configurable wait timeout via `CREATE_AGENT_LOCK_WAIT_SECS`. After acquiring, re-checks for duplicate agent file (TOCTOU between pre-check and lock).
   - Lock held until after `bash -n` validation of launcher.

2. **AWK-based launcher modification** (~lines 305-400):
   - Three separate AWK scripts for three scoped sections (agent_order array, serena_agents array, get_agent_icon function).
   - Each uses begin/end pattern markers to scope edits to the correct section.
   - `--force` path removes existing entries via AWK before adding new ones.
   - Icon glob pattern uses `*name*` without inner quotes (functionally identical in `[[ ]]`, avoids test count conflicts).

3. **Template placeholder cleanup** (~lines 270-290):
   - sed replaces known placeholders (`[agent-name]`, `[Agent Name]`, `[AGENT-NAME-UPPERCASE]`, etc.) using `|` delimiter.
   - python3 regex post-pass strips remaining `[A-Z][A-Za-z -]+]` instructional placeholders.
   - This two-pass approach handles AGENT-TEMPLATE.md's mix of machine-fillable and human-instructional placeholders.

4. **Per-project lock directory** (~lines 27-38):
   - Hash: `printf '%s' "$PROJECT_ROOT" | md5 -q` (macOS) or `md5sum | cut -c1-12` (Linux).
   - Override: `CREATE_AGENT_LOCK_DIR` env var. Tests use this for deterministic lock path control.
   - Prevents cross-repo lock collisions in parallel CI or multi-project dev.

5. **Test helper consolidation** (`tests/conftest.py`):
   - `run_create_agent_script()` shared by both unit and integration tests.
   - Sets `CREATE_AGENT_PROJECT_ROOT` and `CREATE_AGENT_LOCK_DIR` in subprocess env.
   - Integration tests import as `run_script` alias for backward compatibility with test bodies.

## Bug Ledger Coverage

The 18 bugs from PR #12 are documented in `.adversarial/artifacts/ASK-0033-v2-reimplementation-plan.md`. Key coverage:

| Bug | What | How Addressed |
|-----|------|---------------|
| S1 | sed delimiter collision | Uses `\|` delimiter with explicit escaping |
| S5 | Stale lock detection | PID validity + age check in `is_lock_stale()` |
| S6 | Atomic locking | mkdir primitive (POSIX-guaranteed atomic) |
| S10 | Invalid JSON logs | python3 `json.dumps()` for all log entries |
| T2 | Lock cleanup per-call | Once per `setup_method`, not per `run_script` call |
| T4 | Assertion order | returncode checked first in all test assertions |
| T5 | Stale lock test | Creates lock dir with dead PID metadata |
| T7 | Unresolved placeholders | Regex detection `\[[A-Z][A-Za-z -]+\]` |

## Related Documentation

- **Task file**: `delegation/tasks/4-in-review/ASK-0033-agent-creation-automation.md`
- **Reimplementation plan**: `.adversarial/artifacts/ASK-0033-v2-reimplementation-plan.md`
- **Bug ledger**: 18 bugs from PR #12 (S1-S10, T1-T8) in the plan
- **CodeRabbit triage**: PR comment with full 30-item triage table
- **Handoffs**: `.agent-context/ASK-0033-HANDOFF-unit-tests.md`, `.agent-context/ASK-0033-HANDOFF-integration-tests.md`

## Pre-Review Checklist

- [x] All acceptance criteria from task file implemented
- [x] Tests written and passing (143 pass, 1 skip)
- [x] CI passes on all 3 push commits (Lint + Tests)
- [x] CodeRabbit automated review: 2 rounds, 12 items fixed, 18 triaged
- [x] Cursor Bugbot: no blocking findings
- [x] Task moved to `4-in-review/`
- [x] No debug code or console.logs left behind
- [x] Bash function comments throughout script

---

**Ready for code-reviewer agent in new tab**

To start review:
1. Open new Claude Code tab
2. Run: `agents/launch code-reviewer`
3. Reviewer will auto-detect this starter file
