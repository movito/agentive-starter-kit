# Agentive Starter Kit

**Production-ready infrastructure for agentive AI development**

Build software with specialized AI agents, adversarial evaluation, and structured task management.

---

## What Is This?

A complete starter kit for **agentive development** - a methodology for coordinating specialized AI agents to build high-quality software at scale.

This kit provides:

- **10+ Specialized Agents** - Planner, feature-developer, test-runner, and more
- **Task Management System** - Linear-compatible workflow with numbered folders
- **Adversarial Evaluation** - GPT-4o reviews your plans before implementation
- **Serena Integration** - Semantic code navigation across multiple languages
- **TDD Infrastructure** - Pre-commit hooks, test templates, quality gates
- **Comprehensive Documentation** - Agentive development guide included

**Source**: Extracted from a production project with 90+ completed tasks and 85%+ test pass rate.

---

## Prerequisites

Before you begin, verify you have the following:

### Must Have (Required)

| Requirement | How to Check | How to Get |
|-------------|--------------|------------|
| **Claude Account** | You can log into [claude.ai](https://claude.ai) | [Sign up](https://claude.ai) |
| **Claude Code** | `claude --version` | [Download](https://claude.ai/download) or install VS Code/Cursor extension |
| **GitHub Account** | You can log into [github.com](https://github.com) | [Sign up](https://github.com/signup) |
| **Git Configured** | `git config user.name && git config user.email` | [Setup guide](https://docs.github.com/en/get-started/quickstart/set-up-git) |

> **New to Git?** Check out [GitHub's Git Handbook](https://guides.github.com/introduction/git-handbook/) for a quick introduction.

### Should Have (For Core Features)

| Requirement | How to Check | How to Get |
|-------------|--------------|------------|
| **Python 3.9+** | `python3 --version` | [python.org](https://www.python.org/downloads/) or `brew install python` |
| **uvx or pipx** | `uvx --version` or `pipx --version` | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |

### Nice to Have (Optional Enhancements)

| Requirement | Purpose | How to Get |
|-------------|---------|------------|
| **OpenAI API Key** | Adversarial evaluation (~$0.04/eval) | [platform.openai.com](https://platform.openai.com/api-keys) |
| **Linear Integration** | Task sync with Linear issues | See [Linear Integration](#linear-integration) section below |

### Quick Preflight Check

Run this script to validate your environment:

```bash
./agents/preflight
```

It will check all requirements and tell you what's missing.

---

## Quick Start

### 1. Clone the Repository

Open your terminal and navigate to where you keep projects (e.g., `~/Github` or `~/Projects`):

```bash
cd ~/Github
```

Then clone this starter kit with your project name:

```bash
git clone https://github.com/movito/agentive-starter-kit.git my-project-name
cd my-project-name
```

This creates a new `my-project-name` folder with everything inside. **Don't create the folder first** - the clone command does that for you.

Then open the folder in your IDE (VS Code, Cursor, etc.).

### 2. Run First-Time Onboarding

```bash
./agents/onboarding
```

### 3. Follow Interactive Setup

`planner` (your project coordinator) will guide you through:

1. **Project Configuration** - Name your project
2. **Language Selection** - Configure Serena for your languages
3. **API Keys** - Set up Anthropic, OpenAI, and Linear (optional)
4. **Feature Selection** - Enable evaluation, task sync, etc.
5. **First Task** - Create your first task to get started

Setup takes approximately 5-10 minutes.

---

## What's Included

### Agents (`.claude/agents/`)

| Agent | Purpose |
|-------|---------|
| `planner` | Helps you plan, tracks work, keeps things on track |

| `tycho` | Day-to-day project management |
| `feature-developer` | Implementation tasks |
| `test-runner` | TDD and testing |
| `powertest-runner` | Comprehensive test suites |
| `document-reviewer` | Documentation quality |
| `security-reviewer` | Security analysis |
| `ci-checker` | CI/CD verification |
| `agent-creator` | Create new specialized agents |

### Task Management (`delegation/tasks/`)

Linear-compatible folder structure:

```
delegation/tasks/
├── 1-backlog/      → Backlog (planned, not started)
├── 2-todo/         → Todo (ready to start)
├── 3-in-progress/  → In Progress (active work)
├── 4-in-review/    → In Review (awaiting review)
├── 5-done/         → Done (completed)
├── 6-canceled/     → Canceled
├── 7-blocked/      → Blocked (waiting on dependencies)
├── 8-archive/      → Archive (historical)
└── 9-reference/    → Reference (templates, docs)
```

### Adversarial Evaluation (`.adversarial/`)

GPT-4o reviews your task specifications before implementation:

```bash
# Run evaluation on a task
adversarial evaluate delegation/tasks/2-todo/TASK-0001-my-task.md

# Results saved to .adversarial/logs/
```

Cost: ~$0.04-0.08 per evaluation.

### Serena Integration (`.serena/`)

Semantic code navigation with LSP support:

- Python (pylsp)
- TypeScript/JavaScript (typescript-language-server)
- Swift (sourcekit-lsp)
- And more...

Reduces token consumption by 70-98% for code navigation tasks.

---

## Configuration

### Environment Variables (`.env`)

Copy `.env.template` to `.env` and configure:

```bash
# For adversarial evaluation (optional)
OPENAI_API_KEY=sk-your-key

# For Linear task sync (optional) - see Linear Integration section
LINEAR_API_KEY=lin_api_your-key
LINEAR_TEAM_ID=ABC
```

### Serena (`.serena/project.yml`)

Copy `.serena/project.yml.template` to `.serena/project.yml`:

```yaml
project_name: "my-project"
languages:
  - python
  - typescript
```

### Adversarial (`.adversarial/config.yml`)

Copy `.adversarial/config.yml.template` to `.adversarial/config.yml`.

---

## Linear Integration

The starter kit includes a built-in task management system that helps agents do better work and helps you track progress. Tasks are stored as markdown files in `delegation/tasks/` folders.

**You can optionally sync these tasks with [Linear](https://linear.app)** for team visibility and project management. This is more involved than just adding an API key.

### Setting Up Linear (Optional)

**1. Create a Linear account**

Sign up at [linear.app](https://linear.app) if you don't have an account.

**2. Create a new team**

Go to Settings → Teams → [Create new team](https://linear.app/settings/new-team)

**Important:** Use the same identifier for your Linear team as you use for task prefixes in the codebase. For example:
- If your task files are named `ABC-0001-feature.md`, `ABC-0002-bugfix.md`
- Set your Linear team identifier to `ABC`

This keeps task IDs consistent between your codebase and Linear.

**3. Get your Linear API key**

Go to Settings → API → [API settings](https://linear.app/settings/api)

The page shows "OAuth applications" and "Webhooks" - **click "Webhooks"** on the left sidebar to find Personal API keys.

- Scroll down to "Personal API keys"
- Click "Create new API key"
- Give it a name (e.g., "agentive-starter-kit")
- Copy the key (starts with `lin_api_`)

**4. Get your Team ID**

Your Team ID is the identifier you chose in step 2 (e.g., `ABC`).

**5. Configure your `.env` file**

```bash
LINEAR_API_KEY=lin_api_your-key-here
LINEAR_TEAM_ID=ABC
```

### How Linear Sync Works

When configured, the task system:
- Syncs task files in `delegation/tasks/` folders to Linear issues
- Maps folder locations to Linear statuses (e.g., `2-todo/` → "Todo")
- Updates both directions: move a file → Linear updates, change Linear → file moves

See `docs/LINEAR-SYNC-BEHAVIOR.md` for detailed sync behavior.

### Without Linear

Tasks work fine without Linear - they're just markdown files. Agents can create, track, and complete tasks using the folder structure alone. Linear adds team visibility and integrations, but isn't required.

---

## Usage

### First-Time Setup

```bash
# Run onboarding (first time only)
./agents/onboarding
```

### Launching Agents (After Setup)

```bash
# Interactive menu
./agents/launch

# Launch specific agent
./agents/launch planner
./agents/launch feature-developer
./agents/launch test-runner
```

### Creating Tasks

**The easy way:** Just tell `planner` what you want to build. The agent will create and manage tasks for you.

```bash
./agents/launch planner
# Then: "I want to add user authentication to my app"
```

**Manual task creation** (if you prefer):

1. Copy task template: `delegation/tasks/9-reference/templates/task-template.md`
2. Create task file: `delegation/tasks/2-todo/TASK-0001-my-task.md`
3. Run evaluation: `adversarial evaluate delegation/tasks/2-todo/TASK-0001-my-task.md`
4. Assign to agent via `planner`

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=your_project --cov-report=term-missing
```

---

## Documentation

- **Agentive Development Guide**: `docs/agentive-development/README.md`
- **Agent Template**: `.claude/agents/AGENT-TEMPLATE.md`
- **Task Template**: `delegation/tasks/9-reference/templates/task-template.md`
- **Evaluation Workflow**: `.adversarial/docs/EVALUATION-WORKFLOW.md`
- **ADR Template**: `docs/decisions/adr/TEMPLATE-FOR-ADR-FILES.md`

---

## Project Structure

```
your-project/
├── .claude/
│   ├── agents/              # Agent definitions
│   ├── commands/            # Slash commands
│   └── settings.local.json  # Claude Code settings
├── .agent-context/
│   ├── agent-handoffs.json  # Agent coordination state
│   ├── current-state.json   # Project state
│   ├── workflows/           # Workflow documentation
│   └── templates/           # Handoff templates
├── .serena/
│   └── project.yml          # Serena configuration
├── .adversarial/
│   ├── config.yml           # Evaluation config
│   ├── scripts/             # Evaluation scripts
│   └── docs/                # Evaluation docs
├── delegation/
│   ├── tasks/               # Task files (numbered folders)
│   └── handoffs/            # Agent handoff documents
├── docs/
│   ├── agentive-development/# Complete methodology guide
│   ├── decisions/adr/       # Architectural Decision Records
│   └── prd/                 # Product Requirements Documents
├── agents/
│   ├── launch               # Agent launcher (interactive menu)
│   └── onboarding           # First-run setup (run once)
├── tests/                   # Test suite
├── .env                     # Environment variables (git-ignored)
├── .pre-commit-config.yaml  # Pre-commit hooks
└── pyproject.toml           # Python project config
```

---

## Philosophy

### Progressive Refinement Over Perfectionism
- Start simple, iterate based on real feedback
- 2-3 iteration maximum on any task
- Ship with known limitations

### Test-Driven Development
- Tests before implementation
- 80%+ coverage for new code
- Pre-commit hooks catch issues early

### Multi-Model Collaboration
- Claude for implementation
- GPT-4o for evaluation/critique
- Planner for orchestration

### Context Management
- Documentation is infrastructure
- Handoffs prevent context loss
- Shared memory enables coordination

---

## Contributing

This starter kit is extracted from real development practices. Contributions welcome:

1. Found a better pattern? Document what and why
2. Tried this approach? Share your results
3. Adapted for your domain? Share variations

---

## License

MIT

---

## Acknowledgments

Developed through real-world use on production projects. Special thanks to the Claude and GPT-4o teams for making agentive development possible.

---

**Version**: 1.0.0
**Last Updated**: 2025-11-25
