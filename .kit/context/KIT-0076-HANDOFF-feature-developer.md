# KIT-0076 Handoff — feature-developer

**Task**: `.kit/tasks/2-todo/KIT-0076-cut-090.md`
**Target Codebase**: This repo — NOT a target repo (single-repo mode)
**Prepared**: 2026-07-28 (planner-f5)
**Estimated effort**: 0.5-1 day

You are the feature-developer. Implement this task directly — do not
delegate to another agent instance.

## ⚠️ LAUNCH

**Your repository root is
`/Users/broadcaster_three/Github/ask-worktrees/KIT-0076/`** — branch
`feature/KIT-0076-cut-090`, real per-worktree venv. Run
`git pull --ff-only` and verify `git rev-parse HEAD` ==
`origin/main` first. Absolute paths / `git -C` throughout. Serena by
absolute worktree path only. NEVER run `project reconfigure` here
(identity-rewrite incident, WORKTREE-WORKFLOW).

## Mission

Close every 0.9.0 deprecation window and cut the release. The three
removal specs (KIT-0047, KIT-0054, KIT-0059 — read IN FULL first)
are the requirements; this task sequences them plus release
mechanics. What ships is the ADR-0027 end state with zero
compatibility scaffolding.

## Verified facts (planner, 2026-07-28; re-verify)

- The three specs live in `.kit/tasks/1-backlog/` (36/82/60 lines).
  KIT-0059's example-manifest checklist item was satisfied early by
  KIT-0073 (its task file says so — verify, don't redo).
- **KIT-0054 scope check**: it predates the KIT-0067 launcher story
  — it covers the DOOR entrance shims (verify its list against the
  live tree; `.kit/launchers/launch` is DELIBERATELY KEPT per the
  2026-07-28 restoration, KIT-0075. If KIT-0054's text mentions
  launchers, that part is superseded — note the delta in the PR,
  don't delete the launcher).
- The legacy-config notice (KIT-0059 set) lives in the door and
  doctor output paths (KIT-0058 shipped it; grep
  `agentive-kit` / `legacy` in `scripts/local/bootstrap` +
  `doctor.d/90-config-home.sh`).
- Manifest/count tests enforce file-list consistency — removals
  change counts; same-commit rule.
- A background dedup analysis is READING the repo right now
  (read-only, writes one report file under .kit/context/reviews/) —
  if an unexpected untracked DEDUP-ANALYSIS file appears, leave it
  alone; it's the planner's.

## Context you must not lose

- **Removal hygiene**: variant-sweep greps per removed surface
  (item 15: token, .bak, path-prefixed, basename); flag any
  operator-invocable surface to the planner BEFORE deleting (launch
  lesson) — the removal sets are deprecation-noticed so surprises
  are unlikely, but check.
- **Deletion-heavy diff**: evaluators reconstruct pre-fix state —
  run **code-reviewer-fast ONLY** for the Gate-5 record (standing
  rule), action nothing unreproduced, and request the planner's
  tree-grounded verification as the merge gate.
- Expect archive-polish/process-artifact bot noise; resolve with
  rationale, don't fix frozen history (KIT-0062 class).
- CHANGELOG by THEME, not per-PR; keep KIT-0069's compare-link
  format. Tag AFTER merge + CI green — note in the review starter,
  don't tag from the session.
- Worktree-mode bookkeeping per WORKTREE-WORKFLOW (branch carries
  the task moves incl. KIT-0047/0054/0059 → 4-in-review; primary
  mirror uncommitted; planner reconciles).

## Test approach

- Local tests green (expect count updates from removals) →
  code-reviewer-fast → PR open.
- The three specs' own guard tests updated per their text.
- `pytest` directly; `./scripts/core/ci-check.sh` before pushing.
- Scratch: mktemp -d; sweep list at the end.

## Out of scope

- `.kit/launchers/` (KIT-0075 owns modernization; launch stays)
- The downstream pass; dedup findings; all other backlog

## PR sizing

Single PR (removals are enumerated + release mechanics; reviewable
lines modest since most is deletion): branch
`feature/KIT-0076-cut-090` (created).
