# KIT-ADR-0031: `project-intake` ships in the plugin — run intake in the deliverable folder

**Status**: Accepted (2026-08-16, at KIT-0105 completion)
**Date**: 2026-08-13 (drafted 2026-08-09 as part of a combined ADR; split
per operator decision — see KIT-ADR-0030 Provenance)
**Deciders**: Fredrik Matheson (operator), Claude Code
**Depends on**: KIT-ADR-0030 (the door in the package — until the door
ships, the intake agent genuinely cannot run outside a kit checkout)
**Related**: KIT-ADR-0033 (handoff brief primacy — governs this agent's
input), KIT-0066 (the intake flow), KIT-0081 (the live intake that
surfaced its gaps), KIT-0096 (plugin roster + drift guard)
**Owning task**: KIT-0105

**Retires**: `.claude/agents/project-intake.md` "**Where you run**:
from an agentive-starter-kit checkout — the door is kit-side only and
does not ship to consumer projects." Once KIT-ADR-0030 lands, that
sentence is false and the constraint is gone.

## Context

`project-intake` is the graduation agent: it takes a Cowork prototype
folder plus (preferably) a handoff brief and produces the split pair.
Today it must run from a kit checkout, because it reaches the door by
relative path and the door is kit-side only.

That forces the operator's flow through the kit's own workspace: open a
session in `agentive-starter-kit/`, with the kit backlog present, to do
work that has nothing to do with the kit. The live intake of 2026-08-04
(`ev-fast-charging-loads`, KIT-0081) and the 2026-08-11 `/new-project`
test both produced the same operator experience from different angles —
F9: "it isn't clear why I can't just keep working in the session I ran
/new-project in." The session hop and the clone hop are the same defect
at two scales; KIT-ADR-0030 removes the clone hop, this ADR collects
the benefit.

## Decision

`project-intake` moves into the `agentive-workflow` plugin, alongside
the thirteen agents already distributed there.

The intended flow becomes: **open Claude in the Cowork output folder
and run the intake there**. The deliverable is the input, in place. No
navigation, no clone, no factory.

Mechanics (detailed in KIT-0105):

- The agent follows KIT-0096's declarative roster + drift-guard
  release flow; fixes land in the kit's canonical `.claude/` tree,
  never in divergent marketplace edits (KIT-0097's contract).
- The agent becomes location-agnostic: it verifies `agentive` is
  installed (instructing, never dead-ending, if not) and treats its own
  working directory as the candidate prototype folder when the user
  gives no path.
- The door-gap escape hatch changes address: running outside the kit,
  `.kit/tasks/1-backlog/` does not exist. The agent reports gaps to the
  operator as a ready-to-paste task body instead. This preserves the
  KIT-0081 feedback loop, which KIT-ADR-0034 makes the *primary*
  generator of kit work.

## Consequences

**Positive**

- Requirement 1 of the 2026-08-09 conversation (Cowork session →
  systematic repo) gets its shortest possible path — intake runs in the
  deliverable folder itself.
- One more agent ships through the existing plugin channel; nothing new
  to operate.

**Negative / risks**

- The plugin roster grows by the one agent with filesystem-creation
  side effects; its guards (e.g. the `init.defaultBranch` check,
  KIT-0081 F3 — closed upstream, verified 2026-08-12) must move
  unchanged, with tests rather than re-implementation.

## Revisit Triggers

- A Cowork session agent and a code session agent can address each
  other directly — the intake's file-based handoff becomes one of
  several carriers, and this agent's shape should be revisited together
  with KIT-ADR-0033.

## Evaluation Record

2026-08-13, run against the combined draft covering this decision:
`arch-review` (o3) REVISION_SUGGESTED (no findings specific to this
decision); `claude-arch` (claude-opus-4-7) APPROVED. See KIT-ADR-0030's
Evaluation Record for the shared context and log paths.
