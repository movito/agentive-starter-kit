# Starting a Project

How to go from "I have an idea" (or a prototype) to a working,
planner-ready project — with the packaged setup door, `agentive new`
and `agentive adopt`, which run from wherever you are.

This guide is written for someone who has never seen the kit before.
It covers the mental model, the ways to create a project, and what to
do in your first session.

---

## What you need first

- **Claude Code** installed (`claude --version`) and a Claude account
- **git** configured, plus **gh** (the GitHub CLI), authenticated —
  check with `gh auth status`
- **uv** (or any isolated-CLI installer) for the two tool installs
  every project uses: `uv tool install agentive-kit` (the `agentive`
  lifecycle CLI) and `uv tool install adversarial-workflow` (the
  evaluation CLI — `agentive install-evaluators` handles this one for
  you)
- Optional: a model-provider API key for adversarial evaluation, and
  Linear if you want task sync (see `docs/LINEAR-INTEGRATION.md`)

Don't audit this by hand. The door validates what it needs as it runs
— anything missing becomes a printed install instruction, never a
failure — and every created project has the health surface:

```bash
agentive doctor   # any project the door created (new or adopted)
# pre-packaged-era projects (script copies) instead run:
# ./scripts/core/project doctor
```

---

## The sibling layout

Project creation is a package command — `agentive new` /
`agentive adopt`, installed with `uv tool install agentive-kit` — and
runs from wherever you are. **No kit clone is required to create a
project.** What is worth keeping is the layout: your projects side by
side in one folder, with your operator preset as a visible sibling:

```text
~/Github/
├── agentive-config/         ← your operator preset (private, optional)
├── my-product/              ← a code repo the door created
├── my-product-planning/     ← its planning repo (the split pair)
├── my-notes/                ← a single-repo project
└── agentive-starter-kit/    ← optional: the kit's development home
```

The kit clone is the *development* home for the kit itself — and the
home of the guided interviews: `/new-project` and `/setup-preset` are
builder-side commands whose files live in this repo, so they run in a
Claude Code session opened there. The `project-intake` agent ships
with the `agentive-workflow` plugin (KIT-ADR-0031) and runs anywhere
the plugin is installed — its natural home is the prototype's own
folder. Creating a project never requires the kit clone: the door is
the package.

### Where the guided flows run

Slash-commands like `/new-project` and `/setup-preset` only exist
INSIDE a Claude Code session — they are not shell commands — and their
command files ship with this repo, so the session is one opened in
your kit clone:

```bash
cd ~/Github/agentive-starter-kit   # the kit's development home
claude                             # opens the Claude Code session
```

Then, at Claude's prompt, type the command — `/new-project`,
`/setup-preset` — or ask for an agent by name. (The interactive agent
menu is also available from the shell: `./.kit/launchers/launch`.)
Everywhere this guide says "run /X in the kit clone", it means exactly
these steps. Prefer flags over interviews? Skip the session entirely
and run the door directly from any terminal.

Three things follow from this model:

- **Creation happens wherever you are.** `agentive new <dir>` /
  `agentive adopt <dir>` are package subcommands with no path
  relationship to any kit checkout. The guided flows above are
  interviews that drive the same door for you.
- **Projects never contain the kit — and carry no copies of its
  machinery.** A project the door creates is born *packaged*
  (KIT-ADR-0028): it contains content (task folders, templates,
  workflow docs, config, records) while the tooling is **installed** —
  lifecycle scripts via the `agentive-kit` PyPI package,
  agents/skills/commands via the `agentive-workflow` Claude Code
  plugin. The door verifies both installs or prints the exact install
  commands. This holds for `adopt` too — it writes the same content
  skeleton and copies no tooling.
- **Navigation is by tabs, not `cd`.** When a tool finishes creating
  something, it prints where to go next; you open a new tab there
  (see [Tab handoffs](#tab-handoffs-the-launch-convention) below).

Want the kit's development home — for the guided flows, or to work on
the kit itself? Clone it once:

```bash
cd ~/Github  # or wherever your projects live
git clone https://github.com/movito/agentive-starter-kit.git
```

## The one setup door

Every creation flow below ends up running the same command —
`agentive new` / `agentive adopt`, "the door". It asks the install
questions (or reads them from your preset), validates the answers, and
runs the engines that write the project. You never need a second setup
path, and this guide deliberately does not duplicate the door's option
matrix — the authoritative, always-current reference is:

```bash
agentive new --help     # and: agentive adopt --help
```

If anything here and that help output ever disagree, the help output
wins. (Inside a kit checkout, `scripts/local/bootstrap` still works as
an exec shim over the same packaged door; its removal is pinned to the
next minor release — KIT-0107.)

### The operator preset (answer the questions once)

The door resolves every question as **CLI flag → preset → kit default
→ interactive prompt**. A preset file at
`<projects-parent>/agentive-config/preset` — the door anchors the
config home to the TARGET's parent, so keep it a visible sibling of
your projects folder (`AGENTIVE_KIT_CONFIG_DIR` overrides the
location) — pre-answers the door's questions (project shape, review
bots, evaluator install, secrets file, and so on), so with a filled
preset, creating a project is genuinely one command with zero
questions.

Author yours conversationally: start a session in the kit clone
(`cd ~/Github/agentive-starter-kit && claude`) and type
`/setup-preset` at Claude's prompt. It interviews you in plain
language and writes the file. This is worth doing before your first real project —
most of the door's questions then never come up again.

A few rules keep the preset safe:

- **Never distributed.** It lives outside every repo; no sync tier or
  export touches the config home. `--no-preset` gives a stranger-mode
  run.
- **Guardrails, not obscurity.** On first use the door seeds a
  `.gitignore` and README into the config home; keeping the folder in
  a *private* git repo is welcome, and `project doctor` checks it
  (WARN on a public remote, FAIL on a tracked `env.source`).
- **Secrets by reference.** `env-source: <path>` names your own `.env`
  template; on `--new` the door copies it to the target (mode 0600) —
  contents are never printed and never staged.
- **Records beat presets.** On `--adopt` of a project that already
  carries a kit-install record, the record wins; compare with
  `agentive doctor --against-preset`.
- **Malformed fails loud.** A bad line aborts naming the line; unknown
  keys warn and are skipped.

---

## Four ways to create a project

### 1. Graduate a prototype (you already have code)

You prototyped something in a Claude (Cowork) conversation, or you
have a folder of working code, and now it deserves a real home. The
result is the **split pair**: a plain, publishable code repo plus a
private planning repo that manages it (why this split: see
`docs/CROSS-REPO-PATTERN.md`).

1. **Produce the handoff brief.** In the conversation that built the
   prototype, paste the contents of
   `.kit/templates/PROTOTYPE-HANDOFF-TEMPLATE.md` and let it fill the
   template in. Save the result as a markdown file.
2. **Hand it to the intake agent.** Open a **new tab** in the
   prototype's code folder — the agent ships with the
   `agentive-workflow` plugin, so it runs right where the deliverable
   sits — and invoke the `project-intake` agent, giving it the brief
   (the code folder itself is the default candidate when you open the
   tab there):

   ```text
   Use the project-intake agent. Brief: ~/Downloads/my-prototype-brief.md
   Code: ~/Downloads/my-prototype/
   ```

3. The agent composes the door into both repos (your preset supplies
   the answers), seeds the planning repo's backlog from the brief, and
   finishes by printing a LAUNCH line for the planning repo.

### 2. Blank split pair (production default, no code yet)

The same two-repo shape, started empty. Start a session in the kit
clone (`cd ~/Github/agentive-starter-kit && claude`) and type
`/new-project` at Claude's prompt — it asks what you're making, in
plain language, and drives the door for you.

Direct door use (no interview) works too, from any terminal; see
`--shape planning` and the target-pointer flags in
`agentive new --help`.

### 3. Single repo (small tools, notes, experiments)

Everything — planning and code — in one repo. This is the door's
default shape. `/new-project` offers it, or run the door directly:

```bash
agentive new ~/Github/my-tool
```

Docs-only repos (no Python toolchain) are a profile choice within this
shape — again, `agentive new --help` is the reference.

### 4. Adopt an existing repo (you already have a project)

Install the agentive workflow into a repo that already exists — the
`.kit/` content skeleton, records, and pins — preserving every file
already present. Adopt is packaged-mode like `new`: no kit checkout
or local tooling is copied; lifecycle scripts come from the
`agentive-kit` package and agent bodies from the plugin.

```bash
agentive adopt ~/Github/my-app
```

Add `--no-kit` for rung 0 (KIT-ADR-0032): a plain repo with no
`.kit/` and no kit install — the flag exists on BOTH verbs.
Docs-only and planning variants are shape × profile choices —
`agentive adopt --help` is the reference, as always.

**Running without the full review stack?** Declare it and the
completion gates stay honest: `--bots none` (or a subset like
`--bots coderabbit`) records the declaration, so preflight reports
SKIP for the missing bots instead of failing falsely. Installing the
CodeRabbit / BugBot GitHub Apps is an operator step the kit never
automates, and single-key evaluation mode is documented in the
`code-review-evaluator` skill.

---

## Starting from zero (no kit clone)

You do not need one. Install the CLI and run the door:

```bash
uv tool install agentive-kit   # or: pipx install agentive-kit
agentive new ~/Github/my-tool
```

Clone the kit only when you want the guided interviews — the
`/new-project` interview (the one user-facing entry for every
situation: prototype, blank pair, single repo — it routes to the
right flow itself) and `/setup-preset` — or to work on the kit
itself. (The `project-intake` agent needs no clone: it ships with the
`agentive-workflow` plugin.) See [The sibling
layout](#the-sibling-layout) above for the clone command. (The
retired `create-project` agent's job folded into `/new-project` + the
door in KIT-0093; if you find a live user-facing reference to it,
it's stale — historical records and changelogs mention it
accurately.)

---

## Tab handoffs: the LAUNCH convention

Kit tooling never asks you to `cd` around inside one long session.
When a step finishes somewhere else — a project got created, a task
got assigned — the tool prints a **LAUNCH block**:

```text
⚠️ LAUNCH
Open a new tab with working directory /Users/you/Github/my-product-planning
```

That printed path **is** the navigation mechanism: open a new Claude
Code tab (or terminal) at that path and continue there. Two habits
make this work:

- **Agents run in new tabs, never in your main thread.** Agent
  identity is fixed at session launch — a running session cannot
  become another agent mid-flight — so an agent invocation gets its
  own tab; a different contract starts on fresh context, and your
  coordination thread stays yours.
- **One tab per working directory.** A planning repo tab plans; a code
  repo tab codes. The printed LAUNCH path always tells you which one
  you're opening.

## Your first session in a new planning repo

Open the tab the LAUNCH line named and invoke the **`planner` agent
by name** — it is provided by the `agentive-workflow` plugin (the
door's tail printed the install lines if the plugin is missing).
(That tab *is* the agent's tab; no further hop needed.) The planner
triages the backlog — in a graduated prototype it has the seeded tasks from
your brief; in a blank pair it helps you write the first tasks — and
recommends what to start. The seeded `CLAUDE.md` in every new project
carries this same first-session instruction, so an agent opening the
project cold knows it too.

After that, the working loop is the kit's normal one: the planner
prepares and assigns tasks, feature developers implement them in their
own tabs, and completion gates (`/preflight`, review bots, evaluators)
keep the work honest.

## API keys: the operator moves them, never an agent

Every `--new` project starts with a working `.env`: the door seeds it
(mode 0600, gitignored) from your preset's `env-source` when you have
one, else from the project's own `.env.template`, and fills
`PROJECT_NAME`/`TASK_PREFIX`. What the door cannot invent is your API
keys. With no `env-source` there is nothing to carry them over from —
the door says so out loud ("No API keys seeded"), and
`agentive doctor`'s `env-keys` check names what is missing until you
add them to the project's `.env` by hand (a preset `env-source` seeds
them automatically next time).

**Move the keys yourself — do not ask an agent to.** Copying key
material into a project is an operator-only act: the Claude Code
permission classifier blocks agents from doing it (correctly — secrets
handling), so an agent session asked to "fix the missing keys" can
only stall. The seeded `CLAUDE.md` first-session note and
`agentive doctor`'s `env-keys` check both surface still-missing keys
before they can block your first evaluation.

## Checking your environment

Whenever something seems off — missing tools, keys, or config — run
the health surface from inside any created project:

```bash
agentive doctor   # incident-mapped environment checks
```

(Which world is your project in? Check for a `scripts/core/`
directory: absent → packaged, run `agentive doctor`; present → a
pre-packaged project that runs `./scripts/core/project doctor`
instead — see `docs/UPDATING-YOUR-PROJECT.md`.)

---

## Where things are

| You want | Where |
|----------|-------|
| The door's full option reference | `agentive new --help` / `agentive adopt --help` (any terminal) |
| A guided interview instead of flags | `/new-project` (in a kit-clone session) |
| Your preset, authored conversationally | `/setup-preset` (in a kit-clone session) |
| The split-pair pattern explained | `docs/CROSS-REPO-PATTERN.md` |
| The prototype handoff template | `.kit/templates/PROTOTYPE-HANDOFF-TEMPLATE.md` |
| Health checks in a created project | `agentive doctor` |
| Linear task sync | `docs/LINEAR-INTEGRATION.md` |
| Keeping a created project updated (and the rename procedure) | `docs/UPDATING-YOUR-PROJECT.md` |
