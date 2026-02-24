# ASK-0027: Add Project Reconfigure Command

**Status**: Done
**Priority**: High
**Assigned To**: feature-developer
**Estimated Effort**: 2-3 hours
**Created**: 2025-12-04

## Problem Statement

When existing projects fetch upstream updates from agentive-starter-kit, the Serena project activation fix (commit fb2c718) introduces `"your-project"` placeholders in agent files. These placeholders are not populated because:

1. The onboarding agent already ran before the fix existed
2. Onboarding doesn't re-run on upstream merges
3. Agents end up with `"your-project"` which doesn't resolve

Users must manually run sed commands to fix this, which is error-prone and undocumented.

## Solution

Add a `./scripts/project reconfigure` subcommand that re-applies project-specific configuration to agent files after upstream merges.

## Acceptance Criteria

- [ ] **Command exists**: `./scripts/project reconfigure` runs without error
- [ ] **Reads project name**: Extracts name from `.serena/project.yml` (line with `name:`)
- [ ] **Updates agent files**: Replaces `"your-project"` placeholder in all `.claude/agents/*.md` files
- [ ] **Handles re-runs**: Can be run multiple times safely (idempotent)
- [ ] **Handles existing names**: If agents already have a project name (not placeholder), optionally update or skip
- [ ] **Clear output**: Reports what was changed (X files updated, Y already correct)
- [ ] **Documentation updated**: README "Pulling Updates" section mentions running reconfigure
- [ ] **Tests pass**: Existing tests continue to pass, new tests for reconfigure logic

## Technical Requirements

### Implementation Location

Add to `scripts/project` (the existing bash CLI script) as a new subcommand case in the main case statement.

**File**: `scripts/project`
**Function**: Add `reconfigure)` case block around line 200+ (after existing subcommands)

### Logic Flow

```bash
reconfigure)
    # 1. Check .serena/project.yml exists
    if [[ ! -f ".serena/project.yml" ]]; then
        echo "Error: .serena/project.yml not found"
        echo "Run 'agents/onboarding' first to configure your project"
        exit 1
    fi

    # 2. Extract project name from `name:` line (first match, top-level only)
    # Note: grep "^name:" only matches lines starting with "name:" (no indentation)
    # This ensures we get the top-level project name, not nested names
    PROJECT_NAME=$(grep "^name:" .serena/project.yml | head -1 | sed 's/name:[[:space:]]*//' | tr -d '"' | tr -d "'")
    if [[ -z "$PROJECT_NAME" ]]; then
        echo "Error: Could not find 'name:' in .serena/project.yml"
        exit 1
    fi

    # 3. For each .claude/agents/*.md file:
    updated=0
    skipped=0
    for agent_file in .claude/agents/*.md; do
        if grep -q 'activate_project("your-project")' "$agent_file"; then
            sed -i '' "s/activate_project(\"your-project\")/activate_project(\"$PROJECT_NAME\")/" "$agent_file"
            echo "  ✓ $(basename $agent_file) - updated"
            ((updated++))
        else
            echo "  · $(basename $agent_file) - already configured"
            ((skipped++))
        fi
    done

    # 4. Report results
    echo ""
    echo "✅ Reconfigured $updated files ($skipped already correct)"
    ;;
```

### Error Handling

| Condition | Error Message | Exit Code |
|-----------|---------------|-----------|
| `.serena/project.yml` missing | "Error: .serena/project.yml not found. Run 'agents/onboarding' first to configure your project" | 1 |
| `name:` line missing in yml | "Error: Could not find 'name:' in .serena/project.yml. Check your Serena configuration." | 1 |
| `name:` value empty | "Error: Project name is empty in .serena/project.yml" | 1 |
| No agent files exist | "Warning: No agent files found in .claude/agents/" | 0 (success, nothing to do) |

### Edge Cases

1. **No .serena/project.yml**: Error with helpful message about running onboarding first
2. **No project name in yml**: Error with message to check config
3. **Empty project name**: Error with message to check config
4. **No agent files need updating**: Report "All agent files already configured" (success)
5. **Files with different existing name**: Only replaces `"your-project"` placeholder, leaves other names alone
6. **Re-running after success**: Idempotent - reports all files "already configured"

### Handling Existing Project Names

The command ONLY replaces the literal `"your-project"` placeholder. If an agent file has:
- `activate_project("your-project")` → replaced with actual project name
- `activate_project("some-other-name")` → left unchanged (already configured)
- `activate_project("my-project")` → left unchanged (user's choice)

This ensures we don't accidentally overwrite intentional customizations.

### Example Output

```bash
$ ./scripts/project reconfigure

🔧 Reconfiguring project: my-awesome-app

Checking agent files...
  ✓ code-reviewer.md - updated
  ✓ feature-developer.md - updated
  ✓ planner.md - updated
  · test-runner.md - already configured
  ✓ powertest-runner.md - updated
  ✓ tycho.md - updated

✅ Reconfigured 5 files (1 already correct)
```

## Documentation Updates

### README.md - "Pulling Updates" Section

Add after the merge command:

```markdown
**After merging upstream changes**, run reconfigure to update agent files with your project name:

```bash
./scripts/project reconfigure
```

This ensures Serena activation works correctly with your project.
```

## Out of Scope

- Reconfiguring other project-specific settings (just Serena project name for now)
- GUI or interactive mode
- Automatic detection of upstream merge (manual trigger is fine)
- Dry-run option (command is safe and idempotent; showing what would change adds complexity without benefit)
- Force flag to overwrite existing non-placeholder names (intentional customizations should be preserved)

## Testing Strategy

### Unit Tests

1. Test project name extraction from various .serena/project.yml formats
2. Test sed replacement logic
3. Test idempotency (running twice produces same result)

### Integration Tests

1. Create temp directory with mock agent files
2. Run reconfigure
3. Verify files were updated correctly

## Dependencies

- Existing `scripts/project` CLI infrastructure
- `.serena/project.yml` must exist (created by onboarding)
- **Standalone task**: No dependencies on other tasks

## Testing Framework

- **Shell testing**: Use bash assertions and temp directories for integration tests
- **Manual verification**: Run against actual agent files to verify behavior
- No external test framework needed - this is a simple bash script addition

## References

- Original fix: commit fb2c718
- Reported in: thematic-2 project feedback
- Related: KIT-ADR-0012 (task status), though this is infrastructure not task-related
