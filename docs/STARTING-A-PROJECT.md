# Starting a Project

How to go from "I have an idea" (or a prototype) to a working,
planner-ready project — using one permanent clone of this kit as your
project factory.

This guide is written for someone who has never seen the kit before.
It covers the mental model, the ways to create a project, and what to
do in your first session.

---

## What you need first

- **Claude Code** installed (`claude --version`) and a Claude account
- **git** configured, plus **gh** (the GitHub CLI), authenticated —
  check with `gh auth status`
- For code projects: **Python 3.10–3.12** and **uvx or pipx** (for
  `adversarial-workflow`); docs-only and planning repos skip the
  toolchain
- Optional: a model-provider API key for adversarial evaluation, and
  Linear if you want task sync (see `docs/LINEAR-INTEGRATION.md`)

Don't audit this by hand. The door validates what it needs as it runs,
and every created project carries the health surface:

```bash
./scripts/core/project doctor  # run inside any created project
```

---

## The factory model

You clone **agentive-starter-kit once**, keep that clone forever, and
never build product code inside it. Every project you create is a
**sibling folder** next to it — stamped out by the kit's one setup
door (`scripts/local/bootstrap`) and then independent of the factory.

```text
~/Github/
├── agentive-starter-kit/    ← the factory: one permanent clone
├── agentive-config/         ← your operator preset (private, optional)
├── my-product/              ← a code repo the factory created
├── my-product-planning/     ← its planning repo (the split pair)
└── my-notes/                ← a single-repo project
```

### How every kit conversation starts

Slash-commands like `/new-project` and `/setup-preset` only exist
INSIDE a Claude Code session — they are not shell commands. The
literal keystrokes, every time:

```bash
cd ~/Github/agentive-starter-kit   # the factory clone
claude                             # opens the Claude Code session
```

Then, at Claude's prompt, type the command — `/new-project`,
`/setup-preset` — or ask for an agent by name. (The interactive agent
menu is also available from the shell: `./.kit/launchers/launch`.)
Everywhere this guide says "run /X in the kit clone", it means exactly
these steps.

Three things follow from this model:

- **The kit clone is where creation happens.** You start a session in
  `agentive-starter-kit/` (as above) to create projects — the
  `/new-project` command, the `project-intake` agent, the setup door
  itself. You do everything else in the created project's own folder.
- **Projects never contain the factory.** A created project gets the
  agents, scripts, and workflow it needs — not the kit's git history,
  its internal tasks, or the door.
- **Navigation is by tabs, not `cd`.** When a tool finishes creating
  something, it prints where to go next; you open a new tab there
  (see [Tab handoffs](#tab-handoffs-the-launch-convention) below).

Set up the factory once:

```bash
cd ~/Github  # or wherever your projects live
git clone https://github.com/movito/agentive-starter-kit.git
```

## The one setup door

Every creation flow below ends up running the same script —
`scripts/local/bootstrap`, "the door". It asks the install questions
(or reads them from your preset), validates the answers, and runs the
engines that write the project. You never need a second setup path,
and this guide deliberately does not duplicate the door's option
matrix — the authoritative, always-current reference is:

```bash
cd ~/Github/agentive-starter-kit && ./scripts/local/bootstrap --help
```

If anything here and that help output ever disagree, the help output
wins.

### The operator preset (answer the questions once)

The door resolves every question as **CLI flag → preset → kit default
→ interactive prompt**. A preset file at
`<kit-parent>/agentive-config/preset` — a visible sibling of the kit
clone — pre-answers the door's questions (project shape, review bots,
evaluator install, secrets file, and so on), so with a filled preset,
creating a project is genuinely one command with zero questions.

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
  `./scripts/core/project doctor --against-preset`.
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
2. **Hand it to the intake agent.** Open a **new tab** in the kit
   clone and invoke the `project-intake` agent, giving it the brief
   and the code folder:

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

Direct door use (no interview) works too; see `--shape planning` and
the target-pointer flags in `bootstrap --help`.

### 3. Single repo (small tools, notes, experiments)

Everything — planning and code — in one repo. This is the door's
default shape. `/new-project` offers it, or run the door directly:

```bash
cd ~/Github/agentive-starter-kit && ./scripts/local/bootstrap --new ~/Github/my-tool
```

Docs-only repos (no Python toolchain) are a profile choice within this
shape — again, `bootstrap --help` is the reference.

### 4. Adopt an existing repo (you already have a project)

Bootstrap an existing repo with the implementation tools — agents,
scripts, commands, and the minimal `.kit/` workflow skeleton — without
the full builder layer:

```bash
cd ~/Github/agentive-starter-kit && ./scripts/local/bootstrap --adopt ~/Github/my-app
```

Add `--no-kit` to skip the task-management workflow entirely.
Docs-only and planning variants are shape × profile choices —
`bootstrap --help` is the reference, as always.

**Running without the full review stack?** Declare it and the
completion gates stay honest: `--bots none` (or a subset like
`--bots coderabbit`) records the declaration, so preflight reports
SKIP for the missing bots instead of failing falsely. Installing the
CodeRabbit / BugBot GitHub Apps is an operator step the kit never
automates, and single-key evaluation mode is documented in the
`code-review-evaluator` skill.

---

## Other ways through the door

Both of these end at the same door — they exist for when you're not
sitting in a permanent kit clone yet.

- **From a URL (zero setup).** Open Claude Code anywhere and paste:

  ```text
  https://github.com/movito/agentive-starter-kit

  Please set up a new project from this kit.
  ```

  Claude clones the kit and follows the `create-project` agent's
  recipe — same questions, same door. Honest caveat: this relies on
  Claude reading and following the recipe in the main session, so it
  is not a deterministic script and behavior may vary slightly between
  sessions. For a predictable run, clone the kit and use the agent
  directly.

- **The `create-project` agent (deterministic).** From a kit clone,
  open Claude Code and ask: *"Use the create-project agent to set up a
  new project for me."* The agent asks for the target directory, name,
  task prefix, and GitHub visibility, then runs the door, sets your
  project identity, installs evaluators, and creates the GitHub repo.
  The agent file (`.claude/agents/create-project.md`) is the
  authoritative recipe.

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

- **Agents run in new tabs, never in your main thread.** The main
  session is for coordination; an agent invocation gets its own tab so
  its context stays clean and yours stays yours.
- **One tab per working directory.** A planning repo tab plans; a code
  repo tab codes. The printed LAUNCH path always tells you which one
  you're opening.

## Your first session in a new planning repo

Open the tab the LAUNCH line named **as a planner session** — start it
with `claude --agent .claude/agents/planner.md`, or open the tab and
ask for the planner agent by name. (That tab *is* the agent's tab; no
further hop needed.) The planner triages the backlog — in a graduated prototype it has the seeded tasks from
your brief; in a blank pair it helps you write the first tasks — and
recommends what to start. The seeded `CLAUDE.md` in every new project
carries this same first-session instruction, so an agent opening the
project cold knows it too.

After that, the working loop is the kit's normal one: the planner
prepares and assigns tasks, feature developers implement them in their
own tabs, and completion gates (`/preflight`, review bots, evaluators)
keep the work honest.

## Checking your environment

Whenever something seems off — missing tools, keys, or config — run
the health surface from inside any created project:

```bash
./scripts/core/project doctor  # incident-mapped environment checks
```

---

## Where things are

| You want | Where |
|----------|-------|
| The door's full option reference | `./scripts/local/bootstrap --help` (in the kit clone) |
| A guided interview instead of flags | `/new-project` (in the kit clone) |
| Your preset, authored conversationally | `/setup-preset` (in the kit clone) |
| The split-pair pattern explained | `docs/CROSS-REPO-PATTERN.md` |
| The prototype handoff template | `.kit/templates/PROTOTYPE-HANDOFF-TEMPLATE.md` |
| Health checks in a created project | `./scripts/core/project doctor` |
| Linear task sync | `docs/LINEAR-INTEGRATION.md` |
| Keeping a created project updated | `docs/UPDATING-YOUR-PROJECT.md` |
