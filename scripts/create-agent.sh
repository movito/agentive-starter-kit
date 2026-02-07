#!/bin/bash
# =============================================================================
# create-agent.sh - Agent Creation Automation Script
# =============================================================================
#
# Creates new agents from the AGENT-TEMPLATE.md template, automatically
# updating the launcher file with proper registration.
#
# Primary Use Case:
#   The AGENT-CREATOR agent invokes this script to automate agent creation,
#   replacing manual file copying and editing.
#
# Exit Codes:
#   0 - Success
#   1 - User error (invalid input, duplicate name, etc.)
#   2 - System error (missing template, permission issues, etc.)
#
# Usage:
#   ./scripts/create-agent.sh agent-name "Description" [options]
#
# Options:
#   --model MODEL    Model to use (default: claude-sonnet-4-5-20250929)
#   --emoji EMOJI    Icon emoji for the agent (default: ⚡)
#   --serena         Add agent to serena_agents array
#   --position N     Position in agent_order (default: end)
#   --force          Overwrite existing agent
#   --dry-run        Show what would be done without making changes
#   -h, --help       Show this help message
#
# =============================================================================

set -euo pipefail

# =============================================================================
# Configuration
# =============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
TEMPLATE_FILE="$PROJECT_ROOT/.claude/agents/AGENT-TEMPLATE.md"
AGENTS_DIR="$PROJECT_ROOT/.claude/agents"
LAUNCHER_FILE="$PROJECT_ROOT/agents/launch"
LOG_DIR="$PROJECT_ROOT/logs"
LOG_FILE="$LOG_DIR/agent-creation.log"
LOCK_FILE="/tmp/agent-creation-launcher.lock"
LOCK_TIMEOUT=30

# Default values
DEFAULT_MODEL="claude-sonnet-4-5-20250929"
DEFAULT_EMOJI="⚡"

# =============================================================================
# Logging Functions
# =============================================================================

# Escape a string for JSON (handles quotes, backslashes, newlines)
escape_json_string() {
    local input="$1"
    # Escape backslashes first, then quotes, then newlines/tabs
    printf '%s' "$input" | sed -e 's/\\/\\\\/g' -e 's/"/\\"/g' -e 's/	/\\t/g' | tr '\n' ' '
}

log_json() {
    local level="$1"
    local operation="$2"
    local status="$3"
    local message="${4:-}"
    local timestamp
    timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

    # Ensure logs directory exists
    mkdir -p "$LOG_DIR"

    # Escape values that might contain special characters
    local escaped_message
    escaped_message=$(escape_json_string "$message")
    local escaped_agent
    escaped_agent=$(escape_json_string "${AGENT_NAME:-unknown}")

    # Create JSON log entry with escaped values
    printf '{"timestamp":"%s","level":"%s","agent_name":"%s","operation":"%s","status":"%s","message":"%s"}\n' \
        "$timestamp" "$level" "$escaped_agent" "$operation" "$status" "$escaped_message" >> "$LOG_FILE"
}

log_info() {
    log_json "INFO" "$1" "$2" "${3:-}"
}

log_error() {
    log_json "ERROR" "$1" "failed" "$2"
}

# =============================================================================
# Error Handling
# =============================================================================

error_exit() {
    local exit_code="$1"
    local message="$2"
    local operation="${3:-general}"

    echo "ERROR: $message" >&2
    log_error "$operation" "$message"
    exit "$exit_code"
}

user_error() {
    local message="$1"
    local action="${2:-}"
    echo "ERROR: $message" >&2
    if [[ -n "$action" ]]; then
        echo "ACTION: $action" >&2
    fi
    log_error "validation" "$message"
    exit 1
}

system_error() {
    local message="$1"
    echo "ERROR: $message" >&2
    log_error "system" "$message"
    exit 2
}

# =============================================================================
# Cleanup Handler
# =============================================================================

TEMP_FILES=()
AGENT_FILE_CREATED=""
BACKUP_FILE=""
LOCK_ACQUIRED=""

cleanup() {
    local exit_code=$?

    # Remove temporary files (handle empty array safely)
    if [[ ${#TEMP_FILES[@]} -gt 0 ]]; then
        for temp_file in "${TEMP_FILES[@]}"; do
            rm -f "$temp_file" 2>/dev/null || true
        done
    fi

    # If we failed and created an agent file, remove it
    if [[ $exit_code -ne 0 && -n "$AGENT_FILE_CREATED" && -f "$AGENT_FILE_CREATED" ]]; then
        rm -f "$AGENT_FILE_CREATED" 2>/dev/null || true
        log_info "cleanup" "completed" "Removed partial agent file"
    fi

    # Restore backup if exists and we failed
    if [[ $exit_code -ne 0 && -n "$BACKUP_FILE" && -f "$BACKUP_FILE" ]]; then
        mv "$BACKUP_FILE" "$LAUNCHER_FILE" 2>/dev/null || true
        log_info "cleanup" "completed" "Restored launcher backup"
    elif [[ -n "$BACKUP_FILE" && -f "$BACKUP_FILE" ]]; then
        rm -f "$BACKUP_FILE" 2>/dev/null || true
    fi

    # Release lock if held
    if [[ -n "${LOCK_ACQUIRED:-}" ]]; then
        if [[ "$LOCK_ACQUIRED" == "flock" ]]; then
            # Release flock (use fixed FD 200 for bash 3.2 compatibility)
            flock -u 200 2>/dev/null || true
            exec 200>&- 2>/dev/null || true
        elif [[ "$LOCK_ACQUIRED" == "file" ]]; then
            # Remove file-based lock
            rm -f "$LOCK_FILE" 2>/dev/null || true
        fi
    fi

    exit "$exit_code"
}

trap cleanup EXIT

# =============================================================================
# Usage and Help
# =============================================================================

usage() {
    cat <<EOF
Usage: $0 agent-name "description" [options]

Creates a new agent from the AGENT-TEMPLATE.md template.

Arguments:
  agent-name       Agent name in kebab-case (e.g., my-agent)
  description      One-sentence description of the agent's role

Options:
  --model MODEL    Model to use (default: $DEFAULT_MODEL)
  --emoji EMOJI    Icon emoji for the agent (default: $DEFAULT_EMOJI)
  --serena         Add agent to serena_agents array for code navigation
  --position N     Position in agent_order array (default: end)
  --force          Overwrite existing agent file
  --dry-run        Show what would be done without making changes
  -h, --help       Show this help message

Exit Codes:
  0  Success - agent created successfully
  1  User error - invalid input, duplicate name, etc.
  2  System error - missing template, permission issues, etc.

Examples:
  $0 data-analyzer "Analyzes data patterns and generates reports"
  $0 security-scanner "Scans code for security vulnerabilities" --serena --emoji 🔐
  $0 test-helper "Assists with test writing" --model claude-opus-4-5-20251101

EOF
}

# =============================================================================
# String Escaping
# =============================================================================

# Escape special characters for sed replacement strings
# This prevents issues with descriptions containing &, /, \, etc.
escape_sed_replacement() {
    local input="$1"
    # Escape backslash first, then ampersand, then forward slash
    printf '%s' "$input" | sed -e 's/\\/\\\\/g' -e 's/&/\\&/g' -e 's/\//\\\//g'
}

# =============================================================================
# Input Validation
# =============================================================================

validate_agent_name() {
    local name="$1"

    # Check for empty name
    if [[ -z "$name" ]]; then
        user_error "Agent name is required." "Provide a valid kebab-case name."
    fi

    # Check for spaces
    if [[ "$name" =~ [[:space:]] ]]; then
        user_error "Agent name cannot contain spaces." "Use kebab-case like 'my-agent' instead."
    fi

    # Check for special characters (allow only alphanumeric and hyphens)
    if [[ ! "$name" =~ ^[a-zA-Z][a-zA-Z0-9-]*$ ]]; then
        user_error "Invalid agent name: '$name'." "Use kebab-case with only letters, numbers, and hyphens. Must start with a letter."
    fi

    # Check length
    if [[ ${#name} -gt 50 ]]; then
        user_error "Agent name is too long (${#name} characters)." "Agent names must be 50 characters or fewer."
    fi

    # Check for reserved names (use tr for case-insensitive comparison - compatible with bash 3.2)
    local reserved_names=("AGENT-TEMPLATE" "OPERATIONAL-RULES" "TASK-STARTER-TEMPLATE")
    local name_lower
    name_lower=$(echo "$name" | tr '[:upper:]' '[:lower:]')
    for reserved in "${reserved_names[@]}"; do
        local reserved_lower
        reserved_lower=$(echo "$reserved" | tr '[:upper:]' '[:lower:]')
        if [[ "$name_lower" == "$reserved_lower" ]]; then
            user_error "Agent name '$name' is reserved." "Choose a different name."
        fi
    done
}

validate_description() {
    local desc="$1"

    if [[ -z "$desc" ]]; then
        user_error "Description is required." "Provide a one-sentence description of the agent's role."
    fi

    # Description should be reasonable length
    if [[ ${#desc} -gt 500 ]]; then
        user_error "Description is too long (${#desc} characters)." "Keep the description under 500 characters."
    fi
}

check_duplicate() {
    local name="$1"
    local agents_dir="$2"
    local force="$3"

    local agent_file="$agents_dir/${name}.md"

    if [[ -f "$agent_file" ]]; then
        if [[ "$force" == "true" ]]; then
            log_info "validation" "overwrite" "Overwriting existing agent: $name"
            return 0
        else
            user_error "Agent '$name' already exists." "Use --force to overwrite or choose a different name."
        fi
    fi
}

# =============================================================================
# File Locking
# =============================================================================

acquire_lock() {
    log_info "locking" "started" "Acquiring exclusive lock"

    # Check if flock is available (not available by default on macOS)
    if ! command -v flock &> /dev/null; then
        # Fallback: use atomic lock file creation with noclobber
        # This prevents TOCTOU race conditions
        log_info "locking" "fallback" "flock not available, using file-based lock"

        local wait_time=0
        local lock_acquired=false

        while [[ $wait_time -lt $LOCK_TIMEOUT ]]; do
            # Use noclobber (set -C) for atomic file creation
            # This prevents race conditions between check and create
            if (set -C; echo "$$" > "$LOCK_FILE") 2>/dev/null; then
                lock_acquired=true
                break
            fi

            # Check for stale lock (crashed process)
            if [[ -f "$LOCK_FILE" ]]; then
                local lock_pid
                lock_pid=$(cat "$LOCK_FILE" 2>/dev/null || echo "")
                if [[ -n "$lock_pid" ]] && ! kill -0 "$lock_pid" 2>/dev/null; then
                    # Process no longer exists, remove stale lock
                    log_info "locking" "stale_detected" "Removing stale lock from PID $lock_pid"
                    rm -f "$LOCK_FILE"
                    # Try again immediately
                    continue
                fi
            fi

            sleep 1
            wait_time=$((wait_time + 1))
        done

        if [[ "$lock_acquired" != "true" ]]; then
            system_error "Could not acquire lock after ${LOCK_TIMEOUT}s. Another agent creation may be in progress."
        fi

        LOCK_ACQUIRED="file"
        log_info "locking" "completed" "File-based lock acquired"
        return 0
    fi

    # Open lock file on fixed FD 200 (bash 3.2 compatible)
    exec 200>"$LOCK_FILE"

    # Try to acquire lock with timeout
    if ! flock -x -w "$LOCK_TIMEOUT" 200; then
        system_error "Could not acquire lock after ${LOCK_TIMEOUT}s. Another agent creation may be in progress."
    fi

    # Mark that we acquired the lock for cleanup
    LOCK_ACQUIRED="flock"

    log_info "locking" "completed" "Lock acquired"
}

# =============================================================================
# Template Processing
# =============================================================================

process_template() {
    local agent_name="$1"
    local description="$2"
    local model="$3"
    local emoji="$4"
    local template_file="$5"
    local output_file="$6"
    local dry_run="$7"

    log_info "template" "started" "Processing template for $agent_name"

    # Check template exists
    if [[ ! -f "$template_file" ]]; then
        system_error "Template file not found: $template_file"
    fi

    if [[ ! -r "$template_file" ]]; then
        system_error "Template file not readable: $template_file"
    fi

    if [[ "$dry_run" == "true" ]]; then
        echo "Would create agent file: $output_file"
        echo "  - Replace [agent-name] with: $agent_name"
        echo "  - Replace description placeholder with: $description"
        echo "  - Replace model with: $model"
        return 0
    fi

    # Create agent name variants for replacement
    local agent_name_upper
    agent_name_upper=$(echo "$agent_name" | tr '[:lower:]' '[:upper:]' | tr '-' '_')

    local agent_name_title
    agent_name_title=$(echo "$agent_name" | sed 's/-/ /g' | awk '{for(i=1;i<=NF;i++) $i=toupper(substr($i,1,1)) tolower(substr($i,2))}1')

    # Escape description for sed replacement (handles &, /, \ etc.)
    local description_escaped
    description_escaped=$(escape_sed_replacement "$description")

    # Process template with sed
    # Using a temp file to ensure atomic writes
    local temp_file
    temp_file=$(mktemp)
    TEMP_FILES+=("$temp_file")

    # Replace placeholders (use escaped description to handle special chars)
    sed -e "s/\[agent-name\]/${agent_name}/g" \
        -e "s/\[Agent Name\]/${agent_name_title}/g" \
        -e "s/\[AGENT-NAME-UPPERCASE\]/${agent_name_upper}/g" \
        -e "s/\[EMOJI\]/${emoji}/g" \
        -e "s/\[One sentence description of agent role and primary responsibility\]/${description_escaped}/g" \
        -e "s/\[One sentence description[^]]*\]/${description_escaped}/g" \
        -e "s/claude-sonnet-4-20250514/${model}/g" \
        "$template_file" > "$temp_file"

    # Verify processing worked
    if [[ ! -s "$temp_file" ]]; then
        system_error "Template processing failed - output file is empty"
    fi

    # Move to final location
    mv "$temp_file" "$output_file"
    AGENT_FILE_CREATED="$output_file"

    log_info "template" "completed" "Created agent file: $output_file"
}

# =============================================================================
# Launcher Integration
# =============================================================================

update_launcher() {
    local agent_name="$1"
    local emoji="$2"
    local add_serena="$3"
    local position="$4"
    local launcher_file="$5"
    local dry_run="$6"

    log_info "launcher" "started" "Updating launcher arrays"

    # Check launcher exists
    if [[ ! -f "$launcher_file" ]]; then
        system_error "Launcher file not found: $launcher_file"
    fi

    if [[ ! -w "$launcher_file" ]]; then
        system_error "Launcher file not writable: $launcher_file"
    fi

    if [[ "$dry_run" == "true" ]]; then
        echo "Would update launcher: $launcher_file"
        echo "  - Add '$agent_name' to agent_order array"
        if [[ "$add_serena" == "true" ]]; then
            echo "  - Add '$agent_name' to serena_agents array"
        fi
        echo "  - Add icon mapping: $agent_name -> $emoji"
        return 0
    fi

    # Create backup
    BACKUP_FILE="${launcher_file}.backup"
    cp "$launcher_file" "$BACKUP_FILE"

    local temp_file
    temp_file=$(mktemp)
    TEMP_FILES+=("$temp_file")

    # Read launcher content
    local content
    content=$(cat "$launcher_file")

    # 1. Update agent_order array (skip if agent already exists)
    # First check if agent already exists in agent_order
    if ! echo "$content" | grep -q "agent_order=" | grep -q "\"$agent_name\""; then
        # Check within the agent_order block
        if ! echo "$content" | awk -v agent="$agent_name" '
            /agent_order=\(/ { in_array=1 }
            in_array && index($0, "\"" agent "\"") { found=1; exit }
            in_array && /\)/ { exit }
            END { exit !found }
        '; then
            # Agent not found, add it
            content=$(echo "$content" | awk -v agent="$agent_name" '
                /agent_order=\(/ { in_array=1 }
                in_array && /\)/ {
                    sub(/\)/, "        \"" agent "\"\n    )")
                    in_array=0
                }
                { print }
            ')
        fi
    fi

    # 2. Update serena_agents array if requested (skip if agent already exists)
    if [[ "$add_serena" == "true" ]]; then
        # Check if agent already exists in serena_agents
        if ! echo "$content" | awk -v agent="$agent_name" '
            /serena_agents=\(/ { in_array=1 }
            in_array && index($0, "\"" agent "\"") { found=1; exit }
            in_array && /\)/ { exit }
            END { exit !found }
        '; then
            # Agent not found, add it
            content=$(echo "$content" | awk -v agent="$agent_name" '
                /serena_agents=\(/ { in_array=1 }
                in_array && /\)/ {
                    sub(/\)/, "        \"" agent "\"\n    )")
                    in_array=0
                }
                { print }
            ')
        fi
    fi

    # 3. Update get_agent_icon function (skip if mapping already exists)
    # Add new icon mapping before the final echo "$icon"
    # Note: The pattern must be unquoted on the right side of == for glob matching to work
    local icon_line="    [[ \"\$name\" == *\"${agent_name}\"* ]] && icon=\"${emoji}\""

    # Check if icon mapping already exists
    if ! echo "$content" | awk -v agent="$agent_name" '
        /get_agent_icon\(\)/ { in_func=1 }
        in_func && index($0, "\"" agent "\"") { found=1; exit }
        in_func && /^}/ { exit }
        END { exit !found }
    '; then
        # Icon mapping not found, add it
        content=$(echo "$content" | awk -v icon_line="$icon_line" '
            /get_agent_icon\(\)/ { in_func=1 }
            in_func && /echo "\$icon"/ {
                print icon_line
            }
            { print }
        ')
    fi

    # Write to temp file
    echo "$content" > "$temp_file"

    # Validate syntax
    if ! bash -n "$temp_file" 2>/dev/null; then
        system_error "Generated launcher file has syntax errors"
    fi

    # Atomic move
    mv "$temp_file" "$launcher_file"

    # Remove backup on success
    rm -f "$BACKUP_FILE"
    BACKUP_FILE=""

    log_info "launcher" "completed" "Updated launcher with $agent_name"
}

# =============================================================================
# Main Function
# =============================================================================

main() {
    # Parse arguments
    local agent_name=""
    local description=""
    local model="$DEFAULT_MODEL"
    local emoji="$DEFAULT_EMOJI"
    local add_serena="false"
    local position="end"
    local force="false"
    local dry_run="false"

    while [[ $# -gt 0 ]]; do
        case "$1" in
            -h|--help)
                usage
                exit 0
                ;;
            --model)
                model="${2:-}"
                if [[ -z "$model" ]]; then
                    user_error "--model requires a value"
                fi
                shift 2
                ;;
            --emoji)
                emoji="${2:-}"
                if [[ -z "$emoji" ]]; then
                    user_error "--emoji requires a value"
                fi
                shift 2
                ;;
            --serena)
                add_serena="true"
                shift
                ;;
            --position)
                # Note: Position flag is accepted but not yet implemented
                # Agent is always appended at the end of agent_order
                if [[ -z "${2:-}" || "$2" == -* ]]; then
                    user_error "--position requires a numeric value"
                fi
                position="$2"
                if [[ "$position" != "end" ]]; then
                    echo "Warning: --position is not yet fully implemented. Agent will be appended at end." >&2
                fi
                shift 2
                ;;
            --force)
                force="true"
                shift
                ;;
            --dry-run)
                dry_run="true"
                shift
                ;;
            -*)
                user_error "Unknown option: $1" "Run with --help for usage."
                ;;
            *)
                # Positional arguments
                if [[ -z "$agent_name" ]]; then
                    agent_name="$1"
                elif [[ -z "$description" ]]; then
                    description="$1"
                else
                    user_error "Unexpected argument: $1" "Run with --help for usage."
                fi
                shift
                ;;
        esac
    done

    # Store agent name globally for logging
    AGENT_NAME="$agent_name"

    # Validate required arguments
    if [[ -z "$agent_name" ]]; then
        echo "ERROR: Agent name is required." >&2
        echo "" >&2
        usage >&2
        exit 1
    fi

    if [[ -z "$description" ]]; then
        user_error "Description is required." "Provide a one-sentence description after the agent name."
    fi

    # Resolve paths based on current working directory
    # This allows running from different directories (like temp dirs in tests)
    local cwd_agents_dir="$PWD/.claude/agents"
    local cwd_launcher="$PWD/agents/launch"
    local cwd_template="$PWD/.claude/agents/AGENT-TEMPLATE.md"
    local cwd_log_dir="$PWD/logs"

    # Detect if running from a different directory than the script's project
    local use_cwd_paths="false"
    if [[ -d "$cwd_agents_dir" && "$cwd_agents_dir" != "$AGENTS_DIR" ]]; then
        use_cwd_paths="true"
    fi

    # Use CWD paths if running from a different directory
    if [[ "$use_cwd_paths" == "true" ]]; then
        AGENTS_DIR="$cwd_agents_dir"
        TEMPLATE_FILE="$cwd_template"
        LAUNCHER_FILE="$cwd_launcher"
        LOG_DIR="$cwd_log_dir"
        LOG_FILE="$LOG_DIR/agent-creation.log"
    fi

    local agent_file="$AGENTS_DIR/${agent_name}.md"

    log_info "create" "started" "Creating agent: $agent_name"

    # Validate inputs
    validate_agent_name "$agent_name"
    validate_description "$description"
    check_duplicate "$agent_name" "$AGENTS_DIR" "$force"

    # Validate template exists BEFORE acquiring lock (fail fast)
    if [[ ! -f "$TEMPLATE_FILE" ]]; then
        system_error "Template file not found: $TEMPLATE_FILE"
    fi

    # Validate launcher exists BEFORE acquiring lock (fail fast)
    if [[ ! -f "$LAUNCHER_FILE" ]]; then
        system_error "Launcher file not found: $LAUNCHER_FILE"
    fi

    # Acquire lock for launcher updates
    if [[ "$dry_run" != "true" ]]; then
        acquire_lock
    fi

    # Process template
    process_template "$agent_name" "$description" "$model" "$emoji" \
        "$TEMPLATE_FILE" "$agent_file" "$dry_run"

    # Update launcher
    update_launcher "$agent_name" "$emoji" "$add_serena" "$position" \
        "$LAUNCHER_FILE" "$dry_run"

    # Success
    if [[ "$dry_run" == "true" ]]; then
        echo ""
        echo "DRY RUN: No changes made."
    else
        echo "SUCCESS: Agent '$agent_name' created successfully."
        echo "  File: $agent_file"
        echo "  Model: $model"
        if [[ "$add_serena" == "true" ]]; then
            echo "  Serena: enabled"
        fi
    fi

    log_info "create" "completed" "Agent created successfully"
    exit 0
}

# Run main
main "$@"
