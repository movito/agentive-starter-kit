# Task Assignment: KIT-0116 — Phase 3: Tier-3 deep-review workflow (RESUME)

- **Task File**: `.kit/tasks/4-in-review/KIT-0116-automated-review-pipeline.md`
  (in `4-in-review/` by this arc's convention since the Phase 1 handoff —
  do NOT run `project start`/`move`; the folder is correct for this arc)
- **Handoff File**: `.kit/context/KIT-0116-HANDOFF-feature-developer.md`
  (standing 3-phase handoff — its Phase 3 section, verified anchors, and
  **release-timing ruling** remain authoritative; anchors were verified
  2026-08-24 against `c76dff7` — re-verify before relying)

You are the feature-developer. Implement directly.

## Mission

Phases 1 and 2 merged (#148, #149). Phase 3 was **started and nearly
finished** by the prior fd-f5 session, which ended ~2026-08-25 without
pushing: commit `6d53db2` ("Phase 3 — Tier-3 deep-review workflow +
formal escalation contract", 5 files, +343/−28) sits on
`feature/KIT-0116-deep-review` atop the Phase 2 merge, with a coherent
uncommitted refinement round on top (exactly 4 modified files: empty-diff
guard, toolset note, clean-lens short-circuit in `deep-review.js`; +52
test lines; REVIEW-PIPELINE.md twins ×2). Your goal: adopt or complete
that in-flight work, finish Phase 3 to spec, and land it as PR #150 —
then STOP before any release mechanics.

## Resume protocol (before writing anything)

1. Read `6d53db2` and diff the 4 uncommitted files. Judge the
   refinement on CONTENT, not existence (KIT-0103 R6: existence isn't
   integrity) — keep/finish/discard is your call; record the call in
   the PR description.
2. Re-verify the handoff's anchors that Phase 3 touches (REVIEW-PIPELINE.md
   now EXISTS — Phases 1–2 created it; the handoff's "does not exist"
   anchor is satisfied history, not an instruction).
3. `main` has moved past your branch base (planner bookkeeping only:
   `b91426a`, KIT-0120 spec). Rebase or merge-base as you prefer; no
   conflicts expected.

## Acceptance criteria (Phase 3 slice of the spec — spec FR-12 + ACs are authoritative)

- [ ] Deep-review workflow exists, documented, **opt-in only**
      (spec Must-Have), with the formal escalation contract in
      REVIEW-PIPELINE.md (FR-12) — including the never-self-escalate rule
      and the Tier-3 evidence section (incl. requested-but-could-not-run)
- [ ] Single-authority discipline holds: other surfaces cite
      REVIEW-PIPELINE.md, never restate it
- [ ] Drift greps green across all instruction surfaces; contract tests
      pass (`tests/test_review_pipeline_contracts.py` pins workflow
      existence, opt-in metadata, `meta.name` stability, resume-safety,
      contract wording + evidence section name — contract-string caution:
      changing pinned wording means changing the test deliberately, not
      incidentally)
- [ ] Local suite green + `./scripts/core/ci-check.sh` clean; CI green on
      the PR; bot threads triaged per bot-triage skill
- [ ] CHANGELOG entry present (commit `6d53db2` already carries one —
      verify it still matches the final shape)
- [ ] After merge: **report and ask before any release mechanics** —
      planner ruling holds: kit PRs merge per phase, the plugin/marketplace
      release is cut ONCE at arc end, with the planner deciding which
      riders (KIT-0115 / KIT-0103 R6 / KIT-0117 stripping / KIT-0108,
      KIT-0111) board the train. Twins update by copy on that train only
      (`harden_twins_by_copy_not_rederivation`).

## Out of scope — do not touch

- Release train mechanics, plugin/marketplace version bumps, marketplace
  repo operations (its clone may sit on a stale feature branch — leave it)
- Tier 1/Tier 2 surfaces beyond what FR-12's contract requires you to cite
- Discovered gaps → park in `1-backlog/` and note in the PR

## Time estimate

2–4 h (spec allotted 4–6 h for Phase 3; most of it is already on the
branch — the estimate covers adopt/verify, finish, smoke, PR + one
substantive bot round per budget)

## Recommended agent

`feature-developer-f5` — arc continuity: the committed work is fd-f5
authored; Fable-class sessions have run all prior phases of this arc.

⚠️ **LAUNCH** (pre-existing — created by the prior session; verified
present 2026-09-11):

- Worktree: `/Users/broadcaster_three/Github/ask-worktrees/KIT-0116`
- Branch: `feature/KIT-0116-deep-review` (local only — never pushed)

⚠️ **FIRST ACTIONS** (verification only — never `checkout -b`):

1. `git branch --show-current` → expect `feature/KIT-0116-deep-review`;
   anything else: STOP and ask
2. `git rev-parse --show-toplevel` → expect
   `/Users/broadcaster_three/Github/ask-worktrees/KIT-0116`
3. `git log --oneline -1` → expect `6d53db2 feat(KIT-0116): Phase 3 …`
4. `git status --short` → expect EXACTLY 4 modified files
   (`.claude/workflows/deep-review.js`, REVIEW-PIPELINE.md ×2 twins,
   `tests/test_review_pipeline_contracts.py`); any other dirt: STOP and ask

**🚀 Launch checklist (operator)**:

1. Open a new terminal tab:
   `cd /Users/broadcaster_three/Github/ask-worktrees/KIT-0116`
2. `claude --agent feature-developer-f5`
3. Paste this starter as the FIRST message — a bare agent launch idles
   without one (KIT-0101 F8)
4. `/rename KIT-0116 Phase 3 Deep Review Workflow`
