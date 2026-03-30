# Session Handover: agentive-starter-kit

**Date**: 2025-11-27
**From**: planner (rem) @ agentive-starter-kit
**To**: Next agent

---

## Session Summary

Major improvements to onboarding UX and TDD guidance. Focus on making the starter kit accessible to users new to Git, GitHub, and agentive development.

---

## Changes Made (Chronological)

### 1. Onboarding Flow Improvements

**Prerequisites & Preflight** (commits `various`)
- Added prominent Prerequisites section to README.md (tiered: Must Have / Should Have / Nice to Have)
- Created `./agents/preflight` script to validate requirements before onboarding
- Fixed `set -e` bug in preflight (arithmetic operations return 1 when value is 0)
- Updated `./agents/onboarding` to run preflight before launching agent

**Quick Start Clarification**
- Explained "don't create folder first" for `git clone`
- Added link to "Intro to Git" for beginners

**Serena Setup**
- Made Serena optional (not everyone needs semantic code navigation)
- Added warning about browser "can't connect" popup (normal behavior)
- Updated setup script to explain restart requirement

**Documentation Improvements**
- Added detailed Linear Integration section (more than just API key)
- Added explanation of what pre-commit hooks are + link to learn more
- Changed jargon-y agent descriptions to plain language
- Added "(you can always create a new agent later!)" for loss aversion

### 2. Agent Renaming: rem → planner

**Rationale**: "rem" was opaque; "planner" describes the role clearly.

**Files Changed**:
- `.claude/agents/rem.md` → `.claude/agents/planner.md`
- Icon changed: 👓 → 📋
- All references updated across codebase

### 3. Model Recommendations

Added default models to all agents with guidance comment:

| Agent | Model | Rationale |
|-------|-------|-----------|
| planner | Opus 4.5 | Complex planning, coordination |
| feature-developer | Opus 4.5 | Code generation |
| security-reviewer | Opus 4.5 | Security analysis |
| test-runner | Sonnet 4.5 | Testing tasks |
| document-reviewer | Sonnet 4.5 | Documentation |
| agent-creator | Sonnet 4.5 | Agent creation |
| tycho | Sonnet 4.5 | Day-to-day tasks |
| powertest-runner | Sonnet 4.5 | Comprehensive testing |
| onboarding | Sonnet 4.5 | Setup guidance |
| ci-checker | Haiku 4.5 | Fast CI verification |

**Note**: Opus 4.5 uses ~50% fewer tokens, often making total cost similar to Sonnet.

### 4. Removed coordinator Agent

**Rationale**: Redundant with planner. One coordinator is enough.

### 5. Launch Script Documentation

Instead of making order dynamic, documented the hardcoded arrays:
- Clear comments in `.kit/launchers/launch` explaining how to reorder
- Added tip: "To reorder or customize agents, edit .kit/launchers/launch"

### 6. Fixed Empty Slot Bug (commit `49fb4f1`)

**Issue**: Empty slot #10 in agent menu
**Cause**: `TASK-STARTER-TEMPLATE.md` not excluded from agent file detection
**Fix**: Added to exclusion list in `.kit/launchers/launch`

### 7. GitHub Setup Phase (Phase 7)

Added new onboarding phase to help users create their own GitHub repo:
- Checks if `gh` CLI is authenticated
- Creates private repo with `gh repo create`
- Guides manual setup if gh not available

### 8. Upstream Pull Documentation

Added "Pulling Updates from Starter Kit" section to README:
```bash
git remote add upstream https://github.com/movito/agentive-starter-kit.git
git fetch upstream
git merge upstream/main -m "Merge upstream updates"
```

### 9. TDD Seed Task (commit `327ce17`)

**NEW**: Onboarding now creates a first task to guide planner toward TDD practices.

**Files Added**:
- `.kit/tasks/9-reference/templates/SETUP-0001-testing-infrastructure.md`

**Onboarding Updated**:
- Phase 6 creates `[PREFIX]-0001-testing-infrastructure.md` in `2-todo/`
- Phase 8 next steps mention completing TDD setup first

**Flow**:
1. User completes onboarding → seed task created
2. User launches planner → planner sees task in `2-todo/`
3. Planner assigns to **feature-developer** (implementation task)
4. All subsequent work follows TDD practices

### 9b. Seed Task v2.0 Improvements (commit `0e89d7d`)

Based on feedback from agentive-lotion-2's planner:

**Fixed Issues**:
- ❌ Wrong agent (planner) → ✅ Correct agent (feature-developer)
- ❌ Missing pyproject.toml → ✅ Full template included
- ❌ Generic content → ✅ "Existing Assets" section references starter kit files
- ❌ YAML tabs → ✅ Proper spacing
- ❌ No customization guide → ✅ Detailed placeholder table for onboarding agent

**Template v2.0 Key Sections**:
- "Existing Assets to Leverage" - tells devs to adapt, not recreate
- pyproject.toml with pytest, black, ruff config
- Smoke test example
- GitHub Actions CI workflow
- Clear acceptance criteria

---

## Current State

### Repository Structure
```
agentive-starter-kit/
├── .claude/agents/           # 10 agents (coordinator removed)
│   ├── planner.md            # Renamed from rem.md
│   ├── onboarding.md         # First-run setup
│   ├── feature-developer.md
│   ├── test-runner.md
│   ├── powertest-runner.md
│   ├── document-reviewer.md
│   ├── security-reviewer.md
│   ├── ci-checker.md
│   ├── agent-creator.md
│   └── tycho.md
├── agents/
│   ├── launch                # Agent launcher (documented, fixed)
│   ├── onboarding            # First-run script
│   └── preflight             # NEW - Requirement validator
├── .kit/tasks/
│   └── 9-reference/templates/
│       └── SETUP-0001-testing-infrastructure.md  # NEW - TDD seed task
└── docs/decisions/adr/
    └── ADR-0001-*            # System prompt size
```

### Agent Launcher Output
```
1) 📋 planner
2) 🛠️ feature-developer
3) 🧪 test-runner
4) 🧭 tycho
5) 🧪 powertest-runner
6) 📄 document-reviewer
7) 🔒 security-reviewer
8) ✅ ci-checker
9) 🤖 agent-creator
10) ⚡ onboarding
```

---

## Key Commits Today

| Commit | Description |
|--------|-------------|
| `49fb4f1` | fix: Exclude TASK-STARTER-TEMPLATE.md from agent launcher |
| `327ce17` | feat: Add TDD seed task to onboarding flow |
| `8c0b6b6` | docs: Add session handover for 2025-11-27 |
| `0e89d7d` | fix: Improve TDD seed task based on agentive-lotion-2 feedback |

---

## For Next Agent

### If Continuing Starter Kit Work
1. Run `./.kit/launchers/launch` to verify all 10 agents display correctly
2. Test onboarding flow end-to-end with fresh clone
3. Consider adding more ADRs for key decisions

### If User Has New Tasks
1. Use planner for coordination
2. Create tasks in `.kit/tasks/2-todo/`
3. Follow TDD practices (seed task as example)

### Known Working Projects Using This Kit
- **agentive-lotion-2**: Has 5 custom agents (knowledge-graph, interaction-designer, canvas-architect, pdf-processor, onboarding)
- **agentive-ixd-1**: Has custom agents (a11y-reviewer, css-expert, svelte-developer)

---

## Git Commands for Users

**Pull upstream updates**:
```bash
git fetch upstream
git merge upstream/main -m "Merge upstream updates"
```

**Tip**: Use `-m` flag to avoid vim editor for merge commits.

---

*This handover was created by planner @ agentive-starter-kit.*
