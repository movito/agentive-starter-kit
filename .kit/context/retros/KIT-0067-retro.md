## KIT-0067 — Factory Front Door + Structural Cleanup (PRs #97 + #98)

**Date**: 2026-07-28
**Agent**: feature-developer-f5
**Mode**: single-repo
**Scorecard**: 5 threads (4 on #97, 1 on #98), 0 regressions, 2 fix rounds (one batch per PR), 15 commits (stacked pair: #97 = 6, #98 = 9)

### What Worked

1. **Evaluator-before-PR caught the real bugs pre-bot** — the fast
   gate's round-1 finding (`first-session` region surviving a
   `--no-kit` re-bootstrap while the planner is pruned) and round-2's
   two removal-safety edges (customized-body deletion, malformed-marker
   awk runaway) were all genuine, all fixed before #97 opened. Bots then
   found only style/wording — zero substantive rounds burned.
2. **Verify-before-believing neutralized a hallucination-heavy PR2
   trio** — the fast evaluator's three "correctness" FAILs and o3's
   `.kit/launchers/.locks` claim were all refuted in ~4 greps against
   the tree (`setup-serena.sh` exists; engines never copy the template;
   CLAUDE.md has zero launcher refs; `LOCK_DIR` is /tmp). Only 1 real
   latent fix (remedy quoting on space paths) and 1 test gap survived
   from 10 PR2 findings.
3. **Threads-are-the-truth (KIT-0062) paid again** — BugBot's check on
   #98 read "skipping", CodeRabbit's on #97 read "pass"; fetching
   threads anyway surfaced 1 real BugBot finding and 4 CodeRabbit
   threads (a CHANGES_REQUESTED review behind a green check-run).
4. **Stacked-PR structure with parallel work** — implementing F4–F8 on
   the stacked branch while #97's CI/bots ran cost zero wall-clock
   waiting; the rebase after #97's bot round was clean because the two
   PRs' README edits were partitioned deliberately (PR1 adds, PR2
   reworks).
5. **The manifest count tests did their job twice** — both the
   `.kit/launchers/` removal and the baked planning-heredoc version
   bump were caught by `test_core_manifest.py` before commit, exactly
   the enforce-in-same-commit contract the Project Context promises.

### What Was Surprising

1. **`.kit/launchers/launch` was load-bearing for create-agent.sh** —
   D1 read as "delete three operator scripts" but the launcher was
   also the registration target for `scripts/optional/create-agent.sh`
   (~150 lines of array-editing code + a fixture + concurrency tests).
   Retirement needed a degrade-gracefully design (skip-with-notice)
   because pre-0.9.0 consumers still carry launchers until sync prunes
   them.
2. **Stacked PRs get no CI and no CodeRabbit** — test.yml triggers on
   main-based PRs only and CodeRabbit "reviews are disabled for this
   base branch", so #98 shows Gate 1 PENDING by construction. BugBot
   still scanned it (and posted a finding under a "skipping" status).
   The merge-order note in the review starter is the mitigation.
3. **The class sweep missed an indented fence** — my `^```$` sweep for
   CodeRabbit's MD040 finding fixed 4 fences but missed a list-indented
   one three lines away; caught only by re-grepping with the anchor
   relaxed. Zero-hit grep proves the token, not the class — again
   (self-review item 16's exact caveat, now with a whitespace face).
4. **The full-format evaluator input exploded to 966KB on the
   archival PR** — `--format full` vs main re-included all of PR1 plus
   every archived file's moved text. Scoping to `--base <PR1-branch>
   --format diff` cut it to 246KB, at the cost of the diff-only
   hallucination mode the PR2 trio then exhibited on cue.

### What Should Change

1. **prepare-review-input.sh should support stacked PRs natively** —
   a `--base` that defaults to the stack parent when the branch's PR
   base isn't main would have produced the right input on the first
   try, and a size guard (warn >500KB) would flag the
   moved-text blowup before an evaluator spends it.
2. **Preflight Gate 1 should recognize the stacked-PR shape** — when
   the PR's base branch is not the default branch, report
   `PENDING: stacked on <base> — CI runs on retarget`, not "no CI runs
   registered" (which reads as a mystery). Cheap: `gh pr view --json
   baseRefName` is already in the gate's reach.
3. **Fence sweeps must be indentation-tolerant** — the MD040 class
   pattern is `^\s*```(\s*$)`, not `^```$`. Worth a line in the
   bot-triage skill's class-sweep examples.
4. **A migration note for downstream launcher deletion** — the 0.9.0
   downstream pass should explicitly run the manifest sync's deletion
   pruning against DSP/AEL (they carry root `agents/` launchers per
   the migration playbook, now updated to delete-not-move).

### Permission Prompts Hit

None — all Bash calls ran with sandbox override under the session's
standing approval; no interactive permission stalls occurred.

### Process Actions Taken

- [ ] prepare-review-input.sh: stack-aware `--base` default + input
      size warning (tooling change, planner to file)
- [ ] preflight-check.sh Gate 1: name the stacked-PR condition
      (tooling change, planner to file)
- [ ] bot-triage skill: indentation-tolerant fence-sweep pattern
      (doc line)
- [ ] 0.9.0 downstream pass: run deletion pruning for retired
      `.kit/launchers/` in consumers (rides the existing 0.9.0 plan)

### Incident Closure

1. **Stacked PR → no CI / no CodeRabbit / BugBot-still-scans** —
   triage-guide entry: documented in
   `.kit/context/KIT-0067-REVIEW-STARTER.md` (merge-order section) and
   this retro; the proposed Gate 1 wording change (Process Actions) is
   the durable fix. Not cheaply doctor-checkable (PR-shape-dependent,
   not environment state).
2. **Evaluator diff-only fabrications on archival diffs** — already
   covered by the existing verify-before-believing rule in the
   feature-developer Phase 7 text and the prose-sweep exception
   (KIT-0069); this session adds the o3 tenth/eleventh fabrication
   data points to the record. No new check needed — the rule held.
3. No environment incidents (doctor, venv, worktree all behaved).
