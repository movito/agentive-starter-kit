# KIT-0075: Reconcile the launcher restoration — modernize `launch`, amend the D1 record

**Status**: Backlog
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
