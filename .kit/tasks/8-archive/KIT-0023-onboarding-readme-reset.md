# KIT-0023: Onboarding README Reset

**Status**: Done
**Priority**: High
**Type**: Enhancement
**Completed**: 2025-12-08

---

## Summary

When users create projects from agentive-starter-kit, they inherit the starter kit's README. The onboarding agent should reset the README to be project-specific.

## Problem

Current behavior:
- User clones `agentive-starter-kit` as `my-cool-app`
- Runs onboarding, configures project
- README.md still contains 450+ lines about the Agentive Starter Kit
- User's project has misleading documentation

## Solution

Add a new phase to the onboarding agent (after Phase 6, before GitHub setup) that:

### Step 1: Clear the README
Replace the starter kit README with a minimal placeholder.

### Step 2: Ask about the project
Prompt: "What is [project-name] about? (1-2 sentences)"

### Step 3: Generate minimal README
```markdown
# [project-name]

[user's description]

---

Built with [Agentive Starter Kit](https://github.com/movito/agentive-starter-kit)
```

### Step 4: Create backlog task
Create `delegation/tasks/1-backlog/[PREFIX]-0001-write-project-readme.md`:
```markdown
# [PREFIX]-0001: Write Project README

**Status**: Backlog
**Priority**: Medium
**Type**: Documentation

---

## Summary

Write comprehensive documentation for [project-name].

## Suggested Sections

- [ ] Project overview and purpose
- [ ] Features list
- [ ] Installation instructions
- [ ] Usage examples
- [ ] Configuration options
- [ ] Contributing guidelines
- [ ] License

## Notes

This task was auto-generated during onboarding. Update this file with project-specific details when ready to implement.
```

## Acceptance Criteria

- [x] Onboarding clears the starter kit README content
- [x] Onboarding asks user for 1-2 sentence project description
- [x] New README contains project name and description
- [x] Backlog task created for comprehensive README
- [x] Works correctly when user skips description (uses generic placeholder)

## Implementation Notes

- Add as "Phase 6.5" (after configuration, before GitHub setup)
- Use the project name and task prefix from earlier phases
- Handle case where user skips description: "A project built with Agentive Starter Kit"

## Files to Modify

- `.claude/agents/onboarding.md` - Add new README phase

---

**Created**: 2025-12-08
**Context**: User feedback - derived projects retain starter kit README
