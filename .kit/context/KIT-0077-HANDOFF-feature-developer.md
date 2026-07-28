# KIT-0077 Handoff — feature-developer

**Task**: `.kit/tasks/3-in-progress/KIT-0077-dedup-cleanup.md`
**Target Codebase**: This repo — NOT a target repo (single-repo mode)
**Prepared**: 2026-07-28 (planner-f5)
**Estimated effort**: 3-4 hours

You are the feature-developer. Implement this task directly — do not
delegate to another agent instance.

## ⚠️ LAUNCH

**Your repository root is
`/Users/broadcaster_three/Github/ask-worktrees/KIT-0077/`** — branch
`feature/KIT-0077-dedup-cleanup`, real per-worktree venv. Run
`git pull --ff-only` and verify `git rev-parse HEAD` ==
`origin/main` first (post-v0.9.0 main). Serena by absolute worktree
path only. NEVER run `project reconfigure` here.

## Mission

Execute the operator-approved dedup dispositions
(`.kit/context/reviews/DEDUP-ANALYSIS-2026-07-28.md` — the binding
source; the spec's F-items organize it). This is the pre-split
hygiene pass: after it, `.kit/context/` is legible, dispatch is
retired, and the analysis's operator questions are all closed in
the tree.

## Verified facts (planner; re-verify — the tree moved since the analysis)

- **F1 recompute is mandatory**: the analysis counted 74 done-task
  files at `1dc3f0c`; since then KIT-0076/0047/0054/0059 completed —
  their handoffs/starters NOW QUALIFY. Recompute the list from
  scratch: for every `.kit/context/` flat file whose TASK-ID is in
  5-done/6-canceled/7-blocked, `git mv` to `.kit/context/archive/`.
  Live coordination stays: `agent-handoffs.json`, `patterns.yml`,
  `current-state.json` (if present), `REVIEW-INSIGHTS.md`,
  `workflows/`, `retros/`, `reviews/`, and any file for a task NOT
  in a terminal folder.
- **agent-handoffs.json**: `details_link`/`handoff_file` fields for
  DONE tasks may point at old paths post-move — update them (it's a
  live file; the metadata sync rewrites it on future moves anyway).
- **F2 dispatch retirement (operator-confirmed dead)**:
  `.dispatch/config.yml` → `docs/archive/` (rename meaningfully,
  e.g. `dispatch-config.yml.archived`); `scripts/optional/setup-dev.sh`
  loses the `--with-dispatch` gate + steps (KIT-0067 D4 built the
  gate; retirement supersedes — read the script first); sweep live
  mentions of dispatch-as-current-feature (agents, docs, README
  pointers). KEEP: patterns.yml `origin: dispatch-kit` provenance
  headers, skills' origin frontmatter, historical records. Check
  `.gitignore` dispatch entries and `pyproject` `local` extra
  (`dispatch-kit>=0.4.0`) — retire those lines too, with the
  variant sweep.
- **F3 doc archival**: `.kit/docs/UPGRADE-0.4.0.md` and
  `.serena/claude-code/USE-CASES.md` → `docs/archive/`. Citers to
  repoint: test-runner.md / powertest-runner.md reference USE-CASES
  (drop or repoint the lines); engine copy-lists include
  `.serena/` wholesale — verify whether the move changes what ships
  (it moves INTO docs/, which also ships — net fine, but confirm
  no exclusion needed).
- **F4 template pair**: `.kit/context/templates/
  review-starter-template.md` vs `review-template.md` — grep the
  review-handoff skill + both fd agents for which is actually
  cited; merge or archive the loser, repoint citers.
- **F5 annotations**: builder-only note in the three commands'
  frontmatter or body (`new-project`, `setup-preset`, `wrap-up`):
  one line — "builder-side command: operates the kit factory; not
  distributed via the manifest (intended)". OPERATIONAL-RULES: no
  action.
- Manifest/count tests: F2/F3 may change membership
  (.serena USE-CASES is in a shipped path?) — same-commit rule if
  counts move; core VERSION bump only if scripts/core changes
  (setup-dev is scripts/optional — check which tier carries it).

## Context you must not lose

- **evidence_files_append_only**: the dedup report, audit records,
  retros — read, never edit, even where they cite paths you move.
- **Mostly-moves diff**: fast-only evaluator for the Gate-5 record;
  NEVER action unreproduced findings; request the planner's
  tree-grounded verification as the merge gate. Expect bot noise on
  archived files — resolve with the frozen-history rationale.
- Variant sweeps (item 15) for every moved/retired token
  (`dispatch`, `USE-CASES`, `UPGRADE-0.4.0`, template names) — and
  every representation (tables/diagrams).
- Worktree-mode bookkeeping per WORKTREE-WORKFLOW (branch carries
  the task move + starter; primary mirror uncommitted; planner
  reconciles). NOTE the irony guard: your own task's handoff file
  (this file) must NOT be archived — KIT-0077 isn't done.

## Test approach

- Link-integrity grep after all moves (no live citer of an old
  path); `pytest` (doc-existence tests may pin paths you touch —
  find them first); `./scripts/core/ci-check.sh` before pushing.
- Scratch: mktemp -d; sweep list at the end.

## Out of scope

- Split-repo restructuring (future ADR); KIT-0061/0075 and other
  backlog; any door/engine logic beyond the setup-dev gate removal.

## PR sizing

One PR (moves dominate). If reviewable non-move lines exceed ~300,
split archive-moves from the dispatch/doc/template edits per the
PR-SIZE archival rules.
