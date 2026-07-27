# KIT-0067: The factory front door + structural cleanup

**Status**: In Review
**Priority**: high
**Assigned To**: unassigned
**Estimated Effort**: 1-1.5 days
**Created**: 2026-07-24
**Linear ID**: (automatically backfilled after first sync)

## Related Tasks

**Parents**: operator flow question (2026-07-24: "the user needs a
consistent place to start their projects from... I want the flow to
be straightforward") + the pre-0.9.0 cruft audit's structural
findings (`.kit/context/reviews/PRE-090-CRUFT-AUDIT-2026-07-24.md`)
**Related**: KIT-0066 (project-intake — the flow this fronts),
KIT-0058 (/setup-preset — the command style to copy), KIT-0054
(door shims removal, 0.9.0 — the launchers join that removal story)

## Overview

Two halves that solve each other. The operator's mental model — ONE
kit clone as the permanent factory; projects and config as siblings;
navigation by opening tabs at printed paths — is real but nowhere
written, and the factory has no single entry point. Meanwhile the
audit confirmed the kit still carries a SECOND setup entrance (the
pre-door `.kit/launchers/` + onboarding agent, A33/A45 + uncertain
finding) and a shelf of dead or foreign docs. Ship the front door;
retire what it supersedes.

## Requirements

- **F1 — `docs/STARTING-A-PROJECT.md`**: the operator flow, written
  for someone who has never seen the kit. The factory model (one
  clone, siblings layout diagram), the three creation flows
  (prototype graduation via PROTOTYPE-HANDOFF-TEMPLATE +
  project-intake; blank split pair; single-repo), the tab-handoff
  convention (LAUNCH blocks are the navigation mechanism), and what
  to do first in a new planning repo. README links it prominently.
- **F2 — `/new-project` command** (`.claude/commands/new-project.md`,
  /setup-preset's structural rules): NO hardcoded flag list — derive
  choices from `./scripts/local/bootstrap --help` at runtime; one
  question at a time, plain language; routes to project-intake (has
  a prototype) or a direct door run (blank); finishes by printing
  the LAUNCH line. Never re-implements door or intake logic, and
  interacts with both ONLY through their public surfaces (the door's
  CLI flags; the intake agent's documented inputs). If the door's
  help does not answer something the flow needs, STOP and tell the
  user — never guess (the help output wins; /setup-preset rule).
- **F3 — seeded self-direction**: the consumer CLAUDE.md seed gains
  one closing line — first session: invoke the planner agent, it
  triages the backlog. (Locate the seed in engine-consumer.sh; this
  is a seed-text change, not an engine-logic change.)
- **F4 — retire the second entrance** (A33, A45, uncertain-finding):
  per Decision D1 below.
- **F5 — archive the dead docs** (A41, A44, A50, A68): per D2.
- **F6 — serena artifacts** (A85-A87, A89, A90): per D3.
- **F7 — dispatch-kit steps in setup-dev.sh** (A18): per D4.
- **F8 — docs/adr ownership** (A61, A62): per D5.

## Decisions (✅ ALL FIVE APPROVED AS RECOMMENDED — operator, 2026-07-24)

- **D1 — launchers + onboarding agent** (recommendation: RETIRE).
  `.kit/launchers/launch|onboarding|preflight` and the onboarding
  agent predate the door and form a parallel setup path that ADR-0027
  abolished. Recommend: delete launch + onboarding launcher and the
  onboarding agent (the door + /new-project + STARTING-A-PROJECT
  replace them); KEEP `.kit/launchers/preflight` ONLY if it is a
  thin wrapper over preflight-check.sh (verify at implementation —
  if it duplicates, retire it too and point at /preflight). A
  deprecation shim is NOT needed: these are operator-facing, not
  API, and 0.9.0 is the breaking release.
- **D2 — dead docs** (recommendation: ARCHIVE, not delete).
  AGENT-SYSTEM-GUIDE.md (pre-kit layout), tmux-tips.md,
  COVERAGE-WORKFLOW.md (another project's), EVALUATION-WORKFLOW.md
  (aider-era verdicts/paths) → `docs/archive/` with a one-line
  tombstone at the old path ONLY where live surfaces link them
  (README, agents — those links get repointed or dropped by this
  task; coordinate with KIT-0069's sweep so neither re-points at
  archived files). COVERAGE-WORKFLOW gets a fresh minimal
  replacement (the 80% rule + the two commands that exist).
- **D3 — serena** (recommendation: PRUNE to what works).
  Delete the Claude-Desktop-era scripts/guides with hardcoded
  operator paths (verify-serena.sh, CONTEXT-CONFIGURATION-GUIDE,
  SETUP-GUIDE's dead ADR-0040 pointer); regenerate
  `.serena/memories/` stale entries or delete them (serena rebuilds
  its own memories); fix project.yml.template's schema key against
  the CURRENT serena version's accepted schema (verify, don't
  assume).
- **D4 — dispatch-kit in setup-dev** (recommendation: gate behind a
  flag). Steps 3/6 install from a hardcoded operator-machine clone —
  make them `--with-dispatch` opt-in with a not-on-PyPI notice, so
  the default path works on any machine.
- **D5 — docs/adr vs .kit/adr** (recommendation: minimal fix now).
  Move the orphan task-starter (A61) to `.kit/context/` history;
  make about-adr.md's claim true (consumer-facing dir stays empty of
  kit ADRs — kit decisions live in `.kit/adr/`, and the seeded
  about-adr.md already tells consumers to start fresh). No larger
  restructure.

## Acceptance Criteria

- [ ] STARTING-A-PROJECT.md exists, README-linked; a newcomer can
      go from clone to planner-ready pair following only it
- [ ] /new-project derives from the door's --help (no hardcoded
      matrix) and routes correctly (transcript in PR for both routes)
- [ ] Seeded CLAUDE.md self-direction line ships in fresh exports
      (demo or test evidence)
- [ ] D1-D5 executed as signed off; every removed surface's citing
      links repointed (grep evidence in PR)
- [ ] Audit A-numbers owned here dispositioned in the PR body

## Time Estimate

1-1.5 days: F1 2h, F2 2h, F3 1h, F4-F8 4-6h

## Out of scope

- Any door/engine logic change; 0.9.0 removals themselves (KIT-0047/
  0054/0059); KIT-0069's class sweeps

## Evaluation

`arch-review-fast` (gemini-2.5-flash, 2026-07-24): **REVISION_SUGGESTED**
— log: `.adversarial/logs/KIT-0067-factory-front-door-and-structural-cleanup--arch-review-fast.md`.
Disposition (planner):

1. **"Parsing --help is fragile; expose a machine-readable
   interface" — DECLINED (premise error).** `/new-project` is a
   Claude-agent-executed command, not parsing code: the agent reads
   the help prose the way a human does, which is robust to
   formatting by construction. Runtime-derivation-over-hardcoding is
   the ADR-0025 rule that keeps the command from drifting from the
   door — the same design already shipped and validated in
   /setup-preset (KIT-0058). A door-side JSON surface would also be
   a door change, out of scope by F2's own rule.
2. **Error handling for unanswerable help — ACCEPTED** (one line in
   F2: stop-and-say-so, help-output-wins).
3. **Reusable derivation utility — DECLINED**: no parsing code
   exists to reuse; the reusable artifact is the command-authoring
   convention F2 already cites.
4. **Coupling to routed components' internals — ACCEPTED** as F2's
   public-surfaces-only clarification.

No outstanding blockers. Working tree verified clean post-run.
Assignment gate CLEARED: D1-D5 approved as recommended (operator,
2026-07-24) — assignable when its turn comes in the chain.
