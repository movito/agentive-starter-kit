# KIT-0067 Review Starter — Factory Front Door + Structural Cleanup

**Task**: `.kit/tasks/4-in-review/KIT-0067-factory-front-door-and-structural-cleanup.md`
**PRs**: [#97](https://github.com/movito/agentive-starter-kit/pull/97) (front door, PR 1/2, base `main`) →
[#98](https://github.com/movito/agentive-starter-kit/pull/98) (retirements D1–D5, PR 2/2, **stacked on #97's branch**)
**Prepared**: 2026-07-28 (feature-developer-f5)

## Merge order (stacked pair)

1. **Merge #97 first** (CI green, CodeRabbit + BugBot clean, 4/4
   threads resolved).
2. GitHub retargets #98 to `main` automatically. **CI runs only
   then** — the test.yml trigger is main-based PRs, so #98 shows
   "no CI runs" while stacked (preflight Gate 1 PENDING is this,
   not a failure). Wait for the retargeted CI before merging.
3. Merge #98. Squash both, per house style.

## What shipped

**PR #97 — the operator flow becomes teachable**
- `docs/STARTING-A-PROJECT.md` (factory model, three creation flows,
  LAUNCH tab-handoff convention, first session) + prominent README link
- `/new-project` command — /setup-preset-style: derives from
  `bootstrap --help` at runtime, routes to project-intake or the door,
  public surfaces only
- Consumer engine seeds a `first-session` KIT-LOCAL region (invoke
  the planner) wherever the kit ships; `--no-kit` skips it and a
  `--no-kit` re-bootstrap removes only an unmodified seed
  (customized = consumer-owned; malformed markers fail loud) — 5 tests

**PR #98 — the five approved decisions executed**
- D1: launchers + onboarding agent deleted (preflight verified NOT a
  thin wrapper → retired too); README/CLAUDE.md reworked;
  create-agent degrades launcher registration to skip-with-notice;
  core scripts 3.9.0 (retired-path remedy replaced, bash-n-pinned)
- D2: four docs archived with banners; fresh minimal
  COVERAGE-WORKFLOW (real 80% gate + real commands); tombstone at the
  EVALUATION-WORKFLOW path; KIT-0069's verdict-vocabulary table
  preserved in the live code-review-evaluator skill
- D3: serena pruned (Desktop-era files deleted, SETUP-GUIDE fixed,
  template regenerated against installed Serena 1.6.1, stale local
  memories deleted from the primary)
- D4: setup-dev dispatch steps behind `--with-dispatch` (default runs
  anywhere; both paths executed live)
- D5: docs/adr/ is consumer-only (kit ADRs → `.kit/adr/`, orphan
  starter → `.kit/context/` with superseded banner)

## Review shortcuts

- A-number dispositions (A18, A33, A41, A44, A45, A50, A61, A62,
  A68, A85–A87, A89, A90 + the launchers-vs-door uncertain finding):
  table in the #98 PR body.
- Evaluator record (3 rounds PR1, 1 round PR2; real fixes vs
  refutations with tree evidence):
  `.kit/context/reviews/KIT-0067-evaluator-review.md`.
- Route transcripts + seed evidence: #97 PR body
  (`/tmp/kit0067-demo/` holds the raw outputs — operator sweep list,
  together with `/tmp/kit0067-smoke-ZOrL/`).
- Bot rounds: #97 CodeRabbit 4 threads (all fixed in one batch,
  resolved); #98 BugBot 1 thread despite "skipping" check status —
  threads-are-the-truth held again (KIT-0062).

## Known follow-ups (not blockers)

- Downstream consumers keep pre-0.9.0 launchers until the 0.9.0
  manifest sync prunes them (the removed `.kit/launchers/` entry
  feeds KIT-0049's deletion pruning); create-agent supports both
  states in the interim.
- `about-kit-adr.md`'s KIT-ADR index table was already stale
  (stops at 0018, pre-existing) — not widened here; a line item for
  the 0.9.0 pass.
