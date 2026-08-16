# KIT-ADR-0030: The door ships in the package — `agentive new` / `agentive adopt`

**Status**: Accepted (2026-08-16, at KIT-0105 completion)
**Date**: 2026-08-13 (drafted 2026-08-09 as part of a combined ADR; split
per operator decision — see Provenance)
**Deciders**: Fredrik Matheson (operator), Claude Code
**Extends**: KIT-ADR-0028 (versioned packages) — this applies that
decision to the one component it exempted: the setup door itself
**Related**: KIT-ADR-0027 (lean kit — P3 single-owner rule, degraded
modes), KIT-ADR-0031 (intake into the plugin — depends on this),
KIT-ADR-0032 (two-rung ladder — its rung 0 needs this door),
`docs/STARTING-A-PROJECT.md`
**Owning task**: KIT-0104

**Retires**: the factory-clone precondition — the rule that project
creation happens *inside* an agentive-starter-kit checkout
(`docs/STARTING-A-PROJECT.md` "The factory model"; `bootstrap --help`
"Kit-side only"). Nothing new is built to replace it; the existing
package channel absorbs it.

## Provenance

Split from the combined draft "KIT-ADR-0030: The door is a tool, not a
place" (PR #128, closed unmerged 2026-08-13). The operator chose one
ADR per concern: large bundles have repeatedly produced outsized
CI/bot fix rounds, and with a single kit consumer the coupling argument
carries no urgency. The combined draft's thesis is unchanged; its six
decisions now live in KIT-ADR-0030 through KIT-ADR-0034.

## Context

The kit's stated purpose is to turn prototypes — typically Cowork
one-off deliverables — into repos that can be worked on systematically.
The operator's report, 2026-08-09:

> "At the moment, I am spending more time working on getting ASK back
> on track than I am on taking Cowork one-offs and turning them into
> usable software."

Four requirements were named: (1) Cowork session → systematic repo;
(2) low friction to *start* that conversion; (3) easy to keep projects
current as the kit develops; (4) does not require working on the kit
just to get a project going.

Requirement 3 is solved (KIT-ADR-0028: pins + two upgrade commands +
doctor). Requirements 2 and 4 fail at one line.

### The factory-clone precondition

KIT-ADR-0028 packaged everything a project *contains*. It did not
package the thing that *creates* a project. The door remains kit-side
by explicit declaration (`bootstrap --help`: "Kit-side only";
`docs/STARTING-A-PROJECT.md`: "You start a session in
`agentive-starter-kit/` … to create projects").

So every graduation begins `cd ~/Github/agentive-starter-kit && claude`
— a session opened inside the repo the operator is trying to stop
working on, with its backlog present and a planner whose job is to
triage it. That is the structural cause of "I spend more time on the
kit than on the work," and no amount of process discipline removes it,
because the precondition is architectural.

The exemption was never argued. It is a residue of the pre-package era,
when the door's job was to *copy the kit tree*. After KIT-0093, `--new`
projects are born packaged — a content scaffold plus pins, no script
copies — so the door's output is package data, not an rsync of a
working tree. The reason for the exemption expired; the exemption did
not.

## Decision

`agentive new` and `agentive adopt` become console subcommands of
`agentive-kit`, taking the same flags, matrix, preset resolution, and
records as `scripts/local/bootstrap` today. The door stops being a
place you must stand and becomes a tool you have installed.

- Both verbs ship together. (KIT-ADR-0028 is Accepted — COMPLETE:
  phase 3 closed as a no-op and phase 4 retired the sync machinery in
  KIT-0102. There is no copying `adopt` left to wait on.)
- **The port is a port, not a rewrite.** Argument parsing, matrix
  validation, and matrix *ownership* move into Python; the three
  engines may initially ship as packaged data scripts invoked by it.
- **The interim is time-boxed, not open-ended** *(claude-arch finding,
  2026-08-13)*: while engines remain shell, the Python front is the
  *sole* source of shape × profile legality — engines become pure
  executors — and the engine-consolidation follow-up is filed on the
  same PR that lands the port. An interim without a filed exit is how
  six doors became six.
- **`--no-kit` exists on both verbs** *(claude-arch finding,
  2026-08-13)*: KIT-ADR-0032's rung 0 must be reachable from `new` as
  well as `adopt`. This is the API-completeness half of the move, not
  follow-on work; it lands with KIT-0104.
- `scripts/local/bootstrap` becomes a thin `exec` shim into the package
  for one release, then goes — per KIT-ADR-0027 P3's rule that
  convergence is structural, not social, and that the removal task is
  filed with the PR that creates the shim.
- The shape × profile matrix keeps its single owner; ownership moves
  with the code, it is not duplicated.

**Consequence**: `cd ~/Github && agentive new my-thing` works from
anywhere. The kit clone reverts to being the *development* home for the
kit, entered when working on the kit and at no other time.

## Consequences

**Positive**

- Requirements 2 and 4 are answered structurally rather than by
  discipline: the creation path no longer passes through the kit's
  workspace.
- No new mechanism, no new channel, no new config surface. Two
  subcommands move into a package that already exists.
- The kit's own front door becomes the thing every consumer runs, so
  door defects surface in real use rather than in audits — the loop
  KIT-ADR-0034 depends on.

**Negative / risks**

- Door logic is shell (`bootstrap` + three engines); moving it into a
  Python package is a port. Mitigation: engines as packaged data
  scripts initially, with parsing and matrix ownership in Python; a
  full rewrite is not required to get the addressability win.
- Two release surfaces move in step for one cycle (package + plugin).
  The 2.0.0 drift guard (KIT-0096) already covers the plugin half.

## Revisit Triggers

- A non-Python profile becomes the majority case — the door's Python
  packaging becomes a question rather than an obvious fit. The door
  CLI's *interface* is language-agnostic; Python is the initial host,
  not part of the decision *(o3 finding, 2026-08-13)*.
- The engine-consolidation follow-up misses its filed release — the
  time-box failed and the interim is drifting toward permanence.

## Evaluation Record

2026-08-13, run against the combined draft covering this decision:

- `arch-review` (o3): **REVISION_SUGGESTED** — no high-risk findings;
  asked for a language-agnostic boundary statement (folded into the
  revisit triggers above) and volatile CLI detail kept out of ADR prose.
- `claude-arch` (claude-opus-4-7): **APPROVED** — flagged the
  matrix-ownership interim (now time-boxed above) and the
  `new --no-kit` asymmetry (now bound into the decision).

Logs (local, gitignored): `.adversarial/logs/KIT-ADR-0030-the-door-is-a-tool-not-a-place--{arch-review,claude-arch}.md`
