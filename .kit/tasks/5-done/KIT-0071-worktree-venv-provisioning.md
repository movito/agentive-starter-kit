# KIT-0071: Worktree provisioning correctness — shared, copied, or misdirected state

> **Scope widened 2026-07-27** (planner, from KIT-0069's
> implementation notes §2-3): the `.venv` symlink is one instance of
> a CLASS — worktree provisioning that shares or misdirects state
> with the primary clone. KIT-0069 hit four instances in one session.

**Status**: Done
**Priority**: high
**Assigned To**: feature-developer-f5
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
- **F5 — Serena per-worktree (widened scope)**: Serena's project
  root follows the REGISTERED project, not cwd —
  `activate_project("agentive-starter-kit")` in a worktree session
  resolves to the primary clone, so `replace_in_files` would bulk-
  edit main's checkout (KIT-0069 caught this pre-use). Codify the
  working fix: worktree sessions activate by ABSOLUTE PATH
  (registers a separate project; `.serena/` in a worktree is a real
  dir). `new-worktree.sh` prints this in its LAUNCH block, and
  WORKTREE-WORKFLOW.md documents it; ensure `.serena/.gitignore`
  covers `project.local.yml` (KIT-0069 added the line — verify it
  ships). Consider having `new-worktree.sh` pre-generate the
  worktree's `.serena/project.yml` from the template with a
  per-worktree name so activation is one obvious step.
- **F6 — doctor check enumerates the class (widened scope)**: F2's
  check grows to a worktree-provisioning audit when run inside a
  worktree: `.venv` symlink (WARN, destruction vector), Serena root
  resolving outside the worktree (WARN if detectable), and INFO
  naming what IS shared by design (`.env`,
  `.adversarial/evaluators` — read-only use). The fourth instance
  (rm -rf) is SETTLED POLICY, not a gap: the operator decided
  2026-07-27 to KEEP the kit's tracked `Bash(rm -rf*)` deny (it
  overrides any allow, by design). Agents use `mktemp -d` for
  scratch and list leftovers for operator sweep — codify that line
  in F3's triage entry; the check must NOT nag about an allowlist.
- **F7 — doctor note: valid key ≠ usable key (KIT-0069 incident
  closure #3)**: `claude-code` evaluator failed at runtime with a
  VALID Anthropic key — zero credit balance. `doctor.d/20-env-keys.py`
  checks presence only; balance has no cheap API. Add the
  can't-check-this note naming the symptom ("valid key, evaluator
  writes no log → check credit balance") — copy the shape of the
  CodeRabbit-quota note in `80-bot-presence.sh`. Rides this task
  because it's a one-note doctor.d change alongside F2/F6's doctor
  work; not worktree-specific, say so in the note.

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
