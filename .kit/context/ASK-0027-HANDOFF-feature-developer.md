# Handoff: ASK-0027 - Project Reconfigure Command

**From**: Planner
**To**: feature-developer
**Date**: 2025-12-04

## Implementation Guidance

### What You're Building

A new `reconfigure` subcommand for `./scripts/project` that updates agent files with the correct project name after upstream merges.

### Why This Is Needed

When users fetch upstream updates, the Serena activation placeholder `"your-project"` arrives in agent files but isn't populated (onboarding already ran). This command fixes that.

### Starting Point

The `scripts/project` file is a bash script with subcommands handled via a `case` statement. Add your new case block after the existing subcommands.

**Look at these for reference:**
- `scripts/project` - the main CLI script, ~300 lines
- `.serena/project.yml` - where project name is stored (line with `name:`)
- `.claude/agents/*.md` - files that need updating

### Implementation Steps

1. **Add the reconfigure case block** to `scripts/project`:
   - After the last existing `;;` and before `*)` default case
   - See task file for complete bash code

2. **Test locally**:
   ```bash
   # First, temporarily replace a project name with placeholder
   sed -i '' 's/agentive-starter-kit/your-project/' .claude/agents/planner.md

   # Run your command
   ./scripts/project reconfigure

   # Verify it was restored
   grep activate_project .claude/agents/planner.md
   ```

3. **Update README.md**:
   - Find "Pulling Updates from the Starter Kit" section
   - Add note about running `./scripts/project reconfigure` after merge

4. **Add help text**:
   - Update the `help)` case in `scripts/project` to include reconfigure

### Key Technical Details

**Extract project name** (handles quotes and whitespace):
```bash
PROJECT_NAME=$(grep "^name:" .serena/project.yml | head -1 | sed 's/name:[[:space:]]*//' | tr -d '"' | tr -d "'")
```

**macOS vs Linux sed**:
- macOS: `sed -i '' "s/old/new/" file`
- Linux: `sed -i "s/old/new/" file`
- The script already handles this elsewhere - check existing patterns

**Only replace placeholder**:
- Match: `activate_project("your-project")`
- Don't match: `activate_project("other-name")` (user's intentional choice)

### Edge Cases to Handle

1. Missing `.serena/project.yml` → error with helpful message
2. Empty project name → error
3. No files need updating → success message "already configured"
4. Re-running → idempotent (all files "already configured")

### Files You'll Modify

1. `scripts/project` - add reconfigure subcommand
2. `README.md` - add note in "Pulling Updates" section

### Evaluation History

- **Round 1**: NEEDS_REVISION - asked for error handling details, file locations
- **Round 2**: NEEDS_REVISION - asked about multiple `name:` entries, testing framework
- **Addressed**: Added `head -1` for first match, clarified standalone task, specified bash testing

Evaluator concerns were minor - the implementation is straightforward bash scripting.

## Success Criteria

- [ ] `./scripts/project reconfigure` works
- [ ] Reads project name from `.serena/project.yml`
- [ ] Updates all agent files with placeholder
- [ ] Clear output showing what was updated
- [ ] Error handling for missing config
- [ ] README updated
- [ ] Idempotent (safe to run multiple times)

## Resources

- Task file: `.kit/tasks/2-todo/ASK-0027-project-reconfigure-command.md`
- Evaluation logs: `.adversarial/logs/ASK-0027-project-reconfigure-command-PLAN-EVALUATION.md`
- Original fix: commit fb2c718
