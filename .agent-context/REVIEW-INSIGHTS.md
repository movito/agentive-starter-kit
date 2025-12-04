# Review Insights Index

Distilled knowledge from code reviews. Updated by planner during task completion.

**Reference**: KIT-ADR-0019 (Review Knowledge Extraction)

---

## How to Use This File

**For Agents Starting Work**:
1. Check relevant module sections before implementation
2. Review "Patterns & Anti-Patterns" for established conventions
3. Note any integration requirements that affect your work

**For Planner Completing Tasks**:
1. After moving task to `5-done/`, read the review file
2. Extract high-signal insights (not everything, just what's reusable)
3. Append entries under appropriate sections
4. Always include task ID for traceability

---

## Index by Module

### Scripts (`scripts/`)

- **ASK-0025**: Inline Python via `-c` in bash scripts follows `teams` command pattern - acceptable for smaller scripts
- **ASK-0025**: For large inline scripts (185+ lines), consider extracting to separate module (e.g., `scripts/check_sync_status.py`) for testability
- **ASK-0027**: Support multiple YAML field names (e.g., both `name:` and `project_name:`) with first-match-wins logic
- **ASK-0027**: Watch for path resolution bugs in `project_dir` handling - use `Path.resolve()` consistently

### CLI (`scripts/project`)

- **ASK-0025**: User-friendly output should include actionable next steps (e.g., "Run ./scripts/project linearsync to sync")
- **ASK-0025**: Limit verbose output lists (e.g., show max 5 missing tasks, then "and N more...")
- **ASK-0027**: Progress reporting pattern - show status for each file/item processed
- **ASK-0027**: Idempotent commands - safe to run multiple times without unintended side effects

### Tests (`tests/`)

- **ASK-0025**: CLI entry points excluded from coverage (pyproject.toml), but core logic should be extractable into testable functions
- **ASK-0025**: Consider extracting comparison/validation logic from CLI commands into utility modules for unit testing

---

## Patterns & Anti-Patterns

### Recommended Patterns

- **Idempotent CLI**: Design commands to be safe for repeated execution (ASK-0027)
- **Actionable Output**: Include specific next-step commands in error/status messages (ASK-0025)
- **Output Limiting**: Cap verbose lists with "and N more..." to avoid overwhelming users (ASK-0025)
- **Dual Config Support**: Accept multiple field names for config values, take first match (ASK-0027)
- **Robust Error Handling**: Graceful handling of missing files without swallowing errors (ASK-0027)
- **Type Hints + Docstrings**: Include for maintainability in all new code (ASK-0027)
- **Progress Reporting**: Show per-item status for batch operations (ASK-0027)

### Anti-Patterns to Avoid

- **Massive Inline Scripts**: Inline Python >100 lines in bash scripts hurts maintainability and testability (ASK-0025)
- **Untestable CLI Logic**: Embedding all logic in CLI entry points prevents unit testing - extract core logic (ASK-0025)
- **Silent Failures**: Operations that can fail silently (like Linear sync) need verification commands (ASK-0025)

---

## Integration Notes

- **Linear Sync**: Use `./scripts/project sync-status` after commits to verify Linear is updated (ASK-0025)
- **Upstream Merges**: Run `./scripts/project reconfigure` after pulling upstream changes to update agent files (ASK-0027)

---

## ADR Candidates

*None currently - insights above are implementation patterns rather than architectural decisions*

---

*Last updated: 2025-12-04 by planner*
