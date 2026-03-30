# Agent System and Coordination Guide

**Created**: 2025-10-16
**Purpose**: Comprehensive guide to the agent coordination system used in this project
**Audience**: Coordinators setting up new projects or handing off context
**Status**: Production-ready methodology validated through thematic-cuts and adversarial-workflow

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Agent System Architecture](#agent-system-architecture)
3. [Directory Structure](#directory-structure)
4. [Agent Roles and Responsibilities](#agent-roles-and-responsibilities)
5. [Coordination Patterns](#coordination-patterns)
6. [Context Management](#context-management)
7. [Task Management](#task-management)
8. [Handoff Protocols](#handoff-protocols)
9. [Setup for New Projects](#setup-for-new-projects)
10. [Best Practices](#best-practices)
11. [Common Patterns](#common-patterns)
12. [Troubleshooting](#troubleshooting)

---

## Executive Summary

### What Is This System?

A **structured coordination framework** for managing complex software projects using Claude Code's agent system. It provides:

- **Role-based agents** with specific responsibilities (coordinator, feature-developer, test-runner, etc.)
- **Context persistence** across sessions via `.kit/context/` directory
- **Task tracking** with active/completed/analysis organization
- **Handoff protocols** for seamless agent-to-agent transitions
- **Documentation standards** for maintaining project memory

### Why Use It?

**Benefits**:
- 📋 **Clarity**: Always know who's working on what
- 🔄 **Continuity**: Context persists across sessions
- 📊 **Tracking**: Clear audit trail of decisions and progress
- 🤝 **Coordination**: Smooth handoffs between specialized agents
- 📚 **Memory**: Project knowledge doesn't get lost

**Proven Results** (thematic-cuts):
- 85.1% → 94.0% test pass rate improvement
- 87.5% efficiency gain through discovery-first approach
- Zero phantom work incidents with multi-agent coordination
- Successful coordination across 6+ specialized agents

---

## Agent System Architecture

### Core Components

```
.kit/context/                    # Agent coordination directory
├── agent-handoffs.json           # PRIMARY: Current agent status
├── current-state.json            # Project state and metrics
├── session-logs/                 # Historical session records
└── AGENT-SYSTEM-GUIDE.md         # This document

delegation/                        # Task management directory
├── tasks/
│   ├── active/                   # Current work
│   ├── completed/                # Finished tasks
│   ├── analysis/                 # Planning and research
│   └── logs/                     # Execution records
└── handoffs/                     # Agent handoff documents
```

### Information Flow

```
┌─────────────────────────────────────────────────────┐
│ User Request                                        │
└──────────────┬──────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────┐
│ Coordinator Agent                                   │
│ - Reviews request                                   │
│ - Checks agent-handoffs.json for context           │
│ - Creates/updates tasks in .kit/tasks/       │
│ - Assigns to specialized agent                     │
└──────────────┬──────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────┐
│ Specialized Agent (feature-developer, etc.)        │
│ - Reads task specification                         │
│ - Executes work                                     │
│ - Updates agent-handoffs.json with progress        │
│ - Creates handoff document when complete           │
└──────────────┬──────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────┐
│ Coordinator Agent (return)                          │
│ - Reviews completion                                │
│ - Updates project state                             │
│ - Archives completed task                           │
│ - Plans next task                                   │
└─────────────────────────────────────────────────────┘
```

---

## Directory Structure

### Required Directories

#### 1. `.kit/context/` (Agent Coordination)

**Purpose**: Persistent agent state and context

**Required Files**:
```
.kit/context/
├── agent-handoffs.json          # CRITICAL: Agent status tracking
├── current-state.json           # Project metrics and state
└── AGENT-SYSTEM-GUIDE.md        # This guide (optional but recommended)
```

**Optional Files**:
```
.kit/context/
├── session-logs/                # Historical session records
├── PHASE-*-RETURN-NOTES.md      # Phase transition notes
└── COORDINATOR-HANDOFF-*.md     # Major handoff documents
```

**Git Tracking**: YES - Commit agent-handoffs.json updates regularly

---

#### 2. `.kit/tasks/` (Task Management)

**Purpose**: Task organization and execution tracking

**Structure**:
```
delegation/
├── tasks/
│   ├── active/                  # Current work (prioritized)
│   │   ├── TASK-YYYY-NNN-description.md
│   │   └── TASK-*-FOLLOWUP-*.md
│   ├── completed/               # Finished tasks (archived)
│   │   ├── phase-1/
│   │   └── phase-2a/
│   ├── analysis/                # Planning and research
│   │   └── *-ANALYSIS.md
│   └── logs/                    # Execution logs and reports
│       ├── PHASE-*-EXECUTION-PLAN.md
│       └── PHASE-*-COMPLETION-SUMMARY.md
└── handoffs/                    # Agent handoff documents
    └── TASK-*-HANDOFF.md
```

**Git Tracking**: YES - Track everything except temporary logs

---

### File Naming Conventions

**Tasks**:
```
TASK-YYYY-NNN-short-description.md
TASK-2025-014-validation-fixes.md
TASK-PACKAGING-001-ONBOARDING-ENHANCEMENT.md
```

**Handoffs**:
```
TASK-NNN-HANDOFF.md
TASK-NNN-READY-FOR-IMPLEMENTATION.md
TASK-NNN-COMPLETE.md
```

**Logs**:
```
PHASE-N-EXECUTION-PLAN.md
PHASE-N-COMPLETION-SUMMARY.md
STRATEGIC-REVIEW-*.md
```

**Analysis**:
```
*-ANALYSIS.md
*-INVESTIGATION-FINDINGS.md
*-DECISION-RECORD.md
```

---

## Agent Roles and Responsibilities

### Core Agents

#### 1. Coordinator Agent

**Role**: Project management, planning, agent coordination

**Responsibilities**:
- ✅ Maintain agent-handoffs.json
- ✅ Create and update task specifications
- ✅ Assign tasks to specialized agents
- ✅ Review completed work
- ✅ Update project state
- ✅ Plan phases and roadmaps
- ✅ Archive completed tasks

**Identity Requirement**:
```
📋 COORDINATOR | [current-task] | [current-status]
```

**Key Files**:
- `.kit/context/agent-handoffs.json` (read/write)
- `.kit/context/current-state.json` (read/write)
- `.kit/tasks/3-in-progress/*` (read/write)

**Handoff Pattern**: Creates task → Assigns to specialist → Reviews completion

---

#### 2. Feature-Developer Agent

**Role**: Code implementation, feature development

**Responsibilities**:
- ✅ Implement features per task spec
- ✅ Write production code
- ✅ Update tests
- ✅ Document changes
- ✅ Update agent-handoffs.json with progress
- ✅ Create handoff document when complete

**Identity Requirement**:
```
👨‍💻 FEATURE-DEVELOPER | [task-id] | [status]
```

**Key Files**:
- `.kit/tasks/3-in-progress/TASK-*.md` (read)
- Source code files (write)
- Test files (write)
- `.kit/context/agent-handoffs.json` (update progress)

**Handoff Pattern**: Receives task → Implements → Documents → Returns to coordinator

---

#### 3. Test-Runner Agent

**Role**: Test execution, validation, quality assurance

**Responsibilities**:
- ✅ Run test suites
- ✅ Analyze test results
- ✅ Create test reports
- ✅ Verify no regressions
- ✅ Document test metrics
- ✅ Update agent-handoffs.json

**Identity Requirement**:
```
🧪 TEST-RUNNER | [task-id] | [status]
```

**Key Files**:
- Test suite (execute)
- `.kit/context/TASK-*-VERIFICATION.md` (create)
- `.kit/context/agent-handoffs.json` (update)

**Handoff Pattern**: Receives implementation → Runs tests → Creates report → Returns to coordinator

---

#### 4. Media-Processor Agent

**Role**: Audio/video processing, timecode validation (domain-specific)

**Responsibilities**:
- ✅ Implement media processing features
- ✅ Handle timecode calculations
- ✅ Validate frame-accurate operations
- ✅ Create precision tests

**Identity Requirement**:
```
🎬 MEDIA-PROCESSOR | [task-id] | [status]
```

**Key Files**:
- Media processing modules (write)
- Timecode utilities (write)
- Precision tests (write)

---

### Project-Specific Agents

Create additional agents as needed:
- `api-developer`: API integration work
- `security-reviewer`: Security analysis
- `document-reviewer`: Documentation quality
- `edl-generator-developer`: EDL/XML format work (domain-specific)

---

## Coordination Patterns

### Pattern 1: Sequential Task Execution

**Use Case**: Single task, clear dependencies

```
Coordinator → Create Task → Assign to Feature-Developer
                                      ↓
                                 Implement
                                      ↓
                             Update handoffs.json
                                      ↓
                             Create HANDOFF.md
                                      ↓
Coordinator ← Review ← Return with handoff
     ↓
Archive task → Update project state
```

**Example** (thematic-cuts TASK-2025-014):
1. Coordinator created task specification
2. Feature-developer implemented validation fixes
3. Feature-developer updated agent-handoffs.json
4. Feature-developer created TASK-2025-014-COMPLETE.md
5. Coordinator reviewed, merged, archived task

---

### Pattern 2: Task with Verification Step

**Use Case**: Code changes requiring test validation

```
Coordinator → Create Task → Feature-Developer
                                      ↓
                                 Implement
                                      ↓
                             Update handoffs.json
                                      ↓
Coordinator ← Request Testing ← Return for validation
     ↓
Test-Runner → Run tests → Create verification report
                                      ↓
Coordinator ← Approve/Reject ← Return with results
     ↓
Archive or Request Fixes
```

**Example** (thematic-cuts TASK-2025-012):
1. Coordinator assigned precision timecode fixes
2. Feature-developer implemented fixes
3. Test-runner executed 54 precision tests
4. Test-runner created verification report (100% pass rate)
5. Coordinator approved and merged

---

### Pattern 3: Investigation-First Approach

**Use Case**: Uncertain requirements, complex changes

```
Coordinator → Create Investigation Task
                    ↓
            Feature-Developer (Phase 0)
                    ↓
            Investigate codebase
                    ↓
            Create findings document
                    ↓
Coordinator ← Review findings ← Return with analysis
     ↓
Create Implementation Task (Phase 1)
     ↓
Feature-Developer → Implement → Test-Runner → Coordinator
```

**Example** (thematic-cuts TASK-2025-015):
1. Coordinator requested OTIO investigation
2. Feature-developer researched codebase (grep, read)
3. Feature-developer created INVESTIGATION-FINDINGS.md
4. Coordinator reviewed, approved plan
5. Feature-developer implemented (4 tests fixed)

---

### Pattern 4: Multi-Agent Collaboration

**Use Case**: Large feature requiring multiple specializations

```
Coordinator → Create Master Task
     ↓
Split into sub-tasks
     ↓
     ├─→ Feature-Developer (API changes)
     ├─→ Media-Processor (Domain logic)
     └─→ Document-Reviewer (Documentation)
           ↓        ↓           ↓
           └────────┴───────────┘
                    ↓
            Test-Runner (Integration)
                    ↓
Coordinator ← Review all work ← Return with reports
     ↓
Merge and archive
```

**Example**: Could be used for complex features requiring multiple domains

---

## Context Management

### Primary Context File: agent-handoffs.json

**Structure**:
```json
{
  "agent-name": {
    "current_focus": "✅ TASK-ID COMPLETE - Brief description",
    "task_file": ".kit/tasks/3-in-progress/TASK-*.md",
    "status": "task_complete | in_progress | blocked",
    "priority": "high | medium | low",
    "dependencies": "Description of blockers or requirements",
    "deliverables": [
      "✅ Completed item 1",
      "✅ Completed item 2",
      "🔄 In progress item 3"
    ],
    "technical_notes": "Implementation details, decisions, findings",
    "coordination_role": "How this fits into larger project",
    "last_updated": "YYYY-MM-DD Description of update"
  }
}
```

**Best Practices**:
1. **Update immediately** when starting/finishing work
2. **Use emojis** for visual status: ✅ (complete), 🔄 (in progress), ⚠️ (blocked)
3. **Be specific** in current_focus (include task ID)
4. **Document decisions** in technical_notes
5. **Track dependencies** explicitly
6. **Commit regularly** - This is project memory!

---

### Secondary Context: current-state.json

**Purpose**: Project-wide metrics and state

**Structure**:
```json
{
  "project": "project-name",
  "version": "1.0.2",
  "status": "phase_name",
  "test_pass_rate": "85.1% (298/350 tests)",
  "current_phase": "Phase 2A (25% complete)",
  "recent_achievements": [
    "✅ Achievement 1",
    "✅ Achievement 2"
  ],
  "next_milestone": "TASK-ID: Description",
  "documentation_references": {
    "key_doc": "path/to/doc.md"
  }
}
```

**Update Frequency**: After major milestones (releases, phase completions)

---

### Session Logs (Optional)

**Purpose**: Historical record of agent sessions

**Structure**:
```
.kit/context/session-logs/
├── YYYY-MM-DD-agent-name-summary.md
├── 2025-10-16-coordinator-phase1-completion.md
└── 2025-10-13-feature-developer-task-014.md
```

**Content**: Session objectives, work completed, decisions made, handoff notes

**When to Create**: After significant sessions or complex work

---

## Task Management

### Task Lifecycle

```
1. CREATED (coordinator)
   └─→ .kit/tasks/3-in-progress/TASK-*.md

2. ASSIGNED (coordinator updates agent-handoffs.json)
   └─→ Agent picks up task

3. IN_PROGRESS (agent updates agent-handoffs.json)
   └─→ deliverables tracking with 🔄

4. BLOCKED (if issues arise)
   └─→ Update dependencies field, notify coordinator

5. COMPLETE (agent updates agent-handoffs.json)
   └─→ Create handoff document
   └─→ Mark deliverables with ✅

6. VERIFIED (test-runner or coordinator)
   └─→ Create verification report

7. ARCHIVED (coordinator)
   └─→ Move to .kit/tasks/5-done/
   └─→ Update project state
```

---

### Task Specification Template

```markdown
# TASK-YYYY-NNN: Task Title

**Task ID**: TASK-YYYY-NNN
**Status**: READY_FOR_IMPLEMENTATION | IN_PROGRESS | COMPLETE
**Priority**: HIGH | MEDIUM | LOW
**Created**: YYYY-MM-DD
**Assigned**: agent-name
**Dependencies**: TASK-IDs or "None"

---

## Overview

Brief description of what needs to be done and why.

---

## Requirements

1. Specific requirement 1
2. Specific requirement 2
3. Specific requirement 3

---

## Acceptance Criteria

- [ ] Criterion 1 (testable)
- [ ] Criterion 2 (measurable)
- [ ] Criterion 3 (verifiable)

---

## Technical Approach

### Investigation Findings (if Phase 0 done)
- Finding 1
- Finding 2

### Implementation Plan
1. Step 1
2. Step 2
3. Step 3

### Files to Modify
- `path/to/file1.py` - Description of changes
- `path/to/file2.py` - Description of changes

---

## Testing Plan

- Test case 1
- Test case 2
- Regression testing approach

---

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Risk 1 | HIGH | HIGH | Mitigation strategy |

---

## Deliverables

1. [ ] Deliverable 1
2. [ ] Deliverable 2
3. [ ] Documentation updated
4. [ ] Tests passing

---

## Handoff Checklist

- [ ] Implementation complete
- [ ] Tests passing (no regressions)
- [ ] agent-handoffs.json updated
- [ ] Handoff document created
- [ ] Code committed and pushed

---

**Document Created**: YYYY-MM-DD
**Last Updated**: YYYY-MM-DD by agent-name
```

---

## Handoff Protocols

### When to Create a Handoff Document

**Always**:
- Completing a major task
- Transitioning between project phases
- Handing off to a different agent
- Before extended breaks in work

**Optional**:
- Small tasks (<1 hour)
- Trivial fixes
- Documentation updates

---

### Handoff Document Template

```markdown
# TASK-NNN Handoff: Brief Title

**Date**: YYYY-MM-DD
**From**: agent-name
**To**: coordinator | specific-agent
**Task**: TASK-NNN
**Status**: COMPLETE | NEEDS_REVIEW | BLOCKED

---

## Summary

Brief summary of what was accomplished (2-3 sentences).

---

## What Was Done

### Files Modified
- `file1.py` - Description
- `file2.py` - Description

### Key Changes
1. Change 1 with rationale
2. Change 2 with rationale

### Test Results
- X/Y tests passing
- Notable test fixes
- Any regressions?

---

## Decisions Made

### Decision 1: Title
**Context**: Why decision was needed
**Options**: Alternatives considered
**Choice**: What was chosen and why
**Impact**: What this affects

---

## Issues Encountered

### Issue 1
**Problem**: Description
**Solution**: How it was resolved
**Time Lost**: Estimate

---

## Next Steps

1. Immediate next action
2. Follow-up tasks needed
3. Areas for improvement

---

## Verification

- [ ] All acceptance criteria met
- [ ] Tests passing (no regressions)
- [ ] Code committed (SHA: xxxxxxx)
- [ ] agent-handoffs.json updated
- [ ] Documentation updated

---

## Questions for Reviewer

1. Question about approach?
2. Concern about design decision?

---

**Handoff Complete**: YYYY-MM-DD HH:MM
**Available for Questions**: Until [date]
```

---

## Setup for New Projects

### Quick Setup Checklist

```bash
# 1. Create directory structure
mkdir -p .kit/context
mkdir -p .kit/tasks/{1-backlog,2-todo,3-in-progress,4-in-review,5-done,6-canceled,7-blocked,8-archive,9-reference}
# Handoff files go in .kit/context/ alongside other agent coordination files

# 2. Copy template files
cp /path/to/existing-project/.kit/context/AGENT-SYSTEM-GUIDE.md .kit/context/

# 3. Initialize agent-handoffs.json
cat > .kit/context/agent-handoffs.json << 'EOF'
{
  "coordinator": {
    "current_focus": "Initial project setup",
    "task_file": "None - Starting new project",
    "status": "setup",
    "priority": "high",
    "dependencies": "None",
    "deliverables": [
      "🔄 Agent system initialized",
      "🔄 Project structure created"
    ],
    "technical_notes": "New project initialization using agent coordination system",
    "last_updated": "YYYY-MM-DD Initial setup"
  }
}
EOF

# 4. Initialize current-state.json
cat > .kit/context/current-state.json << 'EOF'
{
  "project": "project-name",
  "version": "0.1.0",
  "status": "initial_setup",
  "current_phase": "Phase 0: Foundation",
  "recent_achievements": [],
  "next_milestone": "Complete project initialization",
  "last_updated": "YYYY-MM-DD"
}
EOF

# 5. Add to .gitignore (optional excludes)
cat >> .gitignore << 'EOF'

# Agent Context (mostly tracked)
.kit/context/session-logs/*.tmp
.adversarial/logs/*.tmp
EOF

# 6. Initial commit
git add .kit/
git commit -m "feat: Initialize agent coordination system

- Created .kit/context/ with agent-handoffs.json
- Created .kit/tasks/ task management structure
- Added AGENT-SYSTEM-GUIDE.md for reference"
```

---

### Minimal Setup (Bare Bones)

If you only want the essentials:

```bash
# Just the critical files
mkdir -p .kit/context .kit/tasks/{1-backlog,2-todo,3-in-progress,4-in-review,5-done}

# agent-handoffs.json (minimal)
echo '{"coordinator":{"current_focus":"Setup","status":"active","last_updated":"'$(date +%Y-%m-%d)'"}}' > .kit/context/agent-handoffs.json

# That's it! Expand as needed.
```

---

### Migrating from Existing Project

**Option 1: Copy Structure**
```bash
# Copy from existing project
rsync -av --exclude='*.tmp' \
  /path/to/thematic-cuts/.kit/context/ \
  /path/to/new-project/.kit/context/

rsync -av --exclude='*.tmp' \
  /path/to/thematic-cuts/delegation/ \
  /path/to/new-project/delegation/

# Clean up project-specific content
rm /path/to/new-project/.kit/tasks/3-in-progress/*
rm /path/to/new-project/.kit/tasks/5-done/*

# Edit agent-handoffs.json to reset state
```

**Option 2: Start Fresh with Guide**
```bash
# Just copy the guide
cp /path/to/thematic-cuts/.kit/context/AGENT-SYSTEM-GUIDE.md \
   /path/to/new-project/.kit/context/

# Follow Quick Setup Checklist above
```

---

## Best Practices

### 1. Agent Identity

**Always start responses with identity header**:
```
📋 COORDINATOR | task-name | status
👨‍💻 FEATURE-DEVELOPER | TASK-2025-014 | implementing
🧪 TEST-RUNNER | verification | running_tests
```

**Why**: Immediate context for user and logging

---

### 2. Update agent-handoffs.json Frequently

**Update Triggers**:
- Starting a new task
- Completing a task
- Making significant progress
- Encountering blockers
- End of work session

**Example Update**:
```json
{
  "feature-developer": {
    "current_focus": "✅ TASK-2025-014 COMPLETE - Validation API fixed (6/6 tests)",
    "status": "task_complete",
    "deliverables": [
      "✅ Separated validation concerns in Clip model",
      "✅ Enhanced validate_clip() with type checking",
      "✅ Fixed 6/6 target tests (100% pass rate)",
      "✅ Zero regressions (298 tests passing)"
    ],
    "last_updated": "2025-10-13 Task complete, ready for merge"
  }
}
```

---

### 3. Task Specifications Before Implementation

**Never start implementing without**:
1. Clear task specification file
2. Acceptance criteria defined
3. Technical approach outlined
4. Assigned in agent-handoffs.json

**Exception**: Trivial fixes (<10 lines, <15 minutes)

---

### 4. Handoff Documents for Major Work

**Create handoff when**:
- Task takes >1 hour
- Multiple files modified
- Architectural decisions made
- Tricky bugs encountered
- Someone else needs to understand work

**Keep concise**: 1-2 pages, focus on decisions and next steps

---

### 5. Archive Completed Tasks

**Immediately archive when**:
- Task verified complete
- Tests passing
- Code merged to main
- No follow-up needed

**How**:
```bash
mv .kit/tasks/3-in-progress/TASK-*.md \
   .kit/tasks/5-done/
```

**Update agent-handoffs.json**: Mark as completed with ✅

---

### 6. Document Decisions

**Use technical_notes field** for:
- Why approach X was chosen over Y
- Key implementation insights
- Tricky bugs and solutions
- Performance considerations
- Breaking changes avoided

**Example**:
```json
"technical_notes": "Chose integer arithmetic for drop-frame (30fps nominal) to avoid rounding errors. Fraction arithmetic for non-drop-frame (exact rates 24000/1001). Split approach eliminates cumulative error while maintaining SMPTE ST 12-1 compliance."
```

---

### 7. Use Emojis for Quick Status

**Standard Emojis**:
- ✅ Complete
- 🔄 In progress
- ⚠️ Blocked / Warning
- 🚀 Ready to start
- 📋 Planning
- 🧪 Testing
- 🎯 High priority
- 💡 Idea / Suggestion

**Why**: Visual scanning of status is faster

---

### 8. Git Commit agent-handoffs.json Updates

**Commit frequency**: With every significant update

**Commit message pattern**:
```
chore: Update [agent-name] status - [brief description]

[Optional details about what changed]
```

**Example**:
```
chore: Update feature-developer status - TASK-2025-014 complete

All 6 validation tests now passing. Zero regressions detected.
Ready for coordinator review and merge.
```

---

## Common Patterns

### Pattern: Discovery-First Approach

**When**: Requirements unclear, complex codebase

```markdown
## Phase 0: Investigation (Before Implementation)

**Time**: 30-60 minutes
**Output**: INVESTIGATION-FINDINGS.md

**Steps**:
1. Grep for relevant code patterns
2. Read key files
3. Understand current architecture
4. Document findings
5. Propose approach

**Deliverable**:
- .kit/tasks/3-in-progress/TASK-NNN-INVESTIGATION-FINDINGS.md
- Update task spec with confirmed approach

## Phase 1: Implementation (After Investigation)

Proceed with implementation knowing exactly what needs to change.
```

**Result**:
- thematic-cuts: Saved 15 hours through discovery-first in Phase 1
- Prevented phantom work (TASK-2025-014 failure scenario)

---

### Pattern: Multi-Stage Verification

**When**: High-risk changes, critical functionality

```markdown
## Stage 1: Plan Evaluation
- Coordinator reviews implementation plan
- Uses aider + GPT-4o for evaluation
- Output: APPROVED / NEEDS_REVISION

## Stage 2: Implementation
- Feature-developer implements
- Updates agent-handoffs.json with progress

## Stage 3: Code Review
- Review git diff for phantom work
- Verify real code changes (not TODOs)
- Output: APPROVED / NEEDS_REVISION

## Stage 4: Test Validation
- Test-runner executes tests
- Verifies no regressions
- Output: Tests passing / failing

## Stage 5: Final Approval
- Coordinator reviews all artifacts
- Merges if approved
- Archives task
```

**Tools**: adversarial-workflow package (developed in thematic-cuts)

---

### Pattern: Follow-Up Tasks

**When**: Implementation reveals side effects

```markdown
## Original Task: TASK-2025-014
- Fixed 6/6 validation tests
- **But**: Discovered 4 new test failures (side effects)

## Follow-Up Task: TASK-2025-014-FOLLOWUP
- Created immediately
- Addresses side effects
- Tracks as separate deliverable
```

**Why**: Keeps tasks focused, maintains clean completion status

---

### Pattern: Phase Transitions

**When**: Moving between project phases (Phase 1 → Phase 2)

```markdown
## Transition Checklist

1. [ ] Create PHASE-N-COMPLETION-SUMMARY.md
2. [ ] Archive all completed tasks
3. [ ] Update agent-handoffs.json (all agents)
4. [ ] Update current-state.json (project metrics)
5. [ ] Create PHASE-N+1-EXECUTION-PLAN.md
6. [ ] Commit and push all updates
7. [ ] Create handoff document for next phase

## Phase Handoff Document

- PHASE-N-COMPLETION-SUMMARY.md: What was done
- PHASE-N+1-EXECUTION-PLAN.md: What comes next
- COORDINATOR-HANDOFF-PHASE-N.md: Transition guide
```

**Example**: thematic-cuts Phase 1 → Phase 2 transition (this document!)

---

## Troubleshooting

### Issue: Agent Doesn't Have Context

**Symptoms**:
- Agent asks for information already provided
- Agent doesn't follow project conventions
- Agent makes decisions without context

**Solution**:
1. Check agent-handoffs.json exists and is updated
2. Point agent to relevant task file
3. Ensure agent reads .kit/context/ on startup
4. Update coordination_role field with project context

---

### Issue: Tasks Getting Lost

**Symptoms**:
- Can't find what needs to be done
- Duplicate work
- Unclear priorities

**Solution**:
1. Keep .kit/tasks/3-in-progress/ organized
2. Use clear task naming: TASK-YYYY-NNN-description.md
3. Update agent-handoffs.json task_file field
4. Archive completed tasks immediately

---

### Issue: Unclear Agent Responsibilities

**Symptoms**:
- Multiple agents working on same thing
- Gaps in coverage
- Confusion about ownership

**Solution**:
1. Define clear agent roles (see Agent Roles section)
2. Update current_focus in agent-handoffs.json
3. Use coordinator for assignment clarity
4. Document responsibility boundaries

---

### Issue: Lost Decisions or Context

**Symptoms**:
- Repeating old discussions
- Forgetting why decisions were made
- Re-implementing rejected approaches

**Solution**:
1. Document decisions in technical_notes
2. Create decision records in .kit/tasks/9-reference/
3. Commit agent-handoffs.json updates
4. Use handoff documents for major work

---

### Issue: Agent Identity Not Clear

**Symptoms**:
- User confusion about who's working
- Inconsistent response patterns
- Difficult to trace work

**Solution**:
1. **Always** start responses with identity header
2. Format: `📋 COORDINATOR | task | status`
3. Update identity when switching contexts
4. Use standard emojis (📋 coordinator, 👨‍💻 feature-dev, 🧪 test-runner)

---

## Examples from Real Projects

### Example 1: thematic-cuts (Complex Multi-Phase Project)

**Setup**:
```
.kit/context/
├── agent-handoffs.json         # 6 agents tracked
├── current-state.json          # Project metrics
└── AGENT-SYSTEM-GUIDE.md       # This guide

delegation/
├── tasks/
│   ├── active/                 # 22 active tasks
│   ├── completed/              # 12 completed tasks
│   ├── analysis/               # 8 planning docs
│   └── logs/                   # Phase reports
└── handoffs/                   # Agent handoffs
```

**Results**:
- 85.1% → 94.0% test pass rate
- 8+ major tasks coordinated
- Zero phantom work with multi-stage workflow
- 87.5% efficiency gain (Phase 1)

**Key Pattern**: Discovery-first + Multi-stage verification

---

### Example 2: adversarial-workflow (New Project Setup)

**Setup** (copying from thematic-cuts):
```bash
# Copied structure from thematic-cuts
mkdir -p .kit/context .kit/tasks/{1-backlog,2-todo,3-in-progress,4-in-review,5-done}

# Initialized with minimal agent-handoffs.json
cp ../thematic-cuts/.kit/context/AGENT-SYSTEM-GUIDE.md .kit/context/

# Ready for development in <5 minutes
```

**Result**: Smooth Phase 2 transition with full context

---

## Appendix: Template Files

### A. Minimal agent-handoffs.json

```json
{
  "coordinator": {
    "current_focus": "Project setup",
    "status": "active",
    "last_updated": "2025-10-16"
  }
}
```

### B. Full agent-handoffs.json Example

```json
{
  "coordinator": {
    "current_focus": "✅ PHASE 1 COMPLETE - Ready for Phase 2",
    "task_file": ".kit/tasks/9-reference/PHASE-2-PLAN.md",
    "status": "phase_transition",
    "priority": "high",
    "dependencies": "None - Phase 1 verified complete",
    "deliverables": [
      "✅ Phase 1: 6 tasks completed",
      "✅ Test pass rate: 85.4%",
      "✅ v1.0.1 released",
      "🔄 Phase 2 planning in progress"
    ],
    "technical_notes": "Phase 1 completed ahead of schedule. Zero regressions. All acceptance criteria met.",
    "coordination_role": "Planning Phase 2 execution with quality-first sequential approach",
    "next_critical_path": "Phase 2A: Core fixes (4 tasks, 16 tests)",
    "last_updated": "2025-10-10 Phase 1 Complete"
  },
  "feature-developer": {
    "current_focus": "✅ TASK-2025-012 COMPLETE - Precision timecode fixed",
    "task_file": ".kit/tasks/5-done/TASK-2025-012.md",
    "status": "task_complete",
    "priority": "completed",
    "dependencies": "None - Ready for next assignment",
    "deliverables": [
      "✅ Fixed 86 frame error at 23.976fps",
      "✅ Fixed drop frame round-trip",
      "✅ 54/54 precision tests passing (100%)",
      "✅ Zero regressions"
    ],
    "technical_notes": "Used integer arithmetic for DF, Fraction for NDF. Achieves frame-perfect accuracy per SMPTE ST 12-1.",
    "coordination_role": "Ready for TASK-2025-014 assignment (Validation API)",
    "last_updated": "2025-10-10 Task complete, verified by test-runner"
  },
  "test-runner": {
    "current_focus": "✅ TASK-2025-012 VERIFIED - 100% precision pass rate",
    "task_file": ".kit/context/TASK-2025-012-VERIFICATION.md",
    "status": "verification_complete",
    "priority": "completed",
    "dependencies": "None - Verification passed",
    "deliverables": [
      "✅ 54/54 precision tests passing",
      "✅ Zero regressions (298/350 overall)",
      "✅ Performance validated (<5ms per operation)",
      "✅ SMPTE compliance confirmed"
    ],
    "technical_notes": "Verification complete. Recommend immediate merge to main. LOW RISK, HIGH CONFIDENCE.",
    "coordination_role": "Available for next verification task",
    "recommendation": "MERGE TO MAIN - Production Ready",
    "last_updated": "2025-10-10 Verification complete, approved for merge"
  }
}
```

### C. Task Template (Copy-Paste Ready)

See "Task Specification Template" section above.

---

## Conclusion

This agent coordination system provides:

✅ **Clear responsibility** through role-based agents
✅ **Persistent context** via agent-handoffs.json
✅ **Task tracking** with active/completed organization
✅ **Smooth handoffs** with documented protocols
✅ **Project memory** through git-tracked context

**Proven Results**:
- thematic-cuts: 85.1% → 94.0% test pass rate
- adversarial-workflow: Successful multi-phase coordination
- Zero phantom work with verification patterns

**Getting Started**:
1. Create `.kit/context/` and `.kit/tasks/` directories
2. Initialize `agent-handoffs.json`
3. Start using identity headers
4. Update context regularly
5. Archive completed work

**Questions?** Reference this guide or consult thematic-cuts for working examples.

---

**Document Version**: 1.0
**Created**: 2025-10-16
**Tested On**: thematic-cuts, adversarial-workflow
**Status**: Production-ready methodology

---

**For new projects**: Copy this guide to `.kit/context/AGENT-SYSTEM-GUIDE.md` and follow the Setup section.

**Good luck with your coordination!** 📋✨
