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
- **ASK-0033**: Dual locking strategy (flock + file-based fallback) provides robust concurrency on macOS where flock may not be available
- **ASK-0033**: Implement stale lock detection with timeout - delete locks older than configured threshold
- **ASK-0033**: Sed escaping for templates: escape `&`, `/`, and newlines in replacement strings to prevent injection
- **ASK-0033**: Use trap with cleanup function for atomic operations - restore backups on failure, remove partial files

### CLI (`scripts/project`)

- **ASK-0025**: User-friendly output should include actionable next steps (e.g., "Run ./scripts/project linearsync to sync")
- **ASK-0025**: Limit verbose output lists (e.g., show max 5 missing tasks, then "and N more...")
- **ASK-0027**: Progress reporting pattern - show status for each file/item processed
- **ASK-0027**: Idempotent commands - safe to run multiple times without unintended side effects
- **ASK-0028**: Subprocess calls should use `capture_output=True, text=True` for proper error capture
- **ASK-0028**: Truncate long error output (e.g., `stderr[-500:]`) with manual remediation instructions
- **ASK-0028**: Detect corrupted state (e.g., missing venv python) and suggest `--force` flag
- **ASK-0029**: Library installers should track version + commit hash in `.installed-version` for auditability
- **ASK-0029**: Pin external content installers to specific versions (tags), not just "latest"
- **ASK-0029**: Support `--force` for reinstallation and `--ref <tag>` for version override

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
- **Optional Dependencies**: Use `GQL_AVAILABLE` flag pattern instead of `sys.exit(1)` at import time (ASK-0028, KIT-ADR-0005)
- **Subprocess Error Capture**: Always use `capture_output=True, text=True` and check return codes (ASK-0028)
- **Provider-Agnostic Design**: Avoid hard-coded model/provider names in documentation; use generic terms with "see docs for options" (ASK-0029)
- **Version Pinning for External Content**: Pin to tags by default, record commit hash for auditability (ASK-0029)
- **Dual Locking Strategy**: Use flock where available, fallback to file-based locking for cross-platform compatibility (ASK-0033)
- **Atomic File Operations**: Backup before modify, validate result, cleanup on failure via trap (ASK-0033)
- **Input Validation in Shell**: Validate names, descriptions, and paths before processing - fail fast with clear errors (ASK-0033)

### Anti-Patterns to Avoid

- **Massive Inline Scripts**: Inline Python >100 lines in bash scripts hurts maintainability and testability (ASK-0025)
- **Untestable CLI Logic**: Embedding all logic in CLI entry points prevents unit testing - extract core logic (ASK-0025)
- **Silent Failures**: Operations that can fail silently (like Linear sync) need verification commands (ASK-0025)

---

## Integration Notes

- **Linear Sync**: Use `./scripts/project sync-status` after commits to verify Linear is updated (ASK-0025)
- **Upstream Merges**: Run `./scripts/project reconfigure` after pulling upstream changes to update agent files (ASK-0027)
- **New Project Setup**: Run `./scripts/project setup` to create venv and install dependencies (ASK-0028)
- **Evaluator Installation**: Run `./scripts/project install-evaluators` to add additional evaluation providers (ASK-0029)

---

## ADR Candidates

*None currently - insights above are implementation patterns rather than architectural decisions*

---

*Last updated: 2026-02-09 by planner (ASK-0033 insights added)*
