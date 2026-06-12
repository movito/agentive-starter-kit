# Cross-Repo Agent Pattern

Use a dedicated **planning repo** (bootstrapped from agentive-starter-kit) to
orchestrate work against a separate **target repo** containing the actual
codebase.

> **Canonical copy.** This document is the single source of truth for the
> cross-repo pattern (KIT-ADR-0024 §5). Project repos link here instead of
> forking; project-specific deltas (target path, branch rules, stack commands)
> live in a short stub in each project.

**History**: 2026-04-16 (initial, ixda-services-2.0), 2026-04-17 (revised
after field testing), 2026-04-22 (adversarial evaluator recipe added,
suwinex-planning), 2026-06-12 (forks merged into this canonical copy,
KIT-0028). Field-tested through multiple task cycles (ID2-0008, ID2-0004,
ID2-0011, suwinex SUW tasks).

## When to Use This

**Good fit:**

- Uplifting or modernizing an existing codebase without polluting it with
  planning artifacts
- The target repo has its own CI, toolchain, and contribution norms that
  conflict with the Python-based agent workflow tooling
- You want planning history (task specs, evaluations, analysis) separate
  from implementation history (code changes)
- Managing work across multiple target repos from one planning repo
- Teams where some members work directly in the target repo and shouldn't
  need to understand the agent workflow

**Poor fit:**

- Greenfield projects where the planning repo and application repo can be
  one thing
- Very small projects (< 10 tasks) where the overhead isn't justified
- Situations where the target repo is already well-suited to host planning
  artifacts (e.g., it already has a `.kit/` or similar structure)

Per KIT-ADR-0024 §1, the split is the **default for production projects**
(anything with CI, bot reviews, evaluators, or a deployable artifact);
monorepo remains fine for one-offs and small experiments.

## How It Works

```
planning-repo/                    target-repo/
├── CLAUDE.md (## Target Repository config)
├── .claude/agents/      ←──────── agent definitions live here
├── .claude/commands/    ←──────── slash commands (cross-repo aware)
├── .kit/tasks/          ←──────── agents read specs from here
├── .kit/context/        ←──────── handoffs, analysis, reviews, retros
├── .adversarial/        ←──────── evaluation logs
└── (no application code)         ├── src/
                                  ├── tests/
                                  └── (all code changes land here)
```

1. **Planner agent** operates in the planning repo: creates task specs, runs
   evaluations, writes handoff files, manages backlog, presents task starters
   to the user
2. **User opens a new tab** and pastes the task starter
3. **Feature-developer agent** reads the task spec and handoff from the
   planning repo, then works in the target repo on a feature branch
4. **Code review** happens on PRs in the target repo; review artifacts
   (starters, evaluator output, retros) are stored in the planning repo
5. **Task status** is tracked in the planning repo throughout

## Configuration

The planning repo's `CLAUDE.md` declares the target with a machine-readable
section — this exact heading and bullet format is what slash commands parse:

```markdown
## Target Repository

This project uses the **cross-repo pattern**: planning and coordination happen
here, code changes land in the target repo.

- **Path**: `../my-target-repo`
- **GitHub**: `owner/my-target-repo`

Commands like `/retro` and `/wrap-up` detect this section and route git/gh
operations to the target repo automatically. If this section is removed,
all commands fall back to single-repo behavior.
```

Commands detect this section automatically. If it's absent, all commands fall
back to single-repo behavior. Per KIT-ADR-0024 §2 this section is mandatory
for cross-repo projects and preflight-validated.

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

### 2. Ensure sibling directory layout

Both repos must be siblings on disk:

```
~/Github/
├── my-project/           # target repo (the codebase)
└── my-project-planning/  # planning repo (agentive-starter-kit)
```

Naming convention (KIT-ADR-0024 §1): `<project>-planning` and
`<project>-code` (or the target's existing name).

### 3. Configure CLAUDE.md

Add the `## Target Repository` section shown under Configuration above.
Optionally add a prose "Key Focus Areas" subsection describing the target's
stack and priorities.

### 4. Create cross-repo-aware agents

Agent definitions need explicit cross-repo instructions. Key elements:

```markdown
## Cross-Repo Pattern

- **Planning repo**: Task specs, handoffs, evaluations, coordination
- **Target repo** (`../my-target-repo`): All code changes go here

Rules:
- Read task specs from the planning repo
- Create feature branches in the TARGET repo
- Git operations (commit, push, PR) happen in the target repo
- Never commit code to the planning repo
```

Agent definitions must also be **stack-aware**: the planning repo's Python
tooling (pytest, black, ruff) doesn't apply to a JavaScript/Go/Ruby target.
Override these defaults with the target's toolchain (vitest, eslint,
`npm run check`, …).

### 5. Write handoff files with explicit paths

The handoff file (`.kit/context/<TASK-ID>-HANDOFF-feature-developer.md`) is
the bridge between repos. It must explicitly state:

- The target repo path and that the feature branch goes there
- File paths relative to the target repo
- Testing approach for the target stack (not the planning stack)
- The exact commands to start work in the target repo

Without a good handoff file, the feature-developer agent gets confused about
which repo to work in.

### 6. Run evaluators from the planning repo

Evaluators need API keys that live in the planning repo's `.env`. Always
source it before running:

```bash
set -a && source .env && set +a
adversarial arch-review-fast .kit/tasks/2-todo/TASK-FILE.md
```

## Conventions

### Path references

Always use `../target-repo/` relative paths in handoff files and task specs.
Never hardcode absolute paths — they break across machines.

### Explicit flags, never `cd`

Any command that runs `git` or `gh` must check for cross-repo mode first.
Use `git -C <path>` and `gh --repo <owner/repo>` flags — never `cd` into the
target repo. `cd` creates stateful side effects that break subsequent
commands (the key fix in ID2-0011).

### Branch rules

The planning repo stays on `main` at all times; planning artifacts commit
straight to `main`. The target repo uses `feature/<TASK-ID>-*` branches with
PRs.

### Task completion

When a task is done in the target repo:

1. Merge the PR in the target repo
2. Move the task to `5-done/` in the planning repo
3. Extract review insights if applicable

This is a two-repo operation — it cannot be atomic. Accept that some drift
is inevitable and reconcile periodically. The `/wrap-up` command handles
both sides: it runs retro (reading from the target repo) and saves artifacts
(to the planning repo).

### PR descriptions

PRs in the target repo should include enough context that reviewers don't
need to cross-reference the planning repo. Summarize the task motivation and
key decisions in the PR description; link to the planning repo task spec if
the team has access.

## Advantages

1. **Clean separation of concerns**: planning artifacts (task specs, analysis
   reports, evaluation logs, handoffs, coordination state) don't pollute the
   application codebase. Developers working directly in the target repo never
   see `.kit/` folders or adversarial evaluation logs — they just see clean
   PRs arriving on feature branches.
2. **No toolchain conflicts**: the planning repo uses Python tooling from the
   kit; the target can use anything. Separate git repos, separate configs —
   they never interfere.
3. **Natural branch isolation** (discovered in practice): the planning repo
   stays on `main` while the target has feature branches. The planner can
   commit task updates, agent definitions, and workflow improvements *during*
   in-flight feature work — without merge conflicts or branch switching.
   Field-proven: two new agents and two command fixes were created during an
   active feature task with zero interference.
4. **Planning history survives independently**: planning-repo history captures
   the *reasoning* (scoping, evaluator findings, priority shifts); target-repo
   history captures the *implementation*. `git blame` in the target shows
   clean implementation commits, not planning noise.
5. **Multiple target repos from one planning repo**: a platform team could
   manage several services from one planning repo, with task prefixes
   distinguishing them. The current `## Target Repository` config supports
   one target; extending to multiple is an open question (below).
6. **Safe experimentation**: iterate on task templates, evaluation workflows,
   agent definitions, and coordination protocols without risking the target
   codebase. A bad planning commit doesn't break production.
7. **Easier onboarding**: a new team member (or agent) can read the planning
   repo to understand priorities, open tasks, and architectural decisions
   without navigating the full application codebase.

## Known Limitations (and Mitigations)

1. **Context switching between repos is real friction.** Agents must know
   which repo they're in at all times; relative paths assume the sibling
   layout. *Mitigation*: standardize the sibling convention; treat the
   `## Target Repository` section as the single source of truth; state
   "changes go in the target repo" explicitly in every task starter.
2. **Commands assume single-repo by default.** `git branch --show-current`
   returns `main` (planning repo), `gh pr view` resolves to the wrong repo.
   *Mitigation (implemented)*: commands detect `## Target Repository` and use
   `git -C` / `gh --repo`. Absent the section, behavior is identical to
   single-repo mode.
3. **Two repos to maintain.** If the planning repo falls out of sync with
   reality, it becomes misleading rather than helpful. *Mitigation*:
   discipline — complete the task lifecycle; `/wrap-up` bakes the planning
   update into the completion protocol; reconcile periodically.
4. **No atomic commits across both repos.** *Mitigation*: the two-step
   `/wrap-up` flow; accept and reconcile.
5. **Heavier setup for small projects.** Overhead exceeds benefit below
   ~10 tasks — use a monorepo instead.
6. **Agent context budget splits across repos.** In practice not a problem —
   specs and handoffs are small relative to code.
7. **Target repo PRs lack planning context.** *Mitigation*: thorough PR
   descriptions (see Conventions).

## Lessons Learned (field-tested)

1. **Handoff files are critical** — they are the bridge between repos (see
   Setup §5).
2. **Agent definitions must be stack-aware** — override the kit's Python
   defaults with the target's toolchain.
3. **Evaluators run from the planning repo** — `.env` keys live there; target
   diffs are piped into the planning repo's `.adversarial/inputs/`.
4. **Branch isolation is a feature, not a bug** — process iteration and
   implementation proceed in parallel.
5. **Cross-repo commands need explicit flags, not `cd`** — `git -C` and
   `gh --repo` only.
6. **Never let a project invent shared machinery without a same-week
   upstream PR** — improvements born in a project (agents, helpers, doc
   revisions) must flow back to the kit immediately, or they strand
   (KIT-ADR-0024; the feature-developer-v7 lesson).

## Adversarial Code Review (Cross-Repo)

The built-in `adversarial review` command **does not work** in cross-repo
mode. It enforces a "you have changed files" guardrail on the current
working directory; the planning repo has no code changes (they live in
the target repo), so the check always fails. Do not try to work around
this with `cd` — the `.adversarial/` config lives in the planning repo,
so running from the target repo fails too ("Not initialized").

### The canonical workflow

Use **file-based evaluators**. They accept an explicit input path and
skip the git-state guardrail.

```bash
# 1. From the planning repo, generate the input file.
#    The helper reads the target repo from CLAUDE.md ## Target Repository
#    and runs `git diff main...HEAD` there.
./scripts/core/prepare-review-input.sh <TASK-ID>
# → .adversarial/inputs/<TASK-ID>-code-review-input.md

# 2. Load API keys and run the evaluators.
set -a && source .env && set +a
adversarial code-reviewer-fast .adversarial/inputs/<TASK-ID>-code-review-input.md
adversarial code-reviewer      .adversarial/inputs/<TASK-ID>-code-review-input.md
adversarial claude-code        .adversarial/inputs/<TASK-ID>-code-review-input.md

# 3. Results land in .adversarial/logs/<TASK-ID>-*.md
# 4. Concatenate all evaluator outputs (fast + o3 + claude-code) into
#    one review artifact tracked in git. An array + nullglob is used
#    because `cp glob dest.md` would fail when the glob matches more
#    than one file, and we want to fail fast if it matches zero
#    (otherwise an empty review artifact silently hides evaluator
#    failures).
shopt -s nullglob
logs=(.adversarial/logs/<TASK-ID>-code-review-input--*.md)
shopt -u nullglob
if [ "${#logs[@]}" -eq 0 ]; then
    echo "ERROR: no evaluator logs found for <TASK-ID> in .adversarial/logs/" >&2
    exit 1
fi
{
    for log in "${logs[@]}"; do
        echo "## Source: $(basename "$log")"
        echo
        cat "$log"
        echo
    done
} > .kit/context/reviews/<TASK-ID>-evaluator-review.md
```

The helper's defaults:

| Flag | Default | Override |
|------|---------|----------|
| Base branch | `main` | `--base develop` |
| Input format | `full` (diff + complete files) | `--format diff` |
| Target repo path | from `CLAUDE.md` `## Target Repository` | edit `CLAUDE.md` (no flag) |

Use `--format full` (the default) unless the PR is too large to fit.
Diff-only input causes model hallucinations on symbols defined outside
the diff hunks — ID2-0002 retro documented Claude Sonnet flagging
`homeSponsorsQuery` as a non-existent export when it was defined just
outside the reviewed range.

> **Helper availability**: `prepare-review-input.sh` and its
> `lib/target_repo.sh` dependency currently ship in projects bootstrapped
> since 2026-04 (reference implementations: ixda-services-2.0,
> suwinex-planning). Upstreaming them into this kit's `scripts/core/` is
> tracked via the manifest sync work (KIT-0026 / KIT-0030).

### Recommended evaluator trio

| Evaluator | Model | Focus | Cost | When to use |
|-----------|-------|-------|------|-------------|
| `code-reviewer-fast` | Gemini Flash | Quick correctness gate | ~$0.01 | Every PR |
| `code-reviewer` | OpenAI o3 | Deep adversarial, edge cases | ~$0.33 | Non-trivial / complex changes |
| `claude-code` | Claude Sonnet | Security, data handling | ~$0.05 | Security-sensitive code |

Each model surfaces a different class of findings with minimal overlap.
ID2-0002 validated this empirically: o3 caught a latent non-array crash
the bots missed, `claude-code` raised security concerns the others didn't,
and `code-reviewer-fast` was cheap enough to run on every task.

Where the evaluator library ≥ v0.10.0 is installed, prefer the `-v2`
variants (`code-reviewer-fast-v2`, etc.) — they pin explicit model IDs
instead of floating tags. The v1 names are deprecated upstream.

### Single-repo fallback

`prepare-review-input.sh` also works in single-repo projects: if
`CLAUDE.md` has no `## Target Repository` section, it reads the diff
from the current working-directory repo. No flag change required.

### Fitting into the agent workflow

The feature-developer agent's evaluator gate (Phase 7 in v6/v7) expects
you to prepare the input, run the trio (or at least the fast gate),
triage FAIL/CONCERNS findings, and persist the results to the planning
repo's review directory before handoff.

## Open Questions

1. **First-class `target_repo` config**: a framework-enforced config that
   agents and commands auto-detect would reduce per-project setup. Tracked
   as KIT-0027; the `## Target Repository` CLAUDE.md section is the current
   convention.
2. **Automatic cross-repo task completion**: a GitHub Action in the target
   repo that calls back to the planning repo on PR merge would close the
   atomicity gap.
3. **Multi-target support**: the current config supports one target repo.
   For platform teams managing multiple services, a per-task target field
   (or prefix mapping) would be needed.

## Reference Implementations

- **First demonstrated** 2026-04-16: `ixda-services-2.0` (planning) managing
  uplift of `ixda-services` (SvelteKit + Sanity). Planner2 analyzed the
  target and produced 9 backlog tasks without modifying it. Key files there:
  `scripts/core/lib/target_repo.sh`, `scripts/core/prepare-review-input.sh`,
  cross-repo-aware `/retro` and `/wrap-up` commands.
- **Active users**: `suwinex-planning` → `suwinex-code`,
  `label-maker-planning` → `label-maker-code`. Their pattern docs are stubs
  linking back to this canonical copy.
