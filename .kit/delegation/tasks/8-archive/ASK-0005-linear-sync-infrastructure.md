# ASK-0005: Linear Sync Infrastructure

**Status**: Done
**Priority**: high
**Assigned To**: feature-developer
**Estimated Effort**: 4-6 hours
**Created**: 2025-11-28
**Completed**: 2025-11-28

## Related Tasks

**Parent Task**: None
**Depends On**: ASK-0001 (pyproject.toml), ASK-0004 (scripts directory)
**Blocks**: None
**Related**: None

## Overview

Add Linear task synchronization infrastructure to the starter kit. This enables projects using the kit to sync their markdown task files (`delegation/tasks/`) to Linear for visual project management.

**Context**: The upstream-project project has a mature Linear sync implementation that needs to be generalized for the starter kit. Currently, projects cloned from the starter kit have documentation referencing `./thematic linearsync` which doesn't exist. AL2 (agentic-lotion-2) discovered this gap when attempting to sync tasks.

**Related Work**:
- upstream-project `scripts/sync_tasks_to_linear.py` (28KB, production-ready)
- upstream-project `scripts/linear_sync_stubs.py` (TDD implementation)
- AL2 ADR-0001 (documented missing infrastructure)

## Requirements

### Functional Requirements
1. **Task sync script** that reads `delegation/tasks/[1-7]-*/` folders and syncs to Linear
2. **Project CLI launcher** (`./scripts/project` or configurable name) with `linearsync` command
3. **GitHub workflow** that auto-syncs on push to task folders
4. **Status mapping** from folder structure to Linear status (e.g., `2-todo/` → "Todo")
5. **Legacy status migration** for non-Linear-native statuses in task files

### Non-Functional Requirements
- [ ] Performance: Batch sync 50+ tasks in <30 seconds
- [ ] Reliability: Exponential backoff on rate limits
- [ ] Security: API key only in `.env` (never committed)
- [ ] Maintainability: No project-specific hardcoding (GitHub URL configurable)

## TDD Workflow (Mandatory)

**Test-Driven Development Approach**:

1. **Before coding**: Create `tests/test_linear_sync.py`
2. **Red**: Write failing tests for sync logic
3. **Green**: Implement minimum code until tests pass
4. **Refactor**: Improve code while keeping tests green
5. **Commit**: Pre-commit hook runs tests automatically

**TDD Benefits for this task**:
- Ensures sync logic handles edge cases (empty files, missing titles)
- Validates status mapping correctness
- Documents expected behavior for future maintainers

### Test Requirements
- [ ] Unit tests for TaskParser (file parsing)
- [ ] Unit tests for status determination (field > folder > default)
- [ ] Unit tests for legacy status migration
- [ ] Integration tests for LinearClient (mocked API)
- [ ] Error handling tests for API failures and rate limits

**Test files to create**:
- `tests/test_linear_sync.py` - Core sync logic tests
- `tests/test_project_cli.py` - CLI launcher tests

## Test Coverage Requirements

**Coverage Targets**:
- [ ] New code: **80%+ line coverage** (mandatory)
- [ ] Critical paths: **100% coverage** (mandatory)

**Critical Paths** (require 100% coverage):
1. Task file parsing (extract ID, title, status)
2. Status determination priority (field > folder > default)
3. Legacy status migration (file modification)

## Implementation Plan

### Files to Create

1. `scripts/sync_tasks_to_linear.py` - Main sync script
   - Purpose: Sync task markdown files to Linear issues
   - Contains: TaskData, TaskParser, LinearClient, main()
   - Estimated lines: ~400 (simplified from upstream-project 863)

2. `scripts/linear_sync_utils.py` - Helper functions
   - Purpose: Status mapping, migration, validation
   - Contains: is_linear_native_status(), determine_status_from_path(), migrate_legacy_status()
   - Estimated lines: ~150

3. `project` - CLI launcher (root directory)
   - Purpose: Simple command interface (`./scripts/project linearsync`)
   - Contains: Command routing to scripts
   - Estimated lines: ~80

4. `.github/workflows/sync-to-linear.yml` - GitHub workflow
   - Purpose: Auto-sync on push to task folders
   - Triggers: Push to `delegation/tasks/[1-7]-*/`
   - Estimated lines: ~50

5. `tests/test_linear_sync.py` - Test suite
   - Purpose: Test sync logic
   - Estimated tests: ~25 tests

### Approach

**Step 1: TDD - Write Failing Tests (1-2 hours)**

1. Create `tests/test_linear_sync.py` with tests for:
   - `test_parse_task_file_extracts_id_and_title()`
   - `test_parse_task_file_handles_missing_title()`
   - `test_determine_status_from_folder_path()`
   - `test_status_field_takes_priority_over_folder()`
   - `test_legacy_status_migration()`
   - `test_should_exclude_archive_folder()`

2. Run tests (should fail): `pytest tests/test_linear_sync.py -v`

**Step 2: Implement Core Logic (2-3 hours)**

1. Create `scripts/linear_sync_utils.py`:
   - `is_linear_native_status()` - Validate status values
   - `determine_status_from_path()` - Folder → status mapping
   - `determine_final_status()` - Priority resolution
   - `migrate_legacy_status()` - File migration

2. Create `scripts/sync_tasks_to_linear.py`:
   - `TaskData` dataclass (generalized, no THEMATIC references)
   - `TaskParser` class (supports TASK-#### pattern)
   - `LinearClient` class (from upstream-project, unchanged)
   - `main()` function (sync mode only, remove comment mode)

3. Run tests (should pass): `pytest tests/test_linear_sync.py -v`

**Step 3: CLI & Workflow (1 hour)**

1. Create `project` CLI launcher
2. Create `.github/workflows/sync-to-linear.yml`
3. Update `.env.template` with Linear config

**Step 4: Documentation (30 min)**

1. Update `README.md` with Linear sync section
2. Update onboarding docs for Linear setup

## Key Generalizations from upstream-project

| upstream-project | starter-kit | Change |
|---------------|-------------|--------|
| `THEMATIC-####` pattern | `TASK-####` pattern | Remove THEMATIC support |
| `github.com/movito/upstream-project` | `GITHUB_REPO_URL` env var | Make configurable |
| `./thematic linearsync` | `./scripts/project linearsync` | Generic CLI name |
| Comment posting mode | Removed | Simplify for starter kit |
| TDD stubs import | Inline | Remove external dependency |

## Acceptance Criteria

### Must Have ✅
- [ ] `./scripts/project linearsync` syncs tasks to Linear
- [ ] Tasks in `1-backlog/` through `7-blocked/` folders sync correctly
- [ ] Tasks in `8-archive/` and `9-reference/` are excluded
- [ ] Status field in file takes priority over folder location
- [ ] Legacy statuses are migrated to Linear-native values
- [ ] GitHub workflow auto-syncs on push
- [ ] All tests passing (25+ tests)
- [ ] 80%+ test coverage on new code

### Should Have 🎯
- [ ] Clear error messages for missing API key
- [ ] Dry-run mode (`./scripts/project linearsync --dry-run`)
- [ ] Batch processing for large task counts

### Nice to Have 🌟
- [ ] Task monitoring daemon (`./scripts/project daemon start`)
- [ ] Bidirectional sync (Linear → files)

## Success Metrics

### Quantitative
- Test pass rate: 100%
- Coverage: 80%+ for new code
- Sync time: <30 seconds for 50 tasks

### Qualitative
- AL2 can successfully sync tasks to Linear
- New projects can set up Linear sync in <10 minutes

## Risks & Mitigations

### Risk 1: Linear API Rate Limiting
**Likelihood**: Medium
**Impact**: Medium
**Mitigation**:
- Implement exponential backoff (1s, 2s, 4s...)
- Batch processing with delays between batches

### Risk 2: Breaking Existing Task Files
**Likelihood**: Low
**Impact**: High
**Mitigation**:
- Migration only updates Status field, preserves everything else
- Dry-run mode for preview before actual changes

## Time Estimate

| Phase | Time | Status |
|-------|------|--------|
| TDD: Write failing tests | 1-2 hours | [ ] |
| TDD: Implement core logic | 2-3 hours | [ ] |
| CLI & Workflow | 1 hour | [ ] |
| Documentation | 30 min | [ ] |
| **Total** | **4-6 hours** | [ ] |

## References

### Source Implementation
- `upstream-project/scripts/sync_tasks_to_linear.py` (863 lines)
- `upstream-project/scripts/linear_sync_stubs.py` (580 lines)
- `upstream-project/thematic` (CLI launcher, 79 lines)
- `upstream-project/.github/workflows/sync-to-linear.yml` (54 lines)

### Documentation
- Linear API: https://developers.linear.app/docs/graphql/working-with-the-graphql-api
- ADR-0038: Task status Linear alignment (from upstream-project)

## Notes

- The upstream-project implementation includes TDD stubs and comment posting features that are overkill for the starter kit
- Focus on core sync functionality; advanced features can be added later
- GitHub URL should default to auto-detection from `git remote get-url origin` if env var not set

---

**Template Version**: 1.0.0
**Created**: 2025-11-28
