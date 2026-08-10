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

## Bot status at handoff — Gate 3 is PENDING, not passed

- **Cursor Bugbot**: reviewed `68072c0`. **1 Low finding — real, and mine.**
  Two consecutive `## Cross-Repo Mode` headings in `ci-checker`: the kit
  backported that section in KIT-0097 F8 while the plugin already carried
  the 2.0.0 restoration, and my three-way merge kept both. Fixed in
  `5d9f01c` by dropping the older plugin-side block and keeping the kit's
  (a strict superset — adds the no-Bash delegation path and uses the
  file's `$GH_REPO_ARG` convention instead of a hardcoded `--repo`).
  Thread replied. Swept all 27 shipped components for duplicate headings;
  this was the only one. Guard re-verified green after the fix.
- **CodeRabbit**: **no review submitted.** Its own reply states the
  account has reached the Fair Usage review limit, next included review
  ~49 min out (as of 20:53 UTC). The earlier "review in progress" note
  never resolved for the same reason. **This is a rate limit, not a clean
  review** — do not read the absence of findings as approval.

Operator's call before merge: either wait out the window and re-trigger
with `@coderabbitai full review`, or merge on Bugbot + the mechanical
verification (this being a mechanical sync whose content was already
reviewed upstream on #120/#121, with a machine-verified acceptance
criterion). Posted as a comment on the PR too.

## Remaining after merge (KIT-0099 step 5)

- [ ] Kit main's Plugin Drift Guard run GREEN — cite the run URL
- [ ] `claude plugin marketplace update agentive-skills` +
      `claude plugin update agentive-workflow@agentive-skills` →
      `claude plugin list` shows 2.0.1
- [ ] Closure comment on agentive-skills#4 referencing KIT-0097/0098/0099

## Follow-ups for the kit (not this PR)

- Two "Phase 6" → "Phase 7" cross-refs in both `feature-developer` variants
- `README.md` in agentive-skills claims the repo is private; it is public
- `ci-checker`'s Cross-Repo Mode section still lives only in the plugin —
  the standing backport candidate from #4
