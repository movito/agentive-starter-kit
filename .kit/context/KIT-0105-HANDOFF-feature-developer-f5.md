# KIT-0105: `project-intake` ships in the plugin — Implementation Handoff

**You are the feature-developer-f5. Implement this task directly. Do
not delegate or spawn other agents.**

**Date**: 2026-08-14
**From**: planner-f5  **To**: feature-developer-f5
**Task**: .kit/tasks/4-in-review/KIT-0105-project-intake-into-the-plugin.md
**Status**: Ready
**Evaluation**: arch-review-fast APPROVED (2026-08-14), two findings
dispositioned in the spec header. The parent ADR (KIT-ADR-0031) was
evaluated at the 0030-split. Don't re-litigate either.
**Target Codebase**: kit repo (PRs 1–2, worktree) + marketplace repo
(PR 3, planner-created branch, via `git -C` — the KIT-0109/0110
precedent)

## Session topology (read before anything else)

- **Session home / PRs 1–2**: worktree
  `/Users/broadcaster_three/Github/ask-worktrees/KIT-0105`, branch
  `feature/KIT-0105-intake-into-plugin` (real venv,
  planner-provisioned). PR 2 gets a fresh branch off updated main —
  ask the planner when PR 1 merges (never create branches).
- **PR 3**: branch `release/agentive-workflow-2.1.0` in
  `/Users/broadcaster_three/Github/agentive-skills` — planner-created;
  verify with `git -C … branch --show-current` before any commit
  there.
- The spec's `## PR Plan` is authoritative for what rides where.

## Verified anchors (2026-08-14 — re-verify before relying)

- `.claude/agents/project-intake.md:165` (init.defaultBranch
  rationale) and `:200` (`branch --show-current` must print `main`) —
  the F4 guard, verified TODAY at exactly those lines. Carry through
  the rewrite unchanged; add a test, not a fix.
- `roster.yaml:146–151` (marketplace): `project-intake` is
  `ships: false` with the why-line KIT-0104 made false — F1 flips it
  and deletes the rationale. Membership change ⇒ **minor bump
  2.0.4 → 2.1.0**, all version fields (KIT-0099: four of them).
- `scripts/local/plugin_resync.py` — the release tool (KIT-0110).
  `--hashes-only` computes `plugin_sha256`; three-way merge is the
  resync method; base-not-found fails loud. THIS release is its first
  cut — the KIT-0110 AC you close by citing it in the release record.
- Marketplace: `Verify published bodies against roster.yaml` is a
  REQUIRED check on main (ruleset 20868466, active) — your release PR
  cannot merge without it. `verify_plugin_integrity.py` also flags
  unrostered files: the new `agents/project-intake.md` body MUST have
  its roster entry in the same commit.
- Bots on marketplace: CodeRabbit AND BugBot both verified present
  (PR #10). CodeRabbit spending-cap face: status can read "pass —
  rate limited" while NO review exists — reviewThreads first; recovery
  = operator raises cap, then `@coderabbitai review`.

## Mission notes beyond the spec

- **F2 location-agnosticism**: the packaged agent's install-check
  instruction should mirror the shim's own degradation text
  (`uv tool install agentive-kit` … — see `scripts/local/bootstrap`
  lines 172–178 for the voice). Working-directory-as-candidate: state
  it, verify it, never assume the operator gave a path.
- **F5 prose sweep**: the class is "intake runs kit-side" — grep it,
  don't fix only the four listed sites. Packaged-twin mirror rule
  applies (`test_door_data_sync.py`) — PROTOTYPE-HANDOFF-TEMPLATE has
  a door-data twin.
- **F6 acceptance test**: extend `tests/test_scaffold_acceptance.py`
  — create → doctor → assert every file path referenced by the seeded
  agents exists (the KIT-0081 F2 class, by machine). This is
  KIT-ADR-0034's enforcement mechanism; treat its assertions as the
  deliverable, not decoration.
- **PR 2 passengers**: KIT-0103 R1's work-list is derived by grep at
  execution (its spec's rule); KIT-0112 includes the seventh
  lying-status face insertion into bot-triage (its R2 — text staged in
  that spec). Canon edits only; every touched rostered component gets
  a `version:` frontmatter bump (the KIT-0109 F1 lesson — KIT-0111's
  guard doesn't exist yet, so the discipline is manual this train).
- **Release (PR 3)**: CHANGELOG explicit empty categories (upgrader
  reads it); README component tables updated; markdownlint job added
  to the existing workflow file or a sibling (KIT-0110 F2 rider —
  cheap now).

## Out of scope — do not touch

- The derived-brief fallback (KIT-ADR-0033 — sequenced later).
- KIT-0103 R2–R4 (only R1 rides this train).
- KIT-0107/0108 (0.10.0 pair), KIT-0111.
- Kit-side gaps → `1-backlog/`; marketplace-side → the followups-file
  pattern via the planner.

## Process citations

- Review-surface budget per PR; circuit breaker per PR; evaluator
  before each PR opens (PR 1 code+prose → normal tier; PR 2 canon
  prose → fast-only per the prose-sweep exception; PR 3 release →
  fast, KIT-0109 precedent).
- Task completion: planner moves tasks; KIT-0112 completes with PR 2,
  KIT-0103 stays in backlog with R1 checked off.
