# KIT-0102 — Retire the copy-sync machinery (PR #127, ADR-0028 phase 4)

**Date**: 2026-08-12
**Agent**: feature-developer
**Mode**: single-repo (worktree `../ask-worktrees/KIT-0102`)
**Scorecard**: −3,824 net lines, 7 commits, 10 bot threads (all
resolved: 8 fixed / 1 auto / 1 deferred), 1 evaluator round (fast tier,
3 findings: 2 fixed / 1 acknowledged), **2 spec verdicts overturned by
enumeration**, 2 operator decisions, +4 tests (1085 → 1089). CodeRabbit
APPROVED at `5de7a77`; CI green on all 5 checks.

## What Worked

1. **Enumeration before deletion earned its keep twice.** The spec's
   inventory was a hypothesis, and two rows were wrong in the dangerous
   direction — "delete" on things that must live.
   `40-version-skew.py` reads as manifest machinery from its filename;
   its actual functions are venv-vs-system `adversarial-workflow`
   (KIT-0044) and black-vs-pyproject-pin (KIT-0032), with zero manifest
   involvement. `scripts/core/VERSION` had a second reader
   (`project version`) independent of the manifest that also read it.
   Deleting either would have removed live incident guards — exactly
   the KIT-0067 class the discipline exists to prevent.
2. **F2 measured instead of argued.** The architectural case was
   airtight (this repo IS `source_repo`; `origin` matches), and it
   would have been easy to stop there. Scanning the disk found a real
   manifest-carrying consumer (`varv-planning`, 2.1.0 vs canon 4.0.0)
   and diffing all 47 both-sides slots produced *evidence* for
   "0 consumer-newer" rather than an assertion.
3. **Falsifying new tests, not just running them.** Both the retirement
   tests and the parametrized sweep test were verified by breaking
   their subject: removing the `sync` branch produced
   `Unknown command: sync`; removing the planning sweep failed **only**
   the `[planning]` param. A green test that cannot fail proves nothing.
4. **Checking the drift guard's actual scope before deciding.**
   `COMPONENT_GLOBS` covers `.claude/**` only — which made
   `scripts/README.md` (stale `project sync` instructions) safe to fix
   while `upgrader.md` had to wait for a release train. Guessing either
   way would have been wrong: a red guard, or a missed live doc.

## What Was Surprising

1. **`gh api pulls/<n>/comments` is not the thread list.** It returned
   3 comments; the GraphQL `reviewThreads` query returned **10**. I
   triaged and replied to 3, believing that was the round, and only
   found the other 7 when resolving. Any future triage should start
   from `reviewThreads`, never the REST comments endpoint.
2. **A green CodeRabbit check can mean "Review rate limited".** The
   check showed `pass` while having reviewed nothing. Reading
   `pulls/<n>/reviews` for `state` + `commit_id` is the only way to
   know *what* was actually reviewed — here it revealed APPROVED at
   `5de7a77`, superseding the earlier CHANGES_REQUESTED at `86b2b60`.
3. **My own fix created the sharpest finding against me.** Sweeping the
   engine out of old consumers was correct, but the door never
   overwrites a consumer's `project`, so the sweep left `cmd_sync`
   importing a deleted module — turning a clean retirement message into
   `❌ Sync engine unavailable`. A deletion can be individually right
   and jointly wrong; the interaction is the bug.
4. **The pre-commit hook exceeds the 2-minute tool timeout** (~205–215s
   for pytest-fast). The first commit attempt was killed mid-hook and
   did NOT land — caught only by checking `git log` after, per the
   KIT-0057 rule. Every subsequent commit used a 600s timeout.
5. **A record written mid-investigation goes stale silently.** The
   enumeration artifact's "re-home required" section and its F2 totals
   were both overtaken by later findings. CodeRabbit caught both
   contradictions; I had shipped them without re-reading the document
   against its own conclusion.

## What To Change

1. **Triage from `reviewThreads` (GraphQL), not REST comments.** Worth
   promoting into the bot-triage skill: the REST endpoint silently
   under-reports, and "every thread gets a reply" is unverifiable
   against the wrong list.
2. **Treat bot check *status* as untrustworthy; read the review state.**
   `pass` + "rate limited" is indistinguishable from a real pass in
   `gh pr checks`. The completion gate should be "APPROVED (or findings
   dispositioned) at a commit ≥ the last source change", not a tick.
3. **Re-read living records before commit.** Any artifact written
   during investigation (enumeration tables, review records) needs a
   final pass against the finished work — sections written early
   contradict conclusions reached late.
4. **Consider a standing 600s timeout for commits in this repo.**
   The 120s default cannot accommodate the hook, and a killed hook
   leaves a staged-but-uncommitted tree that looks like success.

## Judgment Calls (for the planner)

- **Bootstrap cleanup pulled into scope** (operator-approved): the door
  was still seeding a manifest and shipping the engine into new repos.
  Leaving it would have made the retirement cosmetic.
- **Baked-version guard allowed to die** rather than re-homed: deleting
  both heredocs removed every `core_version` from `engine-consumer.sh`,
  so the desync it guarded became structurally impossible. Coverage was
  preserved a different way — the ship-list contract was *inverted*
  (`MUST_SHIP` → `MUST_NOT_SHIP`).
- **Stale `project` in old consumers deferred** (operator-approved):
  fixing it means breaking the door's never-overwrite invariant on a
  ~2,200-line file that may carry consumer edits. Needs its own task.

## Follow-ups

1. Release-train cleanup of six rostered `.claude/` files still
   carrying stale sync references (`feature-developer.md:65`,
   `feature-developer-f5.md:70`, `self-review/SKILL.md:99/101`,
   `upgrader.md:56/514`, three command headers).
2. Decide the stale-`project` question: force-refresh on re-bootstrap
   (policy change) vs. detect-and-warn (invariant-preserving).
3. KIT-ADR-0029's trigger fires once #127 merges.
