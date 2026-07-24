# KIT-0066: Prototype intake — Cowork conversation to planner-ready split pair

**Status**: In Progress
**Priority**: high
**Assigned To**: unassigned
**Estimated Effort**: 4-5 hours
**Created**: 2026-07-24
**Linear ID**: (automatically backfilled after first sync)

## Related Tasks

**Related**: KIT-0058 (preset — supplies most door answers), KIT-0053
(the one door), KIT-0048 (planning shape), KIT-0065 (create-project
aider cleanup — touches the same agent family), KIT-ADR-0027 P3/P7

## Overview

The operator's recurring real-world flow: prototype a tool with a
Claude agent (Cowork), then graduate it into structured development.
Today the graduation is manual. Target end state (operator scenario,
2026-07-24):

1. Operator pastes a **boilerplate handoff prompt** into the
   prototyping conversation; the agent returns a structured brief
   (tech, decisions, context, state, next steps).
2. Operator hands **brief + code folder** to a **project-intake
   agent** in a new tab.
3. Result: the operator's split pair — a plain, publishable **code
   repo** and a private **planning repo** pointed at it (preset
   supplies shape/bots/evaluators/env) — planner-ready.

## Verified runtime facts (planner, 2026-07-24)

- `--name`/`--prefix` are `--new --shape single` only — the door
  REFUSES them for planning (`scripts/local/bootstrap:385-386,
  397-398`). Planning repos have no door-side prefix mechanism; the
  prefix must land via the project-context region.
- `--design-materials` is adopt+single+python only, hard-errored
  otherwise (`bootstrap:383-384, 394-395, 403-404`), and execs an
  interactive claude session.
- The operator preset (`~/Github/agentive-config/preset`) resolves
  shape=planning, bots, evaluators, env-source; `--target-path`/
  `--target-github` remain per-run flags (planning only,
  `bootstrap:389`).
- Non-TTY door runs never hang: every question has a flag; missing
  required answers exit 2.

## Requirements

- **F1 — `PROTOTYPE-HANDOFF-TEMPLATE.md`** (in `.kit/templates/`):
  the paste-able boilerplate for the prototyping agent. Its sections
  MIRROR the bootstrap agent's Step-1 extraction list
  (`.claude/agents/bootstrap.md`: purpose, languages, architecture /
  key components, domain vocabulary, suggested task prefix) PLUS the
  prototype-only knowledge: decisions made and why, what is solid vs
  rough, known issues, dependencies and required secrets (names
  only, never values), and suggested next steps. Next-steps entries
  must be concrete enough to seed backlog tasks. Keep it paste-able:
  one fenced block, no kit jargon the receiving agent can't resolve.
- **F2 — `project-intake` agent** (`.claude/agents/project-intake.md`,
  from AGENT-TEMPLATE): drives the whole graduation in one session.
  Inputs: path to the brief, path to the prototype code folder,
  project name. Steps:
  1. **Code repo**: `git init` + first commit of the prototype code,
     `gh repo create` with a visibility question (default private —
     publishable later; the split exists so this CAN go public), and
     **no kit install** — record in the agent text that the planning
     repo manages it (cite `docs/CROSS-REPO-PATTERN.md`).
  2. **Planning repo**: run the door —
     `bootstrap --new <parent>/<name>-planning --target-path
     ../<name> --target-github <owner>/<name>` — flags only (non-TTY
     safe); everything else resolves from the operator preset. Never
     re-implement door logic; the door's own doctor tail is the
     install verdict, and the door's **exit contract (0/1/2) is the
     interface** the agent programs against (accepted evaluation
     note) — re-verify this spec's runtime-fact anchors against the
     current door before writing the agent.
  3. **Seed from the brief**: fill the planning repo's KIT-LOCAL
     project-context region (tech stack, repo pair, task prefix,
     language, rules) and create initial `1-backlog/` task stubs from
     the brief's next-steps section (task template, prefix-numbered
     from 0001). **Stubs only** (accepted evaluation boundary):
     transcribe next-steps into task-template skeletons — no AI
     elaboration, prioritization, or task decomposition. If backlog
     seeding ever needs more, that is a separate component.
  4. **Finish loudly**: print both repo paths + URLs, the doctor
     verdict relayed from the door, and the exact next action ("open
     a planner tab in `<name>-planning`").
  The agent is user-invoked in a new tab (operator rule: never
  main-thread); it must not delegate via Task.
- **F3 — prefix decision recorded**: the intake agent derives the
  prefix (from the brief's suggestion, else bootstrap-agent's
  derivation rule) and writes it into the project-context region. No
  door changes — verify at implementation where the planning
  scaffold's placeholders expect it and anchor the line numbers in
  the agent text.
- **F4 — zero door changes**: the flow composes existing door runs.
  If implementation discovers a genuine door gap, file it as a
  follow-up task instead of widening this one.
- **F5 — docs**: `docs/CROSS-REPO-PATTERN.md` gains the intake
  recipe (template → agent → pair); README one-liner under the
  setup-door section; `create-project.md` gets a pointer ("for the
  split pair, use project-intake") without other edits (KIT-0065
  owns its cleanup).

## Acceptance Criteria

- [ ] Template exists; sections cover bootstrap's extraction list +
      decisions/state/next-steps; secrets-by-name-only rule stated
- [ ] project-intake agent creates the full pair end-to-end in a
      demo run (scratch prototype folder → two repos; transcript in
      the PR; demo repos cleaned up afterward)
- [ ] Planning repo's project-context region filled from the brief;
      ≥1 backlog task seeded from next-steps; prefix present
- [ ] Code repo has no kit install; visibility question asked;
      decision + rationale cited in the agent text
- [ ] Zero changes to `scripts/local/bootstrap` (F4)
- [ ] Docs updated (F5)

## Success Metrics

- **Quantitative**: operator path from "brief saved" to
  "planner-ready pair" is one agent invocation; demo run completes
  with door exit 0 and doctor verdict relayed
- **Qualitative**: the template produces a brief a fresh agent can
  act on without the original conversation

## Time Estimate

4-5 hours: template 1h, agent 2h, demo + docs 1-2h

## Evaluation

`arch-review-fast` (gemini-2.5-flash, 2026-07-24): **REVISION_SUGGESTED**
— log: `.adversarial/logs/KIT-0066-prototype-intake-flow--arch-review-fast.md`.
Disposition (planner):

1. **CLI abstraction layer — DECLINED.** Fourth appearance of the
   forge-abstraction suggestion class (third declined in KIT-0058).
   The agent is prose instructions, not code; evaluator itself rates
   it minor. Decline-by-reference.
2. **Bootstrap-dependency risk — ACCEPTED** as spec text: exit
   contract 0/1/2 named as the interface (F2.2); anchor
   re-verification at implementation; the demo run in acceptance
   criteria is the requested integration exercise.
3. **Task-seeding scope creep — ACCEPTED** as boundary: stubs only
   (F2.3); a smarter backlog seeder is explicitly a future separate
   component.

No outstanding blockers. Working tree verified clean post-run.
