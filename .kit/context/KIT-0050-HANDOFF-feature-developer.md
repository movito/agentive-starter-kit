# KIT-0050 Handoff — feature-developer

**Task**: `.kit/tasks/4-in-review/KIT-0050-language-profiles.md`
**Target Codebase**: This repo — NOT a target repo (single-repo mode)
**Prepared**: 2026-07-15 (planner-f5)
**Estimated effort**: 4–6 hours

You are the feature-developer. Implement this task directly — do not
delegate to another agent instance.

## ⚠️ LAUNCH

**Your repository root is
`/Users/broadcaster_three/Github/ask-worktrees/KIT-0050/`** — branch
`feature/KIT-0050-language-profiles`, fully provisioned. Run
`git pull --ff-only` first (worktree cut just before the spec landed).

## Mission

ADR-0027 P1 — transformation 3 of 6, and the one that unwinds the
kit's founding presumption: the Python gauntlet stops being imposed
and becomes the seeded default behind one project-owned hook. The spec
was evaluated **APPROVED, zero findings** — everything is decided;
this is execution.

## Context you must not lose

- **The hook contract is fixed** (ADR-0027 P1 + spec F2): `--mode
  ci|local`, exit 0/1 only, stdout diagnostics, repo-root invocation,
  no env guarantees. A paragraph and a header template — never a
  schema (N3).
- **N1 is the whole trust story**: hook-absent `ci-check.sh` must be
  byte-identical to today. Characterization first, exactly as
  KIT-0048 did for bootstrap. Move the gauntlet content, don't rewrite
  it (the KIT-0035 Black-drift warning comes along).
- **Reuse KIT-0048's mechanisms, don't parallel them**: the
  `kit-install` region gains a `profile:` line (same kit_markers
  writer/reader — extend `_doctor_shape()` to a shape+profile reader
  rather than adding a second reader); doctor scoping uses the same
  header-declaration mechanism (`# profiles: python` alongside
  `# shapes:`); malformed values reuse the fail-loud pattern
  (full set + FAIL line).
- **The kit ships no toolchains it doesn't use**: `python` and `none`
  are the only seeded profiles; "js" is the contract plus a hook the
  adopter writes. Do not scaffold empty js/go packs.
- **N4 via KIT-0049**: `scripts/local/checks.sh` must never ride any
  sync tier — it's consumer-owned after seeding. Verify against the
  manifest tiers and pin with a test in the KIT-0049 suite.
- **F6 touches the kit's own CLAUDE.md** (marker-wrapping Project
  Rules): content stays identical; only markers are added. Consumer
  seeding varies by profile. kit_markers round-trip (byte-preserving
  for well-formed regions) is the correctness bar — its test suite
  shows the patterns.

## Implementation guidance

- Suggested order: characterize ci-check → dispatcher (F1) → python
  seed by extraction (F3) → contract header + docs (F2) → record +
  reader (F4) → doctor declarations (F5) → CLAUDE.md region (F6).
- The dispatcher's hook detection is presence-of-file, nothing
  smarter; a hook that exists but isn't executable should be a loud
  error, not a silent fallback (the masking class —
  `intersection_names_drops` thinking applies to fallbacks too).
- Planning-shape forcing of `none` mirrors KIT-0048's hard-coded
  pairing; the P3 matrix generalizes later.
- Self-review items 8 (exit codes), 11 (scoped fixtures), 12
  (block-replacement borders — you'll be moving a big gauntlet block;
  check what sits above and below both ends) all bite on this task's
  exact shape.

## Test approach

- **Ordering rule (all tasks)**: local tests green → evaluator trio →
  PR open; `git status` after every evaluator run.
- Characterization, per-profile scratch consumers (both shapes),
  contract conformance incl. bogus `--mode`, doctor declaration
  extensions, sync-never-touches-hook — per the spec's Test Plan.
- `pytest` directly; `./scripts/core/ci-check.sh` before pushing (its
  own dispatcher path being under test makes this pleasantly
  self-referential — the characterization suite is your net).

## Evaluation summary

`arch-review-fast`: **APPROVED, zero findings** — first clean approve
of the arc. Log:
`.adversarial/logs/KIT-0050-language-profiles--arch-review-fast.md`.
No outstanding blockers, no dispositions to honor beyond the spec.

## Out of scope

- P3 (one door), P7 (presets), pre-commit profile variants (N2)
- Non-Python toolchain packs
- Downstream migration; doctor driver changes beyond declarations

## PR sizing

Single PR (< 550 lines: dispatcher + extracted seed + contract docs +
record/reader + doctor headers + CLAUDE.md markers + tests): branch
`feature/KIT-0050-language-profiles` (already created). If
characterization balloons it, split it out as PR 1 — pre-approved,
KIT-0048 precedent.
