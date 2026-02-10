# Changelog

All notable changes to the Agentive Starter Kit will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.3.2] - 2026-02-11

### Changed

- **Agent models upgraded to Opus 4.6** - Updated planner, feature-developer, security-reviewer, and AGENT-TEMPLATE to use `claude-opus-4-6`
- **Evaluators now installed via library** - Evaluators directory (`.adversarial/evaluators/`) is now gitignored; install with `./scripts/project install-evaluators`
- **Removed deprecated `evaluator_model` config** - Use `adversarial list-evaluators` and `--evaluator NAME` flag instead

### Added

- **UV auto-detection** (ASK-0032) - Setup script automatically detects UV package manager and uses it to create Python 3.12 venvs on Python 3.13+ systems
- **Agent creation automation** (ASK-0033) - New `scripts/create-agent.sh` with concurrent-safe locking, icon patterns, and force overwrite support

## [0.3.1] - 2026-02-02

### Added

- **Multi-provider evaluator configs** - 10 pre-configured evaluators across 4 providers (Anthropic, Google, Mistral, OpenAI) with index.json registry
- **Anthropic evaluator support** - Added claude-adversarial evaluator for critical review

### Fixed

- **Python version ceiling check** (ASK-0030) - Setup now validates `>=3.10,<3.13` upfront with clear error messages and remediation options (pyenv, brew, python.org). Prevents cryptic pip errors on Python 3.13+ due to aider-chat constraint.
- **Shell-aware venv activation** - Onboarding now shows fish/csh alternatives alongside bash/zsh
- **Python version references** - Updated all documentation from "3.9+" to "3.10+" to match actual constraints

### Changed

- **Simplified README setup** - Removed redundant "Set Up Development Environment" section; onboarding handles setup automatically

## [0.3.0] - 2026-02-01

### Changed

- **Upgraded adversarial-workflow to v0.7.0** - Now requires `>=0.7.0` with multi-evaluator support, configurable timeouts, and custom evaluator definitions
- **Provider-agnostic documentation** - Replaced all model-specific language (e.g., "GPT-4o") with evaluator-agnostic descriptions throughout prompts and documentation

### Added

- **Multi-evaluator architecture** (ASK-0029) - Support for multiple evaluation providers via custom evaluators. Users can now use Gemini, Mistral, Anthropic, or local models alongside OpenAI.
- **Evaluator library installer** - New `./scripts/project install-evaluators` command installs pre-built evaluators from adversarial-evaluator-library with version pinning and commit hash tracking.
- **Project setup command** (ASK-0028) - New `./scripts/project setup` creates virtual environment, installs dependencies, and configures pre-commit hooks. Includes Python version check, corrupted venv detection, and `--force` flag for recreation.
- **Evaluator setup in onboarding** - New optional phase in onboarding for installing additional evaluators
- **Custom evaluators directory** - `.adversarial/evaluators/` with README explaining how to create custom evaluators
- **Evaluator discovery** - Documented `adversarial list-evaluators` command to discover built-in and custom evaluators

### Fixed

- **Linear sync no longer breaks test collection** - Changed `sys.exit(1)` at import time to runtime check with `GQL_AVAILABLE` flag. Tests now skip gracefully when gql package not installed instead of failing during pytest collection.
- **Added `requires_gql` marker** - Tests that need the gql package are now marked and can be skipped with `-m "not requires_gql"`. Pattern documented in KIT-ADR-0005.

## [0.2.2] - 2025-12-06

### Added

- **Upstream tracking option in onboarding** - Users can now opt to add the original starter kit as an upstream remote during onboarding, making it easy to pull future updates with `git fetch upstream && git merge upstream/main`.

### Changed

- **Simplified Serena activation instructions** - Removed confusing placeholder references and redundant fallback sections from all 6 agent files. Activation section is now consistent and minimal across all agents.
- **Enhanced CI verification script** - `verify-ci.sh` now uses jq for proper JSON parsing, filters to push events only, reports on latest commit SHA, and provides clear verdicts (PASS/FAIL/IN PROGRESS/MIXED). Added `--wait` flag to block until workflows complete. Exit codes: 0 for pass, 1 for fail.
- **CI-checker model upgraded to Sonnet** - Switched from Haiku to Sonnet (`claude-sonnet-4-20250514`) for more reliable tool invocation behavior.

### Fixed

- **CI-checker agent tool execution** - Added explicit CRITICAL instruction requiring use of Bash tool to execute gh commands, fixing issue where Haiku would sometimes show commands in markdown without actually running them.
- **Code-reviewer Serena activation** - Removed explicit Serena MCP tools from frontmatter (caused activation to be skipped) and added code-reviewer to launcher's serena_agents list. Agents should discover Serena tools after activation, not via frontmatter listing.

## [0.2.1] - 2025-12-04

### Added

- **Structured knowledge capture from code reviews** (KIT-ADR-0019) - Code review insights are now captured in `.agent-context/REVIEW-INSIGHTS.md`, organized by module with recommended patterns and anti-patterns. Future agents can learn from past reviews.
- **Mandatory code review workflow** (KIT-ADR-0014) - Implementation agents now create review starters and request code review before task completion. Reviews are versioned (round 1, round 2) to preserve history.
- **Review fix workflow** - Streamlined process for handling CHANGES_REQUESTED verdicts with lightweight fix prompts instead of full task starters.

### Changed

- **Removed Thematic project-specific content** - Cleaned DaVinci Resolve, SMPTE, Electron references from agent templates for cleaner starter kit experience.
- **Improved Serena activation instructions** - Code-reviewer and other agents now have clearer, more direct activation instructions.

### Fixed

- **Reconfigure command handles upstream project name** - `./scripts/project reconfigure` now uses regex to replace any `activate_project()` call, not just the `"your-project"` placeholder. This fixes the case where downstream projects merge upstream and get `"agentive-starter-kit"` in their agent files instead of their configured project name.
- **Code-reviewer no longer overwrites existing reviews** - Reviews are now versioned (`-round2.md` suffix) to preserve review history.

## [0.2.0] - 2025-12-03

### Added

- **Task lifecycle management** - Agents now run `./scripts/project start <TASK-ID>` when picking up tasks, automatically moving them to `3-in-progress/` and updating status headers for visibility
- **TDD infrastructure out of the box** - pytest, pre-commit hooks, and test workflows ship ready to use
- **Startup task scanning** - Planner agent checks `delegation/tasks/2-todo/` on session start and summarizes pending work
- **CI verification script** - `./scripts/ci-check.sh` for local pre-push validation
- **Browser warning for Serena** - Dashboard flash warning added to prevent confusion during LSP initialization

### Changed

- **Project CLI location** - Moved from `./project` to `./scripts/project` for cleaner root directory
- **Simplified planner startup** - Planner now asks what to build when no tasks exist, recognizes TDD is pre-configured
- **Improved onboarding** - Clearer Linear API key instructions, better Serena activation guidance for new projects
- **Updated adversarial-workflow** - Upgraded to v0.5.0

### Fixed

- Custom task prefix support in glob patterns (e.g., `ASK-*`, `TASK-*`)
- Invalid model ID `claude-sonnet-4-5` corrected to `claude-sonnet-4`
- Dependencies `gql` and `python-dotenv` moved to main dependencies (were missing)
- Various path inconsistencies in documentation and agent instructions

## [0.1.0] - 2025-11-25

### Added

- Initial release of the Agentive Starter Kit
- Multi-agent coordination system with specialized agents (planner, feature-developer, test-runner, etc.)
- Linear task synchronization with bidirectional status updates
- Serena MCP integration for semantic code navigation
- Adversarial evaluation workflow with GPT-4o
- Task delegation system with numbered folder workflow
- Agent handoff protocol via `.agent-context/`
- Pre-configured Claude Code settings and permissions

[0.3.2]: https://github.com/movito/agentive-starter-kit/compare/v0.3.1...v0.3.2
[0.3.1]: https://github.com/movito/agentive-starter-kit/compare/v0.3.0...v0.3.1
[0.3.0]: https://github.com/movito/agentive-starter-kit/compare/v0.2.2...v0.3.0
[0.2.2]: https://github.com/movito/agentive-starter-kit/compare/v0.2.1...v0.2.2
[0.2.1]: https://github.com/movito/agentive-starter-kit/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/movito/agentive-starter-kit/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/movito/agentive-starter-kit/releases/tag/v0.1.0
