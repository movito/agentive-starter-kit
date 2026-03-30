# tmux Quick Reference for dispatch-kit

dispatch-kit uses tmux to run agents in separate panes. This guide covers
the full workflow from spawning to cleanup.

## Spawning agents

```bash
# Spawn an agent (opens in a new tmux pane)
dispatch spawn feature-developer-v3 --session-manager tmux

# Spawn with a starter file (auto-delivered after spawn_delay)
dispatch spawn feature-developer-v3 \
  --starter delegation/tasks/2-todo/DSP-0061-task.md \
  --session-manager tmux

# Spawn with a task ID (emits spawn event with task reference)
dispatch spawn feature-developer-v3 \
  --task DSP-0061 \
  --session-manager tmux

# Output: "Spawned feature-developer-v3 in tmux session 'dispatch' (pane %214)"
# Note the pane ID — you'll use it for everything below
```

**Spawn delay**: The starter message is delivered after a configurable delay
(default 2.0s, set to 10.0s locally). If Claude hasn't loaded yet, the message
is lost. Adjust in `.dispatch/config.local.yml`:

```yaml
interfaces:
  spawn_delay: 10.0
```

## Viewing and navigating

### From a regular terminal

```bash
# Attach to the dispatch tmux session (see all panes)
tmux attach -t dispatch

# Once inside tmux:
Ctrl+b  arrow-key     # Switch between panes
Ctrl+b  z             # Zoom/unzoom current pane (fullscreen toggle)
Ctrl+b  d             # Detach (back to host terminal)
```

### Scrolling

```bash
# Enable mouse scrolling (one-time setup)
echo 'set -g mouse on' >> ~/.tmux.conf
tmux source-file ~/.tmux.conf

# Keyboard scrolling: enter copy mode
Ctrl+b  [             # Enter copy mode
Arrow keys / PgUp     # Scroll
q                     # Exit copy mode
```

### Increase scroll history

```bash
echo 'set -g history-limit 10000' >> ~/.tmux.conf
tmux source-file ~/.tmux.conf
```

## Session management

```bash
# List all running agent panes
dispatch sessions list

# List with JSON output (for scripting)
dispatch sessions list --json

# Attach to a specific pane (brings it to focus)
dispatch sessions attach %214

# Kill a specific agent pane
dispatch sessions kill %214

# Kill ALL dispatch panes (nuclear option)
dispatch sessions kill --all
```

### Raw tmux equivalents

```bash
# List all panes with their commands
tmux list-panes -a -F "#{pane_id} #{pane_current_command}"

# Capture what's on screen in a pane (for checking progress)
tmux capture-pane -t %214 -p -S -30

# Send text to a pane (deliver a message to an agent)
tmux send-keys -t %214 "your message here" Enter

# Send Ctrl-C to interrupt an agent
tmux send-keys -t %214 C-c

# Kill a pane directly
tmux kill-pane -t %214
```

## Delivering messages to agents

```bash
# Via dispatch (writes to agent inbox + sends to tmux)
dispatch message feature-developer-v3 "Bot reviews are ready for PR #59"

# Via raw tmux (no inbox, just screen text)
tmux send-keys -t %214 "Check the bot reviews on PR #59" Enter
```

**Important**: Avoid sending messages with markdown backticks via
`tmux send-keys` — triple backticks can corrupt Claude Code's input
parser. Use `dispatch message` instead, or keep messages plain text.

## Monitoring an agent

```bash
# Quick status check (what's on screen)
tmux capture-pane -t %214 -p | tail -10

# Watch for activity keywords
tmux capture-pane -t %214 -p -S -50 | grep -E "Bash|Read|Edit|commit|FEATURE"

# Check if agent is at the prompt (idle) or working
tmux capture-pane -t %214 -p -S -5 | grep "❯"
```

## Common workflows

### Spawn agent, deliver task, monitor

```bash
# 1. Spawn
dispatch spawn feature-developer-v3 --session-manager tmux
# → pane %214

# 2. Wait for Claude to load (~10-15s)
sleep 15

# 3. Deliver task
tmux send-keys -t %214 "Implement DSP-0061. Read delegation/tasks/2-todo/DSP-0061.md" Enter

# 4. Monitor progress
watch -n 30 'tmux capture-pane -t %214 -p | tail -5'
```

### Clean up after a session

```bash
# See what's running
dispatch sessions list

# Close a finished agent gracefully
tmux send-keys -t %214 "/exit" Enter
sleep 3
tmux kill-pane -t %214

# Or just kill it
dispatch sessions kill %214
```

### Kill all agents and start fresh

```bash
dispatch sessions kill --all
```

## Autonomous operation tips

When running agents unattended (fire-and-forget), `$()` subshells in Bash
calls are the #1 cause of stalls. Claude Code's permission system blocks
command substitution even when the outer command is allowed.

### Avoid `$()` subshells

Instead of composing shell commands inline:

```bash
# BAD — triggers permission prompt, agent stalls
python scripts/pattern_lint.py $(find src -name "*.py")
```

Use the wrapper scripts that internalize the `find | xargs` pattern:

```bash
# GOOD — runs without permission prompts
./scripts/ci-check.sh           # full CI pipeline (format + lint + tests + arch)
./scripts/lint-all.sh            # pattern lint only (all src/ Python files)
./scripts/lint-all.sh tests/     # pattern lint a specific directory
```

### Pre-spawn checklist

Before spawning an agent you intend to leave unattended:

1. **Wrapper scripts available** — verify `./scripts/lint-all.sh` and
   `./scripts/ci-check.sh` exist and are executable
2. **Permission allow-list set** — check `.claude/settings.json` covers
   the `gh`, `git`, and `./scripts/*` commands the agent will need
3. **Spawn delay tuned** — set `spawn_delay` in `.dispatch/config.local.yml`
   high enough for Claude Code to load (~10s) so the starter message
   isn't lost
4. **No `$()` in task instructions** — grep the task spec for `$(` to
   catch any raw subshell patterns before they stall the agent

## Known issues

### Claude Code unresponsive in tmux

Claude Max may limit concurrent Opus sessions. If an agent accepts input
but never responds, check how many Claude sessions are active:

```bash
tmux list-panes -a -F "#{pane_id} #{pane_current_command}" | grep claude
```

Close idle sessions to free up API slots.

### Nested session detection

When `dispatch spawn` runs from inside a Claude Code session, the tmux pane
inherits the `CLAUDECODE` environment variable. The launcher detects this
and refuses to start.

**Already handled**: The default spawn command uses `env -u CLAUDECODE` to
strip this variable. If you see "nested session" errors, check that
`.dispatch/config.yml` has:

```yaml
interfaces:
  spawn_command: env -u CLAUDECODE agents/launch $AGENT_NAME
```

### Starter message lost

If the starter arrives before Claude Code loads, it's lost. Increase
`spawn_delay` in `.dispatch/config.local.yml` (currently 10.0s).

### Sessions are system-wide, not project-scoped

tmux sessions are global to the machine. `tmux list-sessions` shows everything
running across all projects, not just the current one. `dispatch spawn` puts
all agents in a single session called `dispatch` — so if two projects both use
dispatch-kit, their agents share the same session.

**Current workaround**: Only run agents for one project at a time, or manually
create separate tmux sessions per project (`tmux new-session -s myapi`).

**Future fix**: Project-scoped session names (e.g., `dispatch-myapi`) would
solve this. Requires a dispatch-kit config option for the session name.

### Text copied from tmux has invisible characters

tmux capture adds line-break artifacts. For clean text, use:

```bash
tmux capture-pane -t %214 -p -J    # -J joins wrapped lines
```
