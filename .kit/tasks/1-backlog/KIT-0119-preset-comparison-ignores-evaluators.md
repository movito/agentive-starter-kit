# KIT-0119: `doctor --against-preset` ignores the `evaluators:` declaration

**Status**: Backlog
**Priority**: low
**Assigned To**: unassigned
**Estimated Effort**: 1-2 hours
**Created**: 2026-08-24
**Linear ID**: (automatically backfilled after first sync)

## Related Tasks

**Related**: KIT-0118 (added the `evaluators:` record line — this gap is
its discovered rider), KIT-0056 (built the preset-comparison surface),
KIT-0108 (owns collapsing the duplicated record readers)

## Overview

KIT-0118 taught the kit-install record a fourth declaration —
`evaluators: yes|no` — and taught both doctor record readers to parse
it. The `--against-preset` comparison was deliberately left alone in
that task's scope, so it still compares only `shape`, `profile`, and
`bots`.

The result is a small asymmetry rather than a defect: the operator
preset already accepts an `evaluators` key (it is in
`door.PRESET_KEYS`, and the door resolves it in the flag → preset →
prompt chain), and a project's record can now carry a value for it —
but a divergence between the two is invisible to the one surface built
to report divergence.

## Discovered by

feature-developer during KIT-0118 implementation, while tracing the
`bots:` mechanism the new `evaluators:` line mirrors. Filed rather than
fixed inline, per the task's out-of-scope rule.

## Verified facts (2026-08-24, branch `feature/KIT-0118-packaged-door-fixes`)

1. `_print_preset_comparison(shape, profile, bots, record_errors, project_dir)`
   exists in TWO copies — `agentive_kit/doctor/__init__.py` and the
   inline fallback in `scripts/core/project` — and its docstring states
   the omission explicitly: *"Keys other than shape/profile/bots are
   ignored here by design."* That sentence predates the `evaluators:`
   line existing at all.
2. `door.PRESET_KEYS` already contains `"evaluators"`, and
   `preset_get(opts.preset, "evaluators")` is validated to `yes|no`.
3. `_doctor_install` now returns
   `(shape, profile, bots, evaluators, errors)` in both copies, so the
   value is already in hand at the comparison's call site — no new
   plumbing is needed to reach it.

## Requirements

1. Extend the comparison to `evaluators`, following the `bots` row's
   shape exactly (INFO-only; never affects doctor's exit code).
2. Decide and document the DEFAULT for an absent record line. `bots`
   uses "absent = both expected" and marks the row `defaulted`. The
   parallel here is "absent = evaluators expected" (`yes`), but note it
   is genuinely a legacy-install marker rather than a positive answer —
   the row may deserve its own wording rather than a borrowed one.
3. Mirror the `bots_errored` treatment: an invalid recorded declaration
   reports INFO about the invalid record, not a false divergence.
4. Both copies of `_print_preset_comparison` change together, with a
   conformance-style test pinning them to one meaning (the pattern
   KIT-0118 established for the readers themselves).

## Out of scope

- Consolidating the duplicated comparison — that is KIT-0108's charter.
- Any change to doctor's exit contract: `--against-preset` is
  deliberately INFO-only.

## Acceptance Criteria

- [ ] `--against-preset` reports an `evaluators` row
- [ ] Absent-line default chosen, documented in the docstring, and pinned
- [ ] Invalid recorded declaration → INFO about the record, not a
      spurious divergence
- [ ] Both copies changed together; parity test added
- [ ] Existing preset-comparison tests still pass

## References

- KIT-0118 PR (movito/agentive-starter-kit#147) — added the record line
- `.kit/context/reviews/KIT-0118-evaluator-review.md`
- KIT-0056 / KIT-ADR-0027 P7 — the preset-comparison surface
