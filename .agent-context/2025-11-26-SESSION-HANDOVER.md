# Session Handover: agentive-starter-kit

**Date**: 2025-11-26
**From**: planner @ thematic-cuts (coordination session)
**To**: planner @ agentive-starter-kit

---

## Project Overview

**agentive-starter-kit** is a template repository for bootstrapping new projects with AI agent coordination infrastructure. It was extracted from the thematic-cuts project.

**GitHub**: https://github.com/movito/agentive-starter-kit

---

## Recent Session Summary (2025-11-26)

### What Was Accomplished

1. **Onboarding Separation** (commit `c8b69c7`)
   - Created dedicated `onboarding.md` agent (341 lines)
   - Removed onboarding from `planner.md` (now 322 lines)
   - `agents/onboarding` launches onboarding agent, not planner
   - Separation of concerns: onboarding = setup, planner = coordination

2. **Serena MCP Integration** (commit `3f0057b`)
   - Created `.serena/setup-serena.sh` - automated installation script
   - Updated `agents/launch` to check if Serena is configured
   - Added Serena setup to onboarding flow (Phase 2)
   - Updated SETUP.md with installation instructions

3. **ADR-0001 Added**
   - Documents system prompt size considerations
   - Guidelines: 150-400 lines per agent depending on type
   - Recorded overload_error incident and mitigations

### Key Files Changed

| File | Change |
|------|--------|
| `.claude/agents/onboarding.md` | NEW - Dedicated setup agent |
| `.claude/agents/planner.md` | Reduced from 495 to 322 lines |
| `.serena/setup-serena.sh` | NEW - Serena installation script |
| `agents/launch` | Added `is_serena_configured()` check |
| `agents/onboarding` | Now launches onboarding agent |
| `SETUP.md` | Added Serena installation instructions |
| `docs/decisions/adr/ADR-0001-*` | NEW - System prompt size ADR |

---

## Current State

### Repository Structure
```
agentive-starter-kit/
├── .claude/agents/        # Agent definitions (10 agents)
│   ├── onboarding.md      # First-run setup (NEW)
│   ├── planner.md             # Coordinator (slimmed down)
│   ├── feature-developer.md
│   └── ...
├── .serena/
│   ├── setup-serena.sh    # Installation script (NEW)
│   └── project.yml.template
├── agents/
│   ├── launch             # Agent launcher (updated)
│   └── onboarding         # First-run script (updated)
├── delegation/tasks/      # Task management folders
├── docs/decisions/adr/    # ADRs (1 so far)
└── ...
```

### User Flow
1. Clone repo → `./agents/onboarding` (first-time setup)
2. Onboarding agent guides through 6 phases including Serena
3. After setup → `./agents/launch` for daily use
4. Agents auto-activate Serena if configured

---

## Pending / Future Work

### Immediate Opportunities
- [ ] Test the full onboarding flow end-to-end
- [ ] Verify Serena setup script works on fresh system
- [ ] Consider adding more starter ADRs (TDD approach, etc.)

### Known Issues
- None currently blocking

### Ideas Discussed But Not Implemented
- Externalize verbose agent content to reduce system prompt size (decided against for now - ADR-0001)
- Video walkthrough of onboarding

---

## Related Project: agentive-ixd-1

A sibling project using this starter kit was also set up:
- **GitHub**: https://github.com/movito/agentive-ixd-1
- **Status**: Pushed with Serena setup included
- Has custom agents: `a11y-reviewer`, `css-expert`, `svelte-developer`

---

## How to Continue

1. **Activate Serena** (if not already):
   ```bash
   mcp__serena__activate_project("agentive-starter-kit")
   ```

2. **Check current status**:
   ```bash
   git log --oneline -5
   git status
   ```

3. **Review recent changes**:
   - Read ADR-0001 for context on agent sizing decisions
   - Check `.claude/agents/onboarding.md` for the new onboarding flow

4. **If user has tasks**:
   - Use standard coordination workflow
   - Create tasks in `delegation/tasks/`
   - Run evaluations if needed

---

## Session Notes

- The thematic-cuts session ran into API overload with large planner.md (~500 lines)
- Solution: Separate onboarding into dedicated agent
- Both repos now have Serena setup scripts
- User prefers explicit steps (onboarding as separate step, not baked into planner)

---

*This handover was created by planner @ thematic-cuts to provide context continuity.*
