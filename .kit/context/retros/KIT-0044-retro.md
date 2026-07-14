## KIT-0044 — Worktree-Based Implementation Sessions (PR #76) — SECOND WORKTREE PILOT

**Date**: 2026-07-14 (finalized post-merge — PR #76 squash-merged as `fd28703`)
**Agent**: feature-developer-f5
**Mode**: single-repo (session ran in `ask-worktrees/KIT-0044`, pre-provisioned by the planner)
**Scorecard**: 4 threads (3 CodeRabbit + 1 BugBot, all real), 0 regressions, 2 fix rounds, 6 commits

### The four flags (headline items for the planner)

1. **The aider-based evaluator edited the working tree mid-review** —
   `code-reviewer-fast-v2` applied its own suggested fix directly to
   `scripts/local/new-worktree.sh` during the review run. Benign this
   time (nullglob hardening, kept); silently dangerous in general.
   New rule: **`git status` immediately after every evaluator run**,
   before anything is staged. (Detail: Surprising #2, Should Change #1.)
2. **`ADVERSARIAL_UNATTENDED` never existed** — the env flag advertised
   by `prepare-review-input.sh` 1.5.0 appears nowhere in the installed
   adversarial-workflow library; every non-TTY evaluator run on a large
   input died on the interactive prompt. Fixed in 1.5.1 with the
   verified `echo y |` pattern. Lesson: shipped hints about another
   tool's interface need verify-before-believing too. (Detail:
   Surprising #3, Should Change #2.)
3. **The harness resets shell cwd to the primary clone between Bash
   calls even in a worktree-launched session** — pilot friction #1 is
   only half-fixed by the LAUNCH block; `cd`/`git -C` prefixes are still
   required for shell commands. Needs one more worktree session of data,
   then either document as the standing pattern or escalate. (Detail:
   Surprising #1, Should Change #3.)
4. **This worktree needs `git worktree remove --force` post-merge** —
   it was created before the `.gitignore` symlink fix landed, so its
   provisioning symlink still reads as untracked. Worktrees created
   after this merge remove cleanly. (Detail: What Worked #4, lifecycle
   section of WORKTREE-WORKFLOW.md.)

### Six-friction confirmation (the acceptance criterion)

| # | KIT-0043 friction | Status |
|---|-------------------|--------|
| 1 | Session tab not in worktree (~40 `cd` prefixes) | **ADDRESSED** (LAUNCH block un-skippable in template 1.1.0; helper prints it) — but see Surprising #1: the harness *still* resets shell cwd between Bash calls even in a worktree-launched session, so `cd` prefixes persist at a level no kit artifact can fix |
| 2 | Stale pre-created branch | **ADDRESSED** — helper branches from fresh `origin/main` after fetch; reproduced live this session (worktree was 1 behind at start because it predated the planner's task-spec commit; ff-merged) |
| 3 | Missing gitignored runtime artifacts | **ADDRESSED** — enumerated list in the helper, sources pre-flighted before creation (CodeRabbit hardening), `.gitignore` audit done (Serena/dispatch/caches deliberately excluded, reasons in the helper comments) |
| 4 | GIT_DIR env contract | **ADDRESSED** — documented in WORKTREE-WORKFLOW.md (contract + canary); conftest fix NOT re-implemented (N2); canary green after every pre-commit run this session |
| 5 | Bare-repo closeout / bare-hub question | **ADDRESSED** — decision record in the doc: declined at current scale, enumerated migration costs, 3 revisit triggers |
| 6 | Worktree lifecycle ownership | **ADDRESSED** — planner removes post-retro; plain `remove` works once the `.gitignore` symlink fix merges (verified in isolated repo) |

### What Worked

1. **The task was genuinely self-demonstrating** — running the helper from
   *inside* the KIT-0044 worktree proved the `git-common-dir` resolution
   (symlinks landed on the primary, not the invoking worktree), which then
   became the decline evidence for o3's nested-worktree finding. Build
   artifact and test fixture were the same object.
2. **Evaluator-before-PR ordering (KIT-0035 F3) again produced a quiet PR** —
   4 evaluator findings fixed pre-push; the bots then found only 3 issues,
   all fixable in one round, and CodeRabbit flipped to APPROVED on the fix
   commit. Second consecutive validation of the ordering rule.
3. **Verify-before-believing killed two o3 claims in one command each** —
   "`--path-format` needs git ≥2.43" (works on local 2.39.2; landed in
   2.31) and "nested-worktree dirname math is one level too high"
   (`dirname /repo/.git` = `/repo`, verified from both primary and
   worktree). Cost: ~20 seconds; saved: two pointless rewrites.
4. **The scratch-worktree test loop surfaced a real design bug the spec
   didn't anticipate** — plain `git worktree remove` was permanently blocked
   by the unignored evaluators symlink (dir-only `.gitignore` pattern).
   The empirical cycle (create → commit → remove) found it; static review
   had not.
5. **Canary discipline held all session** — `core.bare=false` checked after
   every pre-commit run in the worktree (4 runs). The KIT-0043 leak class
   stayed dead under real hook conditions; the conftest fix is validated.

### What Was Surprising

1. **A worktree-launched session still pays cd prefixes** — the harness
   resets the shell cwd to the *primary clone* after every Bash call
   (`Shell cwd was reset to …/agentive-starter-kit`), even though this
   session's tab was opened in the worktree. Friction #1 is only half-fixed:
   the LAUNCH block puts file tools in the right place, but shell commands
   still need explicit `cd`/`git -C` prefixes. This is harness behavior,
   not something a kit artifact can change — worth a note in
   WORKTREE-WORKFLOW.md if it persists next session.
2. **The aider-based evaluator MUTATED the working tree during review** —
   `code-reviewer-fast-v2` applied its nullglob SEARCH/REPLACE edit
   directly to `scripts/local/new-worktree.sh` mid-review ("Applied edit
   to…" in its log) despite the input being added read-only. The edit was
   benign and kept, but a hostile-or-wrong edit would have been silently
   committed later. New rule: **run `git status` immediately after every
   evaluator invocation**.
3. **`ADVERSARIAL_UNATTENDED` never existed** — all three first-round
   evaluator runs died on the interactive large-input prompt (EOFError).
   The env flag that `prepare-review-input.sh` 1.5.0 advertised (added in
   the KIT-0035/0040 era) appears nowhere in the installed library source.
   I shipped a hint in a core script without verifying it against the
   installed package — same lesson as the bare-repo misattribution, one
   layer down. Fixed in 1.5.1 (`echo y |` piping, verified working).
4. **All four bot findings were real — zero noise threads** —
   CodeRabbit's three (template example drifted: derived slug ≠ shown
   branch; the "from anywhere" claim was wrong; warn-and-continue
   contradicted the "fully-provisioned" contract) plus BugBot's
   second-round catch (lowercase task IDs passed the format regex but
   the case-sensitive spec glob diverged from `project start`'s
   uppercase normalization — fixed in `8942869`). Fix quality benefited
   from the temp-then-commit pattern already being documented —
   pre-flight-then-mutate was the obvious shape.

### What Should Change

1. **Evaluator post-run `git status` check** — add to the
   code-review-evaluator skill and/or Phase 7 of feature-developer:
   aider-based evaluators can write to the repo; diff/status must be
   inspected after every run before anything is staged (Surprising #2).
2. **Verify shipped hints against installed tool versions** — a
   "helpful hint" printed by a core script is a claim about another tool's
   interface; it needs the same verify-before-believing treatment as an
   evaluator finding (grep the installed package, run it once). Candidate
   for the self-review checklist (Surprising #3).
3. **Harness cwd-reset needs one more session of data** — if the next
   worktree session also gets per-call cwd resets to the primary, document
   the `git -C`/`cd`-prefix requirement in WORKTREE-WORKFLOW.md as the
   standing pattern instead of treating it as friction to eliminate
   (Surprising #1).
4. **Preflight arg shape is easy to get wrong** — `preflight-check.sh
   KIT-0044 --pr 76` fails ("Unknown argument"); it wants `--task KIT-0044
   --pr 76`. The preflight skill's own Step 1 example shows the positional
   form. Fix the skill doc (or accept a positional task-id in the script).

### Permission Prompts Hit

None.

### Process Actions Taken

- [x] All six KIT-0043 frictions addressed (table above) — none re-filed
- [x] `prepare-review-input.sh` 1.5.1: dead UNATTENDED hint replaced with
      verified `echo y |` pattern
- [x] Evaluator review + 13-finding disposition persisted
      (`.kit/context/reviews/KIT-0044-evaluator-review.md`)
- [x] Scratch worktree + branch fully cleaned up; primary worktree list
      back to primary + KIT-0044 only
- [ ] Planner: post-merge, remove this worktree (`--force` — it predates
      the `.gitignore` fix), `project complete KIT-0044`, delete branch
- [ ] Planner: consider retro items 1 (evaluator git-status check), 2
      (verify shipped hints), 4 (preflight skill arg example) as process
      fixes; item 3 waits for next worktree session's data
