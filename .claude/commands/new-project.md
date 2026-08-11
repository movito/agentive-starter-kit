---
description: Interview the user and create their new project through the setup door or the intake agent
version: 1.1.0
origin: agentive-starter-kit
last-updated: 2026-07-28
created-by: "@movito with feature-developer-f5 (KIT-0067)"
distribution: builder-only
---

# New Project

> **Builder-side command**: operates the kit factory; not distributed
> via `scripts/.core-manifest.json` (intended — see KIT-0077).

Create a new project from this kit — the front door to the factory
flow described in `docs/STARTING-A-PROJECT.md`. Interview the user in
plain language, one question at a time, route them to the right
creation path, run it, and finish by printing the LAUNCH line for the
created project.

This command runs **from an agentive-starter-kit checkout** (the setup
door is kit-side only). If `./scripts/local/bootstrap` does not exist
in the current repo, STOP and tell the user to open a session in their
kit clone — never hunt for the door elsewhere.

## Binding rules — read before anything else

1. **Derive, never hardcode.** Your FIRST action is:

   ```bash
   ./scripts/local/bootstrap --help
   ```

   Build the entire interview from what that prints: the creation
   modes, the shape × profile legality matrix, the offer flags, and
   the preset/resolution-chain semantics. This command deliberately
   contains **no flag list or shape matrix of its own** — if it named
   them, it would drift from the door (runtime-read, per ADR-0025).
   If this file and the door's help ever appear to disagree, the help
   output wins. If the help does not answer something the flow needs,
   STOP and say so to the user — never guess or improvise an answer.

2. **Public surfaces only.** You interact with the door exclusively
   through its CLI flags, and with the `project-intake` agent
   exclusively through its documented inputs (a handoff brief and a
   code folder — see `.claude/agents/project-intake.md`). Never
   re-implement, patch, or partially reproduce what either of them
   does; you compose them.

3. **Plain language, one question at a time.** Never dump options on
   the user. For each question, explain what it decides and what each
   choice costs or unlocks in ordinary words. Offer an **expert
   shortcut** up front: a user who says "just use my preset/defaults"
   skips the interview — pass only what the door cannot default (per
   its help output) and let the preset answer the rest.

4. **Secrets never transit the chat.** If the user pastes anything
   that looks like key material (API keys, tokens, passwords),
   REFUSE it. Secrets reach a new project only by reference, through
   the preset's secrets-file key (authored via `/setup-preset`,
   edited in the user's own editor).

## Step 1: route the flow

Ask the routing question first, in plain words: **does a prototype
already exist** (code from a Claude/Cowork conversation, or a folder
of working code), or is this a fresh start?

- **Prototype exists → the intake route (Step 2a).**
- **Fresh start → the door route (Step 2b).** The door's help output
  defines the available shapes; present them as plain-language
  choices (roughly: a split planning+code pair for production work,
  or a single repo for smaller things — but derive the actual set
  from the help).

## Step 2a: prototype route (project-intake)

The intake agent needs two inputs; collect what's missing:

1. **The handoff brief.** If the user doesn't have one yet, point
   them at `.kit/templates/PROTOTYPE-HANDOFF-TEMPLATE.md`: paste it
   into the conversation that built the prototype, save the filled
   result as a markdown file, and come back.
2. **The code folder.** The path to the prototype's code.

Before handing off, confirm the brief is a readable, non-empty file
and the code path is a directory — a dangling or wrong-kind path
should be caught here, not by the intake agent one tab later.

Then hand off — agents run in a **new tab**, never in this session.
Print the invocation for the user:

```text
⚠️ LAUNCH
Open a new tab in this kit checkout and paste:

  claude --agent project-intake "Begin the intake. Brief: <path-to-brief.md>  Code: <path-to-code-folder>"
```

**The opening message is part of the command, not decoration.** A session
cannot speak first: `project-intake` runs a FIRST-TURN CONTRACT that
fires on the first USER message, so a launch without one leaves the
operator at an idle prompt wondering whether anything loaded (KIT-0075,
reproduced live under native `--agent` on 2026-08-11). If you ever print
a launch line without the message, print with it: "the agent waits for
your first message — type `begin`".

The intake agent runs the door itself and prints the final LAUNCH
line for the planning repo when it finishes. Your job ends at this
handoff — do not run the door yourself on this route.

## Step 2b: fresh-start route (the door)

1. Interview for what the door needs (rule 1: derived from
   `--help`; rule 3: one question at a time). Typically that is the
   target directory, the shape, and — where no preset or default
   answers them — the door's offers. Tell the user when their preset
   is answering questions for them (the door announces the preset
   path it loaded; a `--no-preset` run is available if they want to
   be asked everything).
2. Run the door with exactly the flags the interview produced, e.g.:

   ```bash
   ./scripts/local/bootstrap --new <target-dir> <flags-from-interview>
   ```

3. Show the user the door's output — especially the doctor verdict it
   ends with. If the door exits non-zero, report the failure honestly
   and stop; do not retry with guessed flags.

## Step 3: finish loudly

End with the LAUNCH line for wherever work continues (the door route:
the created project; on a planning shape, that's the planning repo):

```text
⚠️ LAUNCH
Open a new tab in <absolute-path-to-created-project> and paste:

  claude --agent planner "Triage the backlog and recommend what to start."
```

The launch line carries its opening message for the same reason as the
intake handoff above — a session cannot speak first, so a bare `claude
--agent planner` just idles. The `planner` agent ships with the
`agentive-workflow` plugin (the door's tail printed the install lines if
it is missing); it triages the backlog and recommends what to start, and
the project's seeded `CLAUDE.md` and README say the same thing.
