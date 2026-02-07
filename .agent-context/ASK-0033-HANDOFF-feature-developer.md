# ASK-0033: Agent Creation Automation - Implementation Handoff

**Task**: ASK-0033-agent-creation-automation
**Assigned To**: feature-developer
**Priority**: Medium
**Estimated Effort**: 48 hours (3 days)
**Created**: 2026-02-07

## Mission Statement

Create a robust automation script that enables the AGENT-CREATOR agent to efficiently create new agents through a single command, eliminating manual file creation, template processing, and launcher integration.

## Key Implementation Goals

### Primary Objective
Replace the manual 15-minute agent creation process with a 30-second automated workflow that the AGENT-CREATOR can invoke via `scripts/create-agent.sh`.

### Critical Success Factors
1. **Zero manual file editing** - Complete automation from input to functional agent
2. **Bulletproof concurrency** - Handle simultaneous agent creation safely
3. **AGENT-CREATOR integration** - Clear success/error communication
4. **Production robustness** - Comprehensive error handling and recovery

## Architecture Overview

```bash
User Request → AGENT-CREATOR Agent → scripts/create-agent.sh → Success/Error
     ↓                                        ↓
Interactive Guidance                    Automated Execution:
- Model selection                      1. Template processing
- Tool configuration                   2. Launcher integration
- Responsibility definition            3. File validation
- Icon/positioning                     4. Error handling
```

## Technical Implementation Details

### Core Script Structure
```bash
#!/bin/bash
# scripts/create-agent.sh
# Usage: ./scripts/create-agent.sh agent-name "description" [model] [--emoji=🔭] [--position=2]

main() {
    validate_inputs "$@"
    acquire_lock
    trap cleanup_and_exit EXIT

    process_template "$agent_name" "$description" "$model"
    update_launcher_arrays "$agent_name" "$emoji" "$position"
    validate_generated_files "$agent_name"

    log_success "$agent_name"
    echo "SUCCESS: Agent '$agent_name' created successfully"
}
```

### File Locking Implementation (CRITICAL)
```bash
LOCK_FILE="/tmp/agent-creation-launcher.lock"
LOCK_TIMEOUT=30

acquire_lock() {
    exec 200>"$LOCK_FILE"
    if ! flock -x -w "$LOCK_TIMEOUT" 200; then
        log_error "Lock timeout after ${LOCK_TIMEOUT}s - another creation in progress"
        exit 2
    fi
    log_info "Lock acquired"
}

cleanup_and_exit() {
    local exit_code=$?
    if [ -n "$temp_files" ]; then
        rm -f $temp_files
    fi
    flock -u 200 2>/dev/null
    exec 200>&-
    exit $exit_code
}
```

### Template Processing Strategy
```bash
process_template() {
    local agent_name="$1"
    local description="$2"
    local model="$3"
    local template_file=".claude/agents/AGENT-TEMPLATE.md"
    local output_file=".claude/agents/${agent_name}.md"

    # Verify template exists and is readable
    if [[ ! -r "$template_file" ]]; then
        log_error "Template file not found or not readable: $template_file"
        exit 1
    fi

    # Process with robust placeholder replacement
    sed -e "s/\\[agent-name\\]/${agent_name}/g" \
        -e "s/\\[One sentence description.*\\]/${description}/g" \
        -e "s/claude-sonnet-4-20250514/${model}/g" \
        "$template_file" > "$output_file"

    # Verify no unresolved placeholders
    if grep -q '\[.*\]' "$output_file"; then
        log_error "Unresolved placeholders found in generated agent file"
        rm -f "$output_file"
        exit 1
    fi
}
```

### Launcher Integration (Complex)
```bash
update_launcher_arrays() {
    local agent_name="$1"
    local emoji="${2:-⚡}"
    local position="${3:-auto}"
    local launcher_file="agents/launch"
    local temp_file=$(mktemp)

    # Create backup
    cp "$launcher_file" "${launcher_file}.backup"

    # Update agent_order array
    update_agent_order "$agent_name" "$position" "$launcher_file" "$temp_file"

    # Update serena_agents array (if applicable)
    update_serena_agents "$agent_name" "$launcher_file" "$temp_file"

    # Update icon mapping
    update_icon_mapping "$agent_name" "$emoji" "$launcher_file" "$temp_file"

    # Validate launcher syntax
    if ! bash -n "$temp_file"; then
        log_error "Generated launcher file has syntax errors"
        restore_launcher_backup
        exit 1
    fi

    # Atomic move
    mv "$temp_file" "$launcher_file"
}
```

## Error Handling Strategy

### Exit Codes for AGENT-CREATOR
- **0**: Success - agent created successfully
- **1**: User error - invalid input, duplicate name, etc.
- **2**: System error - lock timeout, file permissions, etc.

### Error Message Format
```bash
# STDERR format for AGENT-CREATOR consumption
echo "ERROR: Agent 'duplicate-name' already exists." >&2
echo "ACTION: Use --force to overwrite or choose different name." >&2
echo "DETAILS: Existing file: .claude/agents/duplicate-name.md" >&2
```

### Logging Format
```json
{
  "timestamp": "2026-02-07T20:45:00Z",
  "level": "ERROR",
  "agent_name": "new-agent",
  "operation": "update_launcher",
  "status": "failed",
  "duration_ms": 1234,
  "error": "Syntax error in generated launcher file",
  "details": {"backup_restored": true, "temp_file": "/tmp/tmp.xyz"}
}
```

## Testing Priorities

### 1. Concurrency Tests (CRITICAL)
```bash
# Test concurrent agent creation
test_concurrent_creation() {
    # Spawn 5 simultaneous processes
    for i in {1..5}; do
        ./scripts/create-agent.sh "test-agent-$i" "Test agent $i" &
    done
    wait

    # Verify only valid agents created, launcher intact
    verify_launcher_integrity
    verify_no_partial_agents
}
```

### 2. Error Recovery Tests
```bash
# Test crash recovery
test_crash_recovery() {
    # Start agent creation, kill mid-process
    ./scripts/create-agent.sh "crash-test" "Test agent" &
    local pid=$!
    sleep 1  # Let it start
    kill -9 $pid

    # Verify cleanup occurred
    [[ ! -f "/tmp/agent-creation-launcher.lock" ]] || fail "Lock not cleaned up"
    [[ -f "agents/launch.backup" ]] && rm "agents/launch.backup"
}
```

### 3. Template Edge Cases
```bash
# Test missing template handling
test_missing_template() {
    mv ".claude/agents/AGENT-TEMPLATE.md" ".claude/agents/AGENT-TEMPLATE.md.backup"
    ./scripts/create-agent.sh "test-agent" "Test description"
    local exit_code=$?
    mv ".claude/agents/AGENT-TEMPLATE.md.backup" ".claude/agents/AGENT-TEMPLATE.md"
    [[ $exit_code -eq 1 ]] || fail "Should exit with code 1 for missing template"
}
```

## Critical Implementation Notes

### AGENT-CREATOR Integration Points
1. **Script Location**: Must be at `scripts/create-agent.sh` (AGENT-CREATOR expects this path)
2. **Exit Codes**: 0=success, 1=user error, 2=system error
3. **Output Format**: Success messages to STDOUT, errors to STDERR
4. **Parameter Format**: `agent-name "description" [model] [--emoji=🔭] [--position=2]`

### Launcher Array Details
The script must update three specific arrays in `agents/launch`:
1. **agent_order** (lines ~44-54): Controls display order in menu
2. **serena_agents** (lines ~162-170): Controls Serena auto-activation
3. **get_agent_icon()** function (lines ~240-248): Maps agent names to emojis

### File Validation Requirements
- Generated agent file must pass bash syntax check
- All `[bracketed]` placeholders must be replaced
- Launcher file must remain syntactically valid
- No orphaned files on failure

## Project Integration

### Project Script Integration
Add to `scripts/project`:
```bash
create-agent)
    shift
    ./scripts/create-agent.sh "$@"
    ;;
```

### AGENT-CREATOR Instructions Update
After completion, update `.claude/agents/agent-creator.md` to use:
```bash
# Replace manual file creation with:
./scripts/create-agent.sh "$agent_name" "$description" "$model" --emoji="$emoji"
```

## Success Verification

### Manual Testing Checklist
1. Create test agent: `./scripts/create-agent.sh test-agent "Test description"`
2. Verify agent appears in `./agents/launch` menu
3. Verify agent can be launched successfully
4. Test concurrent creation (run 3 simultaneous commands)
5. Test error cases (duplicate name, missing template)

### Automated Testing
- Run full test suite: `pytest tests/test_create_agent.py -v`
- Run concurrency tests: `pytest tests/integration/test_concurrent_agent_creation.py -v`
- Verify coverage: `pytest --cov=scripts.create_agent --cov-report=term-missing`

## Resources & References

### Existing Patterns
- **Script Style**: Follow `scripts/project` patterns for argument parsing and error handling
- **Logging**: Use structured JSON logging similar to Linear sync utilities
- **File Operations**: Use atomic operations like in `scripts/sync_tasks_to_linear.py`

### Key Files to Study
- `.claude/agents/AGENT-TEMPLATE.md` - Template structure and placeholders
- `agents/launch` - Launcher arrays and icon mapping (lines 44-54, 162-170, 240-248)
- `.claude/agents/panay.md` - Example of successful agent creation
- `scripts/project` - Project script patterns and style

### Testing References
- `tests/test_template.py` - TDD template and patterns
- Existing test files in `tests/` - Style and coverage patterns
- `.pre-commit-config.yaml` - Code quality requirements

## Evaluation History

**Evaluation Status**: NEEDS_REVISION after 3 rounds
**Key Concerns Addressed**:
- File locking mechanism with flock and timeout handling
- Comprehensive error handling with structured logging
- Concurrency testing with specific test scenarios
- Edge case handling (missing templates, system dependencies)
- CI/CD integration considerations

**Remaining Implementation Flexibility**: The evaluation asked for very specific implementation details that are better determined during the TDD process. The current task spec provides excellent guidance while preserving appropriate development flexibility.

---

**Ready for TDD Implementation**: Start with failing tests, implement incrementally, verify at each step.
**Estimated Completion**: 3 days with comprehensive testing
**Integration Point**: AGENT-CREATOR agent will immediately benefit from this automation