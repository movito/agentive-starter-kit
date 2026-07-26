# KIT-0071: Worktree venv provisioning — kill the symlink destruction vector

**Status**: Todo
**Priority**: high
**Assigned To**: unassigned
**Estimated Effort**: 2-3 hours
**Created**: 2026-07-27
**Linear ID**: (automatically backfilled after first sync)

## Related Tasks

**Parent**: KIT-0065 incident (retro Surprising #1/#2, Incident
Closure #1/#2 — `.kit/context/retros/KIT-0065-retro.md`)
**Related**: KIT-0044 (worktree sessions; the stale-venv split-brain
this compounds), KIT-0068 (the ln-s-into-existing-dir guard —
adjacent vector in the same helper)

## Overview

`scripts/local/new-worktree.sh` symlinks `.venv` from the primary
clone into every new worktree. KIT-0065 proved the design is a
destruction vector: an in-worktree `python3 -m venv --clear` followed
the symlink and EMPTIED THE PRIMARY'S VENV (repaired in-session). The
denial chain that steered there (`rm -rf` denied → `rmtree`
sandbox-blocked → `--clear` as the "safe" workaround) was locally
reasonable at every step — the hazard lives in the provisioning
convention, not the tools. A shared mutable venv behind a symlink is
also the KIT-0044 stale-venv split-brain in permanent form.

## Requirements

- **F1 — stop symlinking `.venv`** in `new-worktree.sh`. Choose at
  implementation, recording the trade-off: (a) provision a real
  per-worktree venv (slower creation, full isolation — preferred if
  `project setup` can be invoked non-interactively for it), or
  (b) leave `.venv` absent with a LAUNCH-block line telling the
  session to run `./scripts/core/project setup` first. Either way,
  `.env` / `.adversarial/evaluators` symlinks stay (read-only use;
  evaluators guarded since KIT-0068).
- **F2 — doctor check** (`scripts/core/doctor.d/`): WARN when
  `.venv` is a symlink — name both risks (split-brain per KIT-0044,
  destruction via `--clear`/rebuild per KIT-0065) and the fix
  (replace with a real venv). Cite KIT-0065 in the header per the
  incident-closure rule.
- **F3 — WORKTREE-WORKFLOW.md triage entry**: symptom "Unable to
  create directory .venv / Errno None on rmtree" → check
  `ls -la .venv` for a symlink + the rm-rf allowlist gap; alongside
  the KIT-0043/0044 friction entries.
- **F4 — existing worktrees**: `new-worktree.sh` fix applies to NEW
  worktrees; the doctor check (F2) is what catches existing ones.
  Nothing else needed.

## Acceptance Criteria

- [ ] Fresh worktree has no `.venv` symlink (test or transcript);
      chosen F1 route + trade-off recorded in the PR
- [ ] Doctor WARNs on a symlinked `.venv` (fixture test), silent on
      real venv / absent venv
- [ ] Triage entry present
- [ ] `venv --clear` inside a fresh worktree provably cannot touch
      the primary (transcript)

## Notes

- Evaluation skipped (planner): single-vector fix, decisions
  in-spec, evidence adversarially lived rather than reviewed.
- Interim mitigation until this lands: KIT-0069's handoff warns the
  session never to rebuild `.venv` through the symlink.
