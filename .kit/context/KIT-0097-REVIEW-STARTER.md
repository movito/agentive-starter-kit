# Review Starter — KIT-0097: Canonical `.claude/` content fixes from the 2.0.0 review

**Task**: `.kit/tasks/4-in-review/KIT-0097-canonical-agent-content-fixes-from-2.0.0-review.md`
**PR**: https://github.com/movito/agentive-starter-kit/pull/120
**Evaluator record**: `.kit/context/reviews/KIT-0097-evaluator-review.md`
(raw logs: `…-evaluator-review-logs.md`)
**Date**: 2026-08-09

## ⚠️ The Plugin Drift Guard is RED — by design

It reports **"kit content is newer than the published release"** for 16
files. That is the fix-here-then-release contract working: this PR lands
the fixes in the canonical tree, and plugin 2.0.1 (this task's release
step) syncs the channel afterward. **It cannot go green on this PR** —
the fix ships in a different repo.

Merge-go is: **green except the by-design drift check** — Tests ×3 and
Lint pass, BugBot clean, all bot threads replied to and resolved.

⚠️ **Verify CodeRabbit's state yourself before merging.** It auto-paused
mid-PR ("influx of new commits") and reported a green check while two
commits sat unreviewed; a forced full review then found 11 more
findings. Check that its most recent review's `commit_id` matches head
rather than trusting the check mark:

```bash
gh api repos/movito/agentive-starter-kit/pulls/120/reviews \
  --jq '[.[] | select(.user.login=="coderabbitai[bot]")] | last | .commit_id'
git rev-parse HEAD
```

Note: `planner` and `planner-f5` appear in the guard's list but were
**not touched by this PR** — that is KIT-0096 completion drift already
sitting on `main`. 2.0.1 sweeps it up too.

## What this PR is

The 2.0.0 marketplace review (movito/agentive-skills#4) put 23 bot
rounds through the kit's canonical agent instructions and found 21 real
defects — including two places where the CANON had regressed behind the
shipped plugin. All fixed at the source, per KIT-ADR-0028.

**Headline (F1, BugBot High)**: the feature-developer Workflow Overview
table ordered `7. Evaluator` after `6. CI + Bots`, contradicting the
pre-PR trio rule mandated since KIT-0035/KIT-0046. An agent following
the table opened the PR first and burned a bot round on every
evaluator-driven rewrite. Phases renumbered (Evaluator 5, Ship 6,
CI+Bots 7), section physically moved, cross-references fixed — **and
pinned by a contract test** so it cannot silently regress again.

## Where to spend your review time

**Read these two closely — I rewrote them three times across bot rounds:**

- `.claude/agents/ci-checker.md`
- `.claude/commands/check-spec.md`

Both now source `scripts/core/lib/target_repo.sh` for topology detection
and then apply a both-or-neither check themselves. The rewrite count is
the honest signal: my first two attempts each had defects the bots
caught (see "Defects I introduced" below).

**Also worth a careful look:**

- `.claude/agents/feature-developer.md` — the phase reordering is the
  largest structural change in the PR.
- `.claude/agents/upgrader.md` — `TARGET_REF`/`CURRENT_REF` resolution
  and the rollback rewrite.

## Verification already done

- **Full suite green per push**: 1204 passed, 13 skipped (pytest-fast
  runs ~300–390 s locally as a pre-commit hook — the ~213 s figure in
  TESTING-WORKFLOW is optimistic; budget ≥360 s).
- **Three new contract-test assertions + one new test**, each broken
  once and observed to fail (house rule):
  - evaluator precedes Ship precedes CI+Bots, by **both** declared phase
    number and document order
  - the overview table row states the pre-PR-open rule
  - `test_agent_pair_bodies_stay_identical` — both pairs' bodies below
    `## Workflow Overview`, normalizing the identity header
- **Pair sync verified** after every edit: feature-developer/-f5 differ
  only in frontmatter, variant preamble, and the response-format line.
- **Topology snippet verified empirically** against the real parser in
  six cases: Path-only, GitHub-only, both, neither, malformed
  `owner/name`, and library-absent.
- **`version:` bumped** on every touched file.

## Defects I introduced and the bots caught — read this before merging

I want this visible rather than buried in the disposition table.

**Counting unit** (stated because two artifacts disagreed until now):
a *finding* is one posted bot thread or one distinct evaluator finding.
CodeRabbit consolidates several file sites into one thread, so a thread
can carry more than one edit — the disposition table in
`.kit/context/reviews/KIT-0097-evaluator-review.md` counts those sites
individually and therefore runs higher. Both are correct at their own
grain; the table is authoritative for per-site detail, this file for
thread-level totals.

At review-starter time: **1 evaluator round + 7 bot rounds**, 34 bot
threads plus 20 evaluator findings. A meaningful share were defects in
my *own* fixes:

1. **My F14/F15 fixes reproduced the bug they were fixing.** The prose
   said "route through the target repo in split mode" while the runnable
   snippet beside it stayed bare. An agent copies the runnable line.
   Both bots found this independently. Fixed at the root: `TARGET` is
   now set in single-repo mode too, so one command form is correct in
   both topologies and there is no bare variant to copy.
2. **I described the parser's contract from its header comment, not its
   code.** `target_repo.sh:23` promises both `Path` and `GitHub`;
   `_target_repo_validate()` returns 0 early when `TARGET_REPO` is
   empty, so nothing enforces it. BugBot rated it High. Correct — see
   the planner note below.
3. **`$PLANNING` written as a shell variable** that persists across tool
   calls. It doesn't; each Bash call is a fresh shell, so
   `"$PLANNING"/scripts/…` would have become `/scripts/…`.
4. **Gate 5 review-record paths left relative** in four places — in
   split mode they'd land in the target worktree, never be found, and
   fail a gate the work had satisfied.
5. **F7 half-applied**: I removed the CI block from the read-only
   reviewers but left them instructed to run `adversarial` (needs Bash)
   and author handoff files (needs Write).

All are fixed and verified. The pattern is why this diff deserves a real
read rather than a rubber stamp on green checks.

6. **A "green" bot check twice meant "not looking".** "23/23 threads
   resolved" hid two Major findings that lived in a review BODY under
   *Outside diff range comments* (never threads). Then CodeRabbit
   **auto-paused** after too many pushes — its check stayed green while
   two commits went unreviewed. A `@coderabbitai full review` produced
   11 further findings. Both are counted above; both are also a
   `bot-triage` gap worth a follow-up (a passing bot check should be
   compared against head's SHA before it counts as coverage).

## Declined findings — the ones with judgment in them

- **F19 (MD029 on babysit-pr)** — the list is genuinely sequential 1–7;
  CodeRabbit was linting numbering that only looked wrong inside the
  diff hunk. Exactly the false-positive class KIT-0094 exists to decide
  once, centrally.
- **F16's premise was wrong** — it claimed `--task` is required.
  `agentive preflight --help` shows it defaults to derived-from-branch.
  Documented the real reason to pass it explicitly alongside `--repo`
  instead of asserting a falsehood.
- **2× wrap-up comments** — severity header and analysis scripts, no
  finding body. Nothing stated to act on; said so rather than changing
  working text on speculation.
- Three evaluator findings that restated an instruction and asserted the
  agent might not follow it (true of every line in every prompt file).

## 📋 For the planner — parser gap, deliberately NOT fixed here

`scripts/core/lib/target_repo.sh` accepts a **half-filled**
`## Target Repository` section. Verified repro in the task spec: with
`Path` only it returns **0**, sets `GIT_DIR_ARG`, and leaves
`GH_REPO_ARG` empty — split-brain, where `git` targets one repo while
`gh` silently hits the planning repo.

Operator decision at triage (2026-08-09) was **fix the docs now, write
the parser up separately**. The write-up is in the task spec with the
repro, the cause (`target_repo.sh:131-137`), and a suggested fix in
`_target_repo_validate()` so every caller benefits. It also notes that
the local both-or-neither checks I added to ci-checker/check-spec become
redundant once the parser enforces it — whoever takes that task should
simplify them back.

## After merge — the 2.0.1 release step (this task's last AC)

1. Refresh the changed files into `movito/agentive-skills` under
   `plugins/agentive-workflow/` with the KIT-0096 generalization
   transforms (KIT-LOCAL regions do not ship)
2. Update `roster.yaml` hashes; bump `plugin.json` → 2.0.1
3. Marketplace PR — CodeRabbit reviews there too (23 threads last time)
4. After that merges: drift guard green on kit `main`;
   `claude plugin marketplace update agentive-skills` +
   `claude plugin update agentive-workflow@agentive-skills` lands 2.0.1
5. Reply on agentive-skills#4's summary thread that the closure shipped

**Rider R2 lands in that PR, not this one**: `plugin.json` /
`marketplace.json` carry your personal email in `author`. The
keep-or-switch-to-noreply choice gets surfaced there for you to decide —
I will not choose silently.
