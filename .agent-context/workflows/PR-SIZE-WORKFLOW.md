# PR Size Workflow

**Purpose**: Keep pull requests under 500 additions for faster review cycles
**Agents**: planner (decomposition), feature-developer (implementation)
**Last Updated**: 2026-02-27

---

## Target

**< 500 additions per PR.** PRs under this threshold consistently receive fewer
bot findings, require zero fix-commit rounds, and merge on first human review.

---

## Planner Responsibilities

### 1. Commit prep materials to main before branching

Planner artifacts go to `main` as `chore:` or `docs:` commits:

- Task specs (`delegation/tasks/`)
- Architecture assessments (`docs/decisions/adr/`)
- Handoff files (`.agent-context/`)
- Evaluator doc updates (`.adversarial/docs/`)

**Do NOT** put these on the feature branch. They inflate PR line counts and
generate irrelevant bot findings.

```bash
# Planner workflow (on main):
git add delegation/tasks/2-todo/TASK-XXXX.md .agent-context/TASK-XXXX-HANDOFF-*.md
git commit -m "chore: Add TASK-XXXX task spec and handoff"
git push origin main
```

The feature-developer then branches from this point.

### 2. Estimate and declare PR splits in task specs

When a task is estimated to exceed 500 additions, add a `## PR Plan` section:

```markdown
## PR Plan

- **PR 1**: `core_module.py` + `test_core.py` — domain module (~400 lines)
- **PR 2**: `cli_integration.py` + `test_cli.py` — CLI wiring (~300 lines)
```

**Split heuristic**: If the task touches files in more than one architecture layer
AND estimated additions exceed 500 lines, pre-define the split.

### 3. Single-PR tasks

Tasks under ~500 estimated additions don't need a PR Plan section. Most bug fixes,
doc changes, and single-module tasks fall here.

---

## Feature-Developer Responsibilities

### Working with stacked PRs

When a task spec defines multiple PRs:

1. **PR 1**: Create feature branch, implement domain layer, open PR
2. **Wait for merge**: PR 1 must merge before starting PR 2
3. **PR 2**: Branch from updated main, implement CLI layer, open PR

Each PR is independently reviewable and testable.

### Branch naming for stacked PRs

```text
feature/TASK-XXXX-domain       # PR 1
feature/TASK-XXXX-integration  # PR 2
```

### When a PR grows beyond 500 lines

If implementation reveals the task is larger than estimated:

1. **Stop and split** — don't push a 1000-line PR
2. Identify a clean cut point (usually at the layer boundary)
3. Open PR for the completed portion
4. Continue remaining work after merge

---

## Quick Reference

| Estimated size | PR Plan needed? | Split strategy |
|----------------|-----------------|----------------|
| < 500 lines | No | Single PR |
| 500-1000 lines | Yes | 2 PRs (domain + integration) |
| > 1000 lines | Yes | 2-3 PRs (consider further decomposition) |

| Content type | Goes where? |
|-------------|-------------|
| Task specs, handoffs, assessments | Direct to `main` (planner) |
| Domain code + tests | Feature branch PR |
| CLI integration + tests | Separate feature branch PR (if stacking) |

---

## Evidence

| PR size | Avg bot comments | Fix rounds | Review interactions |
|---------|-----------------|------------|---------------------|
| < 300 lines | ~10 | 0 | 1 |
| 300-500 lines | ~12 | 0-1 | 1 |
| 1000-2000 lines | ~28 | 2-3 | 2-3 |
| > 2000 lines | 30 (cap) | 2-3 | 3-4 |
