# KIT-0068: Functional repairs from the pre-0.9.0 cruft audit

**Status**: In Review
**Priority**: high
**Assigned To**: unassigned
**Estimated Effort**: 1-1.5 days
**Created**: 2026-07-24
**Linear ID**: (automatically backfilled after first sync)

## Related Tasks

**Parent**: pre-0.9.0 cruft audit —
`.kit/context/reviews/PRE-090-CRUFT-AUDIT-2026-07-24.md` (findings
cited by A-number below; each carries verified evidence)
**Related**: KIT-0065 (aider purge — owns A03/A09/A27/A29/A30/A47/A76),
KIT-0069 (doc truth sweep — owns the prose-only findings), KIT-0062

## Overview

The audit's functional cluster: things that are BROKEN or actively
diverging today, as opposed to stale prose. Three advertised `project`
subcommands fail on paths that moved in v0.4.0 (one masked by a test
fixture built on the old layout), the materials engine ships kit-side
scripts into consumers against its own contract, and the toolchain
disagrees with itself three ways. Fix the behavior; leave the pure
prose corrections to KIT-0069.

## Requirements

- **F1 — `project` caller paths (A00, A01, A02)**:
  - `linearsync` → `scripts/optional/sync_tasks_to_linear.py`
  - `create-agent` → `scripts/optional/create-agent.sh`
  - `reconfigure` identity rewrite → `scripts/core/logging_config.py`
  - Each with a friendly error when the target is absent (consumers
    may not carry `scripts/optional/`), naming the file it looked for.
  - **Fixture honesty (the A02 lesson)**: update
    `tests/test_project_script.py` fixtures to the REAL v0.4.0+
    layout, and add a guard test asserting each fixture path also
    exists in the actual repo tree — a fixture that models a
    nonexistent layout must fail loudly, this class already masked
    one regression for months.
- **F2 — linear-sync internals (A15, A14)**: fix the `.env`
  resolution (`Path(__file__).parent.parent` now lands in `scripts/`,
  not repo root) and widen the hardcoded `TASK-|ASK-` prefix
  acceptance to any `[A-Z]{2,6}-\d{4}` task ID (the kit mints
  arbitrary prefixes; KIT-* itself is currently rejected).
- **F3 — materials-engine consumer leak (A12, A13)**: exclude
  `scripts/local/` from the consumer rsync — the door's own help
  declares it "never ships on any sync tier or consumer rsync"; the
  engine violates the contract it sits next to. Fix the `.kit/`
  exclusion list for the ASK→KIT rename (exclude both prefixes'
  context/tasks entries, or better: exclude by location pattern, and
  per `intersection_names_drops` NAME what the exclusion drops in the
  engine's output). Add a test that a materials-flow export contains
  no `scripts/local/` and no kit-task files.
- **F4 — `.adversarial/config.yml` truth (A67)**: align the tracked
  config with the tree (`task_directory` → `.kit/tasks/`, plus the
  other divergent keys the finding names). Verify against what the
  installed CLI 1.0.1 actually reads (self-review item 10) — do not
  fix keys the CLI ignores; delete them instead, with the finding as
  citation.
- **F5 — evaluators self-symlink (A69)**: remove
  `.adversarial/evaluators/evaluators` (self-referential). Check
  `scripts/local/new-worktree.sh`'s link step for the creation vector
  (linking into the primary from the primary); if reproducible, guard
  it (no-op when source == destination).
- **F6 — toolchain alignment (A84, A88, A91)**:
  - `.pre-commit-config.yaml` Black rev → 26.5.1 (match pyproject's
    exact pin; they diverged again TODAY when #85 merged — consider a
    tiny consistency test pinning pre-commit rev == pyproject pin so
    the next dependabot bump can't split them silently).
  - Ruff: it is declared on three surfaces and run on zero. Decision
    rule: run `ruff check` locally first — if violations are trivial
    (< ~20, mechanical), fix them and add ruff to `ci-check.sh` + CI;
    if it's a flood, REMOVE the config, the dep, and the CLAUDE.md
    claim instead (a linter nothing runs is a false promise). Either
    way the three surfaces end up agreeing.
  - `ci-check.sh` flake8 invocation → byte-match CI's (`test.yml`)
    args, or change the header to stop claiming it mirrors CI.
- **F7 — version surface honesty (A04, A08, A10, A05)**:
  - `project version` reads `scripts/core/VERSION` (single source);
    drop the duplicate line.
  - Evaluator-library fallback `v0.5.3` → fail loud naming
    pyproject.toml as the source instead of silently using a
    5-generations-old default.
  - `main()` venv preference: `.venv` first, and the
    FileNotFoundError help says `./scripts/core/project setup` (not
    `python3 -m venv venv`).
  - `scripts/core/__init__.py` docstring: drop the moved modules
    from the Contains list (2-line fix, riding along).
- **Bookkeeping**: core scripts VERSION 3.5.0 → 3.6.0; both manifests
  + `test_core_manifest.py` counts if any core file list changes;
  CHANGELOG Unreleased entry.

## Acceptance Criteria

- [ ] `project linearsync`, `project create-agent`, and `reconfigure`
      demonstrably work against the real tree (regression tests with
      real-layout fixtures + the fixture-path guard test)
- [ ] Materials export contains no `scripts/local/` and no kit task
      files (test)
- [ ] `.adversarial/config.yml` keys verified against CLI 1.0.1
      behavior; evaluator self-symlink gone and creation vector
      guarded
- [ ] Black pre-commit rev == pyproject pin (with consistency test);
      ruff either enforced or fully removed — no third state
- [ ] `project version` output matches `scripts/core/VERSION`
- [ ] All audit A-numbers addressed here are checked off in the PR
      body with a one-line disposition each

## Success Metrics

- **Quantitative**: 0 advertised-but-broken `project` subcommands;
  toolchain versions agree across pre-commit/pyproject/CLAUDE.md
- **Qualitative**: the A02 fixture class can't recur silently

## Time Estimate

1-1.5 days: F1+fixtures 3h, F2 1h, F3 2-3h, F4-F5 1-2h, F6 2h, F7 1h

## Out of scope

- All prose-only audit findings (KIT-0069) and aider residue
  (KIT-0065); structural launcher/onboarding questions (KIT-0067/0070)
- Any behavior change beyond making surfaces match their own claims

## Notes (accepted evaluation additions)

- **Two-homes rule**: wherever this task touches a fact that lives in
  two places (Black rev, version strings, prefix patterns), prefer a
  consistency TEST pinning the pair over prose promising alignment.
  If the same pin shape appears 3+ times, propose a patterns.yml rule
  in the PR (`two_homes_get_a_pin` or similar) — planner will review.

## Evaluation

`arch-review-fast` (gemini-2.5-flash, 2026-07-24): **REVISION_SUGGESTED**
— log: `.adversarial/logs/KIT-0068-functional-repairs-audit--arch-review-fast.md`.
Disposition (planner):

1. **Declarative resource-location/registry for script paths —
   DECLINED.** The post-ADR-0027 layout is stable; a path registry is
   indirection without a second consumer (same class as the four
   declined forge abstractions). The fixture-path guard test (F1) is
   the structural enforcement, at test cost instead of runtime cost.
2. **Single-source-of-truth policy + proactive enforcement —
   ACCEPTED** as the two-homes rule above (F6 already carried the
   Black instance).
3. **Programmatic contract enforcement for the materials engine —
   already in spec** (F3's export test). No change.

No outstanding blockers. Working tree verified clean post-run.
