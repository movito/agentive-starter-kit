# KIT-0102 — Review Starter

**PR**: https://github.com/movito/agentive-starter-kit/pull/127
**Branch**: `feature/KIT-0102-retire-sync-machinery`
**Task**: ADR-0028 phase 4 — retire the copy-sync machinery
**Net**: −3,800 lines (deletion-shaped)

## What landed

The copy era's last machinery: push Action, pull engine, manifest, the
`project sync` subcommand, the `60-push-sync-token.sh` doctor check
(both homes) and their tests. Plus the two record edits (KIT-ADR-0026 →
Superseded, KIT-ADR-0028 step 4 → DONE) and the live-docs sweep.

## What a reviewer should check first

The three places where enumeration **overruled the spec** — these are
the judgment calls, and they are the ones worth a second opinion:

1. **`40-version-skew.py` PRESERVED** (spec said delete). Its name says
   "version skew"; its functions are venv-vs-system `adversarial-workflow`
   (KIT-0044) and black-vs-pyproject-pin (KIT-0032). No manifest
   involvement. Evidence: `project doctor` emits `venv-skew-adversarial`
   and `black-pin` lines, both still firing.
2. **`scripts/core/VERSION` PRESERVED** (spec said "dies with the
   manifest if that is its only function"). It has a second reader —
   `project version` — pinned by `test_project_script.py`.
3. **Scope grew beyond the inventory**: `tests/test_project_sync.py`
   (709 lines), the packaged doctor-check mirror, and the setup-door
   coupling. The door change was operator-approved mid-task.

## Deliberate omissions (please sanity-check these calls)

- **`.claude/**` untouched.** Roster-shipped; the drift guard pins each
  component's sha256 to the published plugin release, so editing turns
  it red until a release ships. Six files still carry stale sync
  mentions (`feature-developer.md:65`, `feature-developer-f5.md:70`,
  `self-review/SKILL.md:99/101`, `upgrader.md:56/514`, three command
  headers). **This is the main follow-up.**
- **Stale `project` in old consumers.** The door never overwrites a
  consumer-owned file, so a pre-KIT-0102 consumer that re-bootstraps
  keeps `cmd_sync` and sees `❌ Sync engine unavailable` instead of the
  retirement message. Deferred by operator decision — fixing it means
  changing the door's never-overwrite invariant. **Second follow-up.**
- Historical records (retros, other ADRs, archived/canceled tasks,
  `docs/archive/`, CHANGELOG) keep their sync mentions by design.

## Verification already done

- Full suite **1089 passed / 13 skipped / 0 failed**; scaffold
  acceptance 26; drift guard 17 + live run "in sync: 27 shipped
  components".
- `project doctor`: 13 pass / 1 warn (pre-existing `TASK_PREFIX`) / 0 fail.
- **F2 both-directions check clean**: one live manifest-carrying consumer
  (`varv-planning` 2.1.0 vs canon 4.0.0), 47 both-sides slots diffed,
  **0 consumer-newer**. Full method in
  `.kit/context/reviews/KIT-0102-enumeration.md`.
- Evaluator gate ran **before** PR open (fast tier, `--format diff`;
  deep tier skipped with reason recorded). 2 findings fixed, 1
  acknowledged — `.kit/context/reviews/KIT-0102-evaluator-review.md`.
- Bot round: CodeRabbit CHANGES_REQUESTED → **10 threads, all resolved**
  (8 fixed, 1 auto-resolved, 1 deferred with rationale).
- New tests **falsified**, not just green: the retirement tests fail on
  `Unknown command: sync`; the parametrized sweep test fails *only* the
  `[planning]` param when the planning sweep is deleted.

## Follow-ups for the planner

1. Release-train cleanup of the six rostered `.claude/` files carrying
   stale sync references.
2. Decide the stale-`project` question: force-refresh on re-bootstrap
   (policy change) vs. detect-and-warn (invariant-preserving).
3. KIT-ADR-0029's trigger fires once this merges.
