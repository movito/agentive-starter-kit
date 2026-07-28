# KIT-0076 Review Starter — Cut 0.9.0

**PR**: https://github.com/movito/agentive-starter-kit/pull/100
**Branch**: `feature/KIT-0076-cut-090` (worktree `../ask-worktrees/KIT-0076`)
**Prepared**: 2026-07-28 (feature-developer-f5)
**Task**: `.kit/tasks/3-in-progress/KIT-0076-cut-090.md`
**Executed specs**: KIT-0047 + KIT-0054 + KIT-0059 (moved to `4-in-review` on this branch; they complete with this task at closeout)

## ⚠️ Merge gate: planner TREE-GROUNDED VERIFICATION

This is a deletion-heavy diff (~−700 net). Per the standing rule, the
Gate-5 record is **code-reviewer-fast only**
(`.kit/context/reviews/KIT-0076-evaluator-review.md` — CONCERNS: 1
refuted, 2 declined, 0 actioned). Evaluators reconstruct pre-fix
state on diffs like this; **the planner's tree-grounded verification
is the real merge gate.** Suggested verification targets:

1. Variant sweeps reproduce clean (tokens: `verify-setup`,
   `legacy-shim`/`LEGACY_SHIM`, `bootstrap-consumer.sh`,
   `create-project.sh` [the `.sh` — the AGENT stays],
   `.kit/skills`, `agentive-kit`) — live hits only in provenance
   comments, retirement guards/docs, and frozen history.
2. The door's 9 `LEGACY_SHIM` excision points left no orphaned logic
   (`scripts/local/bootstrap` — resolution chain, forced-profile
   note, bots-declaration condition).
3. Version trio agreement: `scripts/core/VERSION` == manifest
   `core_version` == planning-heredoc baked version == **4.0.0**
   (major: core script removed = breaking sync surface).
4. CHANGELOG 0.9.0 themes are accurate against the tree (the new
   Added/Changed entries for KIT-0046/0048/0049/0066/0067/0071/0069/
   0073 were written from memory records — verify claims).
5. Consumer-seed heredoc (engine-consumer.sh) no longer lists
   `core/verify-setup.sh`.

## State at handoff

- CI green across the matrix (3.10/3.12/3.14 + lint) on `5c242d2`
- CodeRabbit: round-1 CHANGES_REQUESTED, 3 minor threads → all fixed
  in `5c242d2`, replied, resolved; round-2 scan completed clean
- BugBot: pass, no threads
- **Unresolved threads: 0**
- Local: `ci-check.sh` all 7 steps green (815 passed, 93% coverage)

## Post-merge actions (NOT done from this session)

1. **Tag `v0.9.0` AFTER merge + CI green on main** — operator or
   planner tags; this session deliberately does not.
2. **Downstream pass** (per the CHANGELOG migration note): each
   consumer's next `project sync` deletion-prunes the retired
   surfaces. KIT-0047's "downstream consumers on core ≥ doctor's
   version" acceptance criterion is delegated here (deprecation
   shipped at core 3.2.0).
3. Move KIT-0076 + KIT-0047/0054/0059 to `5-done` at closeout
   (planner owns).

## Flags for the planner (not actioned in this PR)

- **Stale `.kit/skills` mentions in backlog specs** (planner-owned
  text, deliberately not edited by this task):
  `1-backlog/KIT-0060` (names `.kit/skills/<name>/SKILL.md` as
  upstream plugin-copy sources), `1-backlog/KIT-0026` (claims builder
  skills in `.kit/skills/` are "NOT synced" — the kit_builder tier
  now syncs them from `.claude/skills/`), `1-backlog/ASK-0048`
  (offers `.kit/skills/` as a skills home option).
- **Materials-engine hardening deferred**: KIT-0054's Notes suggest
  ("consider") executing the KIT's copy of `setup-dev.sh` with
  `cwd=$TARGET` instead of the target's copy. Deferred — a behavior
  change on a newly-unfrozen surface doesn't belong in a removal-only
  release PR; candidate backlog task.
- **`run_offers` failure paths untested** (evaluator F3, declined as
  out-of-diff): candidate test-hardening backlog item.

## Review shortcuts

- Removals by commit: `163ad2d` (KIT-0047), the KIT-0054 commit,
  the KIT-0059 commit, `61c7d64` (release mechanics), then
  bookkeeping + review record + `5c242d2` (bot round 1).
- The re-pinned characterization: `tests/test_bootstrap_shapes.py`
  (door `--adopt`, hermetic config pins, exit-2 usage re-pins),
  `tests/test_entrance_shims.py` (door e2e + call-graph +
  removed-entrances guard), `tests/test_skills_homes.py`
  (retirement guard incl. dangling-symlink case).
