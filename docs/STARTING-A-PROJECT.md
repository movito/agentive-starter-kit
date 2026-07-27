# Starting a Project

How to go from "I have an idea" (or a prototype) to a working,
planner-ready project — using one permanent clone of this kit as your
project factory.

This guide is written for someone who has never seen the kit before.
It covers the mental model, the three ways to create a project, and
what to do in your first session.

---

## The factory model

You clone **agentive-starter-kit once**, keep that clone forever, and
never build product code inside it. Every project you create is a
**sibling folder** next to it — stamped out by the kit's one setup
door (`scripts/local/bootstrap`) and then independent of the factory.

```
~/Github/
├── agentive-starter-kit/    ← the factory: one permanent clone
├── agentive-config/         ← your operator preset (private, optional)
├── my-product/              ← a code repo the factory created
├── my-product-planning/     ← its planning repo (the split pair)
└── my-notes/                ← a single-repo project
```

Three things follow from this model:

- **The kit clone is where creation happens.** You open a Claude Code
  session in `agentive-starter-kit/` to create projects (the
  `/new-project` command, the `project-intake` agent, the setup door
  itself). You do everything else in the created project's own folder.
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

Author yours conversationally: open a Claude Code session in the kit
clone and run `/setup-preset`. It interviews you in plain language and
writes the file. This is worth doing before your first real project —
most of the door's questions then never come up again.

---

## Three ways to create a project

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

   ```
   Use the project-intake agent. Brief: ~/Downloads/my-prototype-brief.md
   Code: ~/Downloads/my-prototype/
   ```

3. The agent composes the door into both repos (your preset supplies
   the answers), seeds the planning repo's backlog from the brief, and
   finishes by printing a LAUNCH line for the planning repo.

### 2. Blank split pair (production default, no code yet)

The same two-repo shape, started empty. Open a Claude Code session in
the kit clone and run `/new-project` — it asks what you're making, in
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

---

## Tab handoffs: the LAUNCH convention

Kit tooling never asks you to `cd` around inside one long session.
When a step finishes somewhere else — a project got created, a task
got assigned — the tool prints a **LAUNCH block**:

```
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

Open the tab the LAUNCH line named, then **invoke the `planner`
agent** (in a new tab, per the convention above). The planner triages
the backlog — in a graduated prototype it has the seeded tasks from
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
