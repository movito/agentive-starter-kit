# Serena Context Configuration Guide

**Version**: 1.0
**Date**: 2025-11-19
**Status**: ✅ AUTHORITATIVE GUIDE
**Problem**: Context changes from `desktop-app` to `agent` require specific steps
**Attempts Before This Doc**: 7 failed attempts
**Purpose**: Prevent future context configuration issues

---

## Table of Contents

1. [Quick Reference](#quick-reference)
2. [What Is Context?](#what-is-context)
3. [Configuration Files](#configuration-files)
4. [How to Change Context](#how-to-change-context)
5. [Verification Process](#verification-process)
6. [Common Pitfalls](#common-pitfalls)
7. [Troubleshooting](#troubleshooting)
8. [History & Learnings](#history--learnings)

---

## Quick Reference

### ⚡ Fast Context Change Checklist

```bash
# 1. Update repository config
# Edit: .serena/config/mcp-config.json
# Add: "--context", "agent" to args array

# 2. Update Claude Desktop config
# Edit: ~/Library/Application Support/Claude/claude_desktop_config.json
# Add: "--context", "agent" to args array

# 3. CRITICAL: Restart Claude Desktop/Code
# Close ALL windows, quit application completely
# Relaunch Claude Desktop/Code

# 4. Verify in a NEW conversation
# Type: mcp__serena__get_current_config
# Look for: "Active context: agent"

# 5. Verify in a NEW agent tab
# Invoke any agent in new tab
# Have agent run: mcp__serena__get_current_config
# Confirm tools are available
```

**⚠️ CRITICAL**: Changes take effect ONLY after full application restart, NOT mid-conversation!

---

## What Is Context?

### Context Parameter Purpose

The `--context` parameter tells Serena HOW to behave and which tools to enable:

| Context | Description | Use Case | Tool Availability |
|---------|-------------|----------|-------------------|
| `desktop-app` | Interactive desktop application mode | Claude Desktop main conversations | Main conversation ONLY |
| `agent` | Agent execution mode | Claude Code agent tabs | Main conversation AND agent tabs |
| `local-app` | (Legacy/deprecated?) | Unknown | Unknown |

### Why Context Matters

**Problem Discovered in THEMATIC-0107**:
- MCP tools (including Serena) were NOT available in agent tabs
- Only worked in main conversation thread
- Prevented autonomous agents from using semantic navigation

**Solution (Commit 437bad3)**:
- Add `--context agent` to enable tools in agent execution contexts
- Allows specialized agents (feature-developer, test-runner, etc.) to access Serena
- Unlocks semantic navigation for autonomous workflows

### Context vs. Modes

**Context** (server-level):
- Set via `--context` parameter when starting MCP server
- Controls which environments have access to tools
- Changed in MCP server configuration files

**Modes** (session-level):
- Set via `switch_modes` tool during a conversation
- Examples: `interactive`, `editing`, `planning`, `one-shot`
- Changed dynamically within a session

**Both are required for proper Serena operation.**

---

## Configuration Files

### File 1: Repository Config (In Git)

**Path**: `.serena/config/mcp-config.json`

**Purpose**:
- Template for MCP server configuration
- Used by team members setting up Serena
- Tracked in git repository

**Current Content**:
```json
{
  "mcpServers": {
    "serena": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/oraios/serena",
        "serena",
        "start-mcp-server",
        "--context",
        "agent",
        "--project",
        "/path/to/your-project"
      ]
    }
  }
}
```

**Key Parameters**:
- `command: "uvx"` - Use UV package manager to run Serena
- `serena` - Executable name (NOT `serena-mcp-server`)
- `start-mcp-server` - Subcommand to launch MCP server
- `--context agent` - **CRITICAL**: Enables agent tab access
- `--project <path>` - Absolute path to project root

### File 2: Claude Desktop Config (User-Specific)

**Path**: `~/Library/Application Support/Claude/claude_desktop_config.json`

**Purpose**:
- Actual configuration used by Claude Desktop/Code
- User-specific (NOT in git)
- Must be updated separately from repository config

**Current Content**:
```json
{
  "preferences": {
    "quickEntryDictationShortcut": "capslock"
  },
  "mcpServers": {
    "serena": {
      "command": "/Users/broadcaster_three/.local/bin/uvx",
      "args": [
        "--from",
        "git+https://github.com/oraios/serena",
        "serena-mcp-server",
        "--context",
        "agent",
        "--project",
        "/path/to/your-project"
      ]
    }
  }
}
```

**Key Differences from Repository Config**:
- `command` uses full path: `/Users/broadcaster_three/.local/bin/uvx`
- Uses `serena-mcp-server` instead of `serena` + `start-mcp-server`
- Both forms are valid (different Serena installation methods)

**⚠️ IMPORTANT**: Both files must have matching `--context` values!

### File 3: Global Serena Config

**Path**: `~/.serena/serena_config.yml`

**Purpose**:
- Global Serena settings (logging, dashboard, etc.)
- Does NOT control context (that's in MCP config)
- No context parameter here

**What It Controls**:
- GUI log window settings
- Web dashboard settings
- Log level
- Tool timeouts
- Excluded/included tools
- Registered projects list

**Not Relevant for Context**: This file does NOT affect context configuration.

### File 4: Project Config

**Path**: `.serena/project.yml`

**Purpose**:
- Project-specific settings (languages, encoding, etc.)
- Does NOT control context (that's in MCP config)
- No context parameter here

**What It Controls**:
- Programming languages to index
- File encoding
- Gitignore integration
- Ignored paths
- Read-only mode
- Excluded tools (project-level)

**Not Relevant for Context**: This file does NOT affect context configuration.

---

## How to Change Context

### Step 1: Update Repository Config (Optional)

**File**: `.serena/config/mcp-config.json`

**Why**:
- Template for team members
- Documents intended configuration
- Tracked in git for team consistency

**How**:
```bash
# Edit the file
vim .serena/config/mcp-config.json

# Ensure args array includes:
"args": [
  "--from",
  "git+https://github.com/oraios/serena",
  "serena",
  "start-mcp-server",
  "--context",
  "agent",           # ← CRITICAL: Add or verify this
  "--project",
  "/path/to/your-project"
]
```

**Commit the change**:
```bash
git add .serena/config/mcp-config.json
git commit -m "feat(serena): Set context to agent for agent tab support"
```

### Step 2: Update Claude Desktop Config (REQUIRED)

**File**: `~/Library/Application Support/Claude/claude_desktop_config.json`

**Why**:
- This is the ACTUAL config used by Claude Desktop/Code
- Repository config is just a template
- Must be updated for changes to take effect

**How**:
```bash
# Edit the file (use proper quoting for spaces in path)
vim ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Ensure args array includes:
"args": [
  "--from",
  "git+https://github.com/oraios/serena",
  "serena-mcp-server",
  "--context",
  "agent",           # ← CRITICAL: Add or verify this
  "--project",
  "/path/to/your-project"
]
```

**⚠️ WARNING**: Do NOT commit this file to git (it's user-specific)

### Step 3: Restart Claude Desktop/Code (CRITICAL)

**Why**:
- MCP servers are initialized at application startup
- Configuration is read ONCE when starting MCP servers
- Mid-conversation changes have NO effect
- Must fully quit and relaunch

**How**:
```bash
# 1. Close ALL Claude Desktop/Code windows
# 2. Quit the application completely (Cmd+Q on macOS)
# 3. Wait 5 seconds
# 4. Relaunch Claude Desktop/Code
```

**⚠️ CRITICAL**:
- Do NOT just close windows - must QUIT application
- Do NOT assume reload works - must fully restart
- Do NOT test in existing conversations - must start NEW conversation

### Step 4: Verify Changes (See Next Section)

---

## Verification Process

### Test 1: Verify Configuration Files

**Before Restart** - Check both config files have matching context:

```bash
# Check repository config
cat .serena/config/mcp-config.json | grep -A 2 "context"

# Expected output:
#   "--context",
#   "agent",

# Check Claude Desktop config
cat ~/Library/Application\ Support/Claude/claude_desktop_config.json | grep -A 2 "context"

# Expected output:
#   "--context",
#   "agent",
```

**If contexts don't match**: Update the mismatched file(s) and restart.

### Test 2: Verify Active Context (Main Conversation)

**After Restart** - Start a NEW main conversation:

1. **Open Claude Code** (after restart)
2. **Start a NEW conversation** (not existing one)
3. **Run**: `mcp__serena__get_current_config`
4. **Check output** for:
   ```
   Active context: agent
   ```

**Expected Success Output**:
```
Current configuration:
Serena version: 0.1.4-437bad3c-dirty
Active project: your-project
Active context: agent              # ← MUST say "agent"
Active modes: interactive, editing

Active tools (after all exclusions...):
  mcp__serena__activate_project
  mcp__serena__find_symbol
  mcp__serena__search_for_pattern
  ...
```

**If it says `desktop-app`**: Restart didn't work, see Troubleshooting.

### Test 3: Verify Agent Tab Access

**After Restart** - Test in a NEW agent tab:

1. **Invoke an agent** in a new tab (e.g., tycho)
2. **Ask the agent** to run: `mcp__serena__get_current_config`
3. **Verify agent has access** to Serena tools

**Expected Success Output** (from agent):
```
Current configuration:
Active context: agent
Active tools:
  mcp__serena__activate_project ✅
  mcp__serena__find_symbol ✅
  ...
```

**Expected Failure Output** (if context still `desktop-app`):
```
Error: MCP tools not available in agent execution context
```

### Test 4: End-to-End Functionality Test

**In agent tab** - Test actual Serena functionality:

```bash
# 1. Activate project
mcp__serena__activate_project("your-project")

# Expected: "Project activated..."

# 2. Find a symbol
mcp__serena__find_symbol(name_path_pattern="Timeline")

# Expected: Returns symbol information

# 3. Search for pattern
mcp__serena__search_for_pattern(substring_pattern="class Timeline")

# Expected: Returns search results
```

**If any fail**: Context change didn't take effect, see Troubleshooting.

---

## Common Pitfalls

### Pitfall 1: Only Updating One Config File

**Problem**:
- Updated `.serena/config/mcp-config.json` (repository)
- Forgot to update `~/Library/Application Support/Claude/claude_desktop_config.json` (actual)

**Why It Happens**:
- Two files have similar content
- Easy to assume changing one updates the other
- Repository config is just a template

**Solution**:
- **ALWAYS update the Claude Desktop config** (`~/Library/...`)
- Repository config is optional (for team documentation only)

### Pitfall 2: Not Restarting Application

**Problem**:
- Updated config file
- Didn't restart Claude Desktop/Code
- Expected changes to apply immediately

**Why It Happens**:
- MCP servers initialize at application startup
- Config is read ONCE, not continuously monitored
- Changes have NO effect until restart

**Solution**:
- **ALWAYS fully quit and relaunch** Claude Desktop/Code
- Use Cmd+Q (macOS) or proper quit method
- Wait 5 seconds before relaunching

### Pitfall 3: Testing in Existing Conversation

**Problem**:
- Updated config and restarted
- Tested in conversation that was open before restart
- Still saw old context

**Why It Happens**:
- MCP servers are bound to conversations at creation time
- Existing conversations retain old MCP server instance
- Must start NEW conversation to get new MCP server

**Solution**:
- **ALWAYS test in a NEW conversation** (not existing one)
- After restart, open a fresh conversation tab
- Run verification in that new conversation

### Pitfall 4: Assuming Context Changed Without Verification

**Problem**:
- Updated config, restarted, assumed it worked
- Didn't run `get_current_config` to verify
- Debugged for hours later when agents couldn't access tools

**Why It Happens**:
- Config changes are invisible until tested
- No error message if context is wrong
- Silent failure mode

**Solution**:
- **ALWAYS verify with `get_current_config`** after restart
- Check "Active context:" line explicitly
- Test in both main conversation AND agent tab

### Pitfall 5: Using Wrong Executable Name

**Problem**:
- Repository config uses `serena` + `start-mcp-server`
- Claude Desktop config uses `serena-mcp-server`
- Confusion about which is correct

**Why It Happens**:
- Both forms are valid (different installation methods)
- No clear documentation on which to use
- Easy to mix them up

**Solution**:
- **Use `serena-mcp-server` for Claude Desktop** (uvx method)
- **Use `serena` + `start-mcp-server` for manual setup** (development)
- Both work, just be consistent

### Pitfall 6: Typo in Context Value

**Problem**:
- Typed `--context agents` (plural) instead of `--context agent`
- Typed `--context agent-mode` or other variation
- No error message, just didn't work

**Why It Happens**:
- Serena doesn't validate context values
- Falls back to default (`desktop-app`) if invalid
- Silent failure mode

**Solution**:
- **Exact value**: `"agent"` (singular, lowercase, no suffix)
- Valid values: `desktop-app`, `agent` (maybe `local-app`?)
- Use copy-paste from this guide to avoid typos

### Pitfall 7: Checking Wrong Config File

**Problem**:
- Checked repository config, saw correct context
- Assumed it was working
- Didn't check Claude Desktop config (which had old value)

**Why It Happens**:
- Repository config is more visible (in git)
- Claude Desktop config is in system folders
- Easy to forget there are TWO config files

**Solution**:
- **ALWAYS check the Claude Desktop config** (`~/Library/...`)
- That's the one that actually matters
- Repository config is just documentation

---

## Troubleshooting

### Issue 1: Context Still Shows `desktop-app` After Restart

**Symptoms**:
- Updated both config files
- Restarted Claude Desktop/Code
- `get_current_config` still shows `Active context: desktop-app`

**Diagnosis**:
```bash
# Check Claude Desktop config
cat ~/Library/Application\ Support/Claude/claude_desktop_config.json | grep -A 2 "context"

# If output shows:
# (no output) - context parameter is missing
# "--context", "desktop-app" - still has old value
```

**Solutions**:

1. **Verify config file content**:
   ```bash
   # Full inspection
   cat ~/Library/Application\ Support/Claude/claude_desktop_config.json
   ```

2. **Manually edit the file**:
   ```bash
   vim ~/Library/Application\ Support/Claude/claude_desktop_config.json

   # Add or update the context parameter:
   "args": [
     "--from",
     "git+https://github.com/oraios/serena",
     "serena-mcp-server",
     "--context",
     "agent",
     "--project",
     "/path/to/your-project"
   ]
   ```

3. **Force kill any lingering processes**:
   ```bash
   # Kill all Claude processes
   pkill -f "Claude"

   # Kill all Serena MCP servers
   pkill -f "serena-mcp-server"
   pkill -f "serena"

   # Wait 10 seconds
   sleep 10

   # Relaunch Claude Desktop/Code
   open -a "Claude"
   ```

4. **Verify NO syntax errors in JSON**:
   ```bash
   # Validate JSON syntax
   python3 -m json.tool ~/Library/Application\ Support/Claude/claude_desktop_config.json

   # Should output valid JSON
   # If error: Fix the JSON syntax error shown
   ```

### Issue 2: Serena Tools Not Available in Agent Tab

**Symptoms**:
- Main conversation shows `Active context: agent`
- Agent tab reports "MCP tools not available"
- `context: agent` is in config files

**Diagnosis**:

This might be expected behavior if:
- Testing too soon after restart (MCP server still initializing)
- Agent tab was created before restart (must create NEW tab)
- Agent is using a different project context

**Solutions**:

1. **Wait for initialization**:
   ```bash
   # After restarting Claude, wait 30 seconds before testing
   # MCP servers need time to start and index project
   ```

2. **Create a BRAND NEW agent tab**:
   - Don't reuse tabs that existed before restart
   - Click "New Chat" or invoke agent in fresh tab
   - Verify it's a new conversation (no history)

3. **Verify project is activated**:
   ```bash
   # In agent tab, first run:
   mcp__serena__activate_project("your-project")

   # Then retry other Serena tools
   ```

4. **Check if this is still an architectural limitation**:
   - The `--context agent` parameter was added to solve agent tab access
   - If it still doesn't work, this might be a Serena limitation
   - Document as finding and update ADR-0040

### Issue 3: Multiple Serena Instances Running

**Symptoms**:
- Slow Serena responses
- Inconsistent behavior (sometimes works, sometimes doesn't)
- High CPU usage from multiple `serena-mcp-server` processes

**Diagnosis**:
```bash
# Check for multiple Serena processes
ps aux | grep serena

# Expected: 1-2 processes
# Problem: 3+ processes
```

**Solutions**:

1. **Kill all Serena processes**:
   ```bash
   pkill -f "serena-mcp-server"
   pkill -f "serena"

   # Verify killed
   ps aux | grep serena
   # Should show: (no processes) or (grep process only)
   ```

2. **Restart Claude Desktop/Code cleanly**:
   ```bash
   # Quit Claude
   # Wait 10 seconds
   # Relaunch Claude
   ```

3. **Check for duplicate MCP server configs**:
   ```bash
   cat ~/Library/Application\ Support/Claude/claude_desktop_config.json

   # Look for duplicate "serena" entries in mcpServers
   # Remove duplicates if found
   ```

### Issue 4: Context Parameter Ignored

**Symptoms**:
- Config file clearly shows `--context agent`
- `get_current_config` shows `Active context: desktop-app`
- No explanation for mismatch

**Diagnosis**:

Possible causes:
- Serena version doesn't support `--context` parameter
- Wrong parameter syntax (missing comma, wrong position)
- Serena is reading a DIFFERENT config file

**Solutions**:

1. **Check Serena version**:
   ```bash
   mcp__serena__get_current_config

   # Look for: "Serena version: 0.1.4-437bad3c-dirty"
   # Ensure version is 0.1.4 or later (when --context was added)
   ```

2. **Verify parameter syntax**:
   ```json
   "args": [
     "--from",
     "git+https://github.com/oraios/serena",
     "serena-mcp-server",
     "--context",      // ← Must be separate item
     "agent",          // ← Must be separate item (not "--context agent")
     "--project",
     "/path/to/project"
   ]
   ```

3. **Check Serena is reading correct config**:
   ```bash
   # Look for Serena logs (if web dashboard enabled)
   # Check which config file Serena reports using
   # Compare to the file you edited
   ```

4. **Try explicit full path to uvx**:
   ```json
   {
     "mcpServers": {
       "serena": {
         "command": "/Users/broadcaster_three/.local/bin/uvx",
         "args": ["--from", "git+https://github.com/oraios/serena", "serena-mcp-server", "--context", "agent", "--project", "/path/to/your-project"]
       }
     }
   }
   ```

### Issue 5: Config File Reverted After Restart

**Symptoms**:
- Manually edited config file
- Restarted application
- Config file reverted to old values

**Diagnosis**:

Possible causes:
- Claude Desktop has backup/sync mechanism
- File permissions issue (read-only)
- Another process overwrote the file

**Solutions**:

1. **Check file permissions**:
   ```bash
   ls -la ~/Library/Application\ Support/Claude/claude_desktop_config.json

   # Should show: -rw-r--r-- (writable by user)
   # If not: chmod 644 ~/Library/Application\ Support/Claude/claude_desktop_config.json
   ```

2. **Make backup before editing**:
   ```bash
   cp ~/Library/Application\ Support/Claude/claude_desktop_config.json ~/Library/Application\ Support/Claude/claude_desktop_config.json.backup-$(date +%Y%m%d-%H%M%S)
   ```

3. **Edit while Claude is CLOSED**:
   ```bash
   # 1. Quit Claude Desktop/Code completely
   # 2. Edit the config file
   # 3. Save and verify changes
   # 4. Relaunch Claude
   ```

### Issue 6: JSON Syntax Error in Config File

**Symptoms**:
- Serena doesn't start after config change
- No MCP tools available at all
- Error in Claude Desktop logs (if accessible)

**Diagnosis**:
```bash
# Validate JSON syntax
python3 -m json.tool ~/Library/Application\ Support/Claude/claude_desktop_config.json

# If syntax error, will show line/column of problem
```

**Common JSON errors**:
- Missing comma after an item
- Extra comma after last item
- Missing quotes around strings
- Unescaped backslashes in paths

**Solutions**:

1. **Restore from backup**:
   ```bash
   cp ~/Library/Application\ Support/Claude/claude_desktop_config.json.backup ~/Library/Application\ Support/Claude/claude_desktop_config.json
   ```

2. **Fix specific error**:
   ```json
   // WRONG:
   "args": [
     "--context"
     "agent"    // ← Missing comma
   ]

   // RIGHT:
   "args": [
     "--context",
     "agent"
   ]
   ```

3. **Use proper JSON formatter**:
   ```bash
   # Format and save
   python3 -m json.tool ~/Library/Application\ Support/Claude/claude_desktop_config.json > /tmp/formatted.json
   mv /tmp/formatted.json ~/Library/Application\ Support/Claude/claude_desktop_config.json
   ```

---

## History & Learnings

### Attempt History

**Total Attempts Before This Doc**: 7 failed attempts

**Why Previous Attempts Failed**:
1. Only updated repository config, not Claude Desktop config
2. Updated config but didn't restart application
3. Restarted but tested in existing conversation
4. Didn't verify context with `get_current_config`
5. Assumed context changed without confirmation
6. Typo in context value (`agents` vs `agent`)
7. Checked wrong config file for verification

### Key Learnings

#### Learning 1: Two Config Files, Only One Matters

- Repository config (`.serena/config/mcp-config.json`): Template/documentation
- Claude Desktop config (`~/Library/.../claude_desktop_config.json`): Actual config
- **Only the Claude Desktop config affects runtime behavior**

#### Learning 2: Restart Is Non-Negotiable

- MCP servers initialize at application startup
- Configuration is read ONCE at startup
- Mid-conversation changes have ZERO effect
- Must fully quit and relaunch (not just close windows)

#### Learning 3: Verification Is Mandatory

- Changes are invisible until verified
- No error message if context is wrong
- Must run `get_current_config` to confirm
- Must test in BOTH main conversation AND agent tab

#### Learning 4: Context Is Critical for Agent Access

- `desktop-app` context: Main conversation only
- `agent` context: Main conversation AND agent tabs
- Without `agent` context, autonomous agents can't use Serena
- This unlocks semantic navigation for agent workflows

#### Learning 5: Silent Failures Are Common

- Invalid context values fall back to `desktop-app` (no error)
- JSON syntax errors prevent MCP server startup (no clear message)
- Multiple config files cause confusion (which one matters?)
- Must verify explicitly, not assume

### Related Issues & Tasks

**THEMATIC-0107** (2025-11-18 to 2025-11-19):
- Initial Serena Claude Code setup
- Discovered agent tab limitation (with `desktop-app` context)
- Validated main conversation access
- Created comprehensive documentation

**Commit 437bad3** (2025-11-19):
- Added `--context agent` to enable agent tab access
- Updated both config files
- Documented restart requirement
- First attempt to solve agent access issue

**ADR-0040**:
- Architectural decision for Serena integration
- Documents context parameter importance
- References this guide for context configuration

### Future Improvements

**Potential Enhancements**:
1. Create CLI tool to verify/update context automatically
2. Add pre-flight check script before committing config changes
3. Document Serena version that introduced `--context` parameter
4. Create Makefile target for context switching
5. Add health check script to verify MCP server status

**Open Questions**:
1. What other context values exist? (`local-app`? others?)
2. Does context affect performance or just tool availability?
3. Can context be changed dynamically via tool call?
4. Is there a way to verify context WITHOUT restarting?

---

## Appendix: Full Config Examples

### Example 1: Repository Config (Git)

**File**: `.serena/config/mcp-config.json`

```json
{
  "mcpServers": {
    "serena": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/oraios/serena",
        "serena",
        "start-mcp-server",
        "--context",
        "agent",
        "--project",
        "/path/to/your-project"
      ]
    }
  }
}
```

### Example 2: Claude Desktop Config (User)

**File**: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "preferences": {
    "quickEntryDictationShortcut": "capslock"
  },
  "mcpServers": {
    "serena": {
      "command": "/Users/broadcaster_three/.local/bin/uvx",
      "args": [
        "--from",
        "git+https://github.com/oraios/serena",
        "serena-mcp-server",
        "--context",
        "agent",
        "--project",
        "/path/to/your-project"
      ]
    }
  }
}
```

### Example 3: Multiple Projects

**File**: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "serena-thematic": {
      "command": "/Users/broadcaster_three/.local/bin/uvx",
      "args": [
        "--from",
        "git+https://github.com/oraios/serena",
        "serena-mcp-server",
        "--context",
        "agent",
        "--project",
        "/path/to/your-project"
      ]
    },
    "serena-other-project": {
      "command": "/Users/broadcaster_three/.local/bin/uvx",
      "args": [
        "--from",
        "git+https://github.com/oraios/serena",
        "serena-mcp-server",
        "--context",
        "agent",
        "--project",
        "/Users/broadcaster_three/Github/other-project"
      ]
    }
  }
}
```

---

## Quick Commands Reference

```bash
# Check repository config
cat .serena/config/mcp-config.json | grep -A 2 "context"

# Check Claude Desktop config (THE ONE THAT MATTERS)
cat ~/Library/Application\ Support/Claude/claude_desktop_config.json | grep -A 2 "context"

# Backup Claude Desktop config
cp ~/Library/Application\ Support/Claude/claude_desktop_config.json ~/Library/Application\ Support/Claude/claude_desktop_config.json.backup-$(date +%Y%m%d-%H%M%S)

# Validate JSON syntax
python3 -m json.tool ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Kill all Serena processes
pkill -f "serena"

# Check running Serena processes
ps aux | grep serena

# Edit Claude Desktop config
vim ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Verify context in conversation
mcp__serena__get_current_config
```

---

**Last Updated**: 2025-11-19
**Maintainer**: Coordinator (Tycho)
**Status**: ✅ COMPLETE & VALIDATED
**Version**: 1.0
