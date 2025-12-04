# Review Fix Workflow

When code-reviewer returns `CHANGES_REQUESTED`, this document describes the process for addressing findings and completing the review cycle.

## Overview

```
                                    ┌─────────────────┐
                                    │  4-in-review/   │
                                    │   (task stays)  │
                                    └────────┬────────┘
                                             │
                    ┌────────────────────────┼────────────────────────┐
                    │                        │                        │
                    ▼                        ▼                        ▼
             ┌──────────┐            ┌──────────────┐          ┌─────────────┐
             │ APPROVED │            │  CHANGES     │          │  ESCALATE   │
             │          │            │  REQUESTED   │          │  TO HUMAN   │
             └────┬─────┘            └──────┬───────┘          └──────┬──────┘
                  │                         │                         │
                  ▼                         ▼                         ▼
           ┌──────────┐            ┌────────────────┐          ┌─────────────┐
           │ 5-done/  │            │ Fix & Re-review│          │ User decides│
           └──────────┘            └────────────────┘          └─────────────┘
```

## Process: Addressing CHANGES_REQUESTED

### Step 1: Planner Creates Fix Prompt

When code-reviewer returns `CHANGES_REQUESTED`, the planner creates a **lightweight fix prompt** for the feature-developer. This is simpler than a full task starter because:

- The original task file already exists
- The review file documents exactly what needs fixing
- Context is preserved in existing handoff files

**Fix Prompt Template:**

```markdown
## Review Fix: [TASK-ID]

**Review Verdict**: CHANGES_REQUESTED
**Review File**: `.agent-context/reviews/[TASK-ID]-review.md`
**Task File**: `delegation/tasks/4-in-review/[TASK-ID]-*.md`

### Required Changes

[List HIGH severity findings that must be addressed]

1. **[Finding Title]**: [Brief description]
   - File: `path/to/file.py`
   - Issue: [What's wrong]
   - Fix: [What to do]

### Optional Improvements

[List MEDIUM/LOW findings - nice to have but not blocking]

### After Fixing

1. Run tests: `pytest tests/ -v`
2. Verify CI: `/check-ci` or `./scripts/verify-ci.sh`
3. Create new review-starter (or update existing)
4. Request re-review from code-reviewer

---
**Invoke feature-developer in new tab with this prompt**
```

### Step 2: User Invokes Feature-Developer

User opens new Claude Code tab and provides the fix prompt. Feature-developer:

1. Reads the review file for full context
2. Reads the original task file for acceptance criteria
3. Implements the required changes
4. Runs tests
5. Creates/updates review-starter
6. Notifies completion

### Step 3: Re-Review (Round 2)

User invokes code-reviewer again in new tab. Per KIT-ADR-0014:

- **Maximum 2 review rounds**
- If Round 2 still has issues → `ESCALATE_TO_HUMAN`
- Reviewer should check previous review file for context

### Step 4: Resolution

| Round 2 Verdict | Action |
|-----------------|--------|
| APPROVED | Move task to `5-done/`, merge PR |
| CHANGES_REQUESTED | ESCALATE_TO_HUMAN (no Round 3) |
| ESCALATE_TO_HUMAN | User reviews and decides |

## File Locations

| File | Purpose |
|------|---------|
| `delegation/tasks/4-in-review/[TASK-ID]-*.md` | Original task spec (stays here until approved) |
| `.agent-context/reviews/[TASK-ID]-review.md` | Round 1 review findings |
| `.agent-context/reviews/[TASK-ID]-review-round2.md` | Round 2 review findings |
| `.agent-context/[TASK-ID]-REVIEW-STARTER.md` | Review starter (updated for re-review) |
| `.agent-context/[TASK-ID]-HANDOFF-*.md` | Original implementation handoff |

## Key Principles

1. **Task stays in `4-in-review/`** until approved - don't move back to `3-in-progress/`
2. **Lightweight over heavyweight** - fix prompts, not full task starters
3. **Review file is source of truth** - contains all findings and context
4. **Max 2 rounds** - prevents infinite loops
5. **Document decisions** - if accepting despite findings, note why in review file

## Anti-Patterns to Avoid

| Don't | Do Instead |
|-------|------------|
| Create new task for fixes | Use fix prompt referencing existing task |
| Move task back to `3-in-progress/` | Keep in `4-in-review/` until approved |
| Skip re-review after fixes | Always re-review, even for "simple" fixes |
| Go beyond Round 2 | Escalate to human after Round 2 |
| Overwrite review files | Version them (`-round2.md`) |

## Integration with Linear

Task status in Linear should reflect the review state:

| Task Location | Linear Status |
|---------------|---------------|
| `4-in-review/` | In Review |
| `4-in-review/` (fixing) | In Review (unchanged) |
| `5-done/` (approved) | Done |

The task only moves to Done after code review approval, not after implementation completion.
