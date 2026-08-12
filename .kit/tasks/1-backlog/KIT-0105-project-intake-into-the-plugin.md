# KIT-0105: `project-intake` ships in the plugin — run intake in the deliverable folder

**Status**: Backlog
**Priority**: high — the operator-facing half of KIT-ADR-0030; KIT-0104
removes the technical precondition, this task collects the benefit
**Type**: Architecture / distribution
**Estimated Effort**: 0.5-1 day
**Created**: 2026-08-09
**Source**: KIT-ADR-0030 D2

## Related

**ADR**: `.kit/adr/KIT-ADR-0030-the-door-is-a-tool-not-a-place.md` (D2)
**Blocked by**: KIT-0104 (`agentive new` in the package — until the
door ships, the intake agent genuinely cannot run outside a kit
checkout)
**Related**: KIT-0066 (the intake flow), KIT-0081 (the live intake that
surfaced its gaps — F2's class recurs here), KIT-0096 (plugin release
mechanics + the drift guard)

## Overview

`.claude/agents/project-intake.md` states: "**Where you run**: from an
agentive-starter-kit checkout — the door is kit-side only and does not
ship to consumer projects." Once KIT-0104 lands, that sentence is false
and the constraint is gone.

Move `project-intake` into the `agentive-workflow` plugin, alongside
the thirteen agents already distributed there. The intended flow
becomes: **open Claude in the Cowork output folder and run the intake
in place** — the deliverable is the input, where it already sits.

## Requirements

- **F1 — the agent moves into the plugin roster.** Follow KIT-0096's
  declarative roster + drift-guard mechanics; the guard goes red on the
  first merged change and forces the release, which is the designed
  flow. Behavior parity: fixes land in the kit's canonical `.claude/`
  tree, never in divergent marketplace edits (KIT-0097's
  fix-here-then-release contract).
- **F2 — the agent becomes location-agnostic.** Today it assumes it is
  running in a kit checkout and reaches the door by relative path.
  Rewrite Step 0/2 to (a) verify `agentive` is installed and instruct
  if not — never a dead end, per the door's own convention — and
  (b) treat its own working directory as the candidate prototype folder
  when the user gives no path. Remove the "compose the door, never
  modify it" path assumptions that depend on a kit tree; the rule
  itself stays.
- **F3 — the door-gap escape hatch needs a new home.** The agent
  currently says: file a follow-up in `.kit/tasks/1-backlog/` if the
  flow exposes a door gap. Running outside the kit, that path does not
  exist. Replace with an instruction to report the gap to the operator
  with a ready-to-paste task body — the operator files it in the kit
  when they are next there. This preserves the KIT-0081 feedback loop,
  which KIT-ADR-0030 D5 makes the *primary* generator of kit work.
- **F4 — DONE UPSTREAM, do not re-implement** *(verified 2026-08-12
  against `origin/main`)*: the `init.defaultBranch` guard shipped in
  the intake agent (`project-intake.md:165` rationale, `:200`
  `git -C <code-path> branch --show-current` must print `main`). The
  KIT-0081 F3 gap is closed. Carry the behavior through the move
  unchanged; add a test rather than a fix.
- **F5 — prose sweep by class.** Every surface asserting intake is
  kit-side: the agent body, `docs/STARTING-A-PROJECT.md`,
  `.kit/templates/PROTOTYPE-HANDOFF-TEMPLATE.md` step 3 ("Open a new
  tab from your agentive-starter-kit checkout"), `README.md`. Grep the
  class, do not fix only the instances listed here.

## Acceptance

- [ ] `project-intake` appears in the plugin roster and the drift guard
      is green after release
- [ ] The agent completes an intake from a folder with no path
      relationship to any kit checkout
- [ ] A missing `agentive` CLI produces a printed install command, not
      a failure
- [ ] The existing `main`-branch guard still holds after the move (test, not fix)
- [ ] No live surface still says intake runs from a kit checkout

## Notes

- Model pin and frontmatter conventions: `.kit/templates/AGENT-TEMPLATE.md`;
  verify model IDs against live docs, not memory (KIT-0069 F1 lesson).
- The handoff brief stays the primary input — KIT-ADR-0030 D3. This
  task does **not** implement the derived-brief fallback; that is
  sequenced after KIT-0104 lands, per the ADR's WIP cap.
