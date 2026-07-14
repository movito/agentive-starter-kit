# Worktree-Based Implementation Sessions

**Purpose**: Per-task git worktrees are the default implementation
topology — the primary clone stays on `main` for the planner, code
happens in isolated worktrees
**Agents**: planner (creation + removal), feature-developer (the session)
**Last Updated**: 2026-07-14 (KIT-0044, codifying the KIT-0043 pilot)

---

## Topology

- **Primary clone** (`~/Github/agentive-starter-kit/`): the planner's
  workspace. Always a normal (non-bare) checkout, always on `main`.
  Task bookkeeping, retros, and merges happen here.
- **Task worktrees** (`../ask-worktrees/<TASK-ID>/`): one per active
  implementation task, each on its own `feature/<TASK-ID>-<slug>`
  branch. All code changes, commits, and pushes happen here.

This makes the shared-mutable-branch hazard class structurally
impossible: the planner cannot commit onto a checked-out feature branch
(the f7a6c90 incident), a session cannot be yanked to another branch
mid-turn, and two sessions never contend for one working tree. The
planner-side branch-verify habit stays as defense in depth.

## Creation

One command, run from anywhere in the repo (or any of its worktrees):

```bash
./scripts/local/new-worktree.sh <TASK-ID> [slug]
```

The helper:

1. Fetches origin and branches from **fresh `origin/main`** — never a
   local `main` that may be silently stale (the KIT-0043 pilot's
   pre-created branch was 10 commits behind).
2. Provisions the gitignored runtime artifacts from an **explicit,
   enumerated list** maintained inside the helper itself — currently
   `.venv`, `.env`, and `.adversarial/evaluators/`, all symlinked to
   the primary clone. New artifacts get added to the list by name,
   never via an "everything gitignored" glob.
3. Refuses cleanly if the worktree path or branch already exists.
4. Prints the launch instruction (below).

Deliberately **not** provisioned: `.serena/project.yml` (Serena
registers the project by name against the primary path — a second copy
at another path collides), `.adversarial/logs/` (regenerates),
`.dispatch/` runtime files and tool caches (regenerate on demand), and
user-owned untracked directories such as `.kit/adversarial/` (stay in
the primary; never copied, staged, or deleted).

## Launch

**Open the session tab with its working directory set to the worktree
path.** This is the un-skippable LAUNCH block in every task starter
(`.kit/templates/TASK-STARTER-TEMPLATE.md`). A session run from the
primary clone instead pays a `cd` prefix on every command — measured at
~40 extra prefixes in the KIT-0043 pilot — and risks operating on the
wrong checkout.

## The pre-commit GIT_DIR contract

pre-commit exports an **absolute `GIT_DIR`** when it runs inside a
worktree. Any test or script that shells out to git without cleaning
its environment silently operates on the REAL repository — and the
damage is not limited to failing tests. During the KIT-0043 pilot a
leaked subprocess flipped `core.bare=true` on the primary clone: state
corruption, second occurrence of the KIT-0036 gotcha class.

The contract, since commit `7ef104d`:

- **Suite-wide isolation is in place**: an autouse fixture in
  `tests/conftest.py` strips every ambient `GIT_*` variable for every
  test. Do not re-implement per-module isolation.
- **New tests rely on the fixture, never on ambient env.** Any new test
  (or script a test invokes) that spawns git must assume `GIT_*` can be
  hostile; the conftest fixture covers pytest, but a script that runs
  git outside pytest must scrub `GIT_*` itself.
- **Canary**: after any pre-commit run inside a worktree, the primary
  clone must still report

  ```bash
  git -C <primary> config core.bare   # must print: false
  ```

  Run it after your first commit of a session. The exact leak vector
  from the pilot was never conclusively pinned, so the canary is the
  proof the isolation holds — a `true` here means a new vector is live:
  stop, restore (`git -C <primary> config core.bare false`), and file it.

## Closeout

When the task completes:

1. **Session (feature-developer)**: leave the worktree clean — all
   commits pushed, PR opened/merged per the normal workflow, no
   uncommitted files. The session never removes its own worktree.
2. **Planner**: completes the task in the primary clone (task move to
   `5-done`, retro archived, merged branch deleted).

## Lifecycle — who removes the worktree, and when

The **planner** removes the worktree at task completion, **after the
retro has been read** (the retro may reference in-worktree state worth
inspecting first):

```bash
git worktree remove ../ask-worktrees/<TASK-ID>
git worktree prune
git branch -d feature/<TASK-ID>-<slug>   # if not already deleted at merge
```

`git worktree remove` refuses if the tree is dirty — that refusal is
the safety net, not an obstacle; inspect before forcing. For this to
work, every provisioned artifact must be gitignored in a form that
matches a **symlink** (no trailing slash — dir-only patterns don't
match symlinks; verified empirically in KIT-0044: an unignored
provisioning symlink forces `--force` on every removal and erodes the
safety net). Check `git -C <worktree> status --porcelain` — it must be
empty before removal.

## Design note: bare-hub layout — evaluated and declined (2026-07-14)

**Option considered**: convert the primary clone to a deliberate bare
hub (`agentive-starter-kit.git`) with a standing `ask-worktrees/main`
worktree for the planner, making every checkout — including main — a
worktree peer.

**Real migration costs** (each verified against current tooling):

- **Claude Code scoping is per-path**: sessions, memory, and permission
  allow-lists are keyed to the primary clone's path. A bare-hub
  migration re-keys every one of them; `/resume` history and project
  memory would strand at the old path.
- **The adversarial CLI requires a repo-root `.adversarial/`**
  (ADV-0053 tracks making it configurable). A bare hub has no root
  working tree to host it; every worktree would need its own installed
  evaluator set or the symlink scheme extended.
- **Every script assumes a repo-root working tree**: the ASK-0043
  root-resolution preambles resolve `PROJECT_ROOT` from the script
  path, which does not exist in a bare hub.
- Session cwd conventions, retro/task paths in memory, and the
  operator's muscle memory all point at the current primary path.

**Decision: declined at current scale.** The non-bare primary +
per-task worktrees topology captures the isolation benefit without
paying any migration cost. The KIT-0043 recovery recipe (ff `main`
inside the bare repo, work from worktrees) is a tested starting point
if this is ever revisited.

**Revisit triggers** — re-open this decision if any of these change:

1. Claude Code's per-path session/memory/permission scoping model
   changes (e.g. repo-identity-keyed instead of path-keyed).
2. The adversarial CLI's repo-root requirement lifts (ADV-0053).
3. A second operator joins and the primary clone becomes contended.
