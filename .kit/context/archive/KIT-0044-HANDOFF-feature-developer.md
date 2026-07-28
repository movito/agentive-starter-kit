# KIT-0044 Handoff — feature-developer

**Task**: `.kit/tasks/5-done/KIT-0044-worktree-based-implementation-sessions.md`
**Target Codebase**: This repo — NOT a target repo (single-repo mode)
**Prepared**: 2026-07-14 (planner-f5)
**Estimated effort**: 3–4 hours

You are the feature-developer. Implement this task directly — do not
delegate to another agent instance.

## ⚠️ LAUNCH — second worktree pilot

**Your repository root is
`/Users/broadcaster_three/Github/ask-worktrees/KIT-0044/`** — created from
fresh `origin/main` (7ef104d), branch
`feature/KIT-0044-worktree-sessions`, with `.venv`, `.env`, AND
`.adversarial/evaluators/` symlinked (all three — the pilot's friction #3
is pre-fixed this time). Do not operate on the primary clone.

You are codifying the recipe that created your own workspace — the task
is self-demonstrating. Your retro's acceptance criterion: confirm each of
the six pilot frictions is addressed, or re-file what isn't.

## Mission

Turn the KIT-0043 worktree pilot into the kit's default implementation
topology: a creation helper, an un-skippable launch instruction, a
lifecycle, a workflow doc, and a recorded bare-hub decision. All six
requirements trace to verified frictions in
`.kit/context/retros/KIT-0043-retro.md`.

## Context you must not lose

- **The GIT_DIR incident is the heart of F4's doc**: pre-commit exports
  an absolute `GIT_DIR` in worktrees; during the pilot a leaked
  subprocess flipped `core.bare=true` on the primary clone (state
  corruption, not just test failure — second occurrence of the KIT-0036
  class). The suite-wide fix is already in `tests/conftest.py`
  (`7ef104d`) — **do not re-implement it**; document the contract and the
  canary (`git -C <primary> config core.bare` must stay `false` after
  any pre-commit run in a worktree). Run the canary after your own first
  commit — the exact leak vector was never conclusively pinned.
- **The evaluator's two accepted findings are in the spec**: the
  provisioning list must be explicit and enumerated in the helper (never
  an "everything gitignored" glob), and the F5 bare-hub decision carries
  a revisit trigger (Claude Code scoping change / ADV-0053 / second
  operator).
- The task spec's Evaluation section has the full disposition; the six
  frictions each cite their repro in the retro.

## Implementation guidance

- **F1 helper**: `scripts/local/` placement unless you argue core in the
  PR (N3 — scripts/local is not synced to consumers; a `project
  worktree` subcommand WOULD ship, which is a bigger contract). Remember
  the repo's shell rules if you write bash: no `$()` in agent-facing
  instructions, and the temp-then-commit pattern
  (`TEMP-THEN-COMMIT-PATTERN.md`) if the helper mutates multiple things.
  The recipe to encode is exactly what built your workspace (see LAUNCH
  above + the spec's F1).
- **F2 template**: `.kit/templates/TASK-STARTER-TEMPLATE.md` — a LAUNCH
  block above FIRST ACTIONS. Look at how the KIT-0043/0044 starters
  hand-wrote it; make the template force it.
- **F3/F4 doc**: `WORKTREE-WORKFLOW.md` in `.kit/context/workflows/`,
  linked from CLAUDE.md's Workflow Reference table (see the
  TEMP-THEN-COMMIT row for the precedent). Cover topology, creation,
  GIT_DIR contract + canary, closeout (push from worktree; planner
  completes in primary; planner removes worktree post-retro), lifecycle.
- **F5**: keep it short — the migration costs are already enumerated in
  the spec; your job is the write-up + recorded decision + revisit
  trigger, not new analysis.
- **Self-review note**: if the helper is bash and any new test reads
  `scripts/local/`, the consumer-rsync exclusion rule applies (self-review
  item; `test_kit_markers.py` shows the pattern).

## Test approach

- Scratch-worktree cycle per the spec's Test Plan: create with the
  helper, verify provisioning (`pytest --collect-only` and
  `adversarial --help` inside it), verify refusal on re-run, one full
  commit cycle, canary check, remove.
- `pytest` directly; `./scripts/core/ci-check.sh` before pushing.
- Mixed docs+script task: **doc-dominated ordering applies** — run the
  evaluator trio BEFORE opening the PR (the F3 rule from KIT-0035, now
  standard).

## Evaluation summary

`arch-review-fast`: REVISION_SUGGESTED — two minor findings, both
accepted into the spec (enumerated provisioning list; bare-hub revisit
trigger). Design judged sound. Log:
`.adversarial/logs/KIT-0044-worktree-based-implementation-sessions--arch-review-fast.md`.
No outstanding blockers.

## Out of scope

- Changing `tests/conftest.py` isolation (shipped in 7ef104d)
- Actually migrating to bare-hub (F5 is a decision record only)
- `preflight-check.sh`, KIT-0041, KIT-0045 — separate tracks
- Downstream repos (operator deferral stands)

## PR sizing

Single PR (< 400 lines: helper script + template block + workflow doc +
CLAUDE.md row + decision note): branch
`feature/KIT-0044-worktree-sessions` (already created in the worktree).
