# KIT-0099 — Kit-canonical follow-ups surfaced by the 2.0.1 release review

**Source**: bot review on movito/agentive-skills#5 (Cursor Bugbot +
CodeRabbit, 2 rounds) plus my own pre-PR audit
**Date**: 2026-08-10
**Status**: ✅ **ALL SIX CLOSED** — fixed in KIT-0100
([#124](https://github.com/movito/agentive-starter-kit/pull/124), merged
`7565278`) and shipped in plugin **2.0.2**
([agentive-skills#7](https://github.com/movito/agentive-skills/pull/7),
merged `558e1e9`), 2026-08-11. This file stays as the record.

Verification of the release that closed them: drift guard GREEN on kit
main ([run
31496627532](https://github.com/movito/agentive-starter-kit/actions/runs/31496627532),
`in sync: 27 shipped components`), and `claude plugin list` reports
2.0.2 enabled.

The fixes did not survive review unchanged — seven further findings
across three bot rounds on #124 and one on #7, every one correct and
every one against text the fixes themselves introduced. Two were
genuinely better than what I wrote: `--allow-empty --only` (makes the
retrigger commit structurally unable to carry staged work, rather than
checking first) and the bounded poll loop (a single `gh run view` is a
snapshot, not a wait). Detail: `.kit/context/reviews/KIT-0100-evaluator-review.md`.

## Why none of these were fixed in the release PR

KIT-ADR-0028: canonical content is fixed in the kit, then released. The
plugin drift guard hashes each shipped component against its **kit
source**, so a plugin-only edit re-opens drift and turns the guard red —
the exact condition KIT-0099 exists to clear. CodeRabbit independently
reached the same conclusion twice, writing "Apply the fix in
`agentive-starter-kit` first, then resync this plugin copy."

Each was verified present in kit canon before being filed (not a
plugin-side transform artifact). All are advisory/documentation defects,
not executable breakage — none blocks the 2.0.1 release.

## The six

### 1. Stale "Phase 6" cross-references — `feature-developer` + `-f5`

`.claude/agents/feature-developer.md:21` and `:677` (and the `-f5`
equivalents) say "see Phase 6" where KIT-0097's renumbering moved CI
polling to **Phase 7**:

- L21: "CI polling happens inline via ScheduleWakeup (see Phase 6)"
- L677: "respects the prompt-cache TTL (see Phase 6)"

Residuals of the KIT-0097 renumbering that survived the KIT-0098 repair.
Found independently by me (pre-PR) and CodeRabbit (round 2).
**Pair rule applies**: both variants must change together.

### 2. `gh run watch` has no duration timeout — `ci-checker`

`.claude/agents/ci-checker.md:186` and `:270` use
`gh $GH_REPO_ARG run watch <run-id> --exit-status` while the file
documents a 10-minute watch limit. `gh run watch` has **no duration-timeout
flag** (only `--interval`), so the documented limit is unenforceable as
written. Suggested shape: wrap in `timeout 600s` and treat the timeout
exit as `TIMEOUT`, distinct from failure.

### 3. `git commit --allow-empty` does not imply a clean index — `check-ci`

`.claude/commands/check-ci.md:105` and `:111` (single-repo and split
forms) tell the agent to run `git commit --allow-empty -m "chore:
retrigger CI"`. `--allow-empty` *permits* an empty commit; it does not
prevent staged changes from landing. Run against a dirty index, unrelated
staged work ships inside a retrigger commit.

Fix: guard with `git diff --cached --quiet` before both forms. Same class
as the self-review skill's existing "scoped staging in commit helpers"
rule — the kit fix should cite it.

### 4. Evaluator fallback can escalate past the prose tier — `code-review-evaluator`

`.claude/skills/code-review-evaluator/SKILL.md:286` says "If the required
API key is missing, fall back to another evaluator." On a prose-shaped
PR, that fallback silently escalates to `code-reviewer` or `claude-code`
— the deep tier the prose-sweep rule forbids — reached through the
degraded path rather than a decision. It also sits one section above "No
keys at all — the gate does NOT auto-open", so the two read in tension.

Fix: keep the fallback within the tier the change shape allows; otherwise
report the gate blocked.

### 5. Step 2's evaluator snippet reads as unconditional — `feature-developer` + `-f5`

Phase 5 Step 2 lists three `adversarial ...` commands with a
cost/when-to-use table. The tier-selection contract *does* exist
(the prose-sweep exception in the same section, plus Step 1's
format-by-shape rule), but a reader who lands on Step 2 sees a trio with
no branch. CodeRabbit raised this twice across rounds — presentational,
but it misread the same way both times, which is the evidence.

Fix: make the Step 2 snippet point back at the tier rule.
**Pair rule applies.**

### 6. `wrap-up` prints an unverified review-starter path

`.claude/commands/wrap-up.md:123` and `:134` print
`Review starter: .kit/context/<TASK-ID>-REVIEW-STARTER.md` in both
completion variants, unconditionally. Step 1's check (L84) is a
**repo-wide glob** (`ls .kit/context/*-REVIEW-STARTER.md`), so it can
succeed on another task's starter while the printed task-specific path
does not exist.

The file already legislates against exactly this — "Every line is a claim
— verify before printing it" — and applies it to the retro line
(`Retro: NOT WRITTEN — ...`) but not this one. Fix: same treatment,
`NOT FOUND` when absent.

## Also noted, outside the kit — ✅ RESOLVED 2026-08-11

`movito/agentive-skills` `README.md:7` claimed "This repo is private";
`gh api repos/movito/agentive-skills` reports `"private": false`. Material
to the R2 PII decision (it is the sentence most likely to make the
personal email in `plugin.json` / `marketplace.json` feel lower-stakes
than it is).

**Fixed in agentive-skills#6, merged `7b10dad`.** The README now states the
repo is public, why (a plugin marketplace needs a reachable GitHub source),
and that anything committed — including release metadata — is visible to
anyone. Two residual claims found by sweeping the class repo-wide rather
than stopping at the prompting line:

- the install snippet's `# add this private marketplace (uses your GitHub
  credentials)` — wrong twice over, since a public marketplace needs no
  credentials; and
- `CONSOLIDATION.md`, a dated 2026-05-21 rollout runbook from when the
  marketplace was planned as private. Text kept intact as provenance with
  a "historical record — not current state" note added, rather than
  rewriting a dated document to be consistent with the present.

CodeRabbit independently flagged the README/CONSOLIDATION inconsistency on
that PR, converging on the same defect from the opposite direction, and
approved the result.
