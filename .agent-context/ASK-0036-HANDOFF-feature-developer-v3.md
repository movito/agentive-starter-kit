# ASK-0036 Handoff: Expand Reconfigure to Catch All Identity Leaks

**You are the feature-developer-v3. Implement this task directly. Do not delegate or spawn other agents.**

## Task File

`delegation/tasks/2-todo/ASK-0036-expand-reconfigure.md`

## Mission

Expand `reconfigure_project()` in `scripts/project` (line 177) to replace 8 additional identity patterns beyond the existing Serena activation replacement.

## Scope

**Python code task** — full v3 workflow applies (TDD, pre-implementation, self-review, spec check, bots, evaluator).

Primary file: `scripts/project` (function `reconfigure_project` at line 177)
Test file: `tests/test_project_script.py` (add new test class)

## Current Behavior

The function reads `project_name` from `.serena/project.yml` and replaces `activate_project("...")` calls in `.claude/agents/*.md`. That's all it does.

## What to Add

### New data sources (derive inside `reconfigure_project`):

```python
# 1. Repo URL from git remote
import subprocess
result = subprocess.run(["git", "remote", "get-url", "origin"],
                       capture_output=True, text=True, cwd=project_dir)
repo_url = None
if result.returncode == 0:
    # Extract "github.com/owner/repo" from SSH or HTTPS URL
    url = result.stdout.strip()
    # Handle: git@github.com:owner/repo.git or https://github.com/owner/repo.git
    ...

# 2. Title-case project name for headings
project_title = project_name.replace("-", " ").replace("_", " ").title()
```

### 8 new replacement patterns:

| # | File | Pattern (regex) | Replacement |
|---|------|----------------|-------------|
| 1 | `pyproject.toml` | `# Project configuration for.*Agentive Starter Kit` | `# Project configuration for {project_name}` |
| 2 | `tests/conftest.py` | `agentive-starter-kit test suite` | `{project_name} test suite` |
| 3 | `CHANGELOG.md` | `All notable changes to the Agentive Starter Kit` | `All notable changes to {project_title}` |
| 4 | `CHANGELOG.md` | `github.com/movito/agentive-starter-kit` | `{repo_url}` (if available) |
| 5 | `CLAUDE.md` | `# Agentive Starter Kit` | `# {project_title}` |
| 6 | `README.md` | `# Agentive Starter Kit` (line 1 only) | `# {project_title}` |
| 7 | `scripts/logging_config.py` | `agentive-starter-kit` | `{project_name}` |
| 8 | `.claude/agents/planner.md` | `github.com/movito/agentive-starter-kit` | `{repo_url}` (if available) |

### `--verify` flag

After all replacements, if `--verify` is passed, run the audit grep and report remaining leaks. The audit should exclude:
- `.git/`, `5-done/`, `8-archive/`, `.venv/`
- `.adversarial/`, `.agent-context/`, `.aider`
- `docs/decisions/`, `docs/archive/`, `docs/UPSTREAM`
- `onboarding.md`

## Key Constraints

- **Idempotent**: Running twice produces same result — patterns must match both upstream content AND already-reconfigured content, or only match upstream content
- **Graceful**: If a file doesn't exist, skip it (don't error)
- **Git remote fallback**: If `git remote get-url origin` fails, skip URL replacements with a warning
- **Exclude onboarding.md**: The onboarding agent SHOULD reference the upstream starter kit
- **Don't modify .serena/project.yml**: That's the source of truth

## Testing Approach

Add a new test class `TestReconfigureExpanded` (or similar) to `tests/test_project_script.py`:

- Create a temp directory with mock files containing upstream patterns
- Write a minimal `.serena/project.yml` with a test project name
- Initialize a git repo with a fake origin remote
- Run `reconfigure_project()`
- Verify each file was updated correctly
- Run again to verify idempotency

## First Steps

```bash
# 1. Create feature branch
git checkout -b feature/ASK-0036-expand-reconfigure

# 2. Start the task
./scripts/project start ASK-0036
```

## Serena Activation

```text
mcp__serena__activate_project("agentive-starter-kit")
```
