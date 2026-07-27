# KIT-0071 Handoff — feature-developer

**Task**: `.kit/tasks/5-done/KIT-0071-worktree-venv-provisioning.md`
**Target Codebase**: This repo — NOT a target repo (single-repo mode)
**Prepared**: 2026-07-27 (planner-f5)
**Estimated effort**: 3-4 hours (widened scope: F1-F7)

You are the feature-developer. Implement this task directly — do not
delegate to another agent instance.

## ⚠️ LAUNCH

**Your repository root is
`/Users/broadcaster_three/Github/ask-worktrees/KIT-0071/`** — branch
`feature/KIT-0071-worktree-venv-provisioning`, provisioned by the
CURRENT (buggy) helper. Run `git pull --ff-only` first. Absolute
paths / `git -C` throughout.

**⚠️ THE HAZARD YOU ARE FIXING IS LIVE IN YOUR OWN WORKTREE**: your
`.venv` is a symlink to the primary clone's venv. NEVER `--clear`,
rebuild, or delete it (KIT-0065: that emptied the primary). `pytest`
through it is fine. Once your F1 fix lands you may re-provision your
own worktree venv per your new design — doing so IS the demo.

**Serena**: if you use it, `activate_project` with the ABSOLUTE
worktree path, never the project name (name resolves to the primary
clone — bulk edits would hit main's checkout; KIT-0069 caught this
pre-use).

## Mission

Kill the worktree-provisioning hazard class: no more shared-mutable
state behind symlinks (F1 `.venv`), doctor visibility for what a
worktree shares/misdirects (F2/F6), the WORKTREE-WORKFLOW triage
entry with the settled sweep-list policy (F3), Serena-by-path
codified (F5), and the valid-key≠usable-key doctor note (F7). The
spec's F-items carry the decisions; the rm-rf deny is SETTLED
POLICY (`5497bf6`) — nothing you build may nag about an allowlist.

## Verified facts (planner; re-verify anchors)

- `scripts/local/new-worktree.sh` — the `PROVISION_LINKS` loop
  symlinks `.venv`, `.env`, `.adversarial/evaluators` (existence
  guard added in KIT-0068 at the loop head). F1 changes `.venv`
  handling only; `.env` + evaluators stay symlinked (read-only use).
- `scripts/core/doctor.d/` — check files follow the DOCTOR: 4-field
  contract with `# shapes:` headers; `90-config-home.sh` is the
  freshest exemplar; `80-bot-presence.sh` carries the quota-note
  pattern F7 copies; `20-env-keys.py` is presence-only today.
- `.kit/context/workflows/WORKTREE-WORKFLOW.md` — frictions section
  holds the KIT-0043/0044 entries F3 joins.
- Incident evidence: `.kit/context/retros/KIT-0065-retro.md`
  (Surprising #1/#2), `.kit/context/retros/KIT-0069-retro.md`
  (Incident Closure #2/#3), KIT-0069-IMPLEMENTATION-NOTES §2/§3.

## Context you must not lose

- **F1 route choice is yours, recorded**: real per-worktree venv at
  provisioning vs absent-with-LAUNCH-instruction. Consider provision
  time (a real venv costs ~a minute; the LAUNCH-line route costs the
  session a setup step). Either way: `venv --clear` in a fresh
  worktree must be provably unable to touch the primary (transcript
  — that's an acceptance criterion).
- **Self-review items 15/16 apply** — including the new clauses:
  execute any command you recommend (F3's triage text, LAUNCH
  lines), verify every claim on lines you edit.
- **Two-homes rule**: if the LAUNCH block and WORKTREE-WORKFLOW.md
  both describe the provisioning contract, prefer one source quoting
  the other, or pin them with a test.
- Core scripts touched (doctor.d) → VERSION bump 3.7.0→3.8.0 +
  manifests + `test_core_manifest.py` in the same commit.
- This diff is code+doc mixed — the normal trio ordering applies
  (NOT the prose-sweep exception).

## Test approach

- Ordering rule: local tests green → evaluator trio
  (`echo y | ADVERSARIAL_UNATTENDED=1 …`; log-file-with-verdict is
  the proof; `git status` after every run) → PR open.
- Doctor check: fixture tests (symlinked `.venv` → WARN; real/absent
  → silent), plus the live demo on your own worktree.
- Scratch dirs: `mktemp -d`, list leftovers for operator sweep
  (settled policy — no rm -rf).
- `pytest` directly; `./scripts/core/ci-check.sh` before pushing.

## Out of scope

- rm-rf permission changes (settled); Serena config beyond the
  path-activation codification; KIT-0067's launcher retirement
  (don't touch `.kit/launchers/`); 0.9.0 removals.

## PR sizing

Single PR (~200-300 lines: helper change + doctor check + docs +
tests): branch `feature/KIT-0071-worktree-venv-provisioning`
(created).
