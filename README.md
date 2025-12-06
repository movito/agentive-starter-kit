# Agentive Starter Kit

**A bit of structure to help you get more out of agentive software development**

Using agents to build software works better if you add a bit of structure. Anthropic calls this a [harness](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents). We created the tools in this kit to overcome the usual problems of agentive development: documentation, testing, architecture, and value for money (and tokens).

When we start a new project, we clone this repo and complete the onboarding. This gives us tests, tasks, documentation, and token-efficient tools, all in about ten minutes. You can tweak things as you wish, including how the agents work, and what models you use.

----
## What's inside?

1. An **onboarding agent** to help you get started.

2. A selection of **specialized agents** that have specific tasks, instructions, and tools. Some of them create and track plans, others write code, and so on.

3. A package we created called `adversarial-evaluation` which lets agents get a "second opinion" from an `Evaluator`; a specialized Open AI GPT-4o agent. We found that constructive critique among agents can give a big productivity boost.

4. A **task management setup** with task templates, a task tracking system, and an optional Linear sync.

5. Infrastructure for **test-driven development** (TDD), with test templates, quality gates, pre-commit hooks, and more.

6. A system for creating and maintaining **architectural decision records**; think of it as a knowledgebase for agents – and humans.

7. Integration with Serena, by Oraios, for helping agents work more effectively with the codebase.

8. Detailed documentation on how to select the right agent, size tasks correctly, write good tests, and more

---

## Requirements

If you'd like to try this kit, here are the tools you'll need:

### To get started

| Requirement | How to Check | How to Get |
|-------------|--------------|------------|
| **A Claude account** | Log in to [claude.ai](https://claude.ai) | [Sign up](https://claude.ai) |
| **Claude Code installed** in your terminal or IDE | `claude --version` | [Download](https://claude.ai/download) or install VS Code/Cursor extension |
| **GitHub account** | Log in to [github.com](https://github.com) | [Sign up](https://github.com/signup) |
| **Git configured** | `git config user.name && git config user.email` | [Setup guide](https://docs.github.com/en/get-started/quickstart/set-up-git) |

> **New to Git?** Check out [GitHub's Git Handbook](https://guides.github.com/introduction/git-handbook/) for a quick introduction.

### To start building

| Requirement | How to Check | How to Get |
|-------------|--------------|------------|
| **Python 3.9+** | `python3 --version` | [python.org](https://www.python.org/downloads/) or `brew install python` |
| **uvx or pipx** | `uvx --version` or `pipx --version` | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |

### Evaluation and planning support

| Requirement | Purpose | How to Get |
|-------------|---------|------------|
| **OpenAI API Key** | Adversarial evaluation (~$0.04 per evaluation) | [platform.openai.com](https://platform.openai.com/api-keys) |
| **Linear Integration** | Task sync with Linear issues | See [Linear Integration](#linear-integration) section below |

### Not sure if you have everythng you need?

Clone the repo and run this script to validate your environment:

```bash
agents/preflight
```

It will check all requirements and tell you what's missing.

---

## Quick Start

### 1. Clone the Repository

Open your terminal and navigate to where you keep projects (e.g., `~/Github` or `~/Projects`):

```bash
cd ~/Github
```

Then clone this starter kit, replacing `your-project-name` with your actual project name:

```bash
git clone https://github.com/movito/agentive-starter-kit.git your-project-name
cd your-project-name
```

For example, if you're building a weather app:
```bash
git clone https://github.com/movito/agentive-starter-kit.git weather-app
cd weather-app
```

This creates a new folder with everything inside. **Don't create the folder first** - the clone command does that for you.

Then open the folder in your IDE (VS Code, Cursor, etc.).

### 2. Run First-Time Onboarding

```bash
agents/onboarding
```

### 3. Follow Interactive Setup

The onboarding agent will guide you through:

1. **Project Configuration** - Name your project
2. **Language Selection** - Configure Serena for your languages
3. **API Keys** - Set up Anthropic, OpenAI, and Linear (optional)
4. **Feature Selection** - Enable evaluation, task sync, etc.
5. **First Task** - Create your first task to get started

**Important**: When asked for your project name, use the **same name** you chose for the folder (e.g., `weather-app`). Onboarding uses this to configure Serena and update agent files so they can navigate your codebase.

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
| `code-reviewer` | Reviews implementations for quality |
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

> **Note**: When Serena is configured, your browser may briefly open with the Serena dashboard when launching agents. This is normal behavior - you can close it and continue working in your terminal.

---

## Configuration

The **onboarding agent** handles all configuration automatically:

```bash
agents/onboarding
```

This guides you through setting up:
- Project name and task prefix
- Programming languages (for Serena)
- API keys (OpenAI, Linear)
- GitHub repository
- First task creation

If you prefer to handle setup yourself, copy these template files and configure manually:
- `.env.template` → `.env` (API keys)
- `.serena/project.yml.template` → `.serena/project.yml` (languages)
- `.adversarial/config.yml.template` → `.adversarial/config.yml` (evaluation settings)

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

Go to your Linear workspace settings:
`https://linear.app/{workspace}/settings/account/security`
(Replace `{workspace}` with your Linear workspace name, e.g., `ixda`)

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
- Adds GitHub links to task files in Linear issue descriptions

**Manual sync:**
```bash
./scripts/project linearsync
```

**Auto-sync:** Pushing to `main` or `develop` triggers GitHub Actions workflow.

**GitHub Actions setup:**
1. Go to your repo Settings → Secrets and variables → Actions
2. Add `LINEAR_API_KEY` secret
3. Add `LINEAR_TEAM_ID` secret (optional)

### Without Linear

Tasks work fine without Linear - they're just markdown files. Agents can create, track, and complete tasks using the folder structure alone. Linear adds team visibility and integrations, but isn't required.

---

## Usage

### First-Time Setup

```bash
# Run onboarding (first time only)
agents/onboarding
```

### Launching Agents (After Setup)

```bash
# Interactive menu
agents/launch

# Launch specific agent
agents/launch planner
agents/launch feature-developer
agents/launch test-runner
```

### Creating Tasks

**The easy way:** Just tell `planner` what you want to build. The agent will create and manage tasks for you.

```bash
agents/launch planner
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
- **Starter Kit ADRs**: `docs/decisions/starter-kit-adr/` (18 architectural decisions)
- **Your Project ADRs**: `docs/decisions/adr/` (start fresh here)

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
│   ├── decisions/
│   │   ├── starter-kit-adr/ # Starter kit ADRs (reference)
│   │   └── adr/             # Your project ADRs
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

## Pulling Updates from the Starter Kit

As we improve the starter kit, you can pull updates into your project:

```bash
# Add the starter kit as upstream (one time)
git remote add upstream https://github.com/movito/agentive-starter-kit.git

# Pull updates
git fetch upstream
git merge upstream/main

# Update agent files with your project name
./scripts/project reconfigure
```

The `reconfigure` command updates Serena activation calls in agent files after pulling upstream changes. It replaces any `activate_project("...")` value (whether it's the placeholder `"your-project"` or upstream's `"agentive-starter-kit"`) with your project name from `.serena/project.yml`.

**How merging works:**
- Files **only you changed** → your changes preserved
- Files **only upstream changed** → you get the updates
- Files **both changed** → merge conflict (you decide what to keep)

**Best practices for easy updates:**
- Keep customizations in **new files** when possible (new agents, new docs)
- Avoid heavily editing core starter kit files
- When you do edit core files, the merge is usually straightforward

**Your stuff stays safe:**
- Custom agents you created
- Your `.env` configuration (gitignored)
- Project-specific docs and tasks

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

**Version**: 0.2.2
**Last Updated**: 2025-12-06
