# KIT-0065 Handoff — feature-developer

**Task**: `.kit/tasks/4-in-review/KIT-0065-purge-aider-era-evaluator-scripts.md`
**Target Codebase**: This repo — NOT a target repo (single-repo mode)
**Prepared**: 2026-07-25 (planner-f5)
**Estimated effort**: 3-4 hours

You are the feature-developer. Implement this task directly — do not
delegate to another agent instance.

## ⚠️ LAUNCH

**Your repository root is
`/Users/broadcaster_three/Github/ask-worktrees/KIT-0065/`** — branch
`feature/KIT-0065-purge-aider-era-evaluator-scripts`, fully
provisioned. Run `git pull --ff-only` first. Absolute paths /
`git -C` throughout.

## Mission

Erase every operational trace of aider (retired; floor
`adversarial-workflow>=1.0.1` enforces it): delete the four dead
`.adversarial/scripts/*.sh`, fix the live surfaces that reference
them or aider behavior, and RE-DERIVE the Python `<3.13` ceiling
that aider alone justified. Closure = a final `grep -ri aider` whose
only hits are historical records + the pyproject floor comment
(paste it in the PR body).

## The one behavioral item: the `<3.13` bound (F6/A03)

`requires-python = ">=3.10,<3.13"` has no surviving rationale.
Empirically determine whether the CURRENT dev stack works on 3.13+:
the operator's system python3 is 3.14 — a venv on it running the
full suite + one evaluator trio invocation is the experiment. If it
passes: lift the bound (pyproject + the three setup messages at
`scripts/core/project` cmd_setup — line numbers shifted in PR #93,
re-locate by grep 'aider' — + CI matrix in `.github/workflows/test.yml`
in the SAME PR). If anything genuinely requires <3.13, keep the
bound and write the REAL constraint at the pin. Either way the
aider attribution dies. Update `tests/test_project_script.py`'s
pinned message (F12) to whatever the new text is — fixture-honesty:
test the NEW message, and mind the fresh `TestFixtureHonesty` guard
class from PR #93 when touching that module.

## Verified facts (planner; re-verify anchors — PR #93 shifted lines)

- The four scripts: `.adversarial/scripts/review_implementation.sh`,
  `evaluate_plan.sh`, `validate_tests.sh`, `proofread_content.sh` —
  each invokes `aider` directly (would fail; aider not installed).
- **F1 first**: check whether `adversarial init` (1.0.x — use the
  binary `command -v adversarial` resolves; three-installs lesson)
  re-provisions those scripts. If it does, deletion + a note in
  `.adversarial/docs/` is still right for THIS repo, but say so in
  the PR (downstream inits may resurrect them).
- Live referencing surfaces (F3): `.claude/agents/create-project.md`
  and `.adversarial/docs/EVALUATION-WORKFLOW.md` → repoint at the
  `adversarial` CLI + `prepare-review-input.sh` flow. NOTE:
  EVALUATION-WORKFLOW gets a full rewrite-or-archive in KIT-0067
  (D2 approved) — here, only fix the aider/script references, don't
  rewrite the doc.
- **Skip `onboarding.md` (F10 amendment)**: KIT-0067 D1 (approved)
  retires the onboarding agent entirely — fixing its aider text
  first is wasted motion. Note the skip in the PR body citing D1.
- F8: `test-runner.md` phantom `--yes` → the standing
  `echo y | ADVERSARIAL_UNATTENDED=1 adversarial …` invocation.
- F9: the five agents citing `TASK-*-PLAN-EVALUATION.md` log naming
  (document-reviewer.md was the audit exhibit — grep for the full
  set) → current scheme `<input-name>--<evaluator>.md`.
- F11: `.kit/templates/AGENT-TEMPLATE.md` `aider --yes` line — fix
  the template, then grep `.claude/agents/` for inherited copies.
- F7: `.aider` in `project`'s `exclude_dirs` — drop.
- Historical records stay untouched (retros, done/canceled tasks,
  ADRs, review records, CHANGELOG, memory files).

## Test approach

- Ordering rule: local tests green → evaluator trio
  (`echo y | ADVERSARIAL_UNATTENDED=1 …`; log-file-with-verdict is
  the proof; `git status` after every run) → PR open.
- The 3.13/3.14 venv experiment transcript goes in the PR body
  (pass or fail — it's evidence either way).
- If the bound lifts: CI matrix addition proves it on GitHub too.
- `pytest` directly; `./scripts/core/ci-check.sh` before pushing.

## Out of scope

- EVALUATION-WORKFLOW rewrite, onboarding agent (KIT-0067)
- Prose findings not aider-related (KIT-0069)
- `.claude/settings.local.json` aider allow-entry (user-owned)
- `.kit/adversarial/` (operator-owned — never stage or delete)

## PR sizing

Single PR (deletions + text fixes + the bound change with tests;
well under 400 reviewable lines): branch
`feature/KIT-0065-purge-aider-era-evaluator-scripts` (created).
