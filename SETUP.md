# Setup Guide

This guide walks you through setting up the Agentive Starter Kit for your project.

---

## Prerequisites

Before you begin, ensure you have:

1. **Claude Code** installed and authenticated
   - Download: https://claude.com/claude-code
   - Sign in with your Anthropic account

2. **Python 3.9+** installed
   ```bash
   python3 --version  # Should be 3.9 or higher
   ```

3. **Git** installed and configured
   ```bash
   git --version
   ```

4. **API Keys** (optional but recommended):
   - **OpenAI API Key** for adversarial evaluation
     - Get at: https://platform.openai.com/api-keys
   - **Linear API Key** for task synchronization
     - Get at: https://linear.app/settings/api

---

## Setup Options

### Option A: Interactive Setup (Recommended)

Run the onboarding script to launch `planner` with full setup context:

```bash
./agents/onboarding
```

`planner` will help you:
1. Configure your project name
2. Select programming languages
3. Set up API keys
4. Enable optional features
5. Create your first task

### Option B: Manual Setup

If you prefer to configure manually:

#### Step 1: Copy Environment Template

```bash
cp .env.template .env
```

Edit `.env` and add your API keys:

```bash
# For adversarial evaluation
OPENAI_API_KEY=sk-your-openai-key

# For Linear sync (optional)
LINEAR_API_KEY=lin_api_your-linear-key
LINEAR_TEAM_ID=your-team

# Project configuration
PROJECT_NAME=my-project
TASK_PREFIX=TASK
```

#### Step 2: Install & Configure Serena

Serena provides semantic code navigation (go-to-definition, find-references, symbol search).

**Prerequisites**: You need either `uvx` (recommended) or `pipx`:

```bash
# Install uv (includes uvx)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or install pipx
brew install pipx && pipx ensurepath
```

**Run the setup script:**

```bash
./.serena/setup-serena.sh my-project
```

This will:
1. Add Serena MCP to Claude Code configuration
2. Create `.serena/project.yml` from template

**Enable your languages** in `.serena/project.yml`:

```yaml
project_name: "my-project"
languages:
  - python        # Uncomment languages you use
  # - typescript
  # - swift
```

**Verify Serena is configured:**

```bash
claude mcp list | grep serena
```

**Note**: If you skip Serena setup, agents will still work but without semantic code navigation.

#### Step 3: Configure Adversarial Workflow

```bash
cp .adversarial/config.yml.template .adversarial/config.yml
```

The defaults are usually fine. Edit if needed.

#### Step 4: Initialize Git (if not cloned)

```bash
git init
git add .
git commit -m "Initial commit from agentive-starter-kit"
```

#### Step 5: Install Pre-commit Hooks

```bash
pip install pre-commit
pre-commit install
```

#### Step 6: Verify Setup

```bash
# Test agent launcher
./agents/launch help

# Test pre-commit hooks
git commit --allow-empty -m "Test hooks"
```

---

## API Key Setup Details

### Anthropic API Key

**When needed**: Only if you want programmatic API access outside Claude Code.

**Claude Code users**: You're already authenticated via your claude.ai account. Skip this unless you need direct API access.

**To get a key**:
1. Go to https://console.anthropic.com/settings/keys
2. Click "Create Key"
3. Copy the key (starts with `sk-ant-`)
4. Add to `.env` as `ANTHROPIC_API_KEY`

### OpenAI API Key

**When needed**: For adversarial evaluation (GPT-4o reviews your task specs).

**Cost**: ~$0.04-0.08 per evaluation. A typical task has 2-3 evaluations.

**To get a key**:
1. Go to https://platform.openai.com/api-keys
2. Click "Create new secret key"
3. Copy the key (starts with `sk-`)
4. Add to `.env` as `OPENAI_API_KEY`

**Testing**:
```bash
# Create a test task
cat > delegation/tasks/2-todo/TASK-0001-test.md << 'EOF'
# TASK-0001: Test Task

**Status**: Todo
**Priority**: low

## Overview
Test task to verify evaluation system works.

## Requirements
- [ ] Test requirement 1
- [ ] Test requirement 2
EOF

# Run evaluation
adversarial evaluate delegation/tasks/2-todo/TASK-0001-test.md
```

### Linear API Key

**When needed**: For synchronizing tasks with Linear issues.

**To get a key**:
1. Go to https://linear.app/settings/api
2. Click "Create new API key"
3. Copy the key (starts with `lin_api_`)
4. Add to `.env` as `LINEAR_API_KEY`

**Team ID**: Find at linear.app/YOUR-TEAM - the "YOUR-TEAM" part is your team ID.

---

## Language-Specific Setup

### Python Projects

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install development dependencies
pip install pytest pytest-cov pre-commit black isort flake8

# Install pre-commit hooks
pre-commit install
```

### TypeScript/JavaScript Projects

```bash
# Initialize npm
npm init -y

# Install dependencies
npm install --save-dev typescript jest @types/jest ts-jest

# For Serena LSP support
npm install -g typescript-language-server typescript
```

### Swift Projects

```bash
# Ensure Xcode Command Line Tools installed
xcode-select --install

# sourcekit-lsp is included with Xcode
# Verify it's available
xcrun sourcekit-lsp --help
```

---

## Verification Checklist

After setup, verify each component:

### Agents
- [ ] `./agents/launch` shows agent menu
- [ ] `./agents/launch planner` starts planner agent
- [ ] Serena activates when agent starts

### Task Management
- [ ] Task folders exist (1-backlog through 9-reference)
- [ ] Task template is at `delegation/tasks/9-reference/templates/task-template.md`

### Evaluation (if configured)
- [ ] `.env` contains `OPENAI_API_KEY`
- [ ] `adversarial evaluate` command runs
- [ ] Results appear in `.adversarial/logs/`

### Pre-commit Hooks
- [ ] `git commit` triggers hooks
- [ ] Tests run before commit completes

---

## Troubleshooting

### Agent won't start

```bash
# Check Claude Code is installed
claude --version

# Verify launch scripts are executable
chmod +x agents/launch agents/onboarding
```

### Serena won't activate

```bash
# Check project.yml exists
cat .serena/project.yml

# Verify LSP server is installed for your language
# Python: pip install python-lsp-server
# TypeScript: npm install -g typescript-language-server
```

### Evaluation fails

```bash
# Check API key is set
echo $OPENAI_API_KEY

# Check aider is installed
pip install aider-chat

# Try running aider directly
aider --help
```

### Pre-commit hooks not running

```bash
# Reinstall hooks
pre-commit uninstall
pre-commit install

# Run manually
pre-commit run --all-files
```

---

## Next Steps

After setup:

1. **Create Your First Task**
   - Copy `delegation/tasks/9-reference/templates/task-template.md`
   - Save as `delegation/tasks/2-todo/TASK-0001-your-task.md`
   - Fill in the details

2. **Run Evaluation** (if configured)
   - `adversarial evaluate delegation/tasks/2-todo/TASK-0001-your-task.md`
   - Review feedback in `.adversarial/logs/`

3. **Assign to Agent**
   - Launch `planner`
   - Discuss the task and get it assigned

4. **Read the Guide**
   - `docs/agentive-development/README.md` - Full methodology
   - `docs/agentive-development/00-introduction.md` - Philosophy

---

## Getting Help

- **Agent Issues**: Ask `planner` for help
- **Setup Issues**: Check troubleshooting above
- **Methodology Questions**: See `docs/agentive-development/`
- **Bug Reports**: https://github.com/movito/agentive-starter-kit/issues

---

**Setup Guide Version**: 1.0.0
