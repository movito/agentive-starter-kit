## SESSION-2026-07-04 — Agent versioning, Fable-5 fork, distribution doc

**Date**: 2026-07-04
**Agent**: main session (ad-hoc maintenance, no task branch)
**Mode**: single-repo
**Scorecard**: 4 PRs merged (#61, #62, #66, #67) · 2 substantive review threads · 3 fix/pivot rounds · 5 commits total

Scope: semver + model-pin refresh across 11 agents (#61); distribution-architecture
doc + Mermaid diagram (#62); `feature-developer-f5` Fable-5 fork + bootstrap wiring
+ test coverage (#66, superseding a force-push-blocked #65); `&&`-chain cleanup
across three agents (#67).

### What Worked

1. **Verify-against-live-docs beat arguing from memory** — the `claude-sonnet-5`
   dispute was resolved by `WebFetch` to the models overview page, which proved
   the ID valid. Prevented "fixing" 8 correct pins based on a stale env block.
2. **babysit-pr caught a real defect** — BugBot flagged (Medium) that the new
   `feature-developer-f5.md` shipped KIT-LOCAL regions but was absent from
   `bootstrap-consumer.sh`'s `KIT_AGENTS`/`AGENT_EXCLUDES`, so fresh consumers
   would inherit the kit's own Project Context / Stack Notes (a KIT-ADR-0025
   identity leak). Would have shipped silently without the bot loop.
3. **Fresh-branch pivot on force-push denial** — when `git push --force-with-lease`
   was blocked, cleanly recreated the work on a new branch off current `main`
   (one squashed commit) and opened #66, closing #65 with a pointer. No fighting
   the permission wall.
4. **test count as a tripwire** — `pytest tests/test_kit_markers.py` reading 35
   instead of the expected 37 is what surfaced that I was editing on the wrong
   branch before anything was committed wrong.

### What Was Surprising

1. **The harness model list was stale** — the environment block named Sonnet 4.6
   as newest and omitted Sonnet 5 entirely, directly contradicting the live docs.
   Saved to memory (`reference_current_claude_model_ids.md`) so it isn't
   re-litigated.
2. **Edited the wrong branch after a partially-denied command** — a chained
   `git checkout main && pull | tail …` was denied as a block, so the
   `git checkout main` inside it never ran; I proceeded to edit
   `bootstrap-consumer.sh` still on `feat/feature-developer-f5` (thinking I was
   elsewhere). Caught before commit, but it cost a rebase.
3. **Stale `origin/main` ref masked every post-merge state** — after each remote
   squash-merge, `git status`/`pull` reported "up to date" or refused
   fast-forward until an explicit `git fetch`. Hit this 3+ times.
4. **Force-push is blocked in this environment** — the rebase-then-force path is a
   dead end here; branch-replacement is the supported recovery.

### What Should Change

1. **Forking a marker-bearing agent must wire bootstrap** — any new
   `.claude/agents/*.md` carrying `KIT-LOCAL` markers has to be added to BOTH
   `AGENT_EXCLUDES` and `KIT_AGENTS` in `bootstrap-consumer.sh`, or it leaks kit
   identity. This is mechanical and testable (see actions).
2. **Verify branch before the first edit of a session** — run
   `git branch --show-current` before editing, and never assume a chained git
   command ran when any part of the chain hit a permission prompt.
3. **`git fetch` before asserting sync** — treat "up to date with origin/main"
   as unreliable immediately after a remote merge; fetch first.
4. **One git command per Bash call** — chaining with `&&`/pipes both triggers
   permission prompts and silently drops steps when denied. (Same lesson the
   `&&`-cleanup PR #67 encoded into the agents.)

### Permission Prompts Hit

1. `git push --force-with-lease origin feat/feature-developer-f5` — **denied**;
   blocked the rebase strategy. Pivoted to a fresh branch (#66). New pattern,
   not in allow list (and arguably *should* stay denied).
2. Chained `git checkout main && git pull … | tail -3 …` (multi-command block) —
   **denied**; the `checkout` never executed, causing the wrong-branch edit.
   Split into separate calls thereafter.
3. `git branch -D <stale f5 branches>` — **denied**; user deleted the branches
   manually instead.

### Process Actions Taken

- [ ] Add a test asserting every `.claude/agents/*.md` containing `KIT-LOCAL`
      markers is present in both `KIT_AGENTS` and `AGENT_EXCLUDES` in
      `scripts/local/bootstrap-consumer.sh` (catches the #66/BugBot class
      mechanically). Relevant to KIT-0034 (preflight/bootstrap hardening).
- [ ] Optional: allow-list common read-only/idempotent git ops to cut prompt
      stalls; keep `push --force*` and `branch -D` denied.
- [ ] Cross-agent `&&`-idiom sweep is done for the three rule-bearing agents;
      the same idiom remains (intentionally) in `scripts/core/prepare-review-input.sh`
      and `docs/CROSS-REPO-PATTERN.md` — no action needed, noted for awareness.
