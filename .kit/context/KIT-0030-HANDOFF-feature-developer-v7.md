# KIT-0030: Plugin Consolidation — Implementation Handoff

**You are feature-developer-v7. Implement this task directly. Do not delegate or spawn other agents.**

**Date**: 2026-06-13
**From**: Coordinator (moss session, KIT-ADR-0024 initiative)
**To**: feature-developer-v7 (claude-fable-5)
**Task**: `.kit/tasks/2-todo/KIT-0030-plugin-consolidation.md`
**Status**: Ready for implementation
**Target Codebase**: This repo (agentive-starter-kit) + movito/agentive-skills + three downstream repos (see Repo Map)

---

## Why This Task Exists

KIT-ADR-0024 (2026-06-12) decided that shared skills, commands, and agents
distribute to projects via the `agentive-workflow` plugin
(movito/agentive-skills), semver-pinned per project. Phases 0 (KIT-0028,
canonical pattern doc) and 1 (KIT-0029, canonical feature-developer-v7) are
done and pushed. You are Phase 2: make the plugin the distribution channel
and migrate the three active projects. Phase 3 (KIT-0031, per-project pin
policy) comes after you.

Read these before writing anything:

1. `.kit/tasks/2-todo/KIT-0030-plugin-consolidation.md` — the spec; the
   spike (Requirement 1) gates everything else
2. `.kit/adr/KIT-ADR-0024-*.md` — §3 is the plugin decision you implement
3. `docs/CROSS-REPO-PATTERN.md` — canonical pattern the preflight check
   (Requirement 4) validates

## Repo Map

All repos are checked out locally as siblings:

| Repo | Path | Role in this task |
|------|------|-------------------|
| agentive-starter-kit | `~/Github/agentive-starter-kit` | This repo: spec, inventory artifact, preflight check, CHANGELOG |
| agentive-skills | GitHub: `movito/agentive-skills` (clone if no local checkout) | The plugin — gets agents/commands/skills, semver release |
| label-maker-planning | `~/Github/label-maker-planning` | Migration #1 (lowest risk — already consumes 5 plugin skills) |
| suwinex-planning | `~/Github/suwinex-planning` | Migration #2 (split-topology project, target repo = suwinex) |
| moss-skolemusikkorps | `~/Github/moss-skolemusikkorps` | Migration #3 (monorepo; pre-`.kit/` layout: `delegation/` + `.agent-context/`) |

Use explicit `git -C <path>` / `gh --repo <owner>/<repo>` for every
cross-repo operation. Never rely on `cd` alone — task scripts reset the
shell cwd.

## What Prior Phases Already Learned (do not rediscover)

- **Plugin skill support is proven**: label-maker-planning consumes five
  skills from `agentive-workflow`. Agent and command support is NOT proven —
  that is your spike, and it gates Requirements 3–5.
- **label-maker `.claude/commands/` have ZERO cross-repo detection**
  (Phase 0 finding) — they run git/gh against the planning repo. Folded
  into your Requirement 5: migrating label-maker to plugin commands with
  topology detection fixes this.
- **The newest `/wrap-up` generation lives in suwinex-planning** (v1.3.0:
  Step 0 cross-repo detection, GIT_TARGET/GH_TARGET, planning-repo
  exception). Canonicalize from THAT version, not the kit's or moss's
  (moss v1.1.0 is a monorepo retrofit, a103bbe).
- **Helper scripts exist only downstream**: `prepare-review-input.sh` and
  `lib/target_repo.sh` (suwinex/label-maker). If commands you canonicalize
  depend on them, upstream them as part of this task and note it in the
  CHANGELOG.
- **`feature-developer-v6.md` (kit) is the Opus-class copy of v7** —
  content-identical, pin `claude-opus-4-8`, per user decision. If the
  plugin ships feature-developer agents, ship both; never edit v6's
  workflow directly (edit v7, re-copy — see v6's banner).
- **The kit's v7 (2.1.1) has its extension points filled with kit-specific
  content.** The clean template for distribution is v6's body (unfilled
  ACME example) or git history at v7 2.1.0 (commit 035e839). The plugin
  copy must ship the UNFILLED template.

## Hard Constraints (user decisions — do not relitigate)

- **moss stays a monorepo for now** — topology decision deferred. Plugin
  migration applies regardless; do not push a `.kit/` layout migration.
- **Never stage or delete the untracked `.kit/adversarial/` directory**
  in this kit repo — it is the user's to remove.
- **Pushes, releases, and PRs in ANY repo require explicit user
  confirmation first.** Tagging a plugin release (Requirement 3.2) is
  visible/shared state — ask before tagging.
- **Spike fallback is pre-authorized**: if plugins cannot ship agents,
  stop, record findings, fall back to manifest distribution for agents
  (KIT-0026 mechanism), and add the KIT-ADR-0024 §3 addendum (spec
  Requirement 1.4). No need to ask permission for the fallback itself —
  but report it.

## Suggested Order

1. `./scripts/core/project start KIT-0030` (moves spec to 3-in-progress)
2. **Spike** (Requirement 1) — scratch project, trivial agent on a test
   branch of movito/agentive-skills. Deliverable: invocation conventions
   per artifact type + the migration checklist. STOP and report if agents
   don't work; the fallback changes the rest of the plan.
3. **Inventory** (Requirement 2) — table committed to `.kit/context/`.
   Diff every local copy against its would-be plugin version BEFORE
   classifying; divergences get promoted upstream or recorded as
   overrides (Risk 3 — this is how v7 almost stayed stranded in moss).
4. **Plugin contents + release** (Requirement 3) — ask user before tagging.
5. **Preflight check** (Requirement 4) — fail/warn semantics per spec;
   tests in `tests/` (pytest, 80% coverage on new code, pre-commit
   gauntlet applies).
6. **Migrations** (Requirement 5) — label-maker → suwinex → moss, one
   end-to-end task run in each before declaring done.

This is a 2–3 session task. If you reach the end of a session mid-stream,
write a session handoff in `.kit/context/` so the next session can resume.

## Acceptance Criteria

Mirror of the spec — all six boxes in
`.kit/tasks/3-in-progress/KIT-0030-plugin-consolidation.md` must be
checked, including the CHANGELOG entry stating the KIT-0026 relationship
(channels coexist: plugin = outbound to projects, manifest = kit-to-kit).

---

**Task File**: `.kit/tasks/2-todo/KIT-0030-plugin-consolidation.md`
**ADR**: `.kit/adr/KIT-ADR-0024` (§3)
**Prior phase commits**: KIT-0028 (624a11e, kit 0.5.1), KIT-0029 (035e839 + b2aedc3 + 742c67e, kit 0.6.0)
**Handoff Date**: 2026-06-13
