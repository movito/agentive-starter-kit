# Workflow Freeze Policy

## Rule

Do NOT edit workflow definitions during an active feature task. This includes:
- Skill files (`.claude/skills/`)
- Command files (`.claude/commands/`)
- Agent definition files (`.claude/agents/`)
- Workflow documents (`.agent-context/workflows/`)

## Rationale

Mixing workflow changes with feature work creates:
- **Noisy diffs**: Reviewers can't distinguish feature code from process changes
- **Coupled risk**: A workflow typo can break an unrelated feature PR
- **Untestable changes**: Workflow edits aren't covered by pytest

## How to Make Workflow Changes

1. Finish or pause the current feature task
2. Create a separate `chore` task (e.g., `chore: Update bot-triage skill`)
3. Work on a dedicated branch (e.g., `chore/update-bot-triage`)
4. Get the workflow change reviewed and merged independently

## Exceptions

1. **Typo fixes**: Typo fixes in comments or documentation within workflow files
   may be included in a feature PR if they are clearly unrelated to the feature
   and noted in the PR description.

2. **Spec-deliverable commands/skills**: When a task spec explicitly requires
   creating a new command file (e.g., `.claude/commands/wait-for-bots.md`) or
   skill file as a deliverable, that creation is part of the feature work — not
   a workflow change. The freeze applies to *modifying existing* workflow files
   during feature work, not to *creating new ones* that are spec requirements.
