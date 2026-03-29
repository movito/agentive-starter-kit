# Review Starter: ASK-0027

**Task**: ASK-0027 - Add Project Reconfigure Command
**Task File**: `.kit/tasks/4-in-review/ASK-0027-project-reconfigure-command.md`
**Branch**: main (direct push)
**Commit**: 2eee5c0

## Implementation Summary
- Added `./scripts/project reconfigure` command that updates agent files with project name after upstream merges
- Fixed existing bug where `project_dir` pointed to `scripts/` instead of project root
- Updated README "Pulling Updates" section with reconfigure step
- Also fixed 6 agent files that had lingering "your-project" placeholders

## Files Changed
- `scripts/project` (modified) - Added `reconfigure_project()` function, fixed `project_dir` path, added command case, updated help text
- `README.md` (modified) - Added reconfigure step to "Pulling Updates" section
- `.claude/agents/*.md` (6 files modified) - Fixed placeholder values as side effect of testing

## Test Results
- 68 tests passing, 1 skipped
- 92% coverage
- All CI checks pass (Tests + Linear Sync workflows)

## Areas for Review Focus
- The `reconfigure_project()` function logic (lines 171-243 in scripts/project)
- Error handling for missing config file or empty project name
- The fix for `project_dir` path resolution (line 249) - was causing `start`, `validate`, etc. to fail

## Key Design Decisions
- Supports both `name:` and `project_name:` in .serena/project.yml
- Only replaces literal `"your-project"` placeholder (preserves custom names)
- Idempotent - safe to run multiple times
- Returns success (exit 0) even if no files need updating

## Related ADRs
- None directly applicable (infrastructure improvement)

---
**Ready for code-reviewer agent in new tab**
