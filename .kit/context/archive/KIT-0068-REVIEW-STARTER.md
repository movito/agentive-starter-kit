# KIT-0068 Review Starter — Functional Repairs from the Cruft Audit

**PR**: https://github.com/movito/agentive-starter-kit/pull/93
**Branch**: `feature/KIT-0068-functional-repairs-audit`
**Task spec**: `.kit/tasks/4-in-review/KIT-0068-functional-repairs-audit.md`
**Evidence base**: `.kit/context/reviews/PRE-090-CRUFT-AUDIT-2026-07-24.md`
(every fix cites its A-number; the PR body checks off all 16 with
one-line dispositions)
**Evaluator record**: `.kit/context/reviews/KIT-0068-evaluator-review.md`
**Core scripts**: 3.5.0 → 3.6.0

## What changed, by area

- **F1 — `project` caller paths**: `linearsync`, `create-agent`, and
  reconfigure's identity rewrite target the real v0.4.0+ paths, with
  friendly errors naming the missing file. The old-layout test fixture
  that masked A02 is rebuilt on the real tree; `TestFixtureHonesty`
  pins every fixture-modeled path to the actual repo.
- **F2 — linear-sync internals**: root `.env` resolves from
  `scripts/optional/`; any `[A-Z]{2,6}-NNNN` id accepted; filename id
  anchored and heading id must match it (bot round 1).
- **F3 — materials engine**: `scripts/local/`, kit-only tests,
  prefix-agnostic planning corpus, and `.kit/adversarial/` no longer
  ship; drops named in output; `--scaffold-only` seam +
  `tests/test_engine_materials.py`.
- **F4/F5 — adversarial config + symlink**: config.yml regenerated,
  keys verified against installed CLI 1.0.1 (unread keys deleted);
  self-symlink removed; `new-worktree.sh` refuses to link over an
  existing destination.
- **F6 — toolchain**: Black rev == pyproject pin (test-pinned); ruff
  ENFORCED (ci-check 4/7, CI lint job, seeded checks hook — 24
  mechanical violations fixed); flake8 args byte-match CI
  (test-pinned). New `tests/test_toolchain_consistency.py`.
- **F7 — version surfaces**: `project version` reads
  `scripts/core/VERSION`; evaluator pin read fails loud (lazy, `--ref`
  bypasses it, no-op rerun skips it); `.venv` preferred; core
  `__init__.py` docstring truthful.

## Review history

- Evaluator trio (BEFORE PR open): fast-v2 CONCERNS (1 accepted),
  o3 FAIL (1 real → fixed `--ref` bypass; 2 refuted, 2 out-of-diff),
  claude-code APPROVED. Dispositions in the evaluator record.
- Bot rounds: CodeRabbit round 1 — 5 threads (1 Major: heading/filename
  id mismatch), all accepted, fixed in `049bff9`. BugBot round 2 —
  1 thread (pin read before installed check), fixed in `064a21e`.
  **6/6 threads resolved, CI green, reviewDecision APPROVED.**

## How to verify

```bash
./scripts/core/project version        # v3.6.0 (core scripts)
./scripts/core/project create-agent   # reaches the real script's usage
./scripts/core/ci-check.sh            # 7/7 incl. the new ruff step
pytest tests/ -q                      # 826 tests
bash scripts/local/engine-materials.sh "$(mktemp -d)" --scaffold-only
```

## Open items for planner

- `patterns.yml` proposal `two_homes_get_a_pin` (pin shape appears 3×:
  Black rev, flake8 args, ruff invocation) — in the PR body, awaiting
  planner review; deliberately not in this diff.
- Backlog note candidate: `linearsync` silently ignores unknown args
  (no `--dry-run`) and its logger is invisible when run as a script
  (import fallback) — my verification run performed a REAL idempotent
  sync.
- The self-symlink removal happened in the PRIMARY clone (untracked
  file, plain `rm` — no commit involved).
