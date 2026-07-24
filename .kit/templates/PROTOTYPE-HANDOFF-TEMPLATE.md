# Prototype Handoff Template

**Version**: 1.0.0
**Created**: 2026-07-24 (KIT-0066)
**Purpose**: Paste-able boilerplate for graduating a prototype out of a
prototyping conversation (Cowork or any Claude session) into structured
development.
**Consumed by**: the `project-intake` agent
(`.claude/agents/project-intake.md`), which turns the resulting brief +
the prototype code folder into the split pair — a plain code repo and a
preset-configured planning repo (`docs/CROSS-REPO-PATTERN.md`).

---

## How to use it

1. Near the end of a prototyping conversation, paste the fenced block
   below as a message to the prototyping agent.
2. Save the brief it returns as `PROTOTYPE-BRIEF.md` — inside the
   prototype code folder is the convention the intake agent looks for
   first, but any saved location works.
3. Open a new tab from your agentive-starter-kit checkout, invoke the
   `project-intake` agent, and give it the brief path, the code folder
   path, and (optionally) the project name. It does the rest.

The section list below mirrors what the kit's bootstrap agent extracts
from design materials (`.claude/agents/bootstrap.md`, Step 1), plus the
knowledge that only exists in a prototyping conversation: decisions and
their reasons, what is solid versus rough, known issues, dependencies
and secret NAMES, and concrete next steps. A good brief lets a fresh
agent act without ever seeing the original conversation.

---

## The paste-able block

````markdown
Please write a structured handoff brief for this prototype. It will be
read by a fresh agent that has NOT seen this conversation, so make it
self-contained. Return it as a single markdown document with exactly
these sections:

## Project name and purpose
The working name and 1-2 sentences on what this tool does and for whom.

## Languages and runtimes
Programming languages, runtime versions, and frameworks actually used.

## Architecture and key components
The 3-7 main parts (modules, services, data models, APIs) and how they
fit together. One line each is enough.

## Domain vocabulary
The domain terms we settled on in this conversation, with one-line
definitions — the words a new agent must use for naming to stay
consistent.

## Suggested task prefix
A short uppercase task-ID prefix derived from the project name — no
hyphens, max 6 characters (e.g. "recipe-api" → RECIPE, "my-cool-app"
→ MCA). Tasks will be numbered PREFIX-0001, PREFIX-0002, …

## Decisions made and why
Every significant choice we made (library picks, data shapes, approaches
tried and abandoned) with a one-line reason each. This is the section a
future agent cannot reconstruct from the code — be generous.

## State: solid vs rough
Two lists. Solid: what works and has been exercised. Rough: what is
stubbed, hardcoded, untested, or known-fragile.

## Known issues
Bugs, limitations, and edge cases we observed, one line each.

## Dependencies and required secrets
External packages/services the prototype needs, and the NAMES of any
required secrets or API keys (e.g. OPENAI_API_KEY). Secret NAMES ONLY —
never paste values, tokens, or any part of them into this brief.

## Suggested next steps
3-8 concrete steps to take this beyond prototype, in dependency order
(foundational first). Each entry needs: a short actionable title, 1-2
sentences of what and why, and a "done when" line. Each entry will be
transcribed directly into a backlog task, so write them specific enough
that someone could start work from the entry alone.
````

---

## Rules the brief must follow

- **Secrets by name only.** The brief names required keys
  (`OPENAI_API_KEY`), never their values. If a value was pasted into
  the prototyping conversation, it does NOT belong in the brief.
- **Self-contained.** No "as discussed above" — the reader has not seen
  the conversation.
- **Next steps seed the backlog.** The intake agent transcribes them
  into task stubs verbatim (no elaboration), so vague entries become
  vague tasks.
