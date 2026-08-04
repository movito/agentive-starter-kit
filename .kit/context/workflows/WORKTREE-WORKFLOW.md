# Worktree-Based Implementation Sessions

**Purpose**: Per-task git worktrees are the default implementation
topology — the primary clone stays on `main` for the planner, code
happens in isolated worktrees
**Agents**: planner (creation + removal), feature-developer (the session)
**Last Updated**: 2026-07-27 (KIT-0071, worktree provisioning
correctness; previously KIT-0044, codifying the KIT-0043 pilot)

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

One command, run from the repository root (the primary clone's or any
worktree's — the helper always resolves the primary internally):

```bash
./scripts/local/new-worktree.sh <TASK-ID> [slug]
```

The helper:

1. Fetches origin and branches from **fresh `origin/main`** — never a
   local `main` that may be silently stale (the KIT-0043 pilot's
   pre-created branch was 10 commits behind).
2. Provisions the gitignored runtime artifacts from an **explicit,
   enumerated list** maintained inside the helper itself (the helper
   is the source of truth for the list; this doc describes the
   contract). Symlinks are for **read-only use only** — currently
   `.env` and `.adversarial/evaluators/`, symlinked to the primary
   clone. New artifacts get added to the list by name, never via an
   "everything gitignored" glob.
3. Provisions a **real per-worktree `.venv`** (via
   `project setup --no-hooks`) — never a symlink. The pre-KIT-0071
   design symlinked `.venv`; an in-worktree `python3 -m venv --clear`
   followed the link and **emptied the primary clone's venv**
   (KIT-0065), and the shared venv was the KIT-0044 stale-venv
   split-brain in permanent form. Mutable state is never shared behind
   a symlink. `--no-hooks` because git hooks live in the shared common
   git dir and are already installed by the primary's setup. If venv
   provisioning fails (e.g. network), the helper says so and the
   session runs `./scripts/core/project setup --no-hooks` itself.
4. Generates a worktree-local `.serena/project.yml` with a
   **per-worktree project name** (when the primary uses Serena) — see
   the Serena section below.
5. Refuses cleanly if the worktree path or branch already exists.
6. Prints the launch instruction (below).

Deliberately **not** provisioned: `.adversarial/logs/` (regenerates),
tool caches (regenerate on demand), and user-owned untracked
directories such as `.kit/adversarial/` (stay in the primary; never
copied, staged, or deleted).

`project doctor` audits this contract from inside a worktree (the
`worktree-*` checks): a symlinked `.venv` WARNs, a missing or
name-colliding Serena config WARNs, and the shared-by-design set is
enumerated so nobody re-diagnoses it.

## Serena in worktrees

Serena resolves a project **name** to its **registered path** — inside
a worktree, `activate_project("<primary-name>")` targets the PRIMARY
clone, so bulk edits (`replace_in_files`) would hit main's checkout
(KIT-0069, caught pre-use). The rule:

- **Activate by absolute path**, never by the primary's name:
  `activate_project("/path/to/ask-worktrees/<TASK-ID>")`. This
  registers a separate per-path project.
- The helper pre-generates `.serena/project.yml` with a per-worktree
  `project_name` (`<primary-name>-<TASK-ID>`) so path activation is
  one obvious step; the file is gitignored (`.serena/project.yml` and
  `.serena/project.local.yml` in the root `.gitignore`), so removal
  stays clean.

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

## Triage: venv failures inside a worktree

**Symptom**: `Unable to create directory .venv`, `Errno None` from
`shutil.rmtree`, sandbox-blocked deletions, or a venv rebuild that
"succeeds" but breaks tooling in the *primary* clone.

**First move**: `ls -la .venv`. If it is a **symlink**, this is a
pre-KIT-0071 worktree carrying the KIT-0065 destruction vector —
**never** run `python3 -m venv --clear`, `--force` rebuilds, or any
deletion *through* the link (the mutation follows the link into the
primary clone's venv; KIT-0065 emptied it exactly this way). The fix:

```bash
rm .venv                                  # removes the LINK only
./scripts/core/project setup --no-hooks   # real per-worktree venv
```

(`project setup` refuses on its own when `.venv` is a symlink, and
`project doctor` WARNs on one — trust those signals.)

**Scratch directories** (settled policy, operator decision
2026-07-27): the kit's tracked `Bash(rm -rf*)` deny **stays** — it
overrides any allow, by design, and is not a gap to fix. Agents use
`mktemp -d` for scratch space and end the session with a paste-able
sweep list of leftovers for the operator; nothing in the kit asks for
an rm-rf allowlist.

## Triage: pre-commit `pytest: command not found`

**Symptom**: a bare `git commit` in a fresh worktree fails the
pytest-fast hook with `/bin/bash: pytest: command not found`, even though
the worktree has a provisioned `.venv` (KIT-0084 session, 2026-08-04).

**Cause**: git hooks run with the invoking shell's PATH; nothing activates
the worktree's venv for the hook environment.

**Fix**: prefix the PATH for the commit:

```bash
PATH="$PWD/.venv/bin:$PATH" git commit -m "..."
```

Candidate structural fix (unfiled): make the pytest-fast hook entry prefer
`.venv/bin/pytest` when present. Until then, this incantation is the
supported path. Do NOT reach for `SKIP_TESTS=1` for this symptom — that
skips your own tests too.

## Closeout

When the task completes:

1. **Session (feature-developer)**: leave the worktree clean — all
   commits pushed, PR opened/merged per the normal workflow, no
   uncommitted files. The session never removes its own worktree.
2. **Planner**: completes the task in the primary clone (task move to
   `5-done`, retro archived, merged branch deleted).

### Handoff bookkeeping in worktree mode (KIT-0071 retro)

Preflight Gates 5-7 read from the session's cwd, so **the branch must
carry** the task move to `4-in-review` and the review starter. The
**primary clone** simultaneously needs the mirrored working-tree state
for the planner (handoff paths, retro dropped as an untracked file) —
the session prepares these UNCOMMITTED in the primary; the planner
commits them at closeout. After the squash-merge, reconcile in this
order: **restore any conflicting working-tree paths to HEAD, pull
--ff-only, then VERIFY `git rev-parse HEAD` == `origin/main` before
any bookkeeping** — a pull can print "Updating x..y" and still abort
on uncommitted mirrored files, leaving the primary silently stale
(this happened at KIT-0071's own closeout: `project complete` ran
against the pre-merge tree and a fresh worktree got provisioned by
the OLD helper). Then `project complete`, and delete any leftover
duplicate task copy at the old path.

### Identity-reading commands never run in kit worktrees (KIT-0073)

`project reconfigure` (and anything keyed off `.serena/project.yml`)
reads the WORKTREE-LOCAL Serena config — in a worktree named
`<project>-<TASK-ID>` it rewrote identity strings in 9 tracked files
(README H1, CHANGELOG, more) before being caught by `git status` and
reverted. Symptom: tracked files suddenly carry the worktree's
task-suffixed identity. Rule: run identity-reading commands only in
the primary clone; when a doc displays such a command, verify it in
the context the doc addresses (see patterns.yml
`displayed_commands_are_contracts`).

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

**Harness cwd-reset is the standing pattern, not a bug** (confirmed
over two full sessions, KIT-0044 + KIT-0050): the harness resets the
shell's working directory to the primary clone between Bash calls even
when the session tab was opened in the worktree. File tools follow the
session root correctly; **shell commands must use absolute paths or
explicit `cd`/`git -C` prefixes throughout**. Plan for it; do not
re-diagnose it.

Session-generated evaluator inputs (`.adversarial/inputs/`) are
gitignored as of KIT-0046 — they regenerate from git/PR state, and the
persisted review record lives in `.kit/context/reviews/`. A clean
evaluator session therefore removes cleanly. If removal still refuses,
the dirty file is something *else*: inspect it, preserve anything
non-regenerable into the primary clone, and only then `--force`
(preserve-then-force is the fallback, not the routine).

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
