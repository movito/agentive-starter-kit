# Kit Migration Playbook

**Version**: 1.0.0
**Created**: 2026-03-30
**For**: Downstream repos adopting the `.kit/` builder layer from agentive-starter-kit v0.5.0+

---

## What This Is

A guide for agents migrating downstream repos to the `.kit/` directory layout. This is
not a script — every repo has its own quirks. Read the guide, survey the repo, adapt.

## Who Runs This

A feature-developer agent, launched in the downstream repo, with this playbook provided
as context. The agent should create a single feature branch and PR for the migration.

---

## The Target Layout

After migration, every kit repo should look like this:

```
your-project/
├── .adversarial/          # Evaluation (stays at root — CLI hardcodes path)
├── .claude/               # Implementation layer (stays — Claude Code constraint)
│   ├── agents/            #   agent definitions (synced from ASK via agents_core tier)
│   ├── commands/          #   slash commands (synced via commands_core tier)
│   └── skills/            #   implementation skills (synced via skills_core tier)
├── .dispatch/             # Coordination (stays at root — dispatch-kit hardcodes path)
├── .kit/                  # Builder layer (NEW — synced via kit_builder tier)
│   ├── adr/               #   kit architectural decisions (from docs/decisions/starter-kit-adr/)
│   ├── context/           #   handoffs, reviews, workflows, patterns (from .agent-context/)
│   │   ├── reviews/       #     evaluator review output
│   │   ├── retros/        #     retrospective output
│   │   ├── templates/     #     review-starter template, etc.
│   │   └── workflows/     #     COMMIT-PROTOCOL, TESTING-WORKFLOW, etc.
│   ├── docs/              #   builder documentation
│   ├── launchers/         #   launch, onboarding, preflight scripts (from agents/ at root)
│   ├── skills/            #   builder-only skills (self-review, review-handoff, etc.)
│   ├── tasks/             #   task specs (from delegation/tasks/)
│   │   ├── 1-backlog/
│   │   ├── 2-todo/
│   │   ├── 3-in-progress/
│   │   ├── 4-in-review/
│   │   ├── 5-done/
│   │   ├── 6-canceled/
│   │   ├── 7-blocked/
│   │   ├── 8-archive/
│   │   └── 9-reference/
│   └── templates/         #   agent + task templates (from .claude/agents/AGENT-TEMPLATE.md etc.)
├── .serena/               # LSP config (stays at root — Serena hardcodes path)
├── docs/                  # Project documentation
│   └── adr/               #   project architectural decisions (from docs/decisions/adr/)
├── scripts/
│   ├── core/              #   synced from starter kit (may need restructure first)
│   ├── local/             #   project-specific
│   └── optional/          #   opt-in
├── src/                   # Your code
└── tests/                 # Your tests
```

### What does NOT move

| Directory | Why it stays |
|-----------|-------------|
| `.adversarial/` | CLI hardcodes path (ADV-0053 tracks fix) |
| `.dispatch/` | dispatch-kit hardcodes path |
| `.serena/` | Serena hardcodes path |
| `.claude/` | Claude Code resolution constraint |
| `.pre-commit-config.yaml` | Standard location |
| `.github/` | GitHub convention |

---

## Pre-Flight: Survey the Repo

Before moving anything, the agent MUST survey the repo to understand what exists.
Run these checks and record the results:

### 1. Identify current layout

```bash
# What directories exist?
ls -1d delegation/ .agent-context/ agents/ docs/decisions/ 2>/dev/null

# What's in delegation/?
ls -R delegation/ 2>/dev/null | head -40

# What's in .agent-context/?
ls .agent-context/ | head -30

# Launchers at root?
ls agents/launch agents/onboarding agents/preflight 2>/dev/null

# Templates mixed into .claude/agents/?
ls .claude/agents/AGENT-TEMPLATE.md .claude/agents/TASK-STARTER-TEMPLATE.md .claude/agents/OPERATIONAL-RULES.md 2>/dev/null

# Scripts already restructured?
ls scripts/core/ 2>/dev/null | head -5
cat scripts/.core-manifest.json 2>/dev/null | head -5

# ADR layout?
ls docs/decisions/ 2>/dev/null
ls docs/decisions/adr/ docs/decisions/starter-kit-adr/ 2>/dev/null | head -10
```

### 2. Count path references (estimate rewrite scope)

```bash
# These counts tell you how big the rewrite is
grep -r 'delegation/' --include='*.md' --include='*.yml' --include='*.json' --include='*.sh' --include='*.py' -l | grep -v '.git/' | grep -v '.venv/' | wc -l
grep -r '\.agent-context/' --include='*.md' --include='*.yml' --include='*.json' --include='*.sh' --include='*.py' -l | grep -v '.git/' | grep -v '.venv/' | wc -l
grep -r 'docs/decisions/' --include='*.md' --include='*.yml' --include='*.json' --include='*.sh' --include='*.py' -l | grep -v '.git/' | grep -v '.venv/' | wc -l
```

### 3. Check for repo-specific extras

Look for things not in the standard layout:
- `delegation/handoffs/` (old handoff location — some repos have this)
- `delegation/tasks/evaluations/` (ADV has this)
- `agents/` at root (launcher scripts — all repos have this)
- `tasks/` at root (ADV has stale task files here)
- `audit-results/`, `htmlcov/`, `.vscode/`, `.nova/` (build artifacts, IDE config)
- `.aider.chat.history.md`, `.aider.input.history` (aider history, gitignored)
- `SETUP.md`, `QUICK_START.md`, `UPGRADE.md` at root (may need relocation)

---

## Migration Steps

### Prerequisites

The scripts restructure (ASK-0042 pattern: `scripts/core/` + `local/` + `optional/`)
should ideally be done first, but is not strictly required. If `scripts/` is still flat,
note it but proceed — the sync workflow will handle it on next sync.

Check if there's already a task for the scripts restructure (e.g., DSP-0067, AEL-0012).
If so, do that task first or combine.

### Step 1: Create the `.kit/` skeleton

```bash
mkdir -p .kit/{adr,context/{reviews,retros,templates,workflows},docs,launchers,skills,tasks/{1-backlog,2-todo,3-in-progress,4-in-review,5-done,6-canceled,7-blocked,8-archive,9-reference},templates}
```

### Step 2: Move tasks

```bash
# Move task files (preserve git history)
git mv delegation/tasks/1-backlog/* .kit/tasks/1-backlog/ 2>/dev/null
git mv delegation/tasks/2-todo/* .kit/tasks/2-todo/ 2>/dev/null
git mv delegation/tasks/3-in-progress/* .kit/tasks/3-in-progress/ 2>/dev/null
git mv delegation/tasks/4-in-review/* .kit/tasks/4-in-review/ 2>/dev/null
git mv delegation/tasks/5-done/* .kit/tasks/5-done/ 2>/dev/null
git mv delegation/tasks/6-canceled/* .kit/tasks/6-canceled/ 2>/dev/null
git mv delegation/tasks/7-blocked/* .kit/tasks/7-blocked/ 2>/dev/null
git mv delegation/tasks/8-archive/* .kit/tasks/8-archive/ 2>/dev/null
git mv delegation/tasks/9-reference/* .kit/tasks/9-reference/ 2>/dev/null

# Move delegation/tasks/README.md if present
git mv delegation/tasks/README.md .kit/tasks/ 2>/dev/null

# Move delegation/tasks/evaluations/ if present (ADV-specific)
git mv delegation/tasks/evaluations .kit/tasks/ 2>/dev/null
```

**After moving**: Check for empty `delegation/tasks/*/` directories and remove them.

### Step 3: Move handoffs and context

```bash
# Move .agent-context/ contents to .kit/context/
# First, move the structured subdirectories
git mv .agent-context/workflows/* .kit/context/workflows/ 2>/dev/null
git mv .agent-context/reviews/* .kit/context/reviews/ 2>/dev/null
git mv .agent-context/retros/* .kit/context/retros/ 2>/dev/null
git mv .agent-context/templates/* .kit/context/templates/ 2>/dev/null

# Then move remaining files (handoffs, review starters, session state, etc.)
git mv .agent-context/*.md .kit/context/ 2>/dev/null
git mv .agent-context/*.json .kit/context/ 2>/dev/null

# Move delegation/handoffs/ if it exists (old layout — some repos)
git mv delegation/handoffs/* .kit/context/ 2>/dev/null
```

**Watch for**: `.agent-context/README.md`, `.agent-context/REVIEW-INSIGHTS.md`,
`.agent-context/agent-handoffs.json` — these should all move to `.kit/context/`.

### Step 4: Move launchers

```bash
# Move agents/launch, agents/onboarding, agents/preflight to .kit/launchers/
git mv agents/launch .kit/launchers/ 2>/dev/null
git mv agents/onboarding .kit/launchers/ 2>/dev/null
git mv agents/preflight .kit/launchers/ 2>/dev/null
```

**After moving**: If `agents/` is now empty, remove it with `git rm -r agents/`.
If it has other files, investigate what they are.

### Step 5: Move templates out of `.claude/agents/`

```bash
# These are templates, not agent definitions — move to .kit/templates/
git mv .claude/agents/AGENT-TEMPLATE.md .kit/templates/ 2>/dev/null
git mv .claude/agents/TASK-STARTER-TEMPLATE.md .kit/templates/ 2>/dev/null
git mv .claude/agents/OPERATIONAL-RULES.md .kit/templates/ 2>/dev/null
```

### Step 6: Flatten ADR directories

```bash
# Project ADRs: docs/decisions/adr/ → docs/adr/
if [ -d "docs/decisions/adr" ]; then
  mkdir -p docs/adr
  git mv docs/decisions/adr/* docs/adr/ 2>/dev/null
fi

# Kit ADRs: docs/decisions/starter-kit-adr/ → .kit/adr/
if [ -d "docs/decisions/starter-kit-adr" ]; then
  git mv docs/decisions/starter-kit-adr/* .kit/adr/ 2>/dev/null
fi

# Clean up empty docs/decisions/ if both moved
# Check for other contents first!
ls docs/decisions/ 2>/dev/null
```

**Important**: Some repos have `docs/decisions/archive/` or other subdirectories.
Don't blindly delete `docs/decisions/` — check what's left.

### Step 7: Clean up old directories

```bash
# Remove empty old directories
git rm -r delegation/ 2>/dev/null    # only if completely empty
git rm -r .agent-context/ 2>/dev/null # only if completely empty
git rm -r agents/ 2>/dev/null         # only if completely empty (launchers moved)
```

**Do NOT force-remove non-empty directories.** If something is left, investigate.

### Step 8: Update `.dispatch/config.yml`

If the repo uses dispatch-kit, update the paths:

```yaml
# Old:
interfaces:
  starter_dir: .agent-context/
  task_dir: delegation/tasks/

# New:
interfaces:
  starter_dir: .kit/context/
  task_dir: .kit/tasks/
```

### Step 9: Rewrite path references

This is the biggest step. Use `find` + `sed` for bulk replacement, then manually
verify files that need context-aware edits.

**Path replacements (in order — order matters for overlapping patterns):**

| Old pattern | New pattern | Notes |
|-------------|-------------|-------|
| `delegation/tasks/` | `.kit/tasks/` | Most common |
| `delegation/handoffs/` | `.kit/context/` | Old handoff location |
| `delegation/` | `.kit/tasks/` | Catch remaining (verify context) |
| `.agent-context/workflows/` | `.kit/context/workflows/` | Workflow docs |
| `.agent-context/reviews/` | `.kit/context/reviews/` | Review output |
| `.agent-context/retros/` | `.kit/context/retros/` | Retro output |
| `.agent-context/templates/` | `.kit/context/templates/` | Templates |
| `.agent-context/` | `.kit/context/` | Catch remaining |
| `docs/decisions/starter-kit-adr/` | `.kit/adr/` | Kit ADRs |
| `docs/decisions/adr/` | `docs/adr/` | Project ADRs |
| `docs/decisions/` | `docs/adr/` | Catch remaining (verify context) |
| `agents/launch` | `.kit/launchers/launch` | Launcher references |
| `agents/onboarding` | `.kit/launchers/onboarding` | Launcher references |
| `agents/preflight` | `.kit/launchers/preflight` | Launcher references |

**Bulk sed command:**

```bash
find . -type f \( -name "*.md" -o -name "*.yml" -o -name "*.yaml" \
  -o -name "*.json" -o -name "*.sh" -o -name "*.py" \
  -o -name ".gitignore" -o -name ".coderabbitignore" \) \
  -not -path "./.git/*" -not -path "./.venv/*" -not -path "./venv/*" \
  -exec sed -i '' \
    -e 's|delegation/tasks/|.kit/tasks/|g' \
    -e 's|delegation/handoffs/|.kit/context/|g' \
    -e 's|\.agent-context/workflows/|.kit/context/workflows/|g' \
    -e 's|\.agent-context/reviews/|.kit/context/reviews/|g' \
    -e 's|\.agent-context/retros/|.kit/context/retros/|g' \
    -e 's|\.agent-context/templates/|.kit/context/templates/|g' \
    -e 's|\.agent-context/|.kit/context/|g' \
    -e 's|docs/decisions/starter-kit-adr/|.kit/adr/|g' \
    -e 's|docs/decisions/adr/|docs/adr/|g' \
    -e 's|agents/launch|.kit/launchers/launch|g' \
    -e 's|agents/onboarding|.kit/launchers/onboarding|g' \
    -e 's|agents/preflight|.kit/launchers/preflight|g' \
    {} +
```

**After sed — CRITICAL VERIFICATION:**

```bash
# Check for stale references that sed missed
grep -r 'delegation/' --include='*.md' --include='*.yml' --include='*.json' --include='*.sh' --include='*.py' . | grep -v '.git/' | grep -v '.venv/' | grep -v '.kit/tasks/'

grep -r '\.agent-context/' --include='*.md' --include='*.yml' --include='*.json' --include='*.sh' --include='*.py' . | grep -v '.git/' | grep -v '.venv/'

grep -r 'docs/decisions/' --include='*.md' --include='*.yml' --include='*.json' --include='*.sh' --include='*.py' . | grep -v '.git/' | grep -v '.venv/'
```

Any remaining references need manual attention. Common cases:
- **Historical references** in retros, changelogs, commit messages: leave as-is
- **Python code** referencing `delegation/` paths: update carefully (check logic)
- **`.claude/settings.local.json`** permission patterns: update path globs
- **`.dispatch/config.yml`**: already handled in Step 8, but verify
- **CLAUDE.md**: update directory structure section

### Step 10: Update CLAUDE.md

The repo's `CLAUDE.md` needs its directory structure and key references updated.
Use ASK's `CLAUDE.md` as reference for the new layout.

### Step 11: Update `.gitignore`

Add/update entries for `.kit/`:

```gitignore
# Kit artifacts (logs, evaluator output)
# These should already be covered by .adversarial/ entries
# but add if tasks have gitignored content:
# .kit/tasks/evaluations/  (if applicable)
```

### Step 12: Update `validate_task_status.py` (pre-commit hook)

The task status validator looks for task files. Update its path:

```python
# Old:
TASK_DIR = "delegation/tasks"

# New:
TASK_DIR = ".kit/tasks"
```

Check `scripts/core/validate_task_status.py` and `.pre-commit-config.yaml` for
hardcoded paths.

### Step 13: Update Linear sync paths

If the repo uses Linear sync, update:
- `scripts/core/project` or `scripts/project` — task directory path
- `scripts/optional/sync_tasks_to_linear.py` — task directory path
- `.github/workflows/sync-tasks.yml` — path triggers

---

## Post-Migration Verification

### 1. Run tests

```bash
pytest tests/ -v
```

### 2. Run pre-commit hooks

```bash
git add -A
pre-commit run --all-files
```

### 3. Verify evaluator works (if configured)

```bash
adversarial list-evaluators
# If evaluators are installed, run one:
adversarial evaluate --evaluator arch-review-fast .kit/tasks/1-backlog/SOME-TASK.md
```

### 4. Verify no stale references

```bash
# These should return zero results (excluding historical/changelog content):
grep -rn 'delegation/tasks/' --include='*.md' --include='*.py' --include='*.sh' --include='*.yml' --include='*.json' . | grep -v '.git/' | grep -v '.venv/' | grep -v CHANGELOG | grep -v '5-done/' | grep -v '8-archive/'

grep -rn '\.agent-context/' --include='*.md' --include='*.py' --include='*.sh' --include='*.yml' --include='*.json' . | grep -v '.git/' | grep -v '.venv/' | grep -v CHANGELOG
```

### 5. Verify dispatch config (if applicable)

```bash
cat .dispatch/config.yml | grep -E 'task_dir|starter_dir'
# Should show .kit/tasks/ and .kit/context/
```

### 6. Check CI

```bash
./scripts/core/ci-check.sh  # or ./scripts/ci-check.sh if not restructured yet
```

---

## Known Variance by Repo

### adversarial-workflow (ADV)

| Item | State | Action |
|------|-------|--------|
| Scripts restructure | Done (scripts/core/) | No action |
| Manifest format | Old (flat array, v1.2.0) | Will be updated by next sync |
| `delegation/tasks/evaluations/` | Exists | Move to `.kit/tasks/evaluations/` |
| `tasks/` at root | Stale file(s) | Investigate, likely delete |
| `audit-results/` at root | Build artifact | Add to `.gitignore` or delete |
| `agents/` at root | Launchers only | Move to `.kit/launchers/` |
| `.vscode/` | IDE config | Leave alone |
| `SETUP.md`, `QUICK_START.md`, `UPGRADE.md` | Root docs | Leave or move to `docs/` |
| `delegation/` ref count | ~177 files | Large rewrite |
| `.agent-context/` ref count | ~109 files | Large rewrite |
| Project-specific agents | `pypi-publisher.md`, `feature-developer-sonnet.md`, `feature-developer-v4.md` | Leave in `.claude/agents/` |
| `docs/decisions/archive/` | Exists | Move to `.kit/adr/archive/` or `docs/archive/` |

### dispatch-kit (DSP)

| Item | State | Action |
|------|-------|--------|
| Scripts restructure | NOT done (flat scripts/) | Do DSP-0067 first or combine |
| Manifest format | Missing | Will be created by sync |
| `agents/` at root | Launchers only | Move to `.kit/launchers/` |
| `.nova/` at root | Nova IDE config | Leave alone |
| `delegation/handoffs/` | Empty dir | Remove |
| DSP-specific agents | `bot-watcher.md`, `bus-debugger.md`, `config-validator.md`, `integration-tester.md`, `planner-chrome.md`, `feature-developer2.md`, `feature-developer-v2.md`, `feature-developer-v4.md` | Leave in `.claude/agents/` |
| `delegation/` ref count | ~505 files | Very large rewrite |
| `.agent-context/` ref count | ~478 files | Very large rewrite |
| `docs/` has project docs mixed with builder docs | tmux-tips, architecture, etc. | Sort into docs/ vs .kit/docs/ |
| `docs/decisions/starter-kit-adr/` | Exists | Move to `.kit/adr/` |
| `.agent-context/` has many session handovers | Historical files | Move all to `.kit/context/` |

### adversarial-evaluator-library (AEL)

| Item | State | Action |
|------|-------|--------|
| Scripts restructure | NOT done (flat scripts/) | Do AEL-0012 first or combine |
| Manifest format | Missing | Will be created by sync |
| `agents/` at root | Launchers only | Move to `.kit/launchers/` |
| AEL-specific agents | `tycho.md` | Leave in `.claude/agents/` |
| `delegation/` ref count | ~85 files | Moderate rewrite |
| `.agent-context/` ref count | ~83 files | Moderate rewrite |
| `docs/decisions/starter-kit-adr/` | Exists | Move to `.kit/adr/` |
| `.agent-context/` has ASK-prefixed handoffs | Cross-pollination from early days | Move to `.kit/context/`, leave as-is |
| No `.dispatch/` | Not a dispatch-kit user | Skip Step 8 |

---

## Anti-Patterns to Avoid

1. **Don't split into multiple PRs.** Structural migrations must land atomically.
   A half-migrated repo where some paths point to `delegation/` and others to
   `.kit/tasks/` is worse than the old layout. (Lesson from ASK-0044.)

2. **Don't grep only full paths.** `grep -r 'delegation/tasks/'` misses bare
   references like `"delegation"` in array literals or exclude lists. Also grep
   for bare directory names: `delegation`, `agent-context`, `decisions`. (Lesson
   from ASK-0047.)

3. **Don't trust sed for everything.** Sed handles the bulk, but some files need
   context-aware edits (Python code, JSON, YAML indentation). Verify after sed.

4. **Don't move `.adversarial/` or `.dispatch/`.** Their CLIs hardcode the path.
   This has been tried and reverted. Leave them at root.

5. **Don't delete historical references.** Retros, changelogs, completed task
   files, and archived handoffs should keep their original paths in prose. Only
   update paths that are used for navigation or execution.

6. **Don't forget `.claude/settings.local.json`.** This file contains permission
   allow-list entries with hardcoded paths. It's gitignored but exists locally.
   Update the path patterns or the agent will hit permission prompts.

7. **Don't forget `validate_task_status.py`.** The pre-commit hook that validates
   task status fields has a hardcoded task directory path.

---

## After Migration

Once the PR merges:

1. **Future syncs from ASK will maintain `.kit/`.** The `kit_builder` tier in the
   manifest already syncs `.kit/` contents.

2. **Run `./scripts/core/project reconfigure`** (if available) to update any
   remaining identity leaks from the starter kit name.

3. **Update the repo's CLAUDE.md** to reflect the new layout.

4. **Linear sync** (if configured) will pick up the new task paths on next run.

---

## Reference

- **ASK-0044**: The original builder/project separation PR (agentive-starter-kit #41)
- **ASK-0047**: ADR directory flattening PR (#42)
- **KIT-ADR-0023**: Builder-project separation boundary definition
- **agentive-starter-kit v0.5.0**: First release with full `.kit/` layout
- **REVIEW-INSIGHTS.md**: Anti-patterns section has lessons from ASK-0044/0047
