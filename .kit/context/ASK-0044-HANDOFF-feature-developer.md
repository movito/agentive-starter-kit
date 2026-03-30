# ASK-0044: Builder/Project Separation — Implementation Handoff (PR 1 of 3)

**You are the feature-developer. Implement this task directly. Do not delegate or spawn other agents.**

**Date**: 2026-03-28
**From**: Planner (planner2)
**To**: feature-developer-v5
**Task**: `.kit/tasks/2-todo/ASK-0044-separate-kit-internals.md`
**Status**: Ready for implementation
**Evaluation**: arch-review (o1) — APPROVED ($0.23)
**Scope**: PR 1 only — directory moves and path updates

---

## Task Summary

Create the `.kit/` directory and move all builder infrastructure into it. Update
every reference across agents, commands, skills, CLAUDE.md, and scripts. This is
the foundational PR — PRs 2 and 3 (sync manifest update, consumer template) follow.

## PR 1 Scope: Create `.kit/` and Move Builder Artifacts

### Step 1: Create `.kit/` directory structure

```
.kit/
├── delegation/           ← from delegation/
│   ├── tasks/            ← all task folders (1-backlog through 9-reference)
│   └── handoffs/
├── context/              ← from .kit/context/
│   ├── agent-handoffs.json
│   ├── current-state.json
│   ├── patterns.yml
│   ├── REVIEW-INSIGHTS.md
│   ├── workflows/
│   ├── reviews/
│   ├── retros/
│   └── templates/
├── adversarial/          ← from .kit/adversarial/
│   ├── config.yml
│   ├── config.yml.template
│   ├── docs/
│   ├── evaluators/
│   ├── inputs/
│   ├── logs/
│   ├── scripts/
│   └── templates/
├── decisions/            ← from .kit/decisions/
│   └── KIT-ADR-*.md
├── agents/               ← builder agents from .claude/agents/
│   ├── planner.md
│   ├── planner2.md
│   ├── tycho.md
│   ├── code-reviewer.md
│   ├── document-reviewer.md
│   ├── security-reviewer.md
│   ├── AGENT-TEMPLATE.md
│   ├── OPERATIONAL-RULES.md
│   └── TASK-STARTER-TEMPLATE.md
├── skills/               ← builder skills from .claude/skills/
│   ├── retro/
│   ├── review-handoff/
│   ├── code-review-evaluator/
│   └── self-review/
├── commands/             ← builder commands from .claude/commands/
│   ├── babysit-pr.md
│   ├── retro.md
│   ├── triage-threads.md
│   ├── status.md
│   ├── check-spec.md
│   └── wrap-up.md
├── launchers/            ← from agents/
│   ├── launch
│   ├── onboarding
│   └── preflight
└── docs/                 ← builder docs from docs/
    ├── TESTING.md
    ├── LINEAR-SYNC-BEHAVIOR.md
    └── UPGRADE-0.4.0.md
```

### Step 2: Move files with `git mv`

**IMPORTANT**: Use `git mv`, not `mv`, to preserve git history.

```bash
# Builder coordination
git mv delegation/ .kit/delegation/
git mv .kit/context/ .kit/context/

# Evaluator system
git mv .kit/adversarial/ .kit/adversarial/

# Kit ADRs (keep project ADRs in place)
mkdir -p .kit/decisions/
git mv .kit/decisions/KIT-ADR-*.md .kit/decisions/
# Keep .kit/decisions/README.md or remove empty dir

# Builder agents (move individually, leave implementation agents)
mkdir -p .kit/agents/
git mv .claude/agents/planner.md .kit/agents/
git mv .claude/agents/planner2.md .kit/agents/
git mv .claude/agents/tycho.md .kit/agents/
git mv .claude/agents/code-reviewer.md .kit/agents/
git mv .claude/agents/document-reviewer.md .kit/agents/
git mv .claude/agents/security-reviewer.md .kit/agents/
git mv .claude/agents/AGENT-TEMPLATE.md .kit/agents/
git mv .claude/agents/OPERATIONAL-RULES.md .kit/agents/
git mv .claude/agents/TASK-STARTER-TEMPLATE.md .kit/agents/

# Builder skills
mkdir -p .kit/skills/
git mv .claude/skills/retro/ .kit/skills/
git mv .claude/skills/review-handoff/ .kit/skills/
git mv .claude/skills/code-review-evaluator/ .kit/skills/
git mv .claude/skills/self-review/ .kit/skills/

# Builder commands
mkdir -p .kit/commands/
git mv .claude/commands/babysit-pr.md .kit/commands/
git mv .claude/commands/retro.md .kit/commands/
git mv .claude/commands/triage-threads.md .kit/commands/
git mv .claude/commands/status.md .kit/commands/
git mv .claude/commands/check-spec.md .kit/commands/
git mv .claude/commands/wrap-up.md .kit/commands/

# Launchers
mkdir -p .kit/launchers/
git mv agents/launch .kit/launchers/
git mv agents/onboarding .kit/launchers/
git mv agents/preflight .kit/launchers/

# Builder docs
mkdir -p .kit/docs/
git mv docs/TESTING.md .kit/docs/
git mv docs/LINEAR-SYNC-BEHAVIOR.md .kit/docs/
git mv docs/UPGRADE-0.4.0.md .kit/docs/
```

### Step 3: Update CLAUDE.md

Replace all old paths with `.kit/` paths. Key sections to update:

| Old Path | New Path |
|----------|----------|
| `.kit/tasks/` | `.kit/tasks/` |
| `.kit/context/` | `.kit/context/` |
| `.kit/adversarial/` | `.kit/adversarial/` |
| `.kit/decisions/` | `.kit/decisions/` |
| `.claude/agents/planner*.md` (etc.) | `.kit/agents/` |
| `agents/launch` | `.kit/launchers/launch` |

### Step 4: Update all agent definitions

Every agent that references old paths needs updating. Search and replace:

```bash
# Find all references to old paths in .claude/ and .kit/
grep -rn '.kit/context/' .claude/ .kit/agents/ .kit/commands/ .kit/skills/ CLAUDE.md
grep -rn '.kit/adversarial/' .claude/ .kit/agents/ .kit/commands/ .kit/skills/ CLAUDE.md
grep -rn '.kit/tasks/' .claude/ .kit/agents/ .kit/commands/ .kit/skills/ CLAUDE.md
grep -rn '.kit/decisions/' .claude/ .kit/agents/ .kit/commands/ .kit/skills/ CLAUDE.md
grep -rn 'agents/launch' .claude/ .kit/ CLAUDE.md
```

**This is the most error-prone step.** Be thorough. Every grep must return zero results
for old paths after updates.

### Step 5: Update scripts that reference old paths

```bash
grep -rn '.kit/context/' scripts/
grep -rn '.kit/adversarial/' scripts/
grep -rn '.kit/tasks/' scripts/
```

The `project` script references `.kit/tasks/` for task management. Update it.
The `validate_task_status.py` script references task folders. Update it.

### Step 6: Update pyproject.toml

Pre-commit hooks reference paths (e.g., `validate-task-status` hook). Update them.

### Step 7: Verify

```bash
# No old path references remain
grep -rn '\.kit/context/' --include='*.md' --include='*.py' --include='*.sh' --include='*.json' --include='*.yml' . | grep -v '.git/' | grep -v '.kit/'
grep -rn '\.kit/adversarial/' --include='*.md' --include='*.py' --include='*.sh' --include='*.json' --include='*.yml' . | grep -v '.git/' | grep -v '.kit/'

# CI passes
./scripts/core/ci-check.sh
```

## What Stays in Place (DO NOT MOVE)

- `.claude/agents/{feature-developer*,test-runner,powertest-runner,ci-checker,bootstrap,onboarding,agent-creator}.md`
- `.claude/commands/{check-ci,check-bots,wait-for-bots,start-task,commit-push-pr,preflight}.md`
- `.claude/skills/{pre-implementation,bot-triage}/`
- `.claude/settings.json`, `.claude/settings.local.json`
- `scripts/` (all of it — already well-separated)
- `tests/`
- `docs/decisions/adr/` (project ADRs)
- `.serena/`, `.github/`, root config files

## Known Risks

1. **Path reference count is high** — agents, commands, skills, CLAUDE.md, scripts,
   pyproject.toml all reference the old paths. Missing one means a broken workflow.
   The grep verification in Step 4-5 is your safety net.

2. **`scripts/core/project` is the most complex** — it manages task files in
   `.kit/tasks/`. Every task path reference must update to `.kit/tasks/`.

3. **`.kit/context/` files reference each other** — handoff files point to task files,
   review starters point to handoffs. Internal cross-references need updating too.

4. **Pre-commit hooks** — `validate-task-status` hook and any path-based hooks will break
   if not updated.

## Out of Scope (PR 2 and PR 3)

- Updating `.core-manifest.json` with `kit_builder` tier
- Updating sync Action with `is_kit` flag
- Consumer project bootstrap script
- Downstream kit adoption

## Acceptance Criteria (PR 1)

- [ ] `.kit/` directory exists with all builder artifacts
- [ ] No builder artifacts remain in old locations
- [ ] Implementation agents/commands/skills stay in `.claude/`
- [ ] CLAUDE.md uses `.kit/` paths throughout
- [ ] All agent/command/skill definitions reference `.kit/` paths
- [ ] `scripts/core/project` works with `.kit/tasks/`
- [ ] Pre-commit hooks pass
- [ ] `./scripts/core/ci-check.sh` green
- [ ] Zero grep hits for old paths (excluding `.git/` and `.kit/` internal references)

## Time Estimate

1.5 days:
- Directory moves: 1 hour
- CLAUDE.md rewrite: 1 hour
- Agent/command/skill path updates: 2-3 hours (many files, tedious)
- Script path updates: 1-2 hours (`project` is complex)
- Verification and CI: 1-2 hours

---

**Task File**: `.kit/tasks/2-todo/ASK-0044-separate-kit-internals.md`
**ADR**: `.kit/decisions/KIT-ADR-0023-builder-project-separation.md`
**Evaluation Log**: `.kit/adversarial/logs/ASK-0044-separate-kit-internals--arch-review.md`
**Handoff Date**: 2026-03-28
**Coordinator**: Planner (planner2)
