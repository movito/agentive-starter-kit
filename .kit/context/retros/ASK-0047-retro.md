## ASK-0047 — Flatten ADR Directory Structure (PR #42)

**Date**: 2026-03-30
**Agent**: feature-developer-v5
**Scorecard**: 7 threads, 0 regressions, 1 fix round, 2 commits (squash-merged)

### What Worked

1. **Bulk sed for mass path renames** — With ~137 references across 57+ files, using `sed` for the mechanical replacements was the right call. Doing individual Edit calls would have taken 10x longer. Three sed passes (docs/decisions/adr/ → docs/adr/, .kit/decisions/ → .kit/adr/, docs/decisions/starter-kit-adr/ → .kit/adr/) covered all patterns.
2. **CodeRabbit caught real missed paths** — Found 3 files (`check-sync.sh` KIT_DIRS array, `scripts/core/project` exclude_path_parts, `ADR-CREATION-WORKFLOW.md` README.md refs) that the sed passes missed because they used different string patterns (bare `"decisions"`, `docs/decisions` without trailing slash). These were genuine bugs.
3. **Grep verification gate** — Running `grep -r` for both old paths as a hard gate before committing caught zero matches, confirming the sed passes were thorough for the patterns they targeted. The CodeRabbit findings were in files with non-standard reference formats.

### What Was Surprising

1. **`.DS_Store` files blocked `rmdir`** — After `git mv`, the old directories couldn't be removed because macOS had left `.DS_Store` files behind. Required manual `rm` before `rmdir`. Minor but adds friction to directory renames.
2. **Test fixture hardcoded old paths** — `test_project_script.py::test_excludes_legitimate_references` created a `docs/decisions/adr.md` test fixture that broke when `exclude_path_parts` was updated. This wasn't caught until the fix commit's test run. The sed passes didn't touch test fixtures because they use `tmp_path` construction, not string literals with the old path.
3. **Linter/hook interference with Edit tool** — The Edit tool reported "file modified since read" several times because pre-commit hooks or formatters ran between Read and Edit calls. Re-reading the file resolved it each time, but it slowed the workflow.

### What Should Change

1. **Add `check-sync.sh` KIT_DIRS to grep verification** — The hardcoded `KIT_DIRS` array in `check-sync.sh` uses bare directory names (`"decisions"` not `.kit/decisions/`), so the standard grep didn't catch it. Future structural renames should grep for bare directory names too.
2. **Test fixtures should derive paths from constants** — `test_project_script.py` hardcodes `docs/decisions` in the test fixture. If `exclude_path_parts` were importable, tests could reference the actual constant. This would prevent fixture drift on path renames.
3. **Pre-existing Black failure in CI** — `sync_tasks_to_linear.py` has a formatting issue that causes `ci-check.sh` to fail even with no changes to that file. Should be fixed independently.

### Permission Prompts Hit

None.

### Process Actions Taken

- [ ] Add bare directory name grep to structural rename checklist
- [ ] Fix pre-existing Black formatting in `scripts/optional/sync_tasks_to_linear.py`
- [ ] Consider making `exclude_path_parts` importable for test fixtures
