# KIT-0099 — Review Starter

**Task**: Release plugin 2.0.1 — sync the KIT-0097+KIT-0098 canon, drift guard to green
**PR**: https://github.com/movito/agentive-skills/pull/5
**Branch**: `release/agentive-workflow-2.0.1` (movito/agentive-skills)
**Status**: In Review
**Implementer**: feature-developer (Opus 5), 2026-08-10

## What shipped

Patch release 2.0.1 on the marketplace. 17 components resynced from kit
canon, roster hashes refreshed, four version fields bumped, CHANGELOG
entry by fix family. **Roster membership byte-identical to 2.0.0** — no
roster decisions in a patch, as the spec required.

22 files changed: 17 component bodies + `roster.yaml` + `plugin.json` +
`marketplace.json` + `CHANGELOG.md` + `README.md`.

## The one thing needing your decision

**R2 (PII)** — `author.email` / `owner.email` is your personal address in
both `plugin.json` and `marketplace.json`. **Left unchanged**; it is your
call. Surfaced at the top of the PR body.

A fact that bears on it, found while checking: **`README.md` line 7 says
"This repo is private" — the GitHub API says the repo is public**
(`"private": false`). The README is wrong, and it is the sentence most
likely to make the email feel lower-stakes than it is. PR #4's flag had
this right ("this repo is public"); the README was never corrected.
Correcting it is out of scope for a patch sync — worth a follow-up either
way, independent of the email decision.

## Verification already done (cited in the PR)

- **Drift guard GREEN**: `check_plugin_drift.py --roster-file <branch roster>`
  → `in sync: 27 shipped components`, exit 0 — the task's central
  acceptance criterion, run against the exact roster being shipped.
- Baseline integrity: all 17 pre-refresh kit sources re-hash to the 2.0.0
  roster's recorded values.
- Version agreement across all four fields; JSON/YAML parse.
- Transform sweep clean: no flat command refs, no `KIT-LOCAL` regions, no
  `scripts/local`/`engine-consumer` leaks, no double-namespacing.
- Structure: Phase-1 sentinel in both fd variants; the pair byte-identical
  below its `<!-- SYNC -->` marker; phases 1–9, relocated Evaluator block
  appearing exactly once.

## Two judgment calls worth your eye

1. **Delta derived from roster hashes, not `git diff`.** The guard says 17
   stale; a `git diff` from the 2.0.0 sync commit shows 15. The gap is
   `planner` + `planner-f5`, whose content changed after the 2.0.0 hashes
   were cut. Git-only derivation would have shipped two stale agents and
   left the guard red. This is the roster doing exactly the job its header
   describes.

2. **Two stale "Phase 6" cross-refs NOT fixed.** Both `feature-developer`
   variants say "see Phase 6" where KIT-0097's renumbering means Phase 7
   (preamble ScheduleWakeup note; Shell Rules cache-TTL note). **They exist
   in kit canon** — KIT-0098 repair residuals — so the sync inherits them.
   Fixing plugin-side would re-open drift against kit hashes and turn the
   guard red, contradicting the whole point. Wants a small kit follow-up.

## Evaluator record

Fast tier only + `--format diff`, per the prose-sweep rule (deep tier is
0-for-15 on this diff shape across KIT-0069/0073). Verdict FAIL, both
findings **rejected as non-reproducible** against the tree:

- "roster updated 18, CHANGELOG says 17" — tree says 17 hash changes / 14
  version changes; the evaluator counted the `plugin_version` scalar as a
  component. Drift guard independently agrees.
- "future date 2026-08-10" — that is today.

Record: `.kit/context/reviews/KIT-0099-evaluator-review.md` (includes the
input-scoping deviation and its rationale).

## Bot status — both bots reviewed, all 12 threads resolved

**Correcting my earlier interim note**: CodeRabbit *did* review. The Fair
Usage rate-limit reply was real but transient — after the explicit
`@coderabbitai full review` nudge it submitted **CHANGES_REQUESTED** at
20:55 UTC. Gate 3 is passed, not pending.

- **Cursor Bugbot** (`68072c0`): 1 Low finding — **real, and introduced by
  this sync.** Two consecutive `## Cross-Repo Mode` headings in
  `ci-checker`: the kit backported that section in KIT-0097 F8 while the
  plugin already carried the 2.0.0 restoration, and my three-way merge
  kept both. Fixed in `5d9f01c` (kept the kit's, a strict superset —
  no-Bash delegation path + `$GH_REPO_ARG` convention vs a hardcoded
  `--repo`). Swept all 27 shipped components; this was the only one.
- **CodeRabbit**, 2 rounds, 11 threads. Of the substantive findings:
  - **1 fixed here** — CHANGELOG lacked explicit `Added`/`Removed`/
    `Renamed` categories. Valid and in scope: the upgrader agent *fetches*
    this file to compute the reconcile diff, so an empty category must be
    machine-readable, not inferred from prose. Fixed in `1a188ec`.
  - **6 filed as kit follow-ups** — all verified kit-canonical before
    filing; see `KIT-0099-KIT-FOLLOWUPS.md`. CodeRabbit itself twice
    wrote "Apply the fix in agentive-starter-kit first, then resync this
    plugin copy", which is KIT-ADR-0028 exactly.
  - Remainder auto-resolved as already-addressed.

Every thread carries a reply with its disposition and reasoning, including
the declines. 12/12 resolved.

**Worth knowing**: CodeRabbit independently found the same stale "Phase 6"
reference I had already flagged in the PR body — the two audits converged.
It also caught one thing I had not: the evaluator SKILL's "fall back to
another evaluator" can silently escalate past the prose tier.

## Remaining after merge (KIT-0099 step 5)

- [ ] Kit main's Plugin Drift Guard run GREEN — cite the run URL
- [ ] `claude plugin marketplace update agentive-skills` +
      `claude plugin update agentive-workflow@agentive-skills` →
      `claude plugin list` shows 2.0.1
- [ ] Closure comment on agentive-skills#4 referencing KIT-0097/0098/0099

## Follow-ups for the kit (not this PR)

Six kit-canonical defects, written up with verification and suggested
fixes in **`.kit/context/KIT-0099-KIT-FOLLOWUPS.md`**:

1. Stale "Phase 6" → "Phase 7" cross-refs (`feature-developer` pair)
2. `gh run watch` has no duration timeout, but `ci-checker` documents a
   10-minute limit
3. `git commit --allow-empty` in `check-ci` can ship a dirty index
4. `code-review-evaluator`'s key-missing fallback can escalate past the
   prose tier
5. Phase 5 Step 2's evaluator snippet reads as unconditional
   (`feature-developer` pair)
6. `wrap-up` prints an unverified review-starter path

Plus, in the marketplace repo rather than the kit: `README.md` claims the
repo is private; the API says public. Material to the PII decision.

Note items 1 and 5 are **pair-rule** changes — both `feature-developer`
variants must move together.
