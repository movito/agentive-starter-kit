# KIT-0114: Extract project-intake's credential gate into a tested script

**Status**: Backlog
**Priority**: medium (no live defect — the gate is verified correct as
shipped; this removes the *class* that produced five rounds of them)
**Type**: Refactor / test infrastructure
**Estimated Effort**: ~2 h
**Created**: 2026-08-17
**Source**: KIT-0113 retro recommendation
(`.kit/context/retros/KIT-0113-retro.md`, "Recommendation"); fd raised
it on agentive-starter-kit#137 and in the 2.1.1 release PR thread
**Evaluation**: not run — filing only; the implementer should scope
the interface before writing code

## Requirement

`project-intake` carries a credential-scan gate written as shell
inside its markdown body, duplicated at **two executable sites**
(Step 2.3, Step 4c) plus a **third prose site** (Step 2.1) that must
agree with them by hand. Extract it into one small script the agent
invokes, with tests.

The gate as shipped (1.3.2) is correct and verified — this task is
about the *shape*, not a defect.

## Why

KIT-0113 spent five bot rounds across two repos hardening this gate,
and every round found a defect created by the previous fix. The
sequence is the argument:

| Fix | Defect it created |
|-----|-------------------|
| quiet scan (`-l`) | scan result no longer visible → ungated commit |
| shell gate at 4c | twin at 2.3 left unguarded |
| `add -A` check at 2.3 | re-derived rather than copied → block inherited grep's INVERTED status |
| `false` on blocked branches | only covered staging; scan path still leaked raw status |
| `case $?` | under `set -e`, exit 1 (CLEAN) aborted before `case` ran |

Plus two that a script would have made impossible or trivial:

- `-I` skipped binary files, so a staged binary carrying a credential
  scanned CLEAN — a fail-open that survived two PRs.
- The prose stated the RAW grep polarity (0 = found) as the agent's
  decision rule while the `case` had normalized the block to
  0 = clean. Both true of different exit codes; an agent trusting the
  prose inverts its stop/proceed decision. **This is the tell**: it is
  a documentation-drifted-from-code failure, which is the failure mode
  when executable logic lives in prose across sites that must agree by
  hand.

A script gives the polarity contract **one home and a test**. It also
makes the KIT-0113 verification matrix (below) a permanent regression
suite rather than scratch files in `/tmp`.

## Scope

- One script — location is the implementer's call with a one-line
  rationale, but note the constraint: **`project-intake` ships in the
  plugin and runs in the prototype's own folder, with no kit
  checkout**. A script under `scripts/core/` is NOT reachable from
  there. Options to weigh: ship it as a plugin asset, fold it into the
  `agentive` CLI (`agentive scan-staged <path>`, which the agent
  already requires and verifies at Step 0), or keep the snippet but
  generate it from a tested source. **The CLI route is the obvious
  candidate** — the agent already hard-depends on `agentive` and
  verifies it before anything else.
- Replace both executable sites with the invocation; keep Step 2.1
  correct for whatever the new surface returns.
- Tests covering the matrix KIT-0113 established by hand:

  | Situation | Expected |
  |-----------|----------|
  | credential in a text file | blocked, non-zero, filename only |
  | credential in a **binary** file | blocked (regression pin for the `-I` bypass) |
  | clean index | proceeds, zero |
  | `add`/stage failure | blocked, non-zero |
  | scan errors (non-repo, exit 128) | blocked, non-zero |
  | every case under `set -e` | identical to without |
  | side effects | no commit on any blocked path; commit only on clean; secret never in history |

- The pattern set (`sk-`, `ghp_`, `github_pat_`, `xoxb-`, `AKIA`,
  `BEGIN [A-Za-z0-9 -]*PRIVATE KEY`, `eyJ…`) moves into the script as
  the single definition. Note the PEM form is deliberate: it is a
  superset of both predecessors (8/8 on the KIT-0113 fixture set where
  `BEGIN .* PRIVATE KEY` scored 7/8 and `[A-Z ]*` scored 6/8).

## Acceptance

- [ ] One tested implementation; both executable sites in
      `project-intake` call it rather than inlining shell
- [ ] The polarity contract is stated in exactly one place, and the
      agent body's prose does not restate a contradicting one
- [ ] Test suite covers the matrix above, including the binary case
      and the `set -e` × every-situation cross product
- [ ] Reachability verified from a prototype folder with **no kit
      checkout** — the agent's actual runtime condition
- [ ] Component `version:` bumped; rides a plugin release (drift guard
      red-by-design until that cut)

## Out of scope

- Changing WHAT the gate detects (pattern set moves verbatim; widening
  it is a separate decision)
- The rest of `project-intake` — Steps 0/1/3/5 are untouched
- Retrofitting other agents that embed shell; if this shape works,
  generalizing it is a follow-up

## Notes

- Related pattern: `harden_twins_by_copy_not_rederivation`
  (`.kit/context/patterns.yml`) — this task removes the twin, which is
  the structural version of that rule.
- The gate is correct as shipped in 1.3.2. **If this task is never
  done, nothing is broken today** — the risk is that the next edit to
  either site reopens the class. Worth doing before the next time
  someone touches that construct, not urgently.
