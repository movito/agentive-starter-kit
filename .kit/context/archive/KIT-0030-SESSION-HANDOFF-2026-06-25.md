# KIT-0030 Session Handoff — 2026-06-25

**Supersedes**: `KIT-0030-SESSION-HANDOFF-2026-06-18.md` (stale on plugin merge,
marketplace, label-maker, ADR-0025).
**Task**: `.kit/tasks/3-in-progress/KIT-0030-plugin-consolidation.md` — still in
progress.

## RESUME HERE (in order)

1. **Slim KIT-ADR-0025** (`.kit/adr/KIT-ADR-0025-agent-localization-vs-plugin-upgrades.md`)
   to the "upgrader agent + guide" form. It currently carries a heavy
   schema/render/three-way-handshake design (Status Proposed). The user's reframe:
   it's **only their own projects**, so that machinery is unnecessary. Keep the
   light "local vs upstream, preserve local" idea as agent guidance; drop the
   JSON-schema/render/validate-context pipeline. The three-evaluator review is
   committed at `.kit/context/reviews/KIT-ADR-0025-*.md` (all REVISION_SUGGESTED,
   convergent — schema/boundary/enforcement/escape-hatch). Re-read before editing.

2. **Build the `upgrader` agent** from `docs/PLUGIN-UPGRADE-GUIDE.md` (committed
   `72fd14a`). The guide IS the spec. Agent reconciles four axes: plugin pin
   (`/plugin update` + Provenance), core scripts (existing manifest sync /
   `check-sync.sh`), `model:` pins on local agents (model-rollout trigger),
   Provenance restamp. Deterministic tools for mechanical axes; LLM judgment only
   for (a) which local adaptations to preserve, (b) model-pin rewrites. Scope =
   ongoing upgrades ONLY — initial plugin migration stays manual (user decision).
   Likely lives in `.claude/agents/upgrader.md` (kit), distributed later.

3. **Finish migrations**: suwinex-planning, then moss-skolemusikkorps. Pattern =
   label-maker (commit `8c8620a` in label-maker-planning). moss is a monorepo,
   pre-`.kit/` layout (`delegation/`, `.agent-context/`) — plugin migration only,
   NO layout migration; its path-coupled skills stay as local overrides (only
   `self-review` is path-free). Agent dedup: user chose "delete all 3 (code-reviewer,
   ci-checker, feature-developer-v6), use plugin versions" for label-maker.
   **User pushes** all non-kit repos.

4. **Push** the unpushed kit `main` commits (`72fd14a`, `12f8eaa`) when ready.

## Done (this + prior sessions)

- Spike (plugins ship agents+commands, namespaced) → `KIT-0030-SPIKE-FINDINGS.md`
- Inventory → `KIT-0030-INVENTORY.md`
- Kit → canonical cross-repo generation; **released 0.7.0**, PR #53 MERGED
  (`7d8254769`); scripts 2.1.0; `check_cross_repo_config.py` = ci-check step 6.
- Plugin **v1.1.0 MERGED** (PR #3 `e7261bd3e`): 12 commands + 4 agents + 5 skills;
  code-reviewer/ci-checker genericized for distribution (`7bf230a`).
- Marketplace LIVE from GitHub; v1.1.0 verified end-to-end (21 components).
- **label-maker migrated** (`8c8620a`, pushed) — end-to-end gate still UNRUN.
- KIT-ADR-0025 + `docs/PLUGIN-UPGRADE-GUIDE.md` + review trail committed (`72fd14a`);
  retro (`12f8eaa`).

## Reusable migration tooling

`/tmp/namespace_transform.py` (recreate — /tmp is wiped between sessions):
rewrites flat `/command` and slash-skill refs → `agentive-workflow:<name>`,
leaving script paths and `adversarial` evaluator names flat. Source pattern in
label-maker commit `8c8620a`. Watch for double-namespacing when an Edit
pre-namespaces a line before a `replace_all`.

## Operating constraints (unchanged)

- User pushes the 4 non-kit repos (`! git -C <path> push`); agent pushes kit
  directly. Agent cannot edit its own `settings.json`; resolving review threads
  needs per-request user OK; marketplace must be github-sourced.
- Pre-commit hook reformats then aborts → re-stage + fresh commit, never `--amend`.
- `.kit/adversarial/` is user-owned — never stage/delete.
- Deferred cross-repo review findings tracked in issue #54.
