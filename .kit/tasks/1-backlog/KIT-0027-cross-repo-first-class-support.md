# KIT-0027: First-Class Cross-Repo Agent Support

**Status**: Backlog
**Priority**: medium
**Assigned To**: unassigned
**Estimated Effort**: 2-3 days
**Created**: 2026-04-16

## Overview

The cross-repo pattern (see `docs/CROSS-REPO-PATTERN.md`) works today via
convention: relative paths in handoff files, explicit instructions in CLAUDE.md,
and manual discipline around which repo agents work in. This task elevates it
to a first-class feature with configuration, path resolution, and agent
awareness built in.

**Context**: Pattern discovered during ixda-services-2.0 bootstrap (2026-04-16).
Currently relies on `../target-repo/` hardcoded in handoff files — fragile
across machines and easy for agents to ignore.

## Requirements

### 1. Configuration: `target_repo` in current-state.json

Add an optional `target_repo` field to `.kit/context/current-state.json`:

```json
{
  "project": {
    "name": "ixda-services-2.0",
    "task_prefix": "ID2",
    "version": "0.1.0",
    "target_repo": {
      "path": "../ixda-services",
      "name": "ixda-services",
      "description": "SvelteKit + Sanity CMS monorepo",
      "github": "movito/ixda-services"
    }
  }
}
```

When `target_repo` is present, agents know this is a cross-repo planning
project and adjust behavior accordingly.

### 2. create-project agent: ask about target repo

Update `.claude/agents/create-project.md` to:
- Ask "Will this project manage an existing codebase?" during setup
- If yes: ask for the target repo path, validate it exists, populate
  `target_repo` in `current-state.json`
- Auto-generate the "Target Project" section in CLAUDE.md by reading
  the target repo's `package.json`, `pyproject.toml`, or equivalent

### 3. Agent awareness: inject target_repo context

Update key agent definitions (planner2, feature-developer-v3,
feature-developer-v5) with a startup check:

```markdown
## Startup: Cross-Repo Check

Read `.kit/context/current-state.json`. If `target_repo` is configured:
- **Planner agents**: analysis and task specs reference the target path
  from config, not hardcoded paths
- **Feature-developer agents**: create feature branches in the target
  repo, not the planning repo. Read task specs from the planning repo,
  implement in the target repo.

The resolved target path is: `$PROJECT_ROOT/<target_repo.path>`
```

### 4. Handoff template: auto-populate target path

Update `.kit/templates/TASK-STARTER-TEMPLATE.md` to include a cross-repo
section when `target_repo` is configured:

```markdown
### Target Repository

**Path**: `../ixda-services/` (resolved from current-state.json)
**GitHub**: movito/ixda-services

Code changes go in the target repo. Create feature branches there.
Task specs and handoff files stay in this (planning) repo.
```

### 5. Validation: target repo existence check

Add a check to `scripts/core/ci-check.sh` (or a new script) that verifies
the target repo path exists when `target_repo` is configured. Warn (don't
fail) if the path is missing — the planning repo should be usable
independently for task management even without the target checked out.

### 6. Task completion: cross-repo reminder

Update `.kit/context/workflows/TASK-COMPLETION-PROTOCOL.md` to include
a cross-repo step: after merging the PR in the target repo, update task
status in the planning repo.

## Acceptance Criteria

- [ ] `target_repo` field in `current-state.json` schema documented
- [ ] `create-project` agent asks about target repo and populates config
- [ ] Planner2 and feature-developer agents read target path from config
- [ ] Handoff template includes cross-repo section when target is configured
- [ ] At least one agent (feature-developer) correctly creates branches
      in the target repo based on config, not hardcoded paths
- [ ] Documentation updated (`docs/CROSS-REPO-PATTERN.md`)

## Risks

### Risk 1: Agent path resolution across machines
**Likelihood**: Medium
**Impact**: High
**Mitigation**: Use relative paths from project root. Document the sibling
directory convention. Consider an env var override (`TARGET_REPO_PATH`).

### Risk 2: Agents ignoring the config and working in the planning repo
**Likelihood**: Medium
**Impact**: Medium
**Mitigation**: Add a guard in feature-developer agents: if `target_repo`
is configured and the agent is about to create files outside `.kit/`,
warn and redirect to the target repo.

## Notes

- This task should NOT be done until the pattern has been used at least
  once end-to-end (planning → implementation → PR → merge). ID2 provides
  the first test case.
- The pattern doc (`docs/CROSS-REPO-PATTERN.md`) should be considered the
  source of truth for conventions until this task is complete.
- Consider whether `target_repo` could be a list (multi-target) — don't
  build it, but don't preclude it either.
