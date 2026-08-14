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
