# Operational Rules for All Agents

**Version**: 2.0
**Last Updated**: 2025-11-12
**Applies To**: ALL agents in this project

---

## ⚠️ CRITICAL: Task Tool Permission Requirements

### The Problem (RESOLVED)

**Task tool subagents require explicit tool permissions** in `.claude/settings.local.json` to perform filesystem operations.

### Root Cause (Previously Misunderstood)

**Previous misdiagnosis**: We believed Task tool agents ran in ephemeral sandboxes that couldn't persist changes.

**Actual cause**: Our `.claude/settings.local.json` was missing `Write` and `Edit` permissions. Subagents invoked via Task tool inherit project permissions, which only included `Read` and `Bash` tools.

### Resolution (2025-11-12)

Added the following permissions to `.claude/settings.local.json`:
- `Write`
- `Edit`
- `Glob`
- `Grep`
- `TodoWrite`

Subagents can now perform filesystem operations when launched via Task tool.

---

## ✅ Task Tool Usage Guidelines

### Task Tool CAN Now Be Used For:

With proper permissions configured in `.claude/settings.local.json`, subagents launched via Task tool can:

- **Research and codebase exploration** (Explore agent)
- **Analysis and investigation tasks**
- **Answering questions about code**
- **Searching for patterns or files**
- **Reading documentation**
- **Gathering information**
- **Creating files** (with Write permission)
- **Editing files** (with Edit permission)
- **Git commits** (with Bash permission)
- **Installing dependencies** (with Bash permission)
- **Running tests** (with Bash permission)
- **Building projects** (with Bash permission)

### Best Practices

**When to use Task tool for implementation:**
- ✅ Complex multi-step tasks that benefit from specialized agent context
- ✅ Tasks where delegation improves clarity and separation of concerns
- ✅ When you want implementation work tracked in a separate agent context

**When to use direct tools:**
- ✅ Simple, single-file edits in main conversation
- ✅ Quick fixes that don't need specialized agent overhead
- ✅ When you're already in the appropriate agent context

### User Instruction Clarification

The `.claude/CLAUDE.md` instruction **"Always launch agents in new tabs"** can mean:
- ✅ **UI tabs in Claude Desktop** (multiple conversations) - preferred for user visibility
- ✅ **Task tool invocations** (now functional with proper permissions) - acceptable for complex delegated work

---

## Verification

After completing work that should modify files (whether via Task tool or direct):
1. ✅ Check `git status` shows actual changes
2. ✅ Verify files exist at expected paths
3. ✅ Confirm commits appear in `git log`

If any verification fails, check:
- Are the required tools in `.claude/settings.local.json` permissions?
- Did the operation complete without errors?

---

## Permission Configuration Reference

**Required tools in `.claude/settings.local.json` for full subagent functionality:**

```json
{
  "permissions": {
    "allow": [
      "Write",
      "Edit",
      "Glob",
      "Grep",
      "Read",
      "TodoWrite",
      "Bash(...)"
    ]
  }
}
```

---

## Questions?

If subagents report creating files but nothing appears on disk, check `.claude/settings.local.json` permissions first.
