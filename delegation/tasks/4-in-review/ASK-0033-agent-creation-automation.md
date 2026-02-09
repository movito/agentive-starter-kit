# ASK-0033: Agent Creation Automation Script

**Status**: In Review
**Priority**: medium
**Assigned To**: feature-developer
**Estimated Effort**: 2-3 days
**Created**: 2026-02-07
**Target Completion**: 2026-02-10
**Linear ID**: (automatically backfilled after first sync)

## Related Tasks

**Context Task**: Manual Panay agent creation revealed missing automation
**Blocks**: Future agent creation workflows, agent-creator agent improvements
**Related**: ASK-0034 (Agent creation documentation update - if needed)

## Status History

- **Todo** (from initial) - 2026-02-07 20:45:00

## Overview

Create a robust automation script to help the **AGENT-CREATOR agent** work efficiently when users request agent creation. The script eliminates manual file creation and launcher updates that currently slow down the agent-creator's workflow.

**Primary Use Case**: When users ask the AGENT-CREATOR agent to create new agents, the agent currently has to:
1. Manually copy from `AGENT-TEMPLATE.md`
2. Manually replace placeholders with user specifications
3. Manually update three arrays in `agents/launch`
4. Manually validate agent file format
5. Manually test launcher integration

This manual process is error-prone and time-consuming for the agent. The recent Panay agent creation highlighted that the agent-creator expected `.agent-context/scripts/create-agent.sh` which didn't exist.

**Context**: Users will always get help from the AGENT-CREATOR for agent setup - the script should make the agent-creator's job fast and reliable, not replace the agent's guidance and interaction.

**Related Work**: Agent template system exists (`.claude/agents/AGENT-TEMPLATE.md`) and launcher system is well-established (`agents/launch`).

## Requirements

### Functional Requirements
1. **Script Creation**: Create `scripts/create-agent.sh` that AGENT-CREATOR can call via Bash tool
2. **Template Processing**: Replace all placeholders in `AGENT-TEMPLATE.md` with AGENT-CREATOR's validated inputs
3. **Launcher Integration**: Automatically update three arrays in `agents/launch`:
   - `agent_order[]` array (custom positioning as specified by AGENT-CREATOR)
   - `serena_agents[]` array (Serena auto-activation based on agent type)
   - Icon mapping in `get_agent_icon()` function (custom emoji from AGENT-CREATOR)
4. **Validation**: Verify agent file format and launcher syntax, report issues to AGENT-CREATOR
5. **Error Handling**: Provide clear, actionable error messages that AGENT-CREATOR can interpret and act on
6. **File Locking**: Implement robust locking mechanism to prevent concurrent modifications to `agents/launch`
7. **Logging & Monitoring**: Comprehensive logging for debugging, error tracking, and performance monitoring
8. **Integration with Project Script**: Add `create-agent` subcommand for optional direct access

### Non-Functional Requirements
- [ ] **Performance**: Script completes in <5 seconds for typical agent
- [ ] **Reliability**: 100% success rate for valid inputs, graceful failure for invalid inputs
- [ ] **Concurrency**: Handle multiple simultaneous agent creation requests safely
- [ ] **Security**: Validate all inputs, prevent code injection in generated files
- [ ] **Maintainability**: Well-documented code following project patterns
- [ ] **Observability**: Comprehensive logging for debugging and monitoring

## TDD Workflow (Mandatory)

**Test-Driven Development Approach**:

1. **Before coding**: Create `tests/test_create_agent.py` for automation script testing
2. **Red**: Write failing tests for each feature (template processing, launcher updates, etc.)
3. **Green**: Implement minimum code until tests pass
4. **Refactor**: Improve code while keeping tests green
5. **Commit**: Pre-commit hook runs tests automatically

**TDD Benefits for this task**:
- Ensures script handles all edge cases (duplicate names, invalid inputs, etc.)
- Validates template processing accuracy (no missing placeholders)
- Confirms launcher integration doesn't break existing functionality
- Documents expected behavior for future maintenance

### Test Requirements
- [ ] Unit tests for template processing functions
- [ ] Integration tests for full agent creation workflow
- [ ] Error handling tests for invalid inputs (duplicate names, bad characters, etc.)
- [ ] Launcher integration tests (verify arrays updated correctly)
- [ ] File validation tests (generated agent follows expected format)
- [ ] Rollback tests (cleanup on failure)
- [ ] Edge case tests: special characters, long names, missing template, etc.
- [ ] **Concurrency Tests (CRITICAL)**:
  - Spawn 10 concurrent agent creation processes
  - Verify only one succeeds, others timeout gracefully
  - Test launcher file integrity after concurrent access
  - Test crash recovery (kill process during file update)
  - Test lock timeout scenarios (>30 seconds)

**Test files to create**:
- `tests/test_create_agent.py` - Main test suite for automation script
- `tests/integration/test_agent_creation_workflow.py` - End-to-end workflow tests
- `tests/integration/test_concurrent_agent_creation.py` - Critical concurrent access tests
- `tests/integration/test_crash_recovery.py` - Script crash and recovery scenarios

## Test Coverage Requirements

**Coverage Targets**:
- [ ] New code: **90%+ line coverage** (automation scripts need high coverage)
- [ ] Overall coverage: **≥53%** (maintain baseline)
- [ ] Critical paths: **100% coverage** (template processing, launcher updates)
- [ ] Error paths: **95%+ coverage** (error handling is crucial)

**Coverage Verification**:
```bash
# Check coverage for new automation code
pytest tests/test_create_agent.py --cov=scripts.create_agent --cov-report=term-missing

# Verify no coverage regression
pytest tests/ --cov=thematic_cuts --cov-report=term --cov-fail-under=53
```

**Critical Paths** (require 100% coverage):
1. **Template placeholder replacement** - must replace all [bracketed] values
2. **Launcher array updates** - must update all three arrays correctly
3. **File validation** - must verify generated files are syntactically correct
4. **Error rollback** - must clean up partial changes on failure

## Concurrency & Error Handling (Critical Requirements)

### File Locking Mechanism (CRITICAL)
- [ ] **Exclusive Lock**: Use `flock` with file descriptor locking on `/tmp/agent-creation-launcher.lock`
- [ ] **Timeout Handling**: Maximum 30-second wait for lock acquisition with exponential backoff
- [ ] **Lock Cleanup**: Ensure locks are released even if script crashes (trap signals)
- [ ] **Atomic Operations**: Use temporary files and atomic moves to prevent corruption
- [ ] **Lock Testing**:
  - Simulate 10 concurrent agent creation requests
  - Test timeout scenarios (block for >30 seconds)
  - Test crash recovery (kill script mid-update, verify cleanup)
  - Test deadlock prevention and recovery

### Error Handling & Recovery (MEDIUM Priority)
- [ ] **Structured Logging**: JSON-formatted logs to `logs/agent-creation.log` with rotation
- [ ] **Error Classification**:
  - CRITICAL: Lock timeout, file corruption, system errors
  - HIGH: Template missing/invalid, launcher syntax errors
  - MEDIUM: Invalid input validation, duplicate names
  - LOW: Performance warnings, informational messages
- [ ] **Recovery Strategy**:
  - Automatic rollback on any failure during file modifications
  - Restore `.backup` files if atomic operations fail
  - Clean up temporary files and release locks
- [ ] **Partial State Detection**:
  - Check for orphaned agent files without launcher entries
  - Detect incomplete launcher array updates
  - Identify stale lock files from crashed processes
- [ ] **AGENT-CREATOR Communication**:
  - Exit code 0 = success, 1 = user error, 2 = system error
  - STDOUT: Success messages in structured format
  - STDERR: Error messages with action recommendations
  - Example: "ERROR: Agent 'test-agent' already exists. Use --force to overwrite or choose different name."

### Production Environment Testing
- [ ] **Staging Tests**: Test script in environment mirroring production
- [ ] **Load Testing**: Simulate concurrent agent creation requests (5-10 simultaneous)
- [ ] **Failure Testing**: Intentionally corrupt files and verify recovery
- [ ] **Performance Testing**: Verify <5 second completion under load

### Logging & Monitoring
```bash
# Log format for agent-creation.log
{
  "timestamp": "2026-02-07T20:45:00Z",
  "level": "INFO|WARN|ERROR",
  "agent_name": "new-agent",
  "operation": "create|validate|update_launcher|cleanup",
  "status": "started|completed|failed",
  "duration_ms": 1234,
  "error": "error message if failed",
  "details": {additional context}
}
```

## Edge Cases & Dependencies (Evaluator Requirements)

### Template Edge Cases
- [ ] **Missing Template**: Verify `.claude/agents/AGENT-TEMPLATE.md` exists, fallback to embedded template
- [ ] **Malformed Template**: Validate template structure, detect missing placeholders
- [ ] **Corrupted Template**: Check file integrity, provide clear error to AGENT-CREATOR
- [ ] **Permission Issues**: Handle read/write permission errors gracefully

### System Dependencies
- [ ] **Required Files**: Verify `agents/launch` exists and is writable
- [ ] **Directory Structure**: Create `logs/` directory if missing
- [ ] **Shell Dependencies**: Verify `flock`, `awk`, `sed` availability
- [ ] **File System**: Check available disk space before operations

### CI/CD Integration Considerations
- [ ] **Pre-commit Compatibility**: Generated agents pass pre-commit hooks
- [ ] **Test Integration**: New agents don't break existing test suites
- [ ] **Linting Standards**: Generated code follows project style guides
- [ ] **No CI Changes**: Script doesn't require CI/CD pipeline modifications

### Existing System Integration
- [ ] **Launcher Compatibility**: Maintain backward compatibility with existing agents
- [ ] **Version Compatibility**: Works with all supported Claude models
- [ ] **Project Structure**: Integrates with existing `scripts/project` pattern
- [ ] **Linear Sync**: Generated agents work with Linear task sync (no conflicts)

## Pre-Commit/Pre-Push Requirements (Mandatory)

### Before Every Commit
```bash
git add .
git commit -m "message"
# → Pre-commit hook runs automatically:
#    1. Black (formatting)
#    2. isort (imports)
#    3. flake8 (linting)
#    4. pytest (fast tests)
```

**If tests fail**: Commit is blocked. Fix issues and retry.

### Before Every Push (MANDATORY)
```bash
# MANDATORY: Run full CI check locally
./scripts/ci-check.sh

# Only push if ci-check passes
git push origin main
```

**What ci-check.sh does**:
- ✅ Full test suite (including slow tests)
- ✅ Coverage threshold check (53%+)
- ✅ Pre-commit hooks verification
- ✅ Uncommitted changes check

## Implementation Plan

### Files to Modify

1. `scripts/project` - Add create-agent subcommand
   - Function: `create_agent()` command handler
   - Change: Add option parsing and delegation to create-agent.sh
   - Lines: ~50-75 (new function + help text update)

2. `agents/launch` - NO DIRECT MODIFICATION
   - Change: Script will modify this file programmatically
   - Arrays to update: `agent_order`, `serena_agents`, icon mapping

### Files to Create

1. `scripts/create-agent.sh` - Main automation script
   - Purpose: Automate agent creation from template
   - Contains: Template processing, launcher updates, validation
   - Estimated lines: ~300-400

2. `scripts/lib/agent_creation.py` - Python helper functions (optional)
   - Purpose: Complex template processing and validation
   - Contains: Validation functions, template engine
   - Estimated lines: ~200-250

3. `tests/test_create_agent.py` - Main test suite
   - Test coverage for create-agent.sh functionality
   - Estimated tests: ~25-30 tests

4. `tests/integration/test_agent_creation_workflow.py` - End-to-end tests
   - Test coverage for complete workflows
   - Estimated tests: ~10-15 tests

### Approach

**Step 1: Script Foundation (Day 1 - 6 hours)**

Create the basic automation script with input validation and help text.

**TDD cycle**:
1. Write tests: Input parsing, help text, basic validation
2. Run tests (should fail): `pytest tests/test_create_agent.py::test_input_parsing -v`
3. Implement feature: Basic script structure, argument parsing
4. Run tests (should pass): `pytest tests/test_create_agent.py::test_input_parsing -v`
5. Refactor if needed

**Implementation details**:
```bash
#!/bin/bash
# scripts/create-agent.sh
# Usage: ./scripts/create-agent.sh agent-name "description" [model]

create_agent() {
    local agent_name="$1"
    local description="$2"
    local model="${3:-claude-sonnet-4-5-20250929}"

    # Input validation
    validate_agent_name "$agent_name"
    validate_description "$description"
    validate_model "$model"

    # Process template
    process_template "$agent_name" "$description" "$model"

    # Update launcher
    update_launcher_arrays "$agent_name"

    # Validate results
    validate_generated_files "$agent_name"
}
```

**Step 2: Template Processing (Day 1-2 - 8 hours)**

Implement robust template processing with placeholder replacement.

**TDD cycle**:
1. Write tests: Template loading, placeholder replacement, edge cases
2. Run tests (should fail): `pytest tests/test_create_agent.py::test_template_processing -v`
3. Implement feature: Template processing functions
4. Run tests (should pass): `pytest tests/test_create_agent.py::test_template_processing -v`
5. Refactor for clarity and performance

**Implementation details**:
```bash
process_template() {
    local agent_name="$1"
    local description="$2"
    local model="$3"

    # Load template
    local template_file=".claude/agents/AGENT-TEMPLATE.md"
    local output_file=".claude/agents/${agent_name}.md"

    # Replace placeholders using sed (robust pattern)
    sed -e "s/\[agent-name\]/${agent_name}/g" \
        -e "s/\[One sentence description.*\]/${description}/g" \
        -e "s/claude-sonnet-4-20250514/${model}/g" \
        "$template_file" > "$output_file"

    # Validate all placeholders replaced
    if grep -q '\[.*\]' "$output_file"; then
        echo "Error: Unresolved placeholders in $output_file"
        return 1
    fi
}
```

**Step 3: Launcher Integration (Day 2 - 6 hours)**

Implement automatic launcher array updates with validation.

**TDD cycle**:
1. Write tests: Array updates, icon mapping, position handling
2. Run tests (should fail): `pytest tests/test_create_agent.py::test_launcher_integration -v`
3. Implement feature: Launcher update functions
4. Run tests (should pass): `pytest tests/test_create_agent.py::test_launcher_integration -v`
5. Refactor for maintainability

**Implementation details**:
```bash
update_launcher_arrays() {
    local agent_name="$1"
    local launcher_file="agents/launch"
    local temp_file=$(mktemp)
    local lock_file="/tmp/agent-creation-launcher.lock"

    # Acquire exclusive lock (30 second timeout)
    exec 200>"$lock_file"
    if ! flock -x -w 30 200; then
        log_error "Failed to acquire launcher lock after 30 seconds"
        return 1
    fi

    # Backup original
    cp "$launcher_file" "${launcher_file}.backup"

    # Update agent_order array (add after "planner")
    awk '/agent_order=\(/,/\)/ {
        if(/\"planner\"/) {
            print
            print "        \"'$agent_name'\""
        } else {
            print
        }
    }; !/agent_order=\(/,/\)/' "$launcher_file" > "$temp_file"

    # Update serena_agents array (if agent needs Serena)
    # Update icon mapping
    # Validate syntax

    mv "$temp_file" "$launcher_file"

    # Release lock
    flock -u 200
    exec 200>&-
}
```

**Step 4: Integration & Testing (Day 3 - 4 hours)**

Add project script integration and comprehensive error handling.

**TDD cycle**:
1. Write tests: Project integration, error scenarios, cleanup
2. Run tests (should fail): `pytest tests/test_create_agent.py::test_project_integration -v`
3. Implement feature: Project script updates, error handling
4. Run tests (should pass): `pytest tests/test_create_agent.py::test_project_integration -v`
5. Refactor for production readiness

## Acceptance Criteria

### Must Have ✅
- [ ] **Script Creation**: `scripts/create-agent.sh` successfully creates agents
- [ ] **Template Processing**: All placeholders replaced correctly
- [ ] **Launcher Integration**: All three arrays updated automatically
- [ ] **Input Validation**: Invalid inputs rejected with clear errors
- [ ] **Conflict Detection**: Duplicate agent names detected and rejected
- [ ] **File Locking**: Concurrent modifications prevented with flock mechanism
- [ ] **Error Logging**: Comprehensive JSON logging to `logs/agent-creation.log`
- [ ] **Project Integration**: `./scripts/project create-agent` works
- [ ] **File Validation**: Generated agents pass format validation
- [ ] **Error Cleanup**: Failed creations don't leave partial files
- [ ] **Concurrency Testing**: Multiple simultaneous creations handled safely
- [ ] **All tests passing**: No xfail removals without fixes
- [ ] **Coverage targets met**: 90%+ new code, 53%+ overall

### Should Have 🎯
- [ ] **Interactive Mode**: Prompts for missing parameters
- [ ] **Custom Icons**: Support for specifying custom agent icons
- [ ] **Position Control**: Option to specify position in agent_order array
- [ ] **Serena Detection**: Auto-detect if agent needs Serena activation
- [ ] **Rollback Support**: Option to undo agent creation
- [ ] **Dry Run Mode**: Preview changes without applying them

### Nice to Have 🌟
- [ ] **Batch Creation**: Create multiple agents from config file
- [ ] **Template Validation**: Verify template file integrity before use
- [ ] **Git Integration**: Auto-commit new agent files
- [ ] **Usage Statistics**: Track which agents are created most often

## Success Metrics

### Quantitative
- **Script Performance**: <5 seconds for typical agent creation
- **Test Coverage**: 90%+ for automation code, 100% for critical paths
- **Error Handling**: 100% of invalid inputs properly rejected
- **Reliability**: 0 false positives, 0 false negatives in validation
- **LOC**: ~500-650 lines (script + tests)

### Qualitative
- **User Experience**: Single command creates fully functional agent
- **Maintainability**: Code is well-documented and follows project patterns
- **Robustness**: Handles edge cases gracefully with clear error messages
- **Integration**: Seamlessly fits into existing project workflow

## Risks & Mitigations

### Risk 1: Launcher File Corruption
**Likelihood**: Medium
**Impact**: High (breaks agent launching system)
**Mitigation**:
- Create backup before modifications
- Validate launcher syntax before committing changes
- Include rollback function in error handling
- Comprehensive testing of launcher integration

### Risk 2: Template Processing Edge Cases
**Likelihood**: Medium
**Impact**: Medium (malformed agent files)
**Mitigation**:
- Exhaustive testing of placeholder replacement
- Validation of generated files before finalization
- Clear error messages for unresolved placeholders
- Support for complex descriptions with special characters

### Risk 3: Script Complexity
**Likelihood**: Low
**Impact**: Medium (maintenance burden)
**Mitigation**:
- Follow KISS principle - keep functionality focused
- Extensive documentation and comments
- Modular design with testable functions
- Code review by experienced team members

## Rollback Plan

If automation script causes critical issues:

1. **Immediate**: Remove generated agent files, restore launcher backup
2. **Verification**: Test that `./agents/launch` still works correctly
3. **Root cause**: Analyze logs and test failures to identify script bugs
4. **Prevention**: Add missing test cases and improve validation

## Time Estimate

| Phase | Time | Status |
|-------|------|--------|
| Investigation & Planning | 2 hours | [ ] |
| TDD: Write failing tests | 6 hours | [ ] |
| TDD: Implement script foundation | 6 hours | [ ] |
| TDD: Template processing | 8 hours | [ ] |
| TDD: Launcher integration + locking | 8 hours | [ ] |
| TDD: Concurrency & error handling | 6 hours | [ ] |
| TDD: Logging & monitoring | 4 hours | [ ] |
| TDD: Project integration | 4 hours | [ ] |
| Production testing & validation | 4 hours | [ ] |
| Documentation & code review | 4 hours | [ ] |
| **Total** | **48 hours (3 days)** | [ ] |

## References

### Testing & Development
- **TDD Template**: `tests/test_template.py`
- **Testing Workflow**: `.agent-context/workflows/TESTING-WORKFLOW.md`
- **Commit Protocol**: `.agent-context/workflows/COMMIT-PROTOCOL.md`
- **Pre-commit Config**: `.pre-commit-config.yaml`

### Project Context
- **Agent Template**: `.claude/agents/AGENT-TEMPLATE.md`
- **Agent Launcher**: `agents/launch` (target for updates)
- **Project Script**: `scripts/project` (integration point)
- **Agent Creator Agent**: `.claude/agents/agent-creator.md` (will benefit from this)

### Documentation
- **Related ADRs**: None (this creates new capability)
- **Script Patterns**: `scripts/project`, `scripts/ci-check.sh` (examples of project script style)
- **External References**: Bash best practices, template processing patterns

## Notes

**Design Philosophy**: This script is primarily a **tool for the AGENT-CREATOR agent**, not a direct user interface. Users interact with AGENT-CREATOR, which uses this script for efficient execution.

**Primary User Flow**:
1. User asks AGENT-CREATOR: "Create a new agent called 'data-analyzer'"
2. AGENT-CREATOR gathers requirements interactively (model, tools, responsibilities, etc.)
3. AGENT-CREATOR validates inputs and makes design decisions
4. AGENT-CREATOR calls `scripts/create-agent.sh data-analyzer "description" claude-sonnet-4-5-20250929 --emoji=📊`
5. Script handles all file operations and reports success/errors to AGENT-CREATOR
6. AGENT-CREATOR presents results to user and handles any issues

**Integration Points**:
- AGENT-CREATOR agent is primary consumer (update its instructions after completion)
- Script provides detailed success/error reporting for agent consumption
- Human users can optionally use `./scripts/project create-agent` for direct access
- Launcher system remains backward compatible

**Success Indicator**: AGENT-CREATOR can create agents in seconds instead of minutes, with zero manual file editing.

---

**Template Version**: 1.0.0
**Created**: 2026-02-07
**Maintained By**: agent-creator agent
