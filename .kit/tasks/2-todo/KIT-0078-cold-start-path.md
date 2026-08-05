# KIT-0078: The cold-start path — instruct, don't interrogate

**Status**: Todo
**Priority**: high
**Assigned To**: unassigned
**Estimated Effort**: 1 day
**Created**: 2026-07-29
**Linear ID**: (automatically backfilled after first sync)

## Related Tasks

**Parent**: operator cold-start test 2026-07-29 — five snags in one
afternoon, none visible to per-part gates
**Related**: KIT-0067 (front door), KIT-0066 (intake), KIT-0075
(launcher F2 — native invocation), KIT-0073 (README)
**Sibling (provisioning half)**: KIT-0087 — one provisioning story.
This task decides WHICH door a user walks through; KIT-0087 makes every
door install the same toolchain. Both touch `create-project.md`,
`new-project.md`, `STARTING-A-PROJECT.md`, and `README.md` — land them
together or 0078 first, else two passes over the same files and a
near-certain conflict. F2's "create-project agent: deprecation pointer
or folds away" decision determines how much of KIT-0087 F3 survives.
**Pairing decided (planner, 2026-08-05)**: combined assignment — one
session implements 0078 then 0087 on one branch (stacked PRs if large);
0078's F2 verdict lands first inside the session.

## Overview

Operator verdict, verbatim: **"Everything is backwards; we should
tell the user what to do from the README, not ask them to guess how
this works."** Every part works in isolation; the cold-start JOURNEY
strands a newcomer at the seams: four competing entry surfaces, a
silent launcher-invoked agent that lost its persona to ambient
context, "open a Claude Code session" hand-waves (fixed 9020969),
and an interview that demands artifacts (the brief) the user was
never told to create. Design principle for everything in this task:
**docs instruct in sequence; agents confirm and receive.** By the
time any agent asks for something, the user must already have it and
know why.

## The five recorded snags (evidence base)

1. create-project agent silent at launch; persona lost to
   CLAUDE.md/memory on "Are we ready?" (interim contracts shipped
   576266a; real fix = KIT-0075 F2 native invocation).
2. "Open a Claude Code session and run /X" assumed slash-command
   knowledge (fixed 9020969 — keep and extend the pattern).
3. Intake demanded a brief the user didn't know how to produce.
4. AskUserQuestion misused for free-text paths → tool error →
   awkward recovery.
5. Four user-facing entry surfaces (launcher, create-project agent,
   project-intake agent, /new-project) with no stated hierarchy.

## Requirements

- **F1 — README + STARTING-A-PROJECT become DO-THIS sequences**:
  numbered, keystroke-literal steps per route that PRODUCE each
  artifact before it's needed. Prototype route: (1) paste
  PROTOTYPE-HANDOFF-TEMPLATE into your prototyping conversation,
  (2) save the reply as e.g. `~/Github/my-tool/BRIEF.md` next to the
  code, (3) note both paths, (4) `cd ~/Github/agentive-starter-kit
  && claude`, (5) type `/new-project`, (6) give it the two paths
  when asked. Blank route: steps 4-5 only. Adopt route similarly.
  The reader never meets a question the docs didn't preview.
- **F2 — ONE user-facing entry**: `/new-project` is THE starting
  action for every situation, stated identically in README and
  STARTING-A-PROJECT. The launcher, create-project agent, and
  project-intake agent are demoted to plumbing/reference (intake is
  what /new-project routes to; create-project agent gets a
  deprecation pointer or folds away — decide at implementation with
  a grep of what still needs it; launcher remains the agent-menu
  for WORK sessions, not creation).
- **F3 — /new-project and intake open by INSTRUCTING**: first
  output states the route map and expected inputs with their
  origins ("If you have a prototype: I need the brief [made from
  the template — here's how if you don't have one] and the code
  path. If you have nothing: we go blank, two questions total.").
  "I have nothing yet" is the FIRST offered option everywhere.
  Missing artifact → the agent explains how to produce it or
  reroutes; it never dead-ends or demands.
- **F4 — interview mechanics rule**: free-text inputs (paths,
  names) are asked as plain questions, never as AskUserQuestion
  option lists. One line in both command texts + the intake agent;
  candidate for a patterns.yml interview-mechanics entry if a third
  surface repeats it.
- **F5 — the acceptance test IS the journey**: a cold-start
  transcript — fresh session, empty hands, README as the only
  guide — reaching a working project on BOTH routes (blank; and
  prototype using a scratch prototype+brief). Zero guesses required:
  every step the tester takes must be one the docs or agent
  explicitly named. Transcript in the PR.

## Acceptance Criteria

- [ ] F1 sequences in place; every question any flow asks is
      previewed by the docs
- [ ] One stated entry point; other surfaces demoted with pointers
- [ ] /new-project + intake open with the route map; "nothing yet"
      first; no artifact dead-ends
- [ ] Free-text-vs-option rule applied
- [ ] Both cold-start transcripts in the PR (F5)
- [ ] Planner tree-grounded verification before merge (prose/UX
      diff — fast-only trio per standing rule)

## Notes

- Evaluation: arch-review-fast (2026-07-29): **REVISION_SUGGESTED**
  — findings endorse F1-F5; the one push (ACCEPTED as sequencing):
  the persona/ambient-context fragility is the deeper risk and
  KIT-0075 F2 (native `claude --agent` invocation) must follow
  IMMEDIATELY after this task rather than sit in backlog. KIT-0075
  is hereby promoted to next-after-0078. Log:
  `.adversarial/logs/KIT-0078-cold-start-path--arch-review-fast.md`.
- The five snags above are the checklist; the operator's verdict is
  the design principle. patterns.yml `displayed_commands_are_contracts`
  (claims clause) applies to every printed instruction.
