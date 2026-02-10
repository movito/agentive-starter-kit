#!/bin/bash
# =============================================================================
# create-agent.sh — Agent Creation Automation Script
# Part of Agentive Starter Kit (ASK-0033 v2)
#
# Creates a new Claude Code agent from AGENT-TEMPLATE.md and registers it
# in the agents/launch launcher script.
#
# Uses mkdir-based atomic locking for concurrent safety.
# NFS caveat: mkdir atomicity is not guaranteed on NFS. This script targets
# local development and CI runners, not networked filesystems.
#
# See: docs/decisions/starter-kit-adr/ for architectural decisions
# =============================================================================

set -euo pipefail

# =============================================================================
# Configuration
# =============================================================================
LOCK_STALE_SECS="${CREATE_AGENT_LOCK_STALE_SECS:-60}"
LOCK_WAIT_SECS="${CREATE_AGENT_LOCK_WAIT_SECS:-30}"
DEFAULT_MODEL="claude-sonnet-4-5-20250929"

# Path resolution: env var > script-relative
if [[ -n "${CREATE_AGENT_PROJECT_ROOT:-}" ]]; then
    PROJECT_ROOT="$CREATE_AGENT_PROJECT_ROOT"
else
    PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
fi

# Per-project lock dir to avoid cross-repo collisions (env var overrides)
if [[ -n "${CREATE_AGENT_LOCK_DIR:-}" ]]; then
    LOCK_DIR="$CREATE_AGENT_LOCK_DIR"
else
    _project_hash=$(printf '%s' "$PROJECT_ROOT" | md5 -q 2>/dev/null || printf '%s' "$PROJECT_ROOT" | md5sum 2>/dev/null | cut -c1-12 || echo "default")
    LOCK_DIR="/tmp/agent-creation-${_project_hash}.lock"
fi
LOCK_INFO="$LOCK_DIR/owner"

TEMPLATE_FILE="$PROJECT_ROOT/.claude/agents/AGENT-TEMPLATE.md"
LAUNCHER_FILE="$PROJECT_ROOT/agents/launch"
LOG_DIR="$PROJECT_ROOT/logs"
LOG_FILE="$LOG_DIR/agent-creation.log"

# Script start time for duration tracking
START_TIME=$(date +%s%N 2>/dev/null || python3 -c "import time; print(int(time.time()*1e9))")

# =============================================================================
# Logging (JSON via python3 — fixes S10)
# =============================================================================
log_json() {
    local level="$1"
    local operation="$2"
    local status="$3"
    local agent="${AGENT_NAME:-unknown}"
    local error="${4:-}"
    local now
    now=$(date +%s%N 2>/dev/null || python3 -c "import time; print(int(time.time()*1e9))")
    local duration_ms
    duration_ms=$(python3 -c "print(($now - $START_TIME) // 1000000)")

    mkdir -p "$LOG_DIR"
    python3 -c "
import json, datetime, sys
entry = {
    'timestamp': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'level': sys.argv[1],
    'operation': sys.argv[2],
    'agent_name': sys.argv[3],
    'status': sys.argv[4],
    'duration_ms': int(sys.argv[5]),
    'error': sys.argv[6] if sys.argv[6] else None,
    'details': {}
}
print(json.dumps(entry))
" "$level" "$operation" "$agent" "$status" "$duration_ms" "$error" >> "$LOG_FILE"
}

# =============================================================================
# Error handlers: user_error (exit 1), system_error (exit 2)
# =============================================================================
user_error() {
    echo "Error: $1" >&2
    log_json "ERROR" "validate" "failed" "$1"
    exit 1
}

system_error() {
    echo "System error: $1" >&2
    log_json "ERROR" "system" "failed" "$1"
    exit 2
}

# =============================================================================
# Cleanup trap
# =============================================================================
cleanup() {
    # Only remove lock if we own it
    if [[ -f "$LOCK_INFO" ]]; then
        local lock_pid
        lock_pid=$(grep '^pid=' "$LOCK_INFO" 2>/dev/null | cut -d= -f2)
        if [[ "$lock_pid" == "$$" ]]; then
            rm -rf "$LOCK_DIR"
        fi
    fi
}
trap cleanup EXIT

# =============================================================================
# Locking (mkdir-based atomic — fixes S5, S6)
# =============================================================================
is_lock_stale() {
    # No owner file = lock was JUST created (race window between mkdir and
    # writing owner). Treat as NOT stale to avoid TOCTOU race.
    [[ ! -f "$LOCK_INFO" ]] && return 1

    local lock_pid lock_time now
    lock_pid=$(grep '^pid=' "$LOCK_INFO" 2>/dev/null | cut -d= -f2)
    lock_time=$(grep '^time=' "$LOCK_INFO" 2>/dev/null | cut -d= -f2)
    now=$(date +%s)

    # No valid PID in owner file = corrupted, treat as stale
    [[ -z "$lock_pid" ]] && return 0

    # PID not running = stale
    if ! kill -0 "$lock_pid" 2>/dev/null; then
        return 0
    fi

    # Age exceeds threshold (guards against PID reuse)
    if [[ -n "$lock_time" ]] && [[ $((now - lock_time)) -gt "$LOCK_STALE_SECS" ]]; then
        return 0
    fi

    return 1  # Lock is valid
}

acquire_lock() {
    local max_wait="$LOCK_WAIT_SECS"
    local waited=0

    while ! mkdir "$LOCK_DIR" 2>/dev/null; do
        if is_lock_stale; then
            log_json "WARN" "lock" "started" "Removing stale lock"
            rm -rf "$LOCK_DIR"
            continue
        fi
        if [[ "$waited" -ge "$max_wait" ]]; then
            system_error "Lock acquisition timeout after ${max_wait}s"
        fi
        waited=$((waited + 1))
        sleep 1
    done

    # Write owner metadata
    echo "pid=$$" > "$LOCK_INFO"
    echo "token=$(python3 -c 'import secrets; print(secrets.token_hex(8))')" >> "$LOCK_INFO"
    echo "time=$(date +%s)" >> "$LOCK_INFO"
    log_json "INFO" "lock" "completed" ""

    # Optional delay for concurrency testing (ensures lock is held long enough)
    if [[ -n "${CREATE_AGENT_WORK_DELAY:-}" ]] && [[ "$CREATE_AGENT_WORK_DELAY" -gt 0 ]]; then
        sleep "$CREATE_AGENT_WORK_DELAY"
    fi
}

release_lock() {
    rm -rf "$LOCK_DIR"
}

# =============================================================================
# Input escaping for sed (fixes S1)
# Escaping order: \, &, | (delimiter)
# =============================================================================
escape_sed() {
    local text="$1"
    text="${text//\\/\\\\}"   # \ → \\
    text="${text//&/\\&}"     # & → \&
    text="${text//|/\\|}"     # | → \|
    # Strip newlines — descriptions are single-sentence
    text="${text//$'\n'/ }"
    echo "$text"
}

# =============================================================================
# Input validation
# =============================================================================
validate_name() {
    local name="$1"

    # Length check: 2-30 chars
    if [[ ${#name} -lt 2 ]]; then
        user_error "Agent name must be at least 2 characters (got ${#name})"
    fi
    if [[ ${#name} -gt 30 ]]; then
        user_error "Agent name must be at most 30 characters (got ${#name})"
    fi

    # Format: lowercase letters, digits, hyphens only
    if [[ ! "$name" =~ ^[a-z][a-z0-9-]*[a-z0-9]$ ]] && [[ ! "$name" =~ ^[a-z][a-z0-9]$ ]]; then
        user_error "Agent name must be lowercase letters, digits, and hyphens (got: $name)"
    fi

    # No double hyphens
    if [[ "$name" == *"--"* ]]; then
        user_error "Agent name must not contain consecutive hyphens"
    fi
}

# =============================================================================
# Help / Usage
# =============================================================================
show_help() {
    cat <<'USAGE'
Usage: scripts/create-agent.sh <name> <description> [options]

Required:
  <name>            Agent name (lowercase, hyphens allowed, 2-30 chars)
  <description>     One-sentence description (quoted string)

Options:
  --model <id>      Claude model ID (default: claude-sonnet-4-5-20250929)
  --emoji <char>    Icon emoji for launcher menu (default: auto-assigned)
  --serena          Enable Serena auto-activation for this agent
  --force           Overwrite existing agent (replaces file + launcher entries)
  --dry-run         Show what would be done without making changes
  --help            Show usage information

Exit Codes:
  0  Success
  1  User error (invalid input, duplicate name)
  2  System error (lock timeout, file I/O failure, missing template/dependencies)

Environment:
  CREATE_AGENT_PROJECT_ROOT    Override project root directory
  CREATE_AGENT_LOCK_DIR        Override lock directory path (default: per-project)
  CREATE_AGENT_LOCK_STALE_SECS Lock stale threshold in seconds (default: 60)
  CREATE_AGENT_LOCK_WAIT_SECS  Max seconds to wait for lock (default: 30)
USAGE
}

# =============================================================================
# Template processing
# =============================================================================
process_template() {
    local name="$1"
    local description="$2"
    local model="$3"
    local output_file="$4"

    if [[ ! -f "$TEMPLATE_FILE" ]]; then
        system_error "Template file not found: $TEMPLATE_FILE"
    fi

    local escaped_desc
    escaped_desc=$(escape_sed "$description")

    # Title case the name for display (hyphens → spaces, capitalize words)
    local display_name
    display_name=$(echo "$name" | sed 's/-/ /g' | awk '{for(i=1;i<=NF;i++) $i=toupper(substr($i,1,1)) substr($i,2)}1')

    # Process template with sed using | delimiter (fixes S1)
    # Step 1: Replace known placeholders with actual values
    # Step 2: Replace any remaining [Uppercase Placeholder] patterns with agent-specific defaults
    local uppercase_name
    uppercase_name=$(echo "$name" | tr '[:lower:]-' '[:upper:]_')

    sed \
        -e "s|\[agent-name\]|${name}|g" \
        -e "s|\[Agent Name\]|${display_name}|g" \
        -e "s|\[AGENT-NAME-UPPERCASE\]|${uppercase_name}|g" \
        -e "s|\[EMOJI\]|${emoji}|g" \
        -e "s|\[One sentence description of agent role and primary responsibility\]|${escaped_desc}|g" \
        -e "s|\[role description\]|${escaped_desc}|g" \
        -e "s|\[primary responsibilities\]|${escaped_desc}|g" \
        -e "s|\[current task description or \"Agent Role Name\"\]|${display_name}|g" \
        -e "s|model: .*|model: ${model}|" \
        "$TEMPLATE_FILE" > "$output_file"

    # Step 2: Remove remaining [Uppercase...] template placeholders (T7)
    # Uses python3 for reliable regex replacement across all platforms
    python3 -c "
import re, sys
path = sys.argv[1]
with open(path, 'r') as f:
    content = f.read()
# Replace [Placeholder Text] patterns with empty string
content = re.sub(r'\[[A-Z][A-Za-z -]+\]', '', content)
with open(path, 'w') as f:
    f.write(content)
" "$output_file"

    log_json "INFO" "template" "completed" ""
}

# =============================================================================
# Launcher updates (AWK-based — fixes S3, S4, S9)
# =============================================================================

# Add agent to agent_order array
update_agent_order() {
    local name="$1"
    local launcher="$2"
    local force="$3"

    # If force, first remove existing entry
    if [[ "$force" == "true" ]]; then
        awk -v agent="$name" '
        /local agent_order=\(/ { in_block=1 }
        in_block && $0 ~ "\"" agent "\"" { next }
        /^[[:space:]]*\)/ && in_block { in_block=0 }
        { print }
        ' "$launcher" > "${launcher}.tmp" && mv "${launcher}.tmp" "$launcher"
    fi

    # Check if already present
    if awk '/local agent_order=\(/,/\)/' "$launcher" | grep -q "\"$name\""; then
        return 0  # Already present
    fi

    # Add before closing paren of agent_order array
    awk -v agent="$name" '
    /local agent_order=\(/ { in_block=1 }
    in_block && /^[[:space:]]*\)/ {
        printf "        \"%s\"\n", agent
        in_block=0
    }
    { print }
    ' "$launcher" > "${launcher}.tmp" && mv "${launcher}.tmp" "$launcher"
}

# Add agent to serena_agents array
update_serena_agents() {
    local name="$1"
    local launcher="$2"
    local force="$3"

    # If force, first remove existing entry
    if [[ "$force" == "true" ]]; then
        awk -v agent="$name" '
        /local serena_agents=\(/ { in_block=1 }
        in_block && $0 ~ "\"" agent "\"" { next }
        /^[[:space:]]*\)/ && in_block { in_block=0 }
        { print }
        ' "$launcher" > "${launcher}.tmp" && mv "${launcher}.tmp" "$launcher"
    fi

    # Check if already present
    if awk '/local serena_agents=\(/,/\)/' "$launcher" | grep -q "\"$name\""; then
        return 0
    fi

    # Add before closing paren
    awk -v agent="$name" '
    /local serena_agents=\(/ { in_block=1 }
    in_block && /^[[:space:]]*\)/ {
        printf "        \"%s\"\n", agent
        in_block=0
    }
    { print }
    ' "$launcher" > "${launcher}.tmp" && mv "${launcher}.tmp" "$launcher"
}

# Add icon mapping to get_agent_icon function
update_agent_icon() {
    local name="$1"
    local emoji="$2"
    local launcher="$3"
    local force="$4"

    # If force, remove existing icon mapping (handles both *"name"* and *name* patterns)
    if [[ "$force" == "true" ]]; then
        awk -v agent="$name" '
        /get_agent_icon\(\)/ { in_func=1 }
        in_func && $0 ~ "\\*" agent "\\*" { next }
        in_func && /^}/ { in_func=0 }
        { print }
        ' "$launcher" > "${launcher}.tmp" && mv "${launcher}.tmp" "$launcher"
    fi

    # Check if already present in get_agent_icon function (match literal *name* pattern)
    if awk '/get_agent_icon\(\)/,/^}/' "$launcher" | grep -qF "*${name}*"; then
        return 0
    fi

    # Add before the echo "$icon" line in get_agent_icon
    # Note: glob pattern uses *name* without inner quotes (functionally identical
    # in [[ ]], avoids double-counting "name" when tests count quoted occurrences)
    awk -v agent="$name" -v emoji="$emoji" '
    /get_agent_icon\(\)/ { in_func=1 }
    in_func && /echo "\$icon"/ {
        printf "    [[ \"$name\" == *%s* ]] && icon=\"%s\"\n", agent, emoji
    }
    { print }
    ' "$launcher" > "${launcher}.tmp" && mv "${launcher}.tmp" "$launcher"
}

# Auto-assign emoji based on agent name
auto_assign_emoji() {
    local name="$1"
    # Simple heuristic based on common patterns
    case "$name" in
        *test*)    echo "🧪" ;;
        *review*)  echo "🔍" ;;
        *plan*)    echo "📋" ;;
        *doc*)     echo "📄" ;;
        *secur*)   echo "🔒" ;;
        *deploy*)  echo "🚀" ;;
        *debug*)   echo "🐛" ;;
        *data*)    echo "📊" ;;
        *monitor*) echo "📡" ;;
        *)         echo "⚡" ;;
    esac
}

# =============================================================================
# Main
# =============================================================================
main() {
    local name=""
    local description=""
    local model="$DEFAULT_MODEL"
    local emoji=""
    local serena="false"
    local force="false"
    local dry_run="false"

    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --help)
                show_help
                exit 0
                ;;
            --model)
                [[ $# -lt 2 ]] && user_error "--model requires a value"
                model="$2"
                shift 2
                ;;
            --emoji)
                [[ $# -lt 2 ]] && user_error "--emoji requires a value"
                emoji="$2"
                shift 2
                ;;
            --serena)
                serena="true"
                shift
                ;;
            --force)
                force="true"
                shift
                ;;
            --dry-run)
                dry_run="true"
                shift
                ;;
            --*)
                user_error "Unknown option: $1"
                ;;
            *)
                if [[ -z "$name" ]]; then
                    name="$1"
                elif [[ -z "$description" ]]; then
                    description="$1"
                else
                    user_error "Unexpected argument: $1"
                fi
                shift
                ;;
        esac
    done

    # Validate required args
    [[ -z "$name" ]] && user_error "Missing required argument: <name>. Run with --help for usage."
    [[ -z "$description" ]] && user_error "Missing required argument: <description>. Run with --help for usage."

    # Export for logging
    AGENT_NAME="$name"
    export AGENT_NAME

    log_json "INFO" "validate" "started" ""

    # Validate name format
    validate_name "$name"

    # Preflight: check python3 available (needed for JSON logging and token generation)
    if ! command -v python3 &>/dev/null; then
        system_error "python3 is required but not found in PATH"
    fi

    # Check template exists
    if [[ ! -f "$TEMPLATE_FILE" ]]; then
        system_error "Agent template not found: $TEMPLATE_FILE"
    fi

    # Check launcher exists
    if [[ ! -f "$LAUNCHER_FILE" ]]; then
        system_error "Launcher script not found: $LAUNCHER_FILE"
    fi

    local agent_file="$PROJECT_ROOT/.claude/agents/${name}.md"

    # Duplicate detection
    if [[ -f "$agent_file" ]] && [[ "$force" != "true" ]]; then
        if [[ "$dry_run" == "true" ]]; then
            echo "[dry-run] Agent '$name' already exists. Would need --force to overwrite."
            exit 0
        fi
        user_error "Agent '$name' already exists at $agent_file. Use --force to overwrite."
    fi

    # Auto-assign emoji if not provided
    if [[ -z "$emoji" ]]; then
        emoji=$(auto_assign_emoji "$name")
    fi

    log_json "INFO" "validate" "completed" ""

    # Dry-run mode
    if [[ "$dry_run" == "true" ]]; then
        echo "[dry-run] Would create agent '$name':"
        echo "  Agent file: $agent_file"
        echo "  Model: $model"
        echo "  Emoji: $emoji"
        echo "  Serena: $serena"
        echo "  Launcher: $LAUNCHER_FILE (would update agent_order, icon)"
        if [[ "$serena" == "true" ]]; then
            echo "  Launcher: would also update serena_agents"
        fi
        if [[ -f "$agent_file" ]]; then
            echo "  Note: existing agent would be overwritten (--force implied by --dry-run preview)"
        fi
        log_json "INFO" "validate" "completed" "dry-run"
        exit 0
    fi

    # Acquire lock
    acquire_lock

    # Re-check duplicate after lock (prevents TOCTOU between pre-check and lock)
    if [[ -f "$agent_file" ]] && [[ "$force" != "true" ]]; then
        release_lock
        user_error "Agent '$name' was created by another process while waiting for lock."
    fi

    # Process template
    log_json "INFO" "template" "started" ""
    process_template "$name" "$description" "$model" "$agent_file"

    # Update launcher
    log_json "INFO" "launcher" "started" ""
    update_agent_order "$name" "$LAUNCHER_FILE" "$force"

    if [[ "$serena" == "true" ]]; then
        update_serena_agents "$name" "$LAUNCHER_FILE" "$force"
    fi

    update_agent_icon "$name" "$emoji" "$LAUNCHER_FILE" "$force"
    log_json "INFO" "launcher" "completed" ""

    # Verify launcher is still valid bash (while still holding lock)
    if ! bash -n "$LAUNCHER_FILE" 2>/dev/null; then
        release_lock
        system_error "Launcher syntax validation failed after modification"
    fi

    # Release lock after validation
    release_lock

    log_json "INFO" "cleanup" "completed" ""

    echo "Agent '$name' created successfully."
    echo "  File: $agent_file"
    echo "  Launcher: $LAUNCHER_FILE (updated)"
}

main "$@"
