# KIT-0105 — Review Starter (PR 1 of 3)

**Date**: 2026-08-14
**From**: feature-developer-f5
**PR**: https://github.com/movito/agentive-starter-kit/pull/133
**Branch**: `feature/KIT-0105-intake-into-plugin` (worktree
`../ask-worktrees/KIT-0105`)
**Task**: `.kit/tasks/3-in-progress/KIT-0105-project-intake-into-the-plugin.md`
**Status**: CI green, CodeRabbit APPROVED on head `da9d95d`, BugBot
clean, 2/2 threads resolved — ready for human review

## What this PR is

PR 1 of the three-PR train: `project-intake` becomes location-agnostic
(KIT-ADR-0031). F2 (CLI verify-or-instruct + CWD-as-candidate +
packaged-door composition + inlined kit-tree references), F3 (escape
hatch → report-to-operator body), F4 (main-branch guard carried
through, pinned by `TestIntakeAgentContract`), F5 (prose sweep by
class, end-grep proven, both packaged twins mirrored), F6
(`TestIntakeAcceptance` — the intake's mechanical spine in CI with the
seeded-path existence assertion; KIT-ADR-0034's enforcement mechanism).

## Commits

| SHA | What |
|-----|------|
| `49045fc` | The rewrite: F2–F6 across agent, docs, templates (+twins), tests, CHANGELOG |
| `bbe98d7` | Evaluator-driven test polish + Gate 5 review record |
| `da9d95d` | CodeRabbit round 1: quote user-derived paths in command blocks (by class) |

## Bot rounds

One substantive round (2 threads, both CodeRabbit):

1. **Quote the planning-repo path in the `agentive new` block** —
   FIXED in `da9d95d`, swept by class (Step 4c `git -C` block and
   `gh repo create --source` had the same defect).
2. **Add an installed-console-script smoke test** — DECLINED with
   reasoning: the suite deliberately pins the in-repo package source;
   the `[project.scripts]` entry point is smoke-tested where the wheel
   exists (`publish-agentive-kit.yml`: build → install → `agentive
   version`).

## Evaluator record

`.kit/context/reviews/KIT-0105-evaluator-review.md` — trio run pre-PR
(normal tier). claude-code APPROVED (4 cheap fixes applied);
code-reviewer-fast FAIL and code-reviewer CONCERNS fully dispositioned
— dominated by pre-existing helpers surfaced by the full-format input
(the known KIT-0092 artifact) and two refuted claims.

## Points a human reviewer should weigh

1. **The agent-body rewrite is the product** — the intake's contract
   changed from "run in a kit checkout" to "run anywhere, naturally in
   the prototype folder". Read Steps 0 and 3 for coherence.
2. **Drift guard passed on this PR** — `ships: false` files don't
   count toward drift, so there is NO expected-red window until PR 3
   flips the roster. No justification line was needed at merge.
3. **`TestIntakeAcceptance` scope** — it exercises the mechanical
   spine (git init on main, door run, seeding); the LLM prose work is
   deliberately out of scope (commented in the fixture).
4. Agent `version:` bumped 1.1.0 → 1.2.0; `/new-project` 1.3.0 →
   1.4.0; template 1.0.0 → 1.1.0 (twins mirrored, sync guard green).

## After merge

- PR 2 (canon bundle: KIT-0103 R1 + KIT-0112) needs a **fresh branch
  off updated main from the planner** — the implementer will not
  create branches.
- PR 3 (marketplace release 2.1.0) rides
  `release/agentive-workflow-2.1.0` in
  `/Users/broadcaster_three/Github/agentive-skills` (planner-created,
  verified present).

---

# PR 2 of 3 — canon bundle (2026-08-15)

**PR**: https://github.com/movito/agentive-starter-kit/pull/134
**Branch**: `feature/KIT-0105-pr2-canon-bundle` (head `2bf3c2b`)
**Status**: CodeRabbit APPROVED on head, BugBot clean after fix, 5/5
threads resolved, all CI green EXCEPT the drift guard — the
**expected-red window** (justified in the PR body per the
plugin-drift.yml posture ruling; PR 3 greens it)

## Commits

| SHA | What |
|-----|------|
| `8f9e5c5` | The bundle: KIT-0112 complete + KIT-0103 R1, 8 version bumps |
| `9b5eaf2` | PR 2 evaluator record (fast-only, dispositioned) |
| `5d5b90a` | BugBot round: interpolate the REAL endCursor into the refusal |
| `2bf3c2b` | CodeRabbit round: /wrap-up ships via the plugin — over-claim fixed |

## Bot rounds (2 substantive)

1. **BugBot** (check read `skipping` while reviewing — SIXTH face,
   sighted live on the very PR that documents faces): refusal printed
   a literal `<endCursor>` placeholder → FIXED `5d5b90a`, re-falsified
   (real cursor + exit 1).
2. **CodeRabbit** (check read `pass` over CHANGES_REQUESTED — FOURTH
   face): (a) wrap-up "not distributed" over-claim → FIXED `2bf3c2b`
   (roster says `ships: true`; only new-project/setup-preset are
   `ships: false`, their wording kept); (b) extend fail-closed
   pagination to `review_input.py` / `check-bots.sh` / `preflight.py`
   → DECLINED here (canon-only bundle; single-theme rule) with a
   tracked home — **planner: please widen KIT-0103 R3 to cover
   pagination fail-closed in those three code consumers** (verified
   all three use `first: 100` bare; `preflight.py:679` soft-flags
   `total == 100` but still PASSes). Thread cites this.

## For the tree-grounded verification (the real gate — prose sweep)

- KIT-0112: the ONE `first: N` site in `.claude/` is `retro.md:97`,
  now with `pageInfo` + jq `error(…)` refusal; both arms falsified
  live TWICE (initial + after cursor interpolation).
- KIT-0103 R1 end grep (`core-manifest|copy-sync|project sync[^-a-z]|sync --dry-run`
  over `.claude/`): remaining hits are the upgrader's own retirement
  notice and bot-triage's historical lesson — statements ABOUT the
  retirement. Verified NOT stale and kept: `project sync-status` /
  `linearsync` (live Linear commands), the four agents'
  MANIFEST-UPGRADE-GUIDE model-pin refs (section live in the stub).
- Version bumps: retro 1.5.0, bot-triage 1.2.0, upgrader 1.5.1,
  wrap-up **2.3.3** (two bumps this PR), setup-preset 1.3.1,
  new-project 1.4.1, feature-developer 2.6.1, feature-developer-f5
  1.6.1. PR 3's resync must pick up wrap-up at 2.3.3.

## Preflight

Gate 1 FAIL = drift guard only (Tests: pass) — expected-red. Gates
2–7 PASS (2/3 report ".md-only, review not required"; stronger
evidence verified manually: both bots reviewed and approved/cleared
on head).
