# KIT-0113 — Review Starter (leg 1)

**PR**: https://github.com/movito/agentive-starter-kit/pull/135
**Branch**: `feature/KIT-0113-intake-hardening` → `main`
**Head**: `675f7ab`
**Task**: `.kit/tasks/4-in-review/KIT-0113-project-intake-hardening.md`
**Review record**: `.kit/context/reviews/KIT-0113-evaluator-review.md`

## What changed

One file — `.claude/agents/project-intake.md` (1.2.0 → 1.3.0) — plus
the review record.

- **R1**: three sites echoed staged content or matched credential
  lines into the transcript. All three now scan quietly
  (`git grep -lIE`, filenames only), and the Step 4c commit is gated
  on the scan **in the shell**, not in prose.
- **R2**: Step 5 gated on the door's doctor tail, captured before
  Step 4's seeding. It now re-runs `agentive doctor` after the seeding
  commit and gates on that, relaying both outputs under distinct
  labels (install truth vs repo-state truth).

## Gate status

| Gate | State |
|------|-------|
| Tests (3.10 / 3.12 / 3.14) | ✅ pass |
| Lint & format | ✅ pass |
| CodeRabbit | ✅ APPROVED on head `675f7ab` (SHA-matched) |
| Cursor BugBot | ✅ clean |
| Review threads | ✅ 7/7 replied + resolved, `hasNextPage` false |
| Evaluators | ✅ 2 tiers pre-PR, findings dispositioned |
| Plugin drift guard | ❌ **red by design** — see below |

## The one open item: drift guard

Red because this PR changes a rostered `.claude/` component while the
published plugin is still 2.1.0. That is the guard working, not
breaking. Per the POSTURE ruling in `.github/workflows/plugin-drift.yml`
(operator, 2026-08-14) the guard stays REQUIRED and the remedy is
cadence: a justification comment is posted on the PR, and **leg 2 cuts
plugin release 2.1.1 immediately after merge**.

**This needs an explicit merge decision** — the check is required, so
merging happens over a known-red guard by the ruling's own provision.

## Leg 2 readiness (blocked on merge)

- Marketplace repo `~/Github/agentive-skills` verified **clean on
  `main`** (it is a plain clone; prior sessions have left it on
  feature branches).
- Plan: `scripts/local/plugin_resync.py` three-way merge (never copy),
  plugin 2.1.0 → 2.1.1 across all four version fields, CHANGELOG with
  explicit empty categories, `verify_plugin_integrity.py` 28/28.
- `project-intake` carries no published adaptation, so a clean merge
  is expected — but the tool says so, not me.

## What a reviewer should look hardest at

1. **The Step 4c shell gate** — it is the piece that changed most
   across bot rounds. `case $?` rather than `if`/`else` is deliberate
   (an else branch would commit on a scan that errored). Verified
   against four paths; table in the review record.
2. **The pattern set is duplicated at two sites** and kept in sync by
   an in-document instruction. A markdown agent body has no DRY
   mechanism. If that trade is unacceptable, it wants a follow-up
   task, not a change here.
3. **Declined evaluator findings** — two security findings asking to
   *narrow* the credential regex were declined on fail-closed grounds.
   Reasoning is recorded; disagreement is legitimate and reversible.

## Notes for the retro

Three bot rounds against a one-round baseline. Each round found a real
defect, and rounds 2–3 landed on code that did not exist until the
previous round's fix — introducing a shell gate to close a leak
created a new surface (unchecked `add -A`) for the next round. Also:
CodeRabbit refuted a "verified" claim of mine that was wrong, and
chasing it exposed a genuine coverage regression in the PEM pattern
(6/8 where the original was 7/8). Worth carrying into patterns.
