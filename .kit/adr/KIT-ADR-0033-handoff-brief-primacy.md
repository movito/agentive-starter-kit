# KIT-ADR-0033: The handoff brief stays primary — derivation is a declared degraded mode

**Status**: Proposed
**Date**: 2026-08-13 (drafted 2026-08-09 as part of a combined ADR; split
per operator decision — see KIT-ADR-0030 Provenance)
**Deciders**: Fredrik Matheson (operator), Claude Code — operator
decision 2026-08-09, correcting an earlier proposal to make the brief
optional-by-derivation
**Related**: KIT-ADR-0031 (the intake agent this governs),
KIT-ADR-0027 P5 (degraded loudly — the principle applied here),
`.kit/templates/PROTOTYPE-HANDOFF-TEMPLATE.md`

## Context

The intake flow prefers a handoff brief pasted out of the Cowork
session that built the prototype. An earlier draft proposed making the
brief optional, with intake deriving one by inspecting the folder. The
operator corrected this: the brief's value is not a file inventory — it
is the *rationale*: why the prototype was built the way it was, what is
solid versus rough, which decisions were deliberate.

**Inspection can recover what was built; it can never recover why.**
Until a Cowork session's agent and the resulting code session's agent
can talk to each other directly, the brief is the only carrier for that
knowledge, and asking for it at the end of a prototyping conversation
remains the right practice.

## Decision

The `PROTOTYPE-HANDOFF-TEMPLATE` brief is **the preferred input and
stays so**. When no brief exists, intake does not block and does not
invent:

- It derives a brief **from inspection only** — files, dependency
  manifests, entry points, READMEs, git history if any.
- Every section the template defines that inspection cannot support —
  decisions and their reasons, solid-versus-rough, known issues,
  intended next steps — is emitted verbatim as
  `> RATIONALE NOT RECOVERABLE BY INSPECTION — no handoff brief was
  supplied.` It is **never** filled with a plausible inference.
- The derived file is named and marked as derived, and the intake's
  output says so, so that a following agent reads it as a partial
  record rather than as fact.
- The operator is offered the template block to fill the gap, then or
  later.

This is KIT-ADR-0027 P5's principle applied to intake inputs: degraded,
loudly — never silently green. A fabricated rationale is worse than an
absent one, because the following agent cannot tell the difference.

**The marker is a human contract, not a machine one** *(claude-arch
finding, 2026-08-13)*: the verbatim string above is the seam between
derived and authored content, and downstream tooling that wants to
distinguish them programmatically would be string-matching. Accepted
for now — one operator, human readers. If tooling ever needs the
distinction (e.g. a preflight warning "your brief is fully derived"),
add a structured front-matter flag (`handoff_source:
derived-from-inspection`) alongside the verbatim line rather than
parsing prose.

## Consequences

**Positive**

- No-brief prototypes are not turned away, and nothing false enters the
  record.
- The practice that produces the best input (ask the Cowork session for
  a brief before closing it) keeps its incentive.

**Negative / risks**

- Derived briefs are legitimately thinner; a following agent working
  from one starts with less. That is the honest representation of what
  is known.

## Revisit Triggers

- **A Cowork session agent and a code session agent can address each
  other directly.** The derived-brief fallback becomes largely
  unnecessary; the rationale transfers live rather than through a file.
  Revisit together with KIT-ADR-0031.
- Downstream tooling needs to distinguish derived from authored content
  — implement the structured marker described above.

## Evaluation Record

2026-08-13, run against the combined draft covering this decision:
`arch-review` (o3) REVISION_SUGGESTED (no findings specific to this
decision); `claude-arch` (claude-opus-4-7) APPROVED — praised the
degraded-loudly application, flagged the stringly-typed marker
(addressed above). See KIT-ADR-0030's Evaluation Record for log paths.
