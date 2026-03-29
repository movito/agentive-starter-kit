# Agentive Starter Kit

A structured starter kit for agentive software development with Claude Code.
Provides specialized agents, task management, TDD infrastructure, adversarial
evaluation, and architectural decision records. For full details, see `README.md`.

## Directory Structure

```
.claude/agents/       Implementation agents (feature-developer-v3, ci-checker, etc.)
.claude/commands/     All slash commands (start-task, babysit-pr, retro, etc.)
.claude/skills/       Implementation skills (pre-implementation, bot-triage)
.kit/                 Builder layer (planning, coordination, evaluation)
├── agents/           Builder agents (planner, planner2, code-reviewer, etc.)
├── skills/           Builder skills (self-review, review-handoff, code-review-evaluator)
├── context/          Agent coordination: handoffs, reviews, patterns.yml, workflows/
├── adversarial/      Adversarial evaluation system (config, scripts, docs)
├── delegation/tasks/ Task specs by status: 1-backlog/ through 9-reference/
├── decisions/        Kit ADRs (KIT-ADR-*)
├── launchers/        Agent launcher scripts (launch, onboarding, preflight)
└── docs/             Builder documentation
.serena/              Serena MCP configuration (semantic code navigation)
docs/                 Documentation, ADRs (adr/)
scripts/              Project scripts: core/ (shared), local/ (ASK-specific), optional/
tests/                pytest test suite
```

## Project Rules

### Python (v3.10-3.12)

- **Formatter**: Black (v26.1.0, line-length=88)
- **Import sorting**: isort (profile=black)
- **Linting**: Ruff (E, F, I, N, W rules), flake8
- **Testing**: pytest with TDD workflow (write tests before implementation)
- **Coverage target**: 80% for new code (`fail_under` in pyproject.toml)
- **Pre-commit hooks**: trailing-whitespace, end-of-file-fixer, yaml/toml checks,
  black, isort, flake8, pattern-lint (DK rules -- custom defensive coding patterns),
  validate-task-status, pytest-fast

### Branching and CI

- Feature branches: `feature/<TASK-ID>-short-description`
- Run `./scripts/core/ci-check.sh` before pushing
- Verify CI on GitHub after push (`/check-ci` or `./scripts/core/verify-ci.sh`)
- All PRs require passing CI and code review before merge

### Task Workflow

- Status flow: `2-todo` -> `3-in-progress` -> `4-in-review` -> `5-done`
- Task files live in `.kit/delegation/tasks/<status-folder>/`
- Use `./scripts/core/project start|move|complete <TASK-ID>` to manage status
- Optional Linear sync: `./scripts/core/project linearsync`

### Defensive Coding

- Consult `.kit/context/patterns.yml` before writing new utility functions
- Use `==` for identifier comparison (not `in` unless justified with comment)
- Use `str.removesuffix()` for extension removal (never `.replace()`)
- Follow error strategy by layer: domain modules raise, CLI modules return empty,
  fire-and-forget modules log and continue (see `patterns.yml` -> `error_strategies`)
- Run `python3 scripts/core/pattern_lint.py <files>` to check for pattern violations

## Agent Context

### Key Agents

| Agent | Role |
|-------|------|
| `planner` / `planner2` | Planning and task orchestration |
| `feature-developer-v3` | Implementation with gated workflow |
| `ci-checker` | CI/CD verification |
| `code-reviewer` | Code quality review |
| `test-runner` / `powertest-runner` | TDD and testing |

Full listing: `.claude/agents/` (implementation) and `.kit/agents/` (builder).
See `.kit/agents/AGENT-TEMPLATE.md` for creating new agents.

### Workflow Reference

| Workflow | Location |
|----------|----------|
| Commit protocol | `.kit/context/workflows/COMMIT-PROTOCOL.md` |
| Testing | `.kit/context/workflows/TESTING-WORKFLOW.md` |
| Review fixes | `.kit/context/workflows/REVIEW-FIX-WORKFLOW.md` |
| PR sizing | `.kit/context/workflows/PR-SIZE-WORKFLOW.md` |
| Workflow freeze | `.kit/context/workflows/WORKFLOW-FREEZE-POLICY.md` |
| Coverage | `.kit/context/workflows/COVERAGE-WORKFLOW.md` |
| Task completion | `.kit/context/workflows/TASK-COMPLETION-PROTOCOL.md` |

## Key Scripts

| Script | Purpose |
|--------|---------|
| `./scripts/core/project start <ID>` | Move task to in-progress |
| `./scripts/core/project move <ID> <status>` | Move task to any status |
| `./scripts/core/project complete <ID>` | Move task to done |
| `./scripts/core/project linearsync` | Sync tasks to Linear |
| `./scripts/core/ci-check.sh` | Full CI check (local) |
| `./scripts/core/verify-ci.sh` | Verify CI status on GitHub |
| `./scripts/core/pattern_lint.py` | Check for defensive coding violations |
| `./scripts/optional/create-agent.sh` | Create a new agent definition |
| `.kit/launchers/launch` | Interactive agent launcher |
| `.kit/launchers/onboarding` | First-time project setup |

## Version

See `pyproject.toml` for the current version.
