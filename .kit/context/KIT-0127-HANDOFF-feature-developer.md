# KIT-0127 Handoff — feature-developer

**Task**: `.kit/tasks/3-in-progress/KIT-0127-agentive-workflow-2.3.0-release.md`
**You are the feature-developer. Implement directly.**

## Target Codebase

**`/Users/broadcaster_three/Github/agentive-skills`** (plain clone of
`movito/agentive-skills`) — all commits land there, on branch
`release/agentive-workflow-2.3.0`.

The kit repo (`/Users/broadcaster_three/Github/agentive-starter-kit`,
your CWD) is **read-only** for this session: you run its tooling
(`.venv/bin/python`, `scripts/local/plugin_resync.py`,
`scripts/local/check_plugin_drift.py`) but commit nothing to it.
Planner owns kit-side bookkeeping. The kit primary clone is shared with
planner sessions (KIT-0103 R6 ownership seam) — another reason to
never stage anything there.

## Session topology (verify, never create)

- CWD: `/Users/broadcaster_three/Github/agentive-starter-kit` on `main`
- Write target: `/Users/broadcaster_three/Github/agentive-skills` on
  `release/agentive-workflow-2.3.0` — **already created and pushed by
  planner** from `main` (= `280562c`, the 2.2.0 release). FIRST ACTION:
  `git -C /Users/broadcaster_three/Github/agentive-skills branch --show-current`
  must print `release/agentive-workflow-2.3.0`; if not, check it out —
  never `checkout -b`.
- PRs: `gh --repo movito/agentive-skills …` explicitly, every call.

## Implementation order

1. **Roster surgery first** (`plugins/agentive-workflow/roster.yaml`):
   the resync tool exits 3 while the roster lists o55 as shipped with a
   kit source that no longer exists (verified: see spec §Verified
   current state). Convert the o55 entry (lines 68–76) to the retired
   pattern used by feature-developer-v6/v7 (lines ~187–191): keep
   `name`/`kind`, `ships: false`, `retired: true`, drop
   `source`/`kit_version`/`kit_sha256`/`plugin_sha256`, rewrite `why`.
   Also bump `plugin_version` line 47 — it is STALE at "2.1.1" (spec has
   the evidence); it goes to "2.3.0".
2. **Delete** `plugins/agentive-workflow/agents/feature-developer-o55.md`.
3. **Resync**: from kit root,
   `.venv/bin/python scripts/local/plugin_resync.py --marketplace-root /Users/broadcaster_three/Github/agentive-skills --dry-run`
   → work-list must be exactly feature-developer, feature-developer-f5,
   planner, planner-f5. Then run without `--dry-run`. Three-way merge,
   never plain copy — the script does this; do not hand-copy bodies.
   `git -C … status --short` after the run and verify the changed set.
4. **Version fields** → 2.3.0: marketplace.json (BOTH lines 9 and 16),
   plugin.json, README (line 14; also grep for a component count — 29
   shipped after retirement), roster already done in step 1. Then
   `grep -rn "2\.2\.0\|2\.1\.1" --include="*.json" --include="*.yaml"` to
   prove no field missed — paste that grep in the PR body (KIT-0111
   class has now struck four releases running).
5. **CHANGELOG**: 2.3.0 entry, explicit empty categories (house style —
   see the 2.2.0 entry). Cover: 4 agent pin refreshes (opus-5-5 /
   fable-5-2, kit commit 7f3784c), o55 retirement (membership change ⇒
   minor), roster plugin_version correction 2.1.1→2.3.0.
6. **Commit/PR**: single release commit on the branch, PR to main with
   `gh --repo movito/agentive-skills pr create`. Marketplace-side CI
   (plugin_sha256 guard) must pass. Bot budget: ONE substantive round
   (bot-triage skill; bot truth = reviewThreads GraphQL, statuses lie).
7. **After merge**: dispatch the KIT-side drift guard explicitly on kit
   main and measure it GREEN — it does not re-run on marketplace merge
   (KIT-0113 trap). Then report done with: merged PR URL, guard run URL,
   and the two operator commands
   (`claude plugin marketplace update agentive-skills`,
   `claude plugin update agentive-workflow@agentive-skills`).

## Data shape verification

- Retired-entry shape: read v6/v7 entries in roster.yaml before editing;
  match field order exactly (the resync tool's textual roster editing
  depends on the established field order).
- The 4 refreshed plugin bodies keep plugin-side adaptations via the
  three-way merge (namespacing etc.) — spot-check one diff hunk; a
  wholesale body replacement signals a merge-base problem, stop and
  investigate (base = previously-rostered-hash blob, KIT-0099).

## Test approach

No pytest surface. Verification = `plugin_resync.py --dry-run` clean
after the run (exit 0, empty work-list), marketplace CI green on the PR,
kit drift guard green post-merge, and the no-stale-version grep.

## Review Flags

None declared (spec has no `**Review Flags**:` field) ⇒ default code
review only, per `.kit/context/workflows/REVIEW-PIPELINE.md`.

## Out of scope

Everything in spec §Out of scope. Notably: no kit commits, no KIT-0111
implementation, no consumer-project upgrades, no deletion of the merged
`release/agentive-workflow-2.2.0` local branch.
