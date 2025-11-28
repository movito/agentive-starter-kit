# Serena Context Change: Quick Reference Checklist

**Purpose**: Fast reference for changing Serena MCP context from `desktop-app` to `agent`
**Full Guide**: See `CONTEXT-CONFIGURATION-GUIDE.md` for comprehensive troubleshooting

---

## ⚡ 5-Minute Context Change

### Step 1: Update Repository Config (Optional)
```bash
# Edit .serena/config/mcp-config.json
vim .serena/config/mcp-config.json

# Ensure this exists in args array:
"--context",
"agent",
```

### Step 2: Update Claude Desktop Config (REQUIRED)
```bash
# Edit the actual config file
vim ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Ensure this exists in args array:
"--context",
"agent",
```

### Step 3: Restart Claude Desktop/Code (CRITICAL)
```bash
# 1. Quit application completely (Cmd+Q on macOS)
# 2. Wait 5 seconds
# 3. Relaunch Claude Desktop/Code
```

### Step 4: Verify Context Changed
```bash
# In a NEW conversation (not existing one):
mcp__serena__get_current_config

# Look for this line:
# Active context: agent

# If it still says "desktop-app", see troubleshooting below
```

---

## ✅ Verification Commands

```bash
# Check repository config
cat .serena/config/mcp-config.json | grep -A 2 "context"

# Check Claude Desktop config (THE ONE THAT MATTERS)
cat ~/Library/Application\ Support/Claude/claude_desktop_config.json | grep -A 2 "context"

# Validate JSON syntax
python3 -m json.tool ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Check for orphaned MCP server processes (CRITICAL FOR TROUBLESHOOTING)
ps aux | grep serena-mcp-server | grep -v grep

# If any processes shown above, kill them before restarting:
# kill -9 <PID1> <PID2> ...
```

---

## ❌ Common Mistakes (AVOID THESE)

1. ❌ **Only updated repository config** → Must update Claude Desktop config
2. ❌ **Didn't restart application** → Context won't change without restart
3. ❌ **Tested in existing conversation** → Must test in NEW conversation
4. ❌ **Typo in context value** → Must be exactly `"agent"` (singular, lowercase)
5. ❌ **Assumed it worked** → Must verify with `get_current_config`
6. ❌ **Missing comma in JSON** → Check JSON syntax with validation tool
7. ❌ **Closed windows but didn't quit** → Must fully quit application (Cmd+Q)
8. ❌ **Didn't check for orphaned processes** → MCP servers can survive restarts; check and kill them manually

---

## 🔧 Quick Troubleshooting

### Problem: Still shows `desktop-app` after restart

**Most likely cause**: Claude Desktop config wasn't updated

```bash
# Check the file that actually matters
cat ~/Library/Application\ Support/Claude/claude_desktop_config.json | grep -A 2 "context"

# If it doesn't show "agent", edit it:
vim ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Then restart AGAIN
```

### Problem: Changes keep reverting

**Most likely cause**: JSON syntax error

```bash
# Validate JSON
python3 -m json.tool ~/Library/Application\ Support/Claude/claude_desktop_config.json

# If error shown, fix the syntax error
# Then restart AGAIN
```

### Problem: Multiple Serena processes running

**Root Cause**: MCP server processes don't always terminate when Claude Desktop quits. These orphaned processes continue running with the old context configuration, preventing the new context from taking effect.

**Symptoms**:
- Restarted Claude Desktop 5+ times but context still shows `desktop-app`
- Configuration files are correct but changes don't apply
- `get_current_config` shows old context despite config updates

**Solution**: Kill orphaned processes manually

```bash
# Step 1: Check for orphaned Serena MCP server processes
ps aux | grep serena-mcp-server | grep -v grep

# Example output (these are ORPHANED processes):
# broadcaster_three 97778  ... /bin/python .../serena-mcp-server
# broadcaster_three 2269   ... /bin/python .../serena-mcp-server

# Step 2: Identify the PIDs (first column in output above)
# In this example: 97778 and 2269

# Step 3: Force kill ALL Serena processes (replace PIDs with actual values)
kill -9 97778 2269

# Or kill parent uvx processes too:
kill -9 97778 97771 2269 2260

# Step 4: Verify all processes are terminated
ps aux | grep serena-mcp-server | grep -v grep
# Should return no results

# Step 5: Wait a few seconds
sleep 5

# Step 6: Relaunch Claude Desktop/Code
# New MCP server instance will start with updated config
```

**Quick Kill Command** (kills all Serena processes):
```bash
# Nuclear option - kills everything Serena-related
pkill -9 -f "serena-mcp-server"

# Verify clean state
ps aux | grep serena | grep -v grep
```

**Prevention**:
- Always use Cmd+Q to fully quit Claude Desktop (not just close windows)
- If context changes aren't applying after restart, check for orphaned processes FIRST
- Consider this the default troubleshooting step for "config correct but not working"

---

## 📋 Pre-Restart Checklist

Before restarting, verify these are all ✅:

- [ ] Claude Desktop config has `"--context", "agent"`
- [ ] Repository config has `"--context", "agent"` (optional but recommended)
- [ ] JSON syntax is valid (run validation command above)
- [ ] Both files have matching context values
- [ ] **Checked for and killed orphaned MCP server processes** (`ps aux | grep serena-mcp-server`)
- [ ] You're ready to quit ALL Claude windows (Cmd+Q)
- [ ] You know you need to test in a NEW conversation

---

## 📖 Full Documentation

For comprehensive troubleshooting, see:
- **CONTEXT-CONFIGURATION-GUIDE.md** - 500+ lines of detailed guidance
- **ADR-0040** - Context configuration section

---

## 🎯 Success Criteria

You've successfully changed context when:
1. ✅ `get_current_config` shows `Active context: agent`
2. ✅ Verified in a NEW conversation (not existing one)
3. ✅ Both config files show `"--context", "agent"`
4. ✅ Application was fully restarted (quit and relaunched)

---

**Last Updated**: 2025-11-19 (13:48 PM - Added orphaned process troubleshooting)
**Attempts Before Success**: 8 failed attempts (discovered orphaned process issue on attempt #8)
**Status**: ✅ Validated procedure with comprehensive orphaned process handling
