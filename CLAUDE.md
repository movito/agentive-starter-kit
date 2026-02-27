# Agentive Starter Kit

A structured starter kit for agentive software development with Claude Code.
Provides specialized agents, task management, TDD infrastructure, adversarial
evaluation, and architectural decision records. For full details, see `README.md`.

## Directory Structure

```
.claude/agents/       Agent definitions (feature-developer-v3, planner, ci-checker, etc.)
.claude/commands/     Slash commands (start-task, commit-push-pr, check-ci, check-bots, etc.)
.claude/skills/       Skills (pre-implementation, self-review, bot-triage, review-handoff, code-review-evaluator)
.agent-context/       Agent coordination: handoffs, reviews, patterns.yml, workflows/
.adversarial/         Adversarial evaluation system (config, scripts, docs)
.serena/              Serena MCP configuration (semantic code navigation)
agents/               Agent launcher scripts (launch, onboarding, preflight)
delegation/tasks/     Task specs by status: 1-backlog/ through 9-reference/
docs/                 Documentation, ADRs (starter-kit-adr/ and your adr/)
scripts/              Project management and CI scripts
tests/                pytest test suite
```

## Project Rules

### Python (v3.10-3.12)

- **Formatter**: Black (v23.12.1, line-length=88)
- **Import sorting**: isort (profile=black)
- **Linting**: Ruff (E, F, I, N, W rules), flake8
- **Testing**: pytest with TDD workflow (write tests before implementation)
- **Coverage target**: 80% for new code (`fail_under` in pyproject.toml)
- **Pre-commit hooks**: trailing-whitespace, end-of-file-fixer, yaml/toml checks,
  black, isort, flake8, pattern-lint (DK rules -- custom defensive coding patterns),
  validate-task-status, pytest-fast

### Branching and CI

- Feature branches: `feature/<TASK-ID>-short-description`
- Run `./scripts/ci-check.sh` before pushing
- Verify CI on GitHub after push (`/check-ci` or `./scripts/verify-ci.sh`)
- All PRs require passing CI and code review before merge

### Task Workflow

- Status flow: `2-todo` -> `3-in-progress` -> `4-in-review` -> `5-done`
- Task files live in `delegation/tasks/<status-folder>/`
- Use `./scripts/project start|move|complete <TASK-ID>` to manage status
- Optional Linear sync: `./scripts/project linearsync`

### Defensive Coding

- Consult `.agent-context/patterns.yml` before writing new utility functions
- Use `==` for identifier comparison (not `in` unless justified with comment)
- Use `str.removesuffix()` for extension removal (never `.replace()`)
- Follow error strategy by layer: domain modules raise, CLI modules return empty,
  fire-and-forget modules log and continue (see `patterns.yml` -> `error_strategies`)
- Run `python3 scripts/pattern_lint.py <files>` to check for pattern violations

## Agent Context

### Key Agents

| Agent | Role |
|-------|------|
| `planner` / `planner2` | Planning and task orchestration |
| `feature-developer-v3` | Implementation with gated workflow |
| `ci-checker` | CI/CD verification |
| `code-reviewer` | Code quality review |
| `test-runner` / `powertest-runner` | TDD and testing |
| `tycho` | Day-to-day project management |

Full listing: `.claude/agents/` -- see `AGENT-TEMPLATE.md` for creating new agents.

### Workflow Reference

| Workflow | Location |
|----------|----------|
| Commit protocol | `.agent-context/workflows/COMMIT-PROTOCOL.md` |
| Testing | `.agent-context/workflows/TESTING-WORKFLOW.md` |
| Review fixes | `.agent-context/workflows/REVIEW-FIX-WORKFLOW.md` |
| PR sizing | `.agent-context/workflows/PR-SIZE-WORKFLOW.md` |
| Workflow freeze | `.agent-context/workflows/WORKFLOW-FREEZE-POLICY.md` |
| Coverage | `.agent-context/workflows/COVERAGE-WORKFLOW.md` |
| Task completion | `.agent-context/workflows/TASK-COMPLETION-PROTOCOL.md` |

## Key Scripts

| Script | Purpose |
|--------|---------|
| `./scripts/project start <ID>` | Move task to in-progress |
| `./scripts/project move <ID> <status>` | Move task to any status |
| `./scripts/project complete <ID>` | Move task to done |
| `./scripts/project linearsync` | Sync tasks to Linear |
| `./scripts/ci-check.sh` | Full CI check (local) |
| `./scripts/verify-ci.sh` | Verify CI status on GitHub |
| `./scripts/pattern_lint.py` | Check for defensive coding violations |
| `./scripts/create-agent.sh` | Create a new agent definition |
| `agents/launch` | Interactive agent launcher |
| `agents/onboarding` | First-time project setup |

## Version

Current: 0.3.2 (see `pyproject.toml`)
