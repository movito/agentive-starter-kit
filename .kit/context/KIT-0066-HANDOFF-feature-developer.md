# KIT-0066 Handoff — feature-developer

**Task**: `.kit/tasks/4-in-review/KIT-0066-prototype-intake-flow.md`
**Target Codebase**: This repo — NOT a target repo (single-repo mode)
**Prepared**: 2026-07-24 (planner-f5)
**Estimated effort**: 4-5 hours

You are the feature-developer. Implement this task directly — do not
delegate to another agent instance.

## ⚠️ LAUNCH

**Your repository root is
`/Users/broadcaster_three/Github/ask-worktrees/KIT-0066/`** — branch
`feature/KIT-0066-prototype-intake-flow`, fully provisioned
(.venv/.env/evaluators linked). Run `git pull --ff-only` first.
Absolute paths / `git -C` throughout.

## Mission

Make the operator's prototype-graduation flow real: a paste-able
handoff template for the prototyping conversation (Cowork), and a
`project-intake` agent that turns brief + code folder into the
operator's split pair — plain code repo + preset-configured private
planning repo — in one invocation. This is composition around the
door, never modification of it (F4 is binding).

## Verified anchors (planner, 2026-07-24 — re-verify before coding)

- `scripts/local/bootstrap:385-386, 397-398` — `--name`/`--prefix`
  REFUSED outside `--new --shape single`; the planning repo's task
  prefix must land via the project-context region (F3).
- `bootstrap:383-384, 394-395, 403-404` — `--design-materials` is
  adopt+single+python only; do NOT route the brief through it.
- `bootstrap:389` — `--target-path`/`--target-github` planning-only.
- The operator preset is LIVE at `~/Github/agentive-config/preset`
  (`shape: planning`, bots, evaluators yes, env-source) — the door
  resolves it automatically; your demo must NOT depend on its
  specific values (use `--no-preset` or explicit flags in tests so
  the flow works for any operator, then one preset-resolved demo run
  as the operator-path proof).
- Extraction-list source for the template: Step 1 of
  `.claude/agents/bootstrap.md`.
- Agent scaffold: `.kit/templates/AGENT-TEMPLATE.md`; agent creation
  helper `./scripts/optional/create-agent.sh` exists if useful.
- Split-pattern rationale to cite in the agent text:
  `docs/CROSS-REPO-PATTERN.md`.

## Context you must not lose

- **Door exit contract 0/1/2 is your interface** (accepted
  evaluation note). Relay the doctor verdict; never re-derive
  install state.
- **Stubs only for backlog seeding** (accepted boundary) —
  transcription into task-template skeletons, nothing smarter.
- **Code repo gets NO kit install** — the planning repo manages it;
  record the rationale with the CROSS-REPO-PATTERN citation. The
  visibility question defaults private (publishable later — that's
  the point of the split).
- **Secrets discipline in the template**: dependency/secret NAMES
  only, never values — the template must say so explicitly.
- **The agent is user-invoked in a new tab** and must not delegate
  via Task (operator rules; self-identification line in the agent
  per the anti-self-delegation pattern).
- **Declined**: any CLI-abstraction layer inside the agent
  (evaluation disposition #1) — do not add one.

## Test approach

- Ordering rule: local checks green → evaluator trio
  (`echo y | ADVERSARIAL_UNATTENDED=1 …`; log-file-with-verdict is
  the proof; `git status` after every run) → PR open.
- End-to-end demo: scratch prototype folder + scratch brief →
  intake run → verify pair (planning repo doctor tail, context
  region filled, ≥1 backlog stub, code repo kit-free). Transcript in
  the PR; clean up demo repos afterward (remember: no rm -rf
  allowlist yet — use uniquely-named dirs under /tmp and list
  leftovers for the operator).
- Doc/template/agent files are the bulk of the diff — this is a
  doc-dominated task; the trio still runs pre-PR.
- `pytest` directly; `./scripts/core/ci-check.sh` before pushing.

## Evaluation summary

`arch-review-fast`: REVISION_SUGGESTED — CLI-abstraction declined
(4th of its class), exit-contract + anchor-reverify accepted into
F2.2, stubs-only boundary accepted into F2.3. Disposition in the
task file; log:
`.adversarial/logs/KIT-0066-prototype-intake-flow--arch-review-fast.md`.
No outstanding blockers.

## Out of scope

- Any change to `scripts/local/bootstrap` (file follow-ups instead)
- Extending `--design-materials` to planning shape
- create-project agent cleanup (KIT-0065 owns it) beyond the F5
  pointer line
- Smarter backlog seeding; team presets; 0.9.0 removals

## PR sizing

Single PR (template + agent + docs + demo transcript; well under
400 lines of reviewable diff): branch
`feature/KIT-0066-prototype-intake-flow` (already created).
