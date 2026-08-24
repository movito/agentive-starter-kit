# KIT-0118: Packaged-door fresh-install fixes + agentive-kit 0.4.0 — Implementation Handoff

**You are the feature-developer. Implement this task directly. Do not
delegate or spawn other agents.**

**Date**: 2026-08-24
**From**: planner-f5  **To**: feature-developer
**Task**: .kit/tasks/3-in-progress/KIT-0118-packaged-door-fresh-install-fixes.md
**Status**: Ready
**Evaluation**: REVISION_SUGGESTED, both findings strategic-only and
dispositioned in the spec's Evaluation section — don't re-litigate.
Log: `.adversarial/logs/KIT-0118-packaged-door-fresh-install-fixes--arch-review-fast.md`
**Target Codebase**: This repo (single-repo mode — planning and code together)

## Session topology (read before anything else)

- **Worktree**: `/Users/broadcaster_three/Github/ask-worktrees/KIT-0118`
- **Branch**: `feature/KIT-0118-packaged-door-fixes` (created by the
  planner at authoring time — verify, NEVER create; wrong branch or
  path → STOP and ask, never `checkout -b`)
- **Plan**: single PR, then a post-merge tag (`agentive-kit-v0.4.0`)
  that triggers the publish workflow.

## Mission

Close GitHub issues #145, #146, #144 (that order — code fixes first,
release last). The spec's Requirements Parts A–D are authoritative;
this handoff adds anchors and cautions only.

1. **Part A (#145)**: in `engine-consumer.sh`, derive `target_path` as
   `../${TARGET_GITHUB#*/}` when `--target-path` is omitted but
   `--target-github` given; strip `# TODO` prose from all recorded
   values in the neither-flag case (both `TP` and `TG`).
2. **Part B (#146.1)**: persist `evaluators: yes|no` in the kit-install
   region (mirror the `bots:` flow end to end); doctor's evaluator
   checks SKIP on `evaluators: no`, legacy behavior when absent.
3. **Part C (#146.2)**: `20-env-keys.py` — the TASK_PREFIX finding must
   surface even when the required-key FAIL fires (fresh-install
   fixture: API key commented + prefix empty → BOTH problems visible).
4. **Part D (#144)**: bump `__version__` to `0.4.0`; after merge, tag
   `agentive-kit-v0.4.0`, watch the publish workflow, verify PyPI
   serves 0.4.0 and a clean install exposes `agentive new`/`adopt`.

## Verified anchors (verified 2026-08-24 against main @ cb9ad4f — re-verify before relying)

Planner ran these queries this session; the spec's "Verified Facts"
section carries the outputs. Do not trust the line numbers blindly —
re-grep on your branch:

- `packages/agentive-kit/src/agentive_kit/__init__.py:7` →
  `__version__ = "0.3.1"`; pyproject is `dynamic = ["version"]`
  (`pyproject.toml:15`, `:58`) — ONE bump point.
- Placeholders: `grep -n 'TODO: set the product repo'
  packages/agentive-kit/src/agentive_kit/door/engines/engine-consumer.sh`
  → the `TP=`/`TG=` defaults (~line 668–669).
- Record body written via `KIT_INSTALL_BODY` printf (~line 783–792);
  `bots:` appended conditionally — that's the model for `evaluators:`.
- Record readers: door `load_record()` (`door/__init__.py`, regex
  `target_path:` reader, no `#` handling) and doctor `_parse_record`
  (`doctor/__init__.py` — shape/profile/bots today). **Check for a
  second record reader under `scripts/core/doctor.d/` or the doctor
  driver before assuming single-copy** (spec risk #3).
- `20-env-keys.py`: `REQUIRED_KEYS` loop `print(FAIL); return 0`
  precedes the `TASK_PREFIX` warn block; `.env.template` ships the key
  commented and `TASK_PREFIX=` empty (planner verified both lines).
- Evaluator checks: `30-evaluators.sh` / `31-evaluator-cli.sh` SKIP
  only on `.adversarial/` absent; consumer engine copies `.adversarial/`
  unconditionally (~line 412–417).
- Publish workflow `.github/workflows/publish-agentive-kit.yml`:
  tag-triggered `agentive-kit-v*`, OIDC trusted publishing, guards
  tag == `__version__`, smoke-tests the wheel pre-publish.
- PyPI state (queried 2026-08-24): latest `0.3.1`, releases
  `0.1.0/0.2.0/0.3.0/0.3.1`. PyPI accepts each version exactly once —
  tag only after main is green.

## Twin discipline (MANDATORY — patterns.yml `harden_twins_by_copy_not_rederivation`)

Four files have kit-side twins, byte-identical at task start
(planner-verified `diff -q` clean 2026-08-24):

| Package copy | Kit copy |
|---|---|
| `packages/agentive-kit/src/agentive_kit/door/engines/engine-consumer.sh` | `scripts/local/engine-consumer.sh` |
| `packages/agentive-kit/src/agentive_kit/doctor/checks/20-env-keys.py` | `scripts/core/doctor.d/20-env-keys.py` |
| `packages/agentive-kit/src/agentive_kit/doctor/checks/30-evaluators.sh` | `scripts/core/doctor.d/30-evaluators.sh` |
| `packages/agentive-kit/src/agentive_kit/doctor/checks/31-evaluator-cli.sh` | `scripts/core/doctor.d/31-evaluator-cli.sh` |

Edit once, **copy** across (never re-derive), `diff -q` per pair at PR
time, paste the clean output in the PR body.

## Test approach

- pytest suites under `packages/agentive-kit/` (find the existing
  door/doctor tests first — pre-implementation skill) + repo suite.
- Fixture-driven: fresh-install `.env` fixture for Part C; kit-install
  region fixtures (with/without `evaluators:`) for Part B; record
  round-trip for Part A.
- `./scripts/core/ci-check.sh` before push; CI green on GitHub before
  review handoff.
- Part D verification is POST-MERGE: publish workflow run link + PyPI
  JSON check + clean-env `uv tool install agentive-kit` smoke
  (`agentive version` → 0.4.0, `agentive new --help` exists). Record
  outputs in the task file before wrap-up.

## Out of scope — do not touch

- CI guard for "main changed under a published version" → KIT-0111
  (a scope-note edit to that spec is a Should-Have, code is not).
- Engine consolidation → KIT-0108.
- Doctor checks from issues #142/#143 → separate future task.
- `docs/STARTING-A-PROJECT.md` beyond confirming its promise holds
  post-release (edit only if something it states is still false at
  0.4.0).
- Discovered gaps → file in `.kit/tasks/1-backlog/`, don't fix inline.

## Cautions

- **Doctor output lines are contract strings** (`DOCTOR:name:VERDICT:detail`)
  — preflight gates and tests parse them. Keep the format; check for
  tests pinning exact detail text before rewording.
- **Bot budget**: ONE substantive fix round (standing policy). Bot
  truth = reviewThreads GraphQL, not check statuses (bot-triage skill).
- The evaluator answer flows CLI → door (`door/__init__.py`,
  `with_evaluators`) → engine env → region body. Trace the real seam
  for `bots:` and mirror it exactly rather than inventing a new path.
