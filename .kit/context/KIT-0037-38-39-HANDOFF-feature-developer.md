# KIT-0037 + KIT-0038 + KIT-0039 Handoff — feature-developer (combined bundle)

**Tasks**:
- `.kit/tasks/2-todo/KIT-0037-wrapper-exit-code-convention.md`
- `.kit/tasks/2-todo/KIT-0038-stacked-pr-retarget-workflow.md`
- `.kit/tasks/2-todo/KIT-0039-staging-scope-self-review.md`

**Target Codebase**: This repo — NOT a target repo (single-repo mode)
**Prepared**: 2026-07-05 (planner-f5)
**Estimated effort**: 3–4 hours combined

You are the feature-developer. Implement all three directly — do not
delegate. One branch, one PR: all three are docs/checklist codification from
the KIT-0036 retro, they touch adjacent surfaces, and none exceeds 2 hours
alone.

## Mission

Turn three KIT-0036 retro lessons into durable guardrails: the wrapper
exit-code convention (3 bot findings traced to it), the stacked-PR
retarget-after-squash-merge recipe (derived live, non-obvious), and the
scoped-staging self-review item (recurred twice within one task).

## Implementation guidance

### KIT-0037 — wrapper exit-code convention

- Add the rule to `.kit/skills/self-review/SKILL.md`: *a wrapper around an
  engine with a frozen exit-code contract must not reuse the engine's
  reserved codes (`0`/`1`) for wrapper-level failures; environment/
  precondition failures → exit `2`.* Cite the engine contract in
  `scripts/core/sync_from_manifest.py`'s module docstring.
- Audit `scripts/core/project` (`cmd_sync`, `_create_branch`): the KIT-0036
  fixes should already return `2` on branch-fail and import-fail. Confirm,
  and annotate those exit points with a one-line comment pointing at the
  convention. No behavior change expected — if you find a wrapper failure
  path returning `0`/`1`, that's a real fix, note it in the PR.

### KIT-0038 — stacked-PR retarget workflow doc

- New `.kit/context/workflows/STACKED-PR-WORKFLOW.md` (sibling of
  PR-SIZE-WORKFLOW.md) — the spec's Overview contains the verified command
  sequence from the live KIT-0036 session; keep those exact commands.
- Must cover: when to stack; squash-merge vs merge-commit reconciliation
  (`git rebase --onto origin/main <PR1-tip> <PR2-branch>` for squash); the
  force-with-lease + `gh pr edit --base main` steps; and the
  base-retarget-doesn't-trigger-CI gotcha (`edited` ≠ `synchronize`) with
  both clean nudges (bundle a real push; or close/reopen).
- Two extra facts from later retros worth one line each: CodeRabbit skips
  PRs whose base isn't the default branch (KIT-0036 retro, Surprising #2),
  and force-push may be permission-blocked in agent sessions — the
  branch-replacement fallback (KIT session retro 2026-07-04).
- Link it from CLAUDE.md's Workflow Reference table (the table gained a row
  for TEMP-THEN-COMMIT-PATTERN.md in KIT-0034 — follow that precedent).

### KIT-0039 — scoped-staging self-review item

- Add the checklist item to `.kit/skills/self-review/SKILL.md` (same file
  as KIT-0037's rule — write both in one pass): programmatic
  `git add` + commit helpers must stage exact changed paths from a
  report/manifest, never `-A` / `.` / whole roots; deletions via
  `git add -- <path>`. Reference implementations:
  `scripts/core/project` `_stage_and_commit` and the scoped-add loop in
  `.github/workflows/sync-core-scripts.yml`.
- The optional `pattern_lint` heuristic (flag `git add -A`/`git add .` in
  helpers that also commit): implement only if it lands cleanly in
  `scripts/core/pattern_lint.py`'s existing rule structure with a test —
  otherwise document the decision not to, in the PR. Don't force it.

## Test approach

- Docs/checklist changes: no new test surface except a `pattern_lint` rule
  (if implemented → add to `tests/test_pattern_lint.py`).
- `./scripts/core/ci-check.sh` before pushing (markdown hooks: trailing
  whitespace, end-of-file).
- Verify the KIT-0037 audit claim (`cmd_sync` exit codes) by reading the
  code, not assuming — cite line numbers in the PR description.

## Evaluation summary

**Skipped by planner policy** — docs-only/checklist/process changes (the
explicit skip category), and every item was already independently validated
by the KIT-0036 bot findings and retro. If the optional pattern_lint rule
turns into real logic, run `adversarial code-reviewer-fast` on the diff at
Phase 7 as usual.

## Out of scope

- Changing `sync_from_manifest.py`'s exit-code contract (it's frozen — the
  convention documents it, nothing more)
- Rewriting PR-SIZE-WORKFLOW.md (link, don't merge)
- KIT-0035 items (next task, same skill file will be touched again — don't
  absorb)
- Downstream repos (operator deferral stands)

## PR sizing

Well under 500 lines combined (two skill checklist items, one workflow doc,
one CLAUDE.md row, code comments, optional small lint rule). Single PR:
`feature/KIT-0037-38-39-workflow-hardening`.
