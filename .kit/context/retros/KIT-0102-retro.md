## KIT-0102 — Retire the copy-sync machinery, ADR-0028 phase 4 (PR #127)

**Date**: 2026-08-12
**Agent**: feature-developer
**Mode**: single-repo (worktree `../ask-worktrees/KIT-0102`)
**Scorecard**: 10 threads (0 unresolved at merge), 1 regression of a
known pattern (incomplete sweep — planner records it as the 4th
occurrence across KIT-0098/0100/0102), 2 fix rounds, 8 commits
(squash-merged as `75b73fd`). −3,824 net lines. CodeRabbit APPROVED at
`5de7a77`; 5/5 CI checks green. Evaluator: 1 round, fast tier only
(3 findings: 2 fixed, 1 acknowledged).

> Written post-merge, and it corrects my own pre-merge draft on two
> points the planner's `0d26bc6` judged more accurately. Both
> corrections are against me, and both are verified below rather than
> taken on trust.

### What Worked

1. **Enumeration overturned two spec verdicts, in the dangerous
   direction** — `40-version-skew.py` reads as manifest machinery from
   its filename; its real functions are venv-vs-system
   `adversarial-workflow` (KIT-0044) and black-vs-pyproject-pin
   (KIT-0032), with zero manifest involvement. `scripts/core/VERSION`
   had a second reader (`project version`, `project:2411`) independent
   of the manifest that also read it. Both were spec'd "delete";
   deleting either removes a live incident guard. `project doctor`
   emitting `venv-skew-adversarial` + `black-pin` is the proof.
2. **F2 measured instead of argued** — the architectural case was
   airtight (this repo IS `source_repo`, `origin` matches) and stopping
   there was tempting. Scanning disk found a real manifest-carrying
   consumer (`varv-planning` 2.1.0 vs canon 4.0.0); diffing all 47
   both-sides slots produced evidence for "0 consumer-newer" instead of
   an assertion.
3. **New tests falsified, not just run** — removing the `sync` branch
   made the retirement tests fail on the real regression
   (`Unknown command: sync`); removing the planning-shape sweep failed
   **only** the `[planning]` param. A green test that cannot fail
   proves nothing.
4. **Checked the drift guard's actual scope before deciding** —
   `COMPONENT_GLOBS` covers `.claude/**` only, which made
   `scripts/README.md` safe to edit while `upgrader.md` had to wait for
   a release train. Guessing either way was wrong: a red guard, or a
   missed live doc.

### What Was Surprising

1. **My class grep omitted the command I was retiring** — I searched
   `core-manifest|sync_from_manifest|sync-core-scripts|push-sync|CROSS_REPO_TOKEN`
   but never `project sync`. So `scripts/README.md:32-33`, which
   instructs readers to run `./scripts/core/project sync --dry-run`,
   was never on the work list; CodeRabbit found it. The sweep was
   defined from the artifacts being deleted, not from the class of
   things referencing them. Verified against the pre-change file.
2. **"Prose-dominated → fast tier only" was the wrong read** — I
   invoked the KIT-0069/0073 prose-sweep exception for a diff that was
   ~3,800 deletions plus *authored* records, messages and docs. Two of
   the substantive bot findings (`linearsync` mispresented as the
   replacement; the doc promising a pointer the command did not print)
   were first-draft authored content — precisely what a deep tier
   pre-open would have caught. Ten bot threads were the price.
3. **`gh api pulls/<n>/comments` is not the thread list** — it returned
   3; GraphQL `reviewThreads` returned **10**. I replied to 3 believing
   that was the round, and found the other 7 only while resolving.
4. **A green CodeRabbit check can mean "Review rate limited"** — a pass
   that reviewed nothing. Only `pulls/<n>/reviews` (state + `commit_id`)
   revealed the real state: APPROVED at `5de7a77`, superseding the
   CHANGES_REQUESTED at `86b2b60`.
5. **My own correct fix created the sharpest finding against me** —
   sweeping the engine out of old consumers was right, but the door
   never overwrites a consumer's `project`, so the sweep left
   `cmd_sync` importing a deleted module: a clean retirement message
   became `❌ Sync engine unavailable`. Each deletion was individually
   right; the interaction was the bug.

### What Should Change

1. **Grep-first sweeps** — write the class grep BEFORE editing; its hit
   list IS the work list. Already landed by the planner in
   `bot-triage/SKILL.md` (`0d26bc6`) as the 4th-occurrence fix. My
   session is the confirming instance: the closing grep was clean
   because it inherited the opening grep's blind spot.
2. **Mixed-shape tasks never skip the trio** — landed by the planner in
   `code-review-evaluator/SKILL.md` (`0d26bc6`), citing this PR. The
   skip rules are for trivially small *logic* changes; a task mixing
   deletions with authored content runs at least the fast tier pre-open.
3. **Triage from `reviewThreads` (GraphQL), never REST comments** —
   "every thread gets a reply" is unverifiable against an
   under-reporting list.
4. **Treat bot check *status* as untrustworthy; read the review state** —
   the gate should be "APPROVED (or findings dispositioned) at a commit
   ≥ the last source change", not a green tick.

### Permission Prompts Hit

1. **`rm -rf "$(dirname "$T")"`** in a scratch-dir cleanup while
   hand-simulating the consumer sweep — denied. Not a new pattern worth
   allowlisting: the denial was *correct* and pushed me to the better
   solution (a real parametrized test running the actual door, which
   also became durable coverage). No allow-list change requested.

### Process Actions Taken

- [x] Grep-first sweep rule added to `bot-triage/SKILL.md` (planner, `0d26bc6`)
- [x] Mixed-shape no-skip rule added to `code-review-evaluator/SKILL.md` (planner, `0d26bc6`)
- [x] KIT-0103 filed for both residues; R2 ruled detect-and-warn (planner)
- [ ] Promote "triage from `reviewThreads`, not REST comments" into
      `bot-triage/SKILL.md` — not yet covered by `0d26bc6`
- [ ] Promote "a bot check can pass while rate-limited; verify review
      state + commit SHA" into the preflight/bot-triage gates

### Incident Closure

1. **Pre-commit hook exceeds the 2-minute Bash tool timeout**
   (pytest-fast ~205–245s). First commit attempt was killed mid-hook
   and did **not** land; caught only by `git log` after, per the
   KIT-0057 rule. → **TRIAGE-GUIDE ENTRY.** Not doctor-checkable: the
   timeout is a property of the *caller's* tool budget, not the
   repo environment, so no check can observe it. The symptom→cause
   mapping ("hooks printed Passed but `git log` is unchanged" → killed
   mid-hook, re-run with a longer timeout, never `--amend`) belongs
   with the commit protocol. KIT-0101's retro already recorded
   "timeout >= 600s canonical" — this is the second occurrence, so the
   guidance exists and my session simply predated applying it.

2. **`gh` bot check reports `pass` while the review was rate-limited.**
   → **NOT-CHECKABLE NOTE**, to be added to
   `scripts/core/doctor.d/80-bot-presence.sh` alongside the existing
   CodeRabbit-quota note. Doctor can confirm the bots are *present* on
   a PR (it already does — it reported "CodeRabbit and BugBot both
   active on PR #126" this session), but it cannot know whether a given
   review actually executed: that is per-PR, per-push state discovered
   only by reading `pulls/<n>/reviews`. The existing quota note is the
   established pattern for exactly this shape.

3. **Class grep defined from artifacts, not from the referencing
   class** (the incomplete sweep). → **CLOSED — process rule already
   landed**: `bot-triage/SKILL.md` grep-first rule (`0d26bc6`). Not
   doctor-checkable (it is an authoring discipline, not an environment
   fact) and now has its documented home.

4. **Retirement left a stale `project` importing a deleted module.**
   → **CLOSED — tracked as KIT-0103 R2** with a planner ruling
   (detect-and-warn, invariant-preserving) and an acceptance criterion
   requiring one falsification against the `_old` archive shape.
