## KIT-0073 — Doc curation: 12 dispositions + the 96-line README (PR #99)

**Date**: 2026-07-28
**Agent**: feature-developer-f5
**Mode**: single-repo
**Scorecard**: 4 threads, 1 regression, 2 fix rounds, 7 commits
(4 bot scan rounds total; squash-merged `7af47a9` by operator)

### What Worked

1. **Re-verifying every citation list against HEAD before acting** —
   the audit ran on `0294bc3`, two commits behind; the Phase-2 sweep
   confirmed all citer lists still held AND caught one delta for free
   (AGENT-CREATION's `:526` TEST-SUITE citation no longer existed).
   Cost: ~4 greps. It also produced the PR-body evidence as a
   by-product.
2. **The prose-sweep gate design was vindicated exactly as specced** —
   trio verdicts CONCERNS/CONCERNS/CHANGES_REQUESTED, yet 7 of 8
   correctness claims were pre-fix-state reconstructions (refuted by
   `grep`/`ls` in under a minute each; triage table in
   `.kit/context/reviews/KIT-0073-evaluator-review.md`). Zero wasted
   fix rounds because nothing unreproduced was actioned. This is the
   second 0-for-N trio on a prose sweep (KIT-0069 was 0-for-7).
3. **Bots caught what the trio couldn't** — CodeRabbit ran an actual
   probe proving `git merge upstream/main` aborts on unrelated
   histories (a truth bug README had carried for months), and BugBot
   found the dead `cp -r .adversarial.bak/docs` restore line. Both
   tree-grounded, both real: bots 3-for-4 vs trio 0-for-8 on
   correctness — same asymmetry as KIT-0069.
4. **Batching the manifest edit with its count tests in one commit**
   (`scripts/.core-manifest.json` + `test_core_manifest.py` 11→10,
   49→48) — CI stayed green through all four rounds; the
   test-updates-ride-the-manifest rule left nothing to trip on.
5. **Deleting the `.gitkeep` before rewriting README** meant the F1
   sweep itself flagged README:411 as the one live citer, exactly as
   the audit verifier predicted — the ordering made the checklist
   self-verifying.

### What Was Surprising

1. **`project reconfigure` is destructive inside a kit worktree** —
   executed as a `displayed_commands_are_contracts` check for
   UPDATING-YOUR-PROJECT.md, it read the worktree-local Serena name
   (`agentive-starter-kit-KIT-0073`) and rewrote identity in 9 tracked
   files, including the README H1 anchor ("Agentive Starter Kit Kit
   0073") and CHANGELOG. All collateral reverted same turn; H1
   re-verified with `od -c`. The command works as documented — the
   worktree is simply the wrong context, and nothing warned about it.
2. **A grep can pass while its class fails** — the F1 citer grep for
   `adversarial/docs` returned clean on create-project.md, but the
   file still contained `.adversarial.bak/docs` (line 182). BugBot
   caught it. Fresh instance of REVIEW-INSIGHTS "a grep closes a
   token, not a class" (KIT-0069) — counted as this session's 1
   regression. The class fix removed the adjacent `.bak/scripts` line
   too (dead since KIT-0065).
3. **TESTING-WORKFLOW's "fast subset" claims were stale by 4x** — the
   doc said "~2 seconds (431/433 tests)"; measured reality is 793
   not-slow tests in ~115 s sequential. The trim replaced counts with
   the hook's verbatim command instead of new numbers that would
   drift the same way.
4. **CodeRabbit's `-x`/`--maxfail=3` finding was right about pytest
   and wrong about the fix** — the flags ARE redundant, but the doc
   line quotes `.pre-commit-config.yaml` verbatim; "fixing" the doc
   would reintroduce doc-vs-hook drift. Declined on the thread; the
   real cleanup target is the hook itself.

### What Should Change

1. **WORKTREE-WORKFLOW needs a "commands that read project identity"
   caveat** — `project reconfigure` (and anything else keyed off
   `.serena/project.yml`) must never run inside a kit worktree; the
   worktree-local Serena config makes tracked files absorb the
   worktree's identity. One paragraph in the worktree-mode
   bookkeeping section prevents the next agent repeating my incident.
2. **Extend self-review item 15 with token variants** — after fixing
   token X, grep for X *and its mutations* (`X.bak`, path prefixes,
   basename-only). The `adversarial.bak/docs` miss is the third face
   of grep-closes-a-token-not-a-class; the item should name the
   variant-sweep explicitly.
3. **`displayed_commands_are_contracts` needs an execution-context
   rule** — "execute every displayed command" is right, but mutating
   commands need a context check first (is this repo/worktree the
   context the doc displays it for?). A one-line amendment to the
   patterns.yml entry: *execute in the context the doc addresses, or
   verify inputs/flags and say so*.
4. **Backlog candidate: de-dupe the pytest-fast hook flags** —
   `-x --maxfail=3` in `.pre-commit-config.yaml` is redundant
   (`-x` wins). Trivial, but it's an executable surface, so it was
   out of scope for this prose sweep. Bundling into KIT-0070 or the
   0.9.0 sweep beats a standalone task.
5. **Trio on prose sweeps: consider fast-only** — two sweeps, two
   0-for-N trios, ~$0.40/run for the deep evaluator whose findings
   were 100% reconstruction. The Gate-5 record could be satisfied by
   code-reviewer-fast(-v2) alone on PRs already flagged
   prose-dominated, with the saved spend left for the planner's tree
   verification. Planner's call.

### Permission Prompts Hit

1. `SCRATCH=$(mktemp -d); cd "$SCRATCH" && git clone …` — denied
   (autonomous session; `$()` subshell pattern, a documented gotcha I
   walked into anyway). Reworked to a fixed `/tmp/kit0073-clone-check`
   path in ~30 s; no other prompts all session. Not an allow-list
   gap — the fix is not writing `$()` in Bash calls.

### Process Actions Taken

- [ ] Planner: commit this retro to main at closeout (it rides the
      merged feature branch only; worktree removal would orphan it)
- [ ] Planner: WORKTREE-WORKFLOW caveat — identity-reading commands
      (`project reconfigure`) never run in kit worktrees (#1 above)
- [ ] Planner: self-review item-15 token-variant extension (#2)
- [ ] Planner: patterns.yml `displayed_commands_are_contracts`
      context-rule amendment (#3)
- [ ] Planner: fold pytest-fast `-x`/`--maxfail` de-dupe into an
      existing tooling task (#4)
- [ ] Planner: decide on fast-only trio for prose-dominated PRs (#5)
- [ ] Operator sweep: `/tmp/kit0073-clone-check/`, `/tmp/kit0073-pr-body.md`

### Incident Closure

1. **`project reconfigure` identity rewrite in worktree** —
   **triage-guide entry**: belongs in WORKTREE-WORKFLOW.md's
   worktree-mode section (symptom: tracked files suddenly carry
   `<project>-<TASK-ID>` identity; cause: reconfigure read the
   worktree-local `.serena/project.yml`). Not doctor-checkable
   cheaply: the damage is transient working-tree state, visible to
   plain `git status` the moment it happens.
2. **Grep-token-variant miss (`adversarial.bak/docs`)** —
   **triage-guide entry** via the self-review item-15 extension
   (action #3); not an environment incident, no doctor surface.
3. **Evaluator CLI prints "Unknown fields in evaluator.yml" noise** —
   **not-checkable note**: schema skew between the installed evaluator
   library and the CLI's parser; cosmetic, upstream-owned
   (adversarial-workflow). If it graduates to failures, KIT-0055's
   doctor blind-spot follow-up is the home.
