# KIT-0071 Review Starter — Worktree Provisioning Correctness

**PR**: https://github.com/movito/agentive-starter-kit/pull/96
**Branch**: `feature/KIT-0071-worktree-venv-provisioning`
**Task**: `.kit/tasks/4-in-review/KIT-0071-worktree-venv-provisioning.md`
**Status at handoff**: CI fully green (lint + 3.10/3.12/3.14),
CodeRabbit APPROVED, BugBot pass, **11 review threads across 6 bot
rounds — all replied to and resolved**.

## What shipped (F1–F7)

- **F1**: `new-worktree.sh` provisions a **real per-worktree venv**
  (`project setup --no-hooks`); `.venv` is never symlinked again.
  Route recorded in the PR: every committing session needs the venv
  anyway (pytest-fast hook), so absent-with-instruction just defers
  the same ~1–2 min cost to a forgettable step. Failure is non-fatal
  (paste-safe recovery line printed).
- **`cmd_setup` guard**: refuses on a symlinked `.venv` (incl.
  `--force` and dangling links); `--no-hooks` flag added so worktree
  setup never re-points the shared common-dir hooks.
- **F2/F6**: `doctor.d/55-worktree-provisioning.sh` — WARN on
  symlinked `.venv`/`venv`; in-worktree audit of Serena misdirection
  (missing/unnamed/colliding config, both `name:` keys); enumerates
  shared-by-design state; never nags about permission lists.
- **F3**: WORKTREE-WORKFLOW.md triage entry (venv-failure symptoms,
  `ls -la .venv` first move, settled mktemp/sweep-list policy).
- **F5**: helper pre-generates worktree-local `.serena/project.yml`
  with a per-worktree name; LAUNCH block prints
  activate-by-absolute-path; verified root `.gitignore` covers both
  Serena config files.
- **F7**: valid-key≠usable-key note in `20-env-keys.py`.
- **Core scripts 3.7.0 → 3.8.0** + manifest + engine heredoc + count
  tests in one commit.

## Acceptance evidence (live, in-session)

- **`python3 -m venv --clear .venv` in a fresh worktree**: worktree
  venv cleared (167→2 site-packages entries), primary untouched
  (170→170) — the exact KIT-0065 command is now harmless.
- Own worktree re-provisioned as the demo: doctor WARNed on the live
  symlink → `project setup` refused through it → `rm .venv` + setup
  → real venv (Python 3.14.3) → doctor all-PASS → full suite green
  through the new venv.

## Review trail

- Evaluator trio ran BEFORE PR open:
  `.kit/context/reviews/KIT-0071-evaluator-review.md` — fast
  CONCERNS / deep FAIL / claude-code APPROVED; every finding
  reproduced or refuted (the deep FAIL's headline `venv/ --force`
  destruction claim was refuted with an rmtree reproduction).
- Bot rounds converged on one theme: the pasted remedy string —
  prose removal → root-scoping → shell-comment note → `%q`/shlex
  escaping across all three surfaces (doctor WARN, cmd_setup
  refusal, helper fallback), each shape pinned by tests (incl.
  `bash -n` parsing the actual pasted tail).
- BugBot's check-status oscillated `skipping`/`pass` while it kept
  posting threads — KIT-0062 F6 territory; treat the status as
  unreliable, the threads as real.

## Reviewer focus suggestions

1. The F1 route trade-off (real venv vs absent-with-instruction) —
   recorded in the PR body; disagree there if at all.
2. `55-worktree-provisioning.sh` Serena name parity with the
   `project reconfigure` reader (`name:`/`project_name:`) — kept
   deliberately minimal, not a YAML parser.
3. The `--no-hooks` contract: hooks live in the shared common git
   dir; worktree setup must never reinstall them. Post-merge, fresh
   worktrees get the new script; pre-merge worktrees keep old
   behavior (noted in the evaluator record).

## Planner notes

- Primary-clone task copy moved to 4-in-review in the working tree
  (uncommitted, planner commits at closeout); the branch carries the
  same move, so main is consistent at merge — delete the primary's
  stray untracked copy if both exist after merge.
- This session's worktree (`../ask-worktrees/KIT-0071`) now runs a
  real venv on Python 3.14 — removal at closeout will need `--force`
  only for the untracked venv/Serena artifacts, which regenerate.
- Operator sweep list: `/var/folders/.../T/tmpn_y7fh2o` (rmtree
  refusal reproduction, OS-temp, auto-cleans) — nothing else created
  outside git.
