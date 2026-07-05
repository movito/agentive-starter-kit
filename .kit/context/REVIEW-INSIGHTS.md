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

### Sync & Manifest (`scripts/.core-manifest.json`, `.github/workflows/`)

- **KIT-0024**: Shell variable expansion in YAML (GitHub Actions) is vulnerable to backtick injection — always quote `$()` subshells in workflow files
- **KIT-0024**: Guard against missing directories before `cp` in sync workflows — downstream repos may not have `.claude/commands/` yet
- **KIT-0024**: o3 code-reviewer can produce false positives about basic shell behavior (`$()` strips trailing newlines, GitHub Actions empty outputs are `""` not `null`, `_core$` regex anchoring). Always verify shell-related findings with one-liner tests before accepting.

### Scripts (`scripts/`)

- **ASK-0043**: Root-resolution preamble (`SCRIPT_DIR`/`PROJECT_ROOT`/`cd`) is now standard in all shell scripts. Future scripts must include it. Scripts with `set -e` already handle `cd` failure; scripts without it need `|| exit 1` on the `cd` line.
- **ASK-0044**: Launcher scripts (`launch`, `onboarding`) must self-test `PROJECT_ROOT` resolution — when a script moves to a different directory depth, `dirname` chains silently resolve to the wrong root. Add guard: `[[ -f "$PROJECT_ROOT/pyproject.toml" ]] || exit 1`.

- **ASK-0025**: Inline Python via `-c` in bash scripts follows `teams` command pattern - acceptable for smaller scripts
- **ASK-0025**: For large inline scripts (185+ lines), consider extracting to separate module (e.g., `scripts/check_sync_status.py`) for testability
- **ASK-0027**: Support multiple YAML field names (e.g., both `name:` and `project_name:`) with first-match-wins logic
- **ASK-0027**: Watch for path resolution bugs in `project_dir` handling - use `Path.resolve()` consistently

### CLI (`scripts/core/project`)

- **ASK-0025**: User-friendly output should include actionable next steps (e.g., "Run ./scripts/core/project linearsync to sync")
- **ASK-0025**: Limit verbose output lists (e.g., show max 5 missing tasks, then "and N more...")
- **ASK-0027**: Progress reporting pattern - show status for each file/item processed
- **ASK-0027**: Idempotent commands - safe to run multiple times without unintended side effects
- **ASK-0028**: Subprocess calls should use `capture_output=True, text=True` for proper error capture
- **ASK-0028**: Truncate long error output (e.g., `stderr[-500:]`) with manual remediation instructions
- **ASK-0028**: Detect corrupted state (e.g., missing venv python) and suggest `--force` flag
- **ASK-0029**: Library installers should track version + commit hash in `.installed-version` for auditability
- **ASK-0029**: Pin external content installers to specific versions (tags), not just "latest"
- **ASK-0029**: Support `--force` for reinstallation and `--ref <tag>` for version override
- **ASK-0032**: Use `shutil.which()` for tool detection - simple and reliable
- **ASK-0032**: Provide primary recommendation with alternatives in error messages (uv → pyenv → manual)
- **ASK-0032**: Use generous timeouts (600s) for operations that may download large files

### Tests (`tests/`)

- **ASK-0025**: CLI entry points excluded from coverage (pyproject.toml), but core logic should be extractable into testable functions
- **ASK-0025**: Consider extracting comparison/validation logic from CLI commands into utility modules for unit testing
- **ASK-0032**: Use `conftest.py` for shared fixtures - improves test maintainability
- **ASK-0032**: MockVersionInfo class pattern: handle both tuple comparison (`>=`) and attribute access (`.major`)

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
- **Non-Intrusive Feature Flags**: New features should only activate for relevant scenarios (e.g., Python 3.13+ only) (ASK-0032)
- **Tiered Error Messages**: Primary recommendation → alternatives → manual fallback (ASK-0032)
- **Data-Shape Verification Before Coding**: When implementing against a bot/CI/API signal, capture real output first — KIT-0034's spec said "CodeRabbit check-run" but reality is a commit status; coding to the paraphrase would have shipped a fallback that never fires (KIT-0034)
- **PATH-Stubbed Binary for Shell-Script Testing**: A fake `gh` shim on PATH running the *real* script against canned states is the cheapest credible verification for shell+CLI gate logic with no test harness — re-runs in seconds per fix round (KIT-0034; codification tracked in KIT-0040)
- **Single Shared API Snapshot Across Related Checks**: One GraphQL fetch feeding preflight Gates 2/3/4 eliminated the race where the fallback and thread gate could disagree mid-run, and cut 3 API calls to 1 (KIT-0034)
- **Mutation-Test a New Test Harness**: after building a harness, deliberately break one condition in the system under test and confirm a test fails — turns "the harness passes" into "the harness detects breakage" for ~10 minutes of work (KIT-0040)
- **Stub Every External Touchpoint, Not Just the Obvious One**: the preflight harness stubbed `sleep` (instant poll loops) and `dispatch` (no fire-and-forget event leakage) alongside `gh`; module-scoped fixtures cut runtime 5.3s → 1.8s, inside the pre-commit fast-hook budget (KIT-0040)
- **Two Consistent Detection Paths for Parse-or-Reject Logic**: pair a tolerant parse regex with a deliberately *looser* malformed-input detector so no input falls between "parses fine" and "detected as broken" — the gap between the two is where silent data loss lives (KIT-0040, kit_markers.py)

### Anti-Patterns to Avoid

- **Massive Inline Scripts**: Inline Python >100 lines in bash scripts hurts maintainability and testability (ASK-0025)
- **Untestable CLI Logic**: Embedding all logic in CLI entry points prevents unit testing - extract core logic (ASK-0025)
- **Silent Failures**: Operations that can fail silently (like Linear sync) need verification commands (ASK-0025)
- **Trusting Evaluator Verdicts Without Triage**: o3 code-reviewer can return FAIL based on false positives — always verify individual findings before accepting the overall verdict (KIT-0024)
- **Blanket rm+copy in Sync Actions**: Use manifest-driven file-by-file copy to preserve local/unowned files in downstream repos (KIT-0024, KIT-ADR-0022)
- **Splitting structural migrations into multiple PRs**: Mass directory moves + path rewrites create a half-migrated codebase between PRs that agents cannot navigate. Agents depend on hardcoded paths in prompts, handoff files, and CLAUDE.md — stale paths cause silent failures. Structural migrations must land atomically in a single branch/PR, even if large. The evaluator (arch-review) does not assess intermediate state viability — it only reviews the target architecture. The planner must catch this. (ASK-0044)
- **Grep verification with only full-path patterns**: `grep -r 'old/path/'` misses bare directory name references (e.g., `"decisions"` in array literals, `exclude_path_parts`). Structural renames must also grep for bare directory names. (ASK-0047)
- **Test fixtures with hardcoded paths**: `test_project_script.py` constructs fixtures with literal path strings (`docs/decisions`). When the real paths change, fixtures break. Consider deriving from constants. (ASK-0047)
- **Merged PRs as stable verification fixtures**: retro-referenced PRs are snapshots, not fixtures — PR #58 drifted (2 new unresolved BugBot threads) and could no longer serve as the canonical Gate-2 false-negative case; PR #63 had to substitute. Verify a referenced PR still has the assumed shape before building a test plan on it. (KIT-0034)

---

## Integration Notes

- **Grep False Positives**: `settings.local.json` (gitignored) contains auto-generated permission allow-list entries with old paths — these trigger grep matches during path audits but are not runtime code. Exclude from path-consistency checks. (ASK-0044)
- **CI Verification**: `verify-ci.sh` only checks push-triggered workflows but the Tests workflow triggers on `pull_request`. Fall back to `gh run list` for comprehensive status. (ASK-0044)
- **Linear Sync**: Use `./scripts/core/project sync-status` after commits to verify Linear is updated (ASK-0025)
- **Upstream Merges**: Run `./scripts/core/project reconfigure` after pulling upstream changes to update agent files (ASK-0027)
- **New Project Setup**: Run `./scripts/core/project setup` to create venv and install dependencies (ASK-0028)
- **Evaluator Installation**: Run `./scripts/core/project install-evaluators` to add additional evaluation providers (ASK-0029)
- **adversarial-workflow CLI requires `.adversarial/` at repo root**: The CLI (v0.9.9) hardcodes `.adversarial/` as its working directory. ASK-0044 moved it to `.kit/adversarial/` but this broke the CLI. Reverted: `.adversarial/` now lives at repo root again. Future move requires ADV-0053 (configurable dir) — tracked upstream at movito/adversarial-workflow#58. (ASK-0044 post-mortem)
- **CodeRabbit reports via the legacy commit-status API (`context: "CodeRabbit"`), BugBot via check-runs**: any gate or tooling querying bot review state must hit the right surface for each bot — statuses primary for CodeRabbit, check-runs for BugBot. (KIT-0034)
- **CodeRabbit re-flags stale bookkeeping paths on every task-status move**: `project move` changes the task folder but not `details_link` in agent-handoffs.json or handoff-file metadata; update them in the same commit as the move to preempt a bot round. FIXED in KIT-0040 (PR #70): `project start|move|complete` now rewrites the metadata in the same operation. (KIT-0034 → KIT-0040)
- **`gh pr checks` is stale immediately after a push**: it reports the *previous* head's checks for a window after pushing — an all-green snapshot taken seconds after a push is not proof; disambiguate with a SHA-scoped GraphQL query. (KIT-0040)
- **External-finding yield concentrates on fresh code**: across 8 evaluator/bot findings on PR #70, the 2 real ones were both in code written that session, none in pre-existing code under review. Weight triage attention accordingly. (KIT-0040)

---

## ADR Candidates

*None currently - insights above are implementation patterns rather than architectural decisions*

---

*Last updated: 2026-07-05 by planner-f5 (KIT-0040 extraction: harness mutation-testing, detection-path pairing, stale pr-checks, fresh-code finding yield)*
