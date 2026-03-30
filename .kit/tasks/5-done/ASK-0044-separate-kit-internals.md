# ASK-0044: Separate Builder Layer from Project Layer (`.kit/` Boundary)

**Status**: Done
**Priority**: High
**Assigned To**: unassigned
**Estimated Effort**: 3-4 days (across 3 PRs)
**Created**: 2026-03-25
**Updated**: 2026-03-28
**GitHub Issue**: #35

## Related Tasks

**Related**: KIT-0024 (core scripts standardization — established tiered manifest)
**Related**: ASK-0042 (scripts restructure — established core/local/optional layout)
**ADR**: KIT-ADR-0023 (Builder/Project Separation)

## Overview

Every project built with agentive-starter-kit inherits the full "builder" layer:
planning agents, task management, evaluators, ADRs, review workflows, coordination
state. Cross-repo audits show builder infrastructure outnumbers project code by
5:1 to 12:1 across all four kits. This infrastructure is about *how we work on*
a project, not *what the project does*.

**The goal**: Create a `.kit/` directory that holds all builder internals. The sync
mechanism sends `.kit/` to the 4 kits (via a new `kit_builder` manifest tier) but
never to consumer projects. This is the first step toward a future "project workspace"
where the builder layer lives outside repos entirely.

## Background

### Cross-Repo Audit (2026-03-28)

| Repo | Builder Files | Project Code | Ratio | Done Tasks |
|------|--------------|-------------|-------|------------|
| agentive-starter-kit | ~200 | ~30 | 7:1 | 10 |
| dispatch-kit | ~600+ | ~50 | 12:1 | 101 |
| adversarial-workflow | ~300+ | ~40 | 8:1 | 66 |
| adversarial-evaluator-library | ~150+ | ~30 | 5:1 | 35 |

**Duplicated everywhere**: 18+ agent defs, 11 commands, 5 skills, evaluator configs,
task folders, 22+ KIT-ADRs, 9-11 workflows, handoffs, retros, reviews, session
handovers. The builder layer is ~80% identical across all 4 repos.

### Root Cause

There is no "thick client" or external workspace for planning and coordination.
Every project is its own self-contained workbench, duplicating the same builder
machinery. Claude Code's directory-rooted context model makes extraction non-trivial,
so this ADR establishes the boundary first.

## Design Decisions (Locked 2026-03-28)

1. **`.kit/` is the builder layer root** — all planning/coordination/evaluation
   infrastructure lives under `.kit/`. See KIT-ADR-0023 for full classification.

2. **Sync via manifest tier** — `.core-manifest.json` gets a new `kit_builder` tier.
   The sync Action sends `kit_builder` files to kit repos (`is_kit: true`) but never
   to consumer projects. Reuses existing KIT-ADR-0022 infrastructure.

3. **Kit repos vs consumer projects** — The sync workflow matrix gains an `is_kit`
   flag per repo. Kit repos (ASK, DSP, ADV, AEL) get everything. Consumer projects
   get `scripts_core` + `commands_core` + `commands_optional` (if opted in).

4. **Future workspace-ready** — `.kit/` is designed so that lifting it out into a
   standalone workspace repo is a mechanical `mv` + path updates, not a redesign.

## Classification

### Builder Layer (→ `.kit/`)

| Current Location | New Location | Contents |
|-----------------|-------------|----------|
| `delegation/tasks/` | `.kit/tasks/` | Task specs (1-backlog through 9-reference) |
| `delegation/handoffs/` | *(deleted — handoffs stay in `.kit/context/`)* | Handoff records |
| `.agent-context/` | `.kit/context/` | Coordination state, handoffs, reviews, retros, workflows, patterns.yml |
| `.adversarial/` | `.kit/adversarial/` | Evaluator system (config, evaluators, inputs, logs, scripts) |
| `docs/decisions/starter-kit-adr/` | `.kit/decisions/` | Kit ADRs (KIT-ADR-*) |
| `.claude/agents/planner*.md` | `.kit/agents/` | Builder agents (planner, planner2, tycho, code-reviewer, document-reviewer, security-reviewer) |
| `.claude/agents/AGENT-TEMPLATE.md` | `.kit/agents/` | Agent creation template |
| `.claude/agents/OPERATIONAL-RULES.md` | `.kit/agents/` | Agent operational rules |
| `.claude/agents/TASK-STARTER-TEMPLATE.md` | `.kit/agents/` | Task starter template |
| `.claude/skills/{retro,review-handoff,code-review-evaluator,self-review}/` | `.kit/skills/` | Builder skills |
| `.claude/commands/{babysit-pr,retro,triage-threads,status,check-spec,wrap-up}.md` | `.kit/commands/` | Builder commands |
| `agents/launch,onboarding,preflight` | `.kit/launchers/` | Agent launcher scripts |
| `docs/agentive-development/` | `.kit/docs/agentive-development/` | Curriculum (if present) |
| `docs/{TESTING,LINEAR-SYNC-BEHAVIOR,UPGRADE-0.4.0}.md` | `.kit/docs/` | Builder documentation |

### Project Layer (stays in standard locations)

| Location | Contents |
|----------|----------|
| `.claude/agents/{feature-developer*,test-runner,powertest-runner,ci-checker,bootstrap,onboarding,agent-creator}.md` | Implementation agents |
| `.claude/commands/{check-ci,check-bots,wait-for-bots,start-task,commit-push-pr,preflight}.md` | Implementation commands |
| `.claude/skills/{pre-implementation,bot-triage}/` | Implementation skills |
| `.claude/settings.json`, `.claude/settings.local.json` | Claude Code config |
| `scripts/core/` | Synced core scripts |
| `scripts/local/` | Project-specific scripts |
| `scripts/optional/` | Opt-in scripts |
| `tests/` | Project tests |
| `src/` | Project source (if applicable) |
| `docs/decisions/adr/` | Project-specific ADRs |
| `CLAUDE.md`, `README.md`, `CHANGELOG.md` | Project root docs |
| `pyproject.toml`, `conftest.py` | Project config |
| `.serena/` | Serena config (project-specific) |
| `.github/` | CI/CD workflows |

### Straddlers (used by both layers)

| File | Canonical Location | Rationale |
|------|-------------------|-----------|
| `patterns.yml` | `.kit/context/` | Written by planner, read by feature-devs via CLAUDE.md path |
| `agent-handoffs.json` | `.kit/context/` | Coordination state, read by all agents |
| `REVIEW-INSIGHTS.md` | `.kit/context/` | Written by planner, read by feature-devs |
| `current-state.json` | `.kit/context/` | Project state tracking |

Resolution: Keep in `.kit/`, update CLAUDE.md to point implementation agents there.

## PR Strategy: Single Atomic PR

> **Decision (2026-03-29)**: Originally planned as 3 PRs. Collapsed into a single
> branch after discovering that splitting a structural migration leaves the codebase
> in a half-migrated state that agents cannot navigate. Agents depend on hardcoded
> paths in prompts, handoff files, and CLAUDE.md — stale paths cause silent failures.
> See PR-SIZE-WORKFLOW.md §3 and REVIEW-INSIGHTS.md (ASK-0044 entry).

All work lands on `feature/ASK-0044-kit-boundary` and merges as one PR.

### Phase 1: Directory moves + path rewrites

1. Create `.kit/` directory structure
2. `git mv` all builder artifacts to `.kit/` (see classification table)
3. Update CLAUDE.md with new paths
4. Update all agent definitions that reference moved paths
5. Update all command/skill definitions that reference moved paths
6. Verify no broken references: `grep -r '.agent-context/' .claude/ CLAUDE.md`
7. Verify no broken references: `grep -r '.adversarial/' .claude/ CLAUDE.md`
8. Verify no broken references: `grep -r 'delegation/tasks/' .claude/ CLAUDE.md`

### Phase 2: Sync manifest + workflow

1. Add `kit_builder` tier to `.core-manifest.json` listing all `.kit/` files
2. Add `is_kit` flag to sync workflow matrix
3. Update sync Action to:
   - Send `kit_builder` files only to repos with `is_kit: true`
   - Map `.kit/` paths correctly in downstream copy
4. Update `check-sync.sh` to verify `.kit/` content in kit repos

### Phase 3: Consumer template

1. Create `scripts/local/bootstrap-consumer.sh` — bootstraps a consumer project
   without `.kit/` (just scripts/core + commands + thin CLAUDE.md)
2. Update `agents/onboarding` to detect kit vs consumer project
3. Add `.kit/` to the consumer project `.gitignore` template
4. Document the two project types in README.md

### Final: CI + verification

1. Run `./scripts/core/ci-check.sh`
2. Verify no broken path references (grep sweep)
3. Open single PR for review

## Sync Manifest (Target State)

```json
{
  "core_version": "2.0.0",
  "source_repo": "movito/agentive-starter-kit",
  "synced_at": "2026-03-28T00:00:00Z",
  "files": {
    "scripts_core": ["core/project", "core/ci-check.sh", "..."],
    "commands_core": ["check-ci.md", "check-bots.md", "..."],
    "commands_optional": ["babysit-pr.md", "retro.md", "..."],
    "kit_builder": [
      ".kit/tasks/9-reference/",
      ".kit/context/workflows/",
      ".kit/context/patterns.yml",
      ".kit/context/templates/",
      ".kit/adversarial/config.yml",
      ".kit/adversarial/evaluators/",
      ".kit/adversarial/scripts/",
      ".kit/adversarial/docs/",
      ".kit/agents/",
      ".kit/skills/",
      ".kit/commands/",
      ".kit/launchers/",
      ".kit/decisions/"
    ]
  },
  "opted_in": ["commands_optional", "kit_builder"]
}
```

**Note**: `kit_builder` includes templates and reusable configs, not task histories
or project-specific state (handoffs, retros, reviews, logs). Those are per-project.

## Sync Workflow Matrix (Target State)

```yaml
strategy:
  matrix:
    include:
      - repo: movito/dispatch-kit
        is_kit: true
      - repo: movito/adversarial-workflow
        is_kit: true
      - repo: movito/adversarial-evaluator-library
        is_kit: true
      # Consumer projects would have is_kit: false
```

## Acceptance Criteria

### Must Have
- [ ] KIT-ADR-0023 finalized and committed
- [ ] `.kit/` directory exists with all builder artifacts moved
- [ ] CLAUDE.md updated with `.kit/` paths
- [ ] All agent/command/skill definitions reference correct paths
- [ ] `kit_builder` tier in `.core-manifest.json`
- [ ] Sync Action respects `is_kit` flag
- [ ] `./scripts/core/ci-check.sh` passes
- [ ] No broken path references (verified by grep)

### Should Have
- [ ] Consumer bootstrap script
- [ ] Onboarding detects kit vs consumer
- [ ] Documentation updated

### Won't Have (This Task)
- [ ] Downstream kit adoption (separate tasks per repo)
- [ ] Workspace extraction (future, post `.kit/` stabilization)

## References

- KIT-ADR-0023: `docs/decisions/starter-kit-adr/KIT-ADR-0023-builder-project-separation.md`
- KIT-ADR-0022: `docs/decisions/starter-kit-adr/KIT-ADR-0022-manifest-based-sync-ownership.md`
- GitHub issue: #35
- Cross-repo audit: Conducted 2026-03-28 (ASK, DSP, ADV, AEL)
- adversarial-workflow PR #42: Scripts restructure (14 scripts, 56 file updates)
- adversarial-workflow PR #43: Agent sync (11 agents, manual triage)
