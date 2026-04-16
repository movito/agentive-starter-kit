# Cross-Repo Agent Pattern

Use a dedicated **planning repo** (bootstrapped from agentive-starter-kit) to
orchestrate work against a separate **target repo** containing the actual
codebase.

## When to Use This

- Uplifting or modernizing an existing codebase without polluting it with
  planning artifacts
- The target repo has its own CI, toolchain, and contribution norms that
  conflict with the Python-based agent workflow tooling
- You want planning history (task specs, evaluations, analysis) separate
  from implementation history (code changes)
- Managing work across multiple target repos from one planning repo

**Don't use this** for greenfield projects where the planning and application
repo can be one thing, or for very small projects (< 10 tasks) where the
overhead isn't justified.

## How It Works

```
planning-repo/                    target-repo/
├── .kit/tasks/         ←──────── agents read specs from here
├── .kit/context/       ←──────── handoffs, analysis, reviews
├── .adversarial/       ←──────── evaluation logs
├── CLAUDE.md                     ├── src/
└── (no application code)         ├── tests/
                                  └── (all code changes land here)
```

1. **Planner agent** operates in the planning repo: creates task specs, runs
   evaluations, writes handoff files, manages backlog
2. **Feature-developer agent** reads the task spec and handoff from the
   planning repo, then works in the target repo on a feature branch
3. **Code review** happens on PRs in the target repo; review artifacts are
   stored in the planning repo
4. **Task status** is tracked in the planning repo throughout

## Setup

### 1. Create the planning repo

From the agentive-starter-kit directory:

```bash
# Using the create-project agent (recommended):
# Invoke create-project agent in a new tab and tell it:
#   - target directory
#   - project name
#   - task prefix
#   - that it will manage an existing codebase at <path>

# Or using the script directly:
./scripts/optional/create-project.sh ~/Github/my-project-planning \
  --name "My Project Planning" \
  --prefix MPP
```

### 2. Configure CLAUDE.md

Add a "Target Project" section to CLAUDE.md in the planning repo:

```markdown
## Target Project

The target codebase lives at `../my-project/` — a brief description of
the target's tech stack and structure.

### Key Focus Areas

1. **Area 1**: description
2. **Area 2**: description
```

### 3. Write handoff files with explicit paths

Every handoff file must state clearly:
- Where the target codebase is: `../my-project/`
- That code changes go there, not in the planning repo
- That feature branches are created in the target repo

### 4. Ensure sibling directory layout

Both repos must be siblings on disk:

```
~/Github/
├── my-project/           # target repo (the codebase)
└── my-project-planning/  # planning repo (agentive-starter-kit)
```

## Conventions

### Path references

Always use `../target-repo/` relative paths in handoff files and task specs.
Never hardcode absolute paths — they break across machines.

### Task completion

When a task is done in the target repo:
1. Merge the PR in the target repo
2. Move the task to `5-done/` in the planning repo
3. Extract review insights if applicable

This is a two-repo operation — it cannot be atomic. Accept that some drift
is inevitable and reconcile periodically.

### PR descriptions

PRs in the target repo should include enough context that reviewers don't
need to cross-reference the planning repo. Summarize the task motivation
and key decisions in the PR description.

## Advantages

- **Clean separation**: planning artifacts don't pollute the application codebase
- **No toolchain conflicts**: Python planning tools and JS/Go/Ruby target
  tools never interfere
- **Independent histories**: git blame in the target shows implementation,
  not planning noise
- **Safe experimentation**: iterate on agent workflow without risking the
  target codebase
- **Easier onboarding**: the planning repo is a curated entry point to
  understand priorities and architecture

## Known Limitations

- **Context switching**: agents must know which repo they're in at all times
- **Two repos to maintain**: planning repo can drift if task lifecycle isn't
  completed
- **No atomic cross-repo commits**: task completion touches both repos
- **Agent context budget**: reads from two repos, though planning files are
  small relative to code

## First Demonstrated

2026-04-16: `ixda-services-2.0` (planning repo) managing uplift of
`ixda-services` (SvelteKit + Sanity target repo). Planner2 agent analyzed
the target codebase and produced 9 backlog tasks without modifying it.
