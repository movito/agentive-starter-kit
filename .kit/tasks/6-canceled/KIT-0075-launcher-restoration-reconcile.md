# KIT-0075: Reconcile the launcher restoration — modernize `launch`, amend the D1 record

> **Archived (2026-08-12, backlog review — premise-tested, operator-approved)**: verdict given by usage — F2 answered empirically (`claude --agent` is native, verified 2026-08-10: bare name resolves, persona takes, model pin honored, tools frontmatter enforced); F4 answered behaviorally (the operator has launched natively across every session since, never missing the menu). The kit-side `launch` script remains untouched for whoever still wants it in the kit repo. Revive condition: the operator asks for a menu — the shape would be an `agentive launch` verb, not resurrected bash.

> **Demoted to backlog (2026-08-08, tidy)**: F2 (modernize `launch` to native agent invocation) stays valid. F4 (consumer story) is DECIDED BY the phase 2 spec (KIT-0093) — the door switch determines what ships to consumers; check its verdict before promoting this.

> **F2/F4 evidence (2026-08-10, live)**: the operator's `launch
> feature-developer` habit failed in `~/Github/agentive-skills` (a
> plugin-only, non-kit repo) — third occurrence of the launch-habit
> gap. F2's open question is now ANSWERED: the current CLI supports
> `claude --agent <agent>` natively ("Agent for the current session",
> verified in `claude --help` 2026-08-10). The modernization path is
> real: `launch` can exec `claude --agent <name>` instead of the
> `--append-system-prompt` reconstruction, and the consumer story can
> be "the command is `claude --agent <name>`; the menu is optional
> sugar". Remaining before promoting: the operator's verdict on
> whether the native form is ergonomic enough to retire the menu, or
> whether a thin menu wrapper should ship (package CLI verb or plugin
> command).

**Status**: Canceled
**Priority**: medium
**Assigned To**: unassigned
**Estimated Effort**: 2-3 hours
**Created**: 2026-07-28
**Linear ID**: (automatically backfilled after first sync)

## Related Tasks

**Parent**: operator regression report 2026-07-28 ("the launch
command stopped working... I use it all the time") after KIT-0067
D1 deleted `.kit/launchers/launch`
**Related**: KIT-0067 (D1), KIT-0054/KIT-0059 (0.9.0 removal
narratives that assumed launcher retirement), KIT-0074

## Overview

KIT-0067 D1 conflated two functions: the SETUP entrance (onboarding
— correctly retired; the door replaced it) and the operator's daily
AGENT PICKER (`launch` — over-deleted). The planner restored the
launcher byte-identical same-day as a hotfix. This task reconciles
the record and modernizes the tool.

## Requirements

- **F1 — amend the D1 record**: the launcher is DELIBERATELY kept;
  onboarding stays retired. Fix the surfaces that still narrate full
  launcher retirement as current/pending:
  `.claude/agents/agent-creator.md:~352` ("pre-0.9.0 launcher menu"
  framing), `scripts/optional/create-agent.sh:7,~502` comments, any
  0.9.0-removal-set references implying launchers leave at 0.9.0,
  and STARTING-A-PROJECT/WORKTREE docs if they claim `claude --agent`
  is the only launch path. Verify each with grep -Rn first.
- **F2 — modernize the script** (verify against the installed CLI,
  item 10): if `claude --agent <name>` is supported, exec that
  instead of the `--model + --append-system-prompt` reconstruction
  (native invocation honors the frontmatter pin, killing the stale
  `claude-sonnet-4-5-20250929` fallback at :110); keep the menu UX
  and the `agent_order` array format (create-agent.sh edits it).
- **F3 — worktree awareness (nice-to-have)**: offer launching into a
  `../ask-worktrees/<ID>` cwd when worktrees exist. Skip if it
  bloats the script.
- **F4 — consumer story**: decide and record whether `launch` ships
  to consumers (it did pre-D1 via the kit export; D1's deletion
  removed it from exports). Either way, say so in
  STARTING-A-PROJECT's launching section.

## Acceptance Criteria

- [ ] No live surface claims the launcher is retired/pre-0.9.0
- [ ] `launch` execs the native agent path (or the fallback is
      justified against the installed CLI)
- [ ] create-agent.sh registration still works (its tests)
- [ ] Consumer decision recorded (F4)

## Notes

- Evaluation skipped (planner): reconciliation task, decisions
  in-spec except F4 (present options in the PR).
- Lesson banked in REVIEW-INSIGHTS: a deletion decision must
  enumerate the tool's FUNCTIONS, not its directory.

## Added evidence (2026-08-04, ev-fast-charging-loads intake)

Second operator regression report, same shape as the parent: a fresh
planning-shape repo (door `--new --shape planning`) does not ship
`.kit/launchers/launch`; the operator's first move in the new repo was
`launch planner-f5`, which failed with "no .kit/launchers/launch found
… or any parent". F4's consumer question is now answered empirically
twice: the operator expects `launch` in every repo they work in. The
planner hand-copied the kit's launcher into
ev-fast-charging-loads-planning as an interim fix; F4 should make the
export/scaffold ship it (or the door's tail must say how to get it).

## Added evidence + scope (2026-07-29, fresh-project test)

Operator launched the create-project agent via `launch`: (a) the
agent was silent at start — `--append-system-prompt` sessions cannot
speak first, so interview-first agents wait for input they were
supposed to solicit; (b) on "Are we ready?" the persona LOST to
ambient context (CLAUDE.md + project memory) and did planner-style
kit triage instead of its startup step. Both strengthen F2 (native
`claude --agent` invocation — a real agent identity should win
persona priority) — and F2 gains: verify whether native invocation
can pass an INITIAL prompt so interview agents open the
conversation; if not, the launcher prints "type 'begin' to start"
as the launch instruction. Interim mitigation shipped: FIRST-TURN
CONTRACT blocks in create-project/project-intake/bootstrap agents
(planner, same day).
