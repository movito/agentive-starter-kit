# KIT-ADR-0032: Two rungs — `.kit/` never lives in a repo that holds code

**Status**: Proposed
**Date**: 2026-08-13 (drafted 2026-08-09 as part of a combined ADR; split
per operator decision — see KIT-ADR-0030 Provenance)
**Deciders**: Fredrik Matheson (operator), Claude Code
**Related**: KIT-ADR-0024 (split-pair topology — unchanged by this;
this decides only *when* a project enters it), KIT-ADR-0030 (the door —
rung 0 needs `--no-kit` addressable from both verbs)

## Context

**Operator rule (2026-08-09): "I never, ever want `.kit` inside the
[code] repo."** A repo that holds code is either plain, or it is the
code half of a split pair. There is no middle state.

That collapses what was drafted as a three-rung graduation ladder to
two, and removes the only non-additive promotion from it.

## Decision

| Rung | What the project gets | Reached when |
|---|---|---|
| **0 — repo** | git + GitHub + README + CI running the profile hook + a place for tests. No `.kit/`, no kit install. | every Cowork deliverable, immediately |
| **1 — split pair** | a planning repo (`shape=planning`, `profile=none`) pointed at the *unchanged* code repo (KIT-ADR-0024) | others will read the code, or it goes to production |

Two properties make this work, and both already hold:

- **Rung 1's code repo IS a rung 0 repo.** The split pair keeps the
  code half plain — no kit install, collaborators see ordinary PRs. So
  promotion is purely **additive**: create the planning repo, point it
  at the existing code repo, change nothing in the code repo. No
  migration, no extraction, no restructure.
- **The rungs map onto existing legal cells.** Rung 0 is
  `single`+profile with `--no-kit`; rung 1 is the forced
  `planning`+`none` cell plus an untouched target. Nothing new in the
  shape × profile matrix.

**Which door verb reaches rung 0** *(verified against `origin/main`
2026-08-11)*: `--no-kit` is `adopt, single only`, enforced by explicit
guards (`bootstrap:406-434`). That is not a gap for the graduation path
— a Cowork prototype is always an existing folder, so it is adopted,
never created. What `adopt --no-kit` lacks is addressability
(KIT-ADR-0030), not legality. The `new --no-kit` counterpart — rung 0
for a *blank* project — lands with KIT-ADR-0030's port (KIT-0104), so
the rule is expressible from both verbs.

Under this rule `--no-kit` is not a convenience flag; it is the only
acceptable shape for a code repo that has no planning twin.

**Rung 0 is a legitimate terminal state.** Most one-offs should stay
there, and that reads as success, not as an unfinished install. Nothing
in doctor, preflight, or any agent may report rung 0 as a deficiency,
and nothing may treat an absent `.kit/` in a code repo as drift.

**What survives of the `single`-with-`.kit/` shape**: repos that hold
no code — notes, docs-only projects — and the kit's own development
clone.

## Consequences

**Positive**

- No migration path exists because none is needed — promotion is
  additive by construction.
- The matrix gains no new cells; the rule *removes* a state rather than
  adding one.

**Negative / risks**

- Rung 0 risks becoming a place projects rot in. Accepted deliberately:
  a repo that rots at rung 0 cost one command; a split pair that rots
  cost two repos and a token.

## Revisit Triggers

- **agentive-starter-kit itself splits into a code repo and a planning
  repo** (operator, 2026-08-09: "over time, I might even want to split
  ASK"). This is the last holdout of the `single`-with-`.kit/` shape
  under this rule — and splitting it would make the kit finally
  *consume* the topology it ships. Revisit together with KIT-ADR-0034.
- A second operator — rung 0's "resting place" convention needs to
  become explicit onboarding text.

## Evaluation Record

2026-08-13, run against the combined draft covering this decision:
`arch-review` (o3) REVISION_SUGGESTED (suggested keeping volatile flag
syntax in reference docs — the rung table above states the guarantee;
flag mechanics live with the door); `claude-arch` (claude-opus-4-7)
APPROVED — called the additive rung 0 → rung 1 promotion "a strong
structural property, not a coincidence." See KIT-ADR-0030's Evaluation
Record for log paths.
