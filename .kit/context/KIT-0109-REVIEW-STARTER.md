# KIT-0109 — merge gate + planner handoff (plugin release 2.0.4)

**From**: feature-developer (agentive-skills session)
**To**: planner / operator
**Date**: 2026-08-14
**PR**: [movito/agentive-skills#9](https://github.com/movito/agentive-skills/pull/9)
— `release/agentive-workflow-2.0.4`, head `c790a95`

> Written from the release session; **left uncommitted in the kit tree**
> for the planner to commit, per the KIT-0109 handoff (no kit-repo
> commits from this session). Same route as the two files below.

## State: DONE — merged `9331e4f`, both post-merge proofs green

- **Drift guard GREEN on kit `main`**:
  https://github.com/movito/agentive-starter-kit/actions/runs/31798961041
  (`workflow_dispatch`, conclusion `success`, head `94c8d82`); job log:
  `in sync: 27 shipped components match the published roster.` The two
  preceding runs on `main` (`31785917814`, `31785439793`) were failures
  — this is the first green since the drift set opened 2026-08-12.
- **Installed locally**: `updated from 2.0.3 to 2.0.4`;
  `claude plugin list` → `agentive-workflow@agentive-skills`,
  `Version: 2.0.4`, `Status: ✔ enabled`.
- Closure posted on PR #9
  ([comment](https://github.com/movito/agentive-skills/pull/9#issuecomment-5293102756)).

All five acceptance criteria met. Remaining planner actions: commit the
three handed-over files, rule on F1/F2, and move `KIT-0109` out of
`3-in-progress/`.

## Merge-gate notes (historical — kept for the record)

`mergeStateStatus: CLEAN`, `mergeable: MERGEABLE`, `main` unprotected.
GitHub still reports `reviewDecision: CHANGES_REQUESTED` — **stale, not
live**: it is CodeRabbit's original blocking review, never superseded by
an approval, while every thread it raised is resolved with CodeRabbit's
own acknowledgement. A re-review was deliberately not requested (it
would re-scan 20 derived bodies to flip a cosmetic decision field).

## Acceptance criteria

| # | Criterion | State |
|---|---|---|
| 1 | Delta re-derived from roster hashes at session start; count + membership verified against live guard output | ✅ 20 components, membership identical to the spec's enumeration |
| 2 | All stale components resynced; roster hashes match; version fields consistent at 2.0.4 | ✅ guard reports `in sync: 27 shipped components match the published roster` |
| 3 | Release PR merged; every bot thread resolved; content findings routed, not patched | ✅ merged `9331e4f` (operator, squash); threads 3/3 resolved; 1 finding routed (F2) |
| 4 | Drift guard green on kit `main` (run link cited) | ✅ [run 31798961041](https://github.com/movito/agentive-starter-kit/actions/runs/31798961041) |
| 5 | `claude plugin list` shows 2.0.4 (output quoted) | ✅ `Version: 2.0.4`, `Status: ✔ enabled` |

## Files handed over — three, all uncommitted in this repo

1. `.kit/context/KIT-0109-KIT-FOLLOWUPS.md` — **needs a planner ruling**
   - **F1**: all 20 components changed content with **zero `version:`
     frontmatter bumps**, so `roster.yaml`'s `kit_version` column has
     become a non-signal (`bot-triage` still reads 1.1.0 /
     `last-updated: 2026-04-19` while carrying the KIT-0104 sixth
     face). `89aea3a` bumped versions one release earlier, so this is
     drift from an established practice. Remedy: a CI check, or retire
     the column in favour of the hash.
   - **F2**: `reviewThreads(first: 100)` is unpaginated in canon
     (`.claude/commands/retro.md:97`), and `retro` uses its count to
     assert triage completeness. CodeRabbit-found, verified
     byte-identical to the shipped copy before routing.
2. `.kit/context/reviews/KIT-0109-evaluator-review.md` — Gate 5 record
   (fast tier only, prose-sweep exception; CONCERNS → one clarity
   finding accepted and fixed)
3. `.kit/context/KIT-0109-REVIEW-STARTER.md` — this file

## Task lifecycle — not moved by me

`KIT-0109` is still in `3-in-progress/`. `project move` is a
planning-repo write and this session is forbidden kit-repo commits, so
the move to `4-in-review` (or straight to `5-done` after R5) is the
planner's, on `main`.

## What I still owe after the merge

Both post-merge proofs, run and posted on PR #9:

- `gh --repo movito/agentive-starter-kit workflow run "Plugin Drift
  Guard" --ref main`, then cite the green run
- `claude plugin marketplace update agentive-skills` +
  `claude plugin update agentive-workflow@agentive-skills`, then quote
  `claude plugin list`

## Method note worth keeping (extends KIT-0099's)

KIT-0099 established *derive the delta from roster hashes, never
`git diff`*. This release adds the second half: **resync by three-way
merge, never by copy.** For each component the base was the kit blob at
its *previously rostered* hash — located by walking kit history and
hashing blobs until the match — with kit `HEAD` as theirs and the
published plugin copy as ours. A straight copy would have overwritten
the KIT-ADR-0025 generalization in every body; the merge preserved it,
and all 20 resolved clean. The merged output was then checked for the
KIT-0099 failure mode (newly duplicated headings), leaked `KIT-LOCAL`
markers, and kit-specific paths in added lines — none found.

## Round-1 observation for the retro

CodeRabbit's **check** read `pass` while its **review** was
`CHANGES_REQUESTED` with 3 open threads — the sixth face of the
lying-status class, which this very release ships into `bot-triage`.
The rule paid for itself inside the release that carries it: triage was
built from the `reviewThreads` query, so the check's lie cost nothing.
