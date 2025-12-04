# Changelog

All notable changes to the Agentive Starter Kit will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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

[0.2.1]: https://github.com/movito/agentive-starter-kit/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/movito/agentive-starter-kit/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/movito/agentive-starter-kit/releases/tag/v0.1.0
