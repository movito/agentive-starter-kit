# KIT-0065 Review Starter

**Task**: Whole-repo aider purge + Python `<3.13` ceiling lift
**PR**: https://github.com/movito/agentive-starter-kit/pull/94
**Branch**: `feature/KIT-0065-purge-aider-era-evaluator-scripts`
**Status**: Ready for human review (2026-07-26)

## What shipped

- The four dead aider-era `.adversarial/scripts/*.sh` wrappers are
  deleted (F1 verified first: `adversarial init` 1.0.x provisions only
  config/guide/env.example — no resurrection risk). Manifest kit_builder
  entry removed (14→13); core scripts **3.7.0**.
- Every live surface fixed: five agents' evaluator-log naming to
  `<input-name>--<evaluator>.md`, test-runner's phantom `--yes` flag to
  the `echo y | ADVERSARIAL_UNATTENDED=1` pattern, AGENT-TEMPLATE's
  `aider --yes`, create-project/EVALUATION-WORKFLOW script refs,
  `.gitignore` `.aider*`, `exclude_dirs` `.aider`.
- **`requires-python` lifted to `>=3.10`**: empirically re-derived on
  system Python 3.14.3 (`project setup` + full suite: 799 passed).
  `cmd_setup` drops the uv 3.12-venv workaround; CI test job now a
  3.10/3.12/3.14 matrix — all green on the PR.
- onboarding.md deliberately skipped (KIT-0067 D1 retires that agent).

## Review state

- CI: 6/6 checks green (matrix 3.10/3.12/3.14 + lint + both bots)
- CodeRabbit: round 1 = 3 threads (sibling GPT-4o line, interpreter
  order, test exception suppression) — all fixed in `2137182`,
  replied, resolved; round 2 = **APPROVED**
- BugBot: pass, no findings (both rounds)
- Evaluator trio (pre-PR): fast=CONCERNS (dispositioned),
  o3=CONCERNS (0 real / 2 refuted empirically / 2 pre-existing),
  claude-code=APPROVED — record:
  `.kit/context/reviews/KIT-0065-evaluator-review.md`
- Preflight: gates 1–5, 7 PASS before this starter landed

## Reviewer attention points

- The ceiling-lift is the one behavioral change: `cmd_setup` no longer
  has an upper version bound and the uv fallback is gone
  (`detect_uv`/`create_venv_with_uv` + `tests/test_uv_detection.py`
  deleted — the workaround existed solely for the ceiling).
- `setup-dev.sh` interpreter preference is now newest-explicit-first
  with bare `python3` fallback.
- Planner disposition flagged in the PR: backlog task ASK-0049
  (aider→LiteLLM) is moot — upstream shipped LiteLLM in 1.0.x.

## For the planner (post-merge)

- `./scripts/core/project complete KIT-0065`, delete branch, remove
  worktree `../ask-worktrees/KIT-0065`
- Chain continues: KIT-0069 → KIT-0067 → cut 0.9.0
