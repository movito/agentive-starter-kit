# KIT-ADR-0023: Builder/Project Separation — The `.kit/` Boundary

**Status**: Proposed
**Date**: 2026-03-28
**Author**: Planner Agent + User
**Supersedes**: None
**Related**: KIT-ADR-0022 (Manifest-Based Sync Ownership), ASK-0044, GitHub #35

## Context

Every project built with agentive-starter-kit inherits the full "builder" layer:
planning agents, task management, evaluators, ADRs, review workflows, coordination
state. This infrastructure is about *how we work on* a project, not *what the project
does*. The two concerns are currently fused into every repo.

### The Problem

1. **New projects inherit builder noise**: A fresh project gets 18 agent definitions,
   22 ADRs, 45+ handoff files, evaluator configs, and task folders — none of which
   are the project's own code.

2. **Sync is a judgment call**: When syncing from agentive-starter-kit to downstream
   projects, every file requires manual triage: "Is this builder infrastructure or
   project content?" (See adversarial-workflow PR #42: 56 files updated, manual triage.)

3. **Builder fixes require context-switching**: When a planner workflow or evaluator
   needs fixing, you stop work on the actual project, switch to one of the kits,
   fix it there, and switch back. The builder tools live *inside* the thing being built.

4. **No "thick client"**: There's no external workspace from which to plan and
   coordinate. Every project is its own self-contained workbench, duplicating the
   same builder machinery.

### Long-Term Vision

A **project workspace** (`~/Github/workspace/` or similar) that holds the builder
layer: planning agents, task management, evaluators, ADRs, coordination state.
Projects are clean repos with just code, tests, CI, and a thin `.claude/` for
implementation-time commands.

Working from the workspace, you plan and coordinate. Working from the project repo,
you implement. The builder tools are authored and maintained in one place.

### Why Not Jump Straight to the Workspace?

Claude Code's context model is directory-rooted. Memory, agents, commands, and tasks
resolve relative to the working directory. A workspace at `~/.agentive/` would lose
per-project context unless we solve the multi-project context problem first. That's
a larger design effort.

### This ADR's Scope

Establish the **boundary** between builder and project content via a `.kit/` directory.
This is the prerequisite for any future extraction — you can't lift out the builder
layer if you don't know exactly what it contains.

## Decision

### 1. Create `.kit/` as the Builder Layer Root

All builder infrastructure moves under `.kit/`:

```
.kit/                              ← Builder layer (the "how I work" stuff)
├── delegation/                    ← Task management (tasks/, handoffs/)
│   └── tasks/                     ← 1-backlog/ through 9-reference/
├── context/                       ← Coordination state (was .agent-context/)
│   ├── agent-handoffs.json
│   ├── current-state.json
│   ├── patterns.yml
│   ├── workflows/
│   ├── reviews/
│   ├── retros/
│   ├── templates/
│   └── REVIEW-INSIGHTS.md
├── adversarial/                   ← Evaluator system (was .adversarial/)
│   ├── config.yml
│   ├── docs/
│   ├── evaluators/
│   ├── inputs/
│   ├── logs/
│   └── scripts/
├── decisions/                     ← ADRs (was .kit/adr/)
│   └── KIT-ADR-*.md
├── agents/                        ← Builder agents (planner, coordinator, etc.)
│   ├── planner.md
│   ├── planner2.md
│   ├── tycho.md
│   ├── code-reviewer.md
│   ├── document-reviewer.md
│   ├── security-reviewer.md
│   ├── AGENT-TEMPLATE.md
│   ├── OPERATIONAL-RULES.md
│   └── TASK-STARTER-TEMPLATE.md
├── skills/                        ← Builder skills (retro, review-handoff, etc.)
│   ├── retro/
│   ├── review-handoff/
│   ├── code-review-evaluator/
│   └── self-review/
├── commands/                      ← Builder commands (workflow-only)
│   ├── babysit-pr.md
│   ├── retro.md
│   ├── triage-threads.md
│   ├── status.md
│   ├── check-spec.md
│   └── wrap-up.md
└── docs/                          ← Builder documentation
    ├── TESTING.md
    ├── LINEAR-SYNC-BEHAVIOR.md
    └── UPGRADE-0.4.0.md
```

### 2. Project Layer Stays in Standard Locations

```
.claude/                           ← Implementation-time agents and commands
├── agents/
│   ├── feature-developer.md       ← Implementation agents only
│   ├── feature-developer-v3.md
│   ├── feature-developer-v5.md
│   ├── test-runner.md
│   ├── powertest-runner.md
│   ├── ci-checker.md
│   ├── bootstrap.md
│   └── onboarding.md
├── commands/
│   ├── check-ci.md                ← Implementation commands only
│   ├── check-bots.md
│   ├── wait-for-bots.md
│   ├── start-task.md
│   ├── commit-push-pr.md
│   └── preflight.md
├── skills/
│   ├── pre-implementation/
│   └── bot-triage/
├── settings.json
└── settings.local.json

scripts/                           ← Stays as-is (already well-separated)
├── core/                          ← Synced to downstream
├── local/                         ← Project-specific
└── optional/                      ← Opt-in

tests/                             ← Project tests
src/                               ← Project source (if applicable)
docs/adr/                ← Project ADRs (not kit ADRs)
```

### 3. Classification Principle

**Ask one question**: "Does a downstream project that *uses* this kit need this file
to *build its own product*?"

- **Yes** → Project layer (`.claude/`, `scripts/`, `tests/`)
- **No, it's about planning/coordinating/evaluating** → Builder layer (`.kit/`)

### 4. Versioning via Manifest Tier

`.kit/` is synced between the 4 kits using the existing tiered manifest (KIT-ADR-0022)
with a new `kit_builder` tier. Consumer projects never receive `kit_builder` content.

```yaml
# Sync workflow matrix
strategy:
  matrix:
    include:
      - repo: movito/dispatch-kit
        is_kit: true        # receives kit_builder tier
      - repo: movito/adversarial-workflow
        is_kit: true
      - repo: movito/adversarial-evaluator-library
        is_kit: true
      # Consumer projects would have is_kit: false (or not be listed)
```

| Manifest Tier | Synced to kits | Synced to consumers |
|---------------|---------------|-------------------|
| `scripts_core` | Yes | Yes |
| `commands_core` | Yes | Yes |
| `commands_optional` | If opted in | If opted in |
| `kit_builder` | Yes | **Never** |

**What `kit_builder` syncs**: Templates, reusable configs, evaluator definitions,
workflow docs, builder agents/skills/commands, kit ADRs, launcher scripts.

**What `kit_builder` does NOT sync**: Task histories, handoffs, retros, reviews,
evaluation logs, `current-state.json`, `agent-handoffs.json`. These are per-project
state, not shared infrastructure.

### 5. Boundary Rules

| Rule | Rationale |
|------|-----------|
| `.kit/` is synced to **kit repos only** via `kit_builder` manifest tier | Builder infrastructure shared between kits, not consumers |
| `.kit/` is **gitignored in consumer** projects | New projects don't inherit builder noise |
| `.kit/` **exists in the 4 kits** | The kits are both tools and workbenches |
| CLAUDE.md references `.kit/` paths | So agents can find builder tools when working in a kit |
| `kit_builder` items are versioned with `scripts/core/VERSION` | Single version across all synced content |

### 5. Straddlers (Files That Serve Both Roles)

Some files are used during both planning and implementation:

| File | Current | Decision | Rationale |
|------|---------|----------|-----------|
| `CLAUDE.md` | root | Stays in root | Must be in root for Claude Code |
| `patterns.yml` | `.agent-context/` | `.kit/context/` | Planning artifact, but feature-devs read it. They can reference `.kit/context/patterns.yml` |
| `agent-handoffs.json` | `.agent-context/` | `.kit/context/` | Coordination state, read by all agents |
| `/start-task` command | `.claude/commands/` | `.claude/commands/` | Used by implementation agents at task start |
| `/commit-push-pr` | `.claude/commands/` | `.claude/commands/` | Used by implementation agents |
| `REVIEW-INSIGHTS.md` | `.agent-context/` | `.kit/context/` | Written by planner, read by feature-devs |

**Resolution for straddlers**: Keep them in `.kit/` (canonical location) and update
CLAUDE.md to point agents there. Implementation agents already read CLAUDE.md for
path guidance.

### 6. Migration Path to Workspace (Future)

Once `.kit/` is stable:

```
Step 1 (this ADR): .kit/ inside each kit repo
Step 2 (future):   .kit/ → ~/Github/workspace/.kit/
                   with per-project subdirs or symlinks
Step 3 (future):   Workspace becomes its own repo
                   with multi-project context resolution
```

`.kit/` is designed so that lifting it out is a mechanical `mv` + path updates,
not a redesign.

## Consequences

### Positive

- **Clean downstream projects**: New projects from the kits don't inherit builder noise
- **Clear sync boundary**: Manifest says "never export `.kit/`" — no judgment calls
- **Workspace-ready**: `.kit/` is the future workspace in embryo
- **Reduced context-switching**: Builder tools are in one place, not scattered across
  the repo

### Negative

- **Path updates**: Every reference to `.agent-context/`, `.adversarial/`, and
  `delegation/` needs updating in agents, commands, skills, CLAUDE.md, and scripts.
  This is the bulk of the implementation work.
- **CLAUDE.md complexity**: CLAUDE.md now needs to describe two layers and their paths
- **Git history**: Moving directories creates a history discontinuity. `git log --follow`
  helps but isn't perfect.

### Neutral

- `.kit/` is a dotfile directory, consistent with `.claude/`, `.adversarial/`, etc.
- The 4 kits continue to be self-contained workbenches — the builder layer is just
  better organized within them.
- Implementation agents don't need to know about `.kit/` unless they're reading
  patterns or review insights (and those paths are in CLAUDE.md).
