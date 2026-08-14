# KIT-0109 — kit-side follow-ups from the 2.0.4 release

**From**: feature-developer (agentive-skills session, PR
[movito/agentive-skills#9](https://github.com/movito/agentive-skills/pull/9))
**To**: planner — this file is handed over, not committed by me
(KIT-0109 handoff: no kit-repo commits from the release session)
**Date**: 2026-08-14

Findings against **canonical kit content** surfaced while resyncing the
20-component drift set. Per the fix-here-then-release contract
(KIT-0097 / KIT-ADR-0028) none of these were patched plugin-side — a
plugin-only edit re-opens drift and turns the guard red.

## F1 — Component `version:` frontmatter is no longer bumped with content

**Severity**: medium (process signal, not a defect in shipped behavior)

All 20 resynced components changed content since their 2.0.3-rostered
hashes, and **not one** carried a `version:` frontmatter bump. Examples:

| Component | `version:` | `last-updated:` | Content added since 2.0.3 |
|---|---|---|---|
| `bot-triage` | 1.1.0 (unchanged) | 2026-04-19 | fifth + sixth lying-status faces, reviewThreads-first step 0, grep-first sweeps |
| `code-review-evaluator` | 1.9.0 (unchanged) | — | "mixed-shape tasks never skip the trio" section |
| `planner` / `planner-f5` | 2.1.0 / 1.1.0 (unchanged) | — | the unconditional closing launch checklist (template v2.1.0) |

Consequences:

- `roster.yaml`'s `kit_version` column is now a **non-signal** — it
  records a number that no longer moves with the content, so the only
  real anchor is `kit_sha256`. Anyone reading the roster to answer
  "did this component change?" gets the wrong answer.
- The `upgrader` agent's reconcile story and the README's per-component
  version tables inherit the same staleness (the README's
  `code-review-evaluator` row sat at 1.3.0 through three releases while
  1.9.0 shipped — corrected in 2.0.4, but it was invisible precisely
  because versions stopped moving).

There is precedent for the discipline: `89aea3a` ("bump version
frontmatter on the six components KIT-0100 changed") did exactly this
one release earlier — so this is drift from an established practice,
not a missing one.

Suggested remedy (planner's call): either a CI check that a changed
`.claude/` component carries a `version:` bump in the same commit, or
an explicit ruling that `version:` is release-cadence-only and the
roster's `kit_version` column is retired in favour of the hash.

## F2 — `reviewThreads(first: 100)` is unpaginated in canon

**Severity**: major (CodeRabbit's rating; I concur on the class, and
note the irony below)
**Source**: CodeRabbit on agentive-skills#9, thread
`PRRT_kwDOSj0O5s6ZO02L`, round 1
**Canonical site**: `.claude/commands/retro.md:97` — verified
byte-identical to the shipped plugin copy at
`plugins/agentive-workflow/commands/retro.md:97`, which is why it is
routed here and not patched on the release branch.

```text
reviewThreads(first: 100) { nodes { isResolved } }
```

…counted with `[…nodes[]] | length`. Past 100 threads the query
silently drops the remainder, and `retro` uses that count to assert
triage completeness. No `pageInfo` / `hasNextPage` / `endCursor`
anywhere in canon.

The irony is the point: **the finding is against the very rule this
release ships.** `bot-triage`'s new step 0 makes `reviewThreads` the
mandatory opening query precisely because REST "silently under-counts"
(KIT-0102: 3 vs 10) — and the canonical query we point people at has
the same failure mode one order of magnitude up. A rule that names
under-counting as the enemy should not itself under-count.

Practical risk today is low (this project's PRs top out around a dozen
threads; KIT-0102's worst was 10) — which is exactly why it will not
surface until it certifies a false "clean" on some future large PR.

Suggested remedy (planner's call, one of):

- paginate: loop on `pageInfo.hasNextPage` / `endCursor` and aggregate
- **fail closed**: keep `first: 100` but request `pageInfo.hasNextPage`
  and refuse to certify when it is true — cheaper, and it matches the
  house preference for loud guards over silent completeness
- audit the class, not the site (the skill's own grep-first rule):
  `rg 'first: *[0-9]+' .claude/` — any paginated GitHub collection
  used for a completeness assertion has this shape, not just this one

## F3 — (no further bot findings)

Round 1 was the only round: BugBot passed with zero threads;
CodeRabbit filed three, of which one was routed here (F2), one fixed on
the release branch (a malformed inline-code span in my own CHANGELOG
prose — marketplace content, not canon), and one was a
process-reminder nitpick about the post-merge checks.

---

**Not filed here** (fixed on the release branch, correctly — these are
marketplace-repo content, not kit canon): the README version claim
(2.0.2 → 2.0.4) and its stale `code-review-evaluator` row.
