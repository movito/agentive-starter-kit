# KIT-0056 Handoff — feature-developer

**Task**: `.kit/tasks/4-in-review/KIT-0056-degraded-modes-and-presets.md`
**Target Codebase**: This repo — NOT a target repo (single-repo mode)
**Prepared**: 2026-07-18 (planner-f5)
**Estimated effort**: 4–6 hours

You are the feature-developer. Implement this task directly — do not
delegate to another agent instance.

## ⚠️ LAUNCH

**Your repository root is
`/Users/broadcaster_three/Github/ask-worktrees/KIT-0056/`** — branch
`feature/KIT-0056-degraded-modes-presets`, fully provisioned. Run
`git pull --ff-only` first. Shell cwd resets between calls — absolute
paths / `git -C` throughout (standing pattern).

## Mission

ADR-0027 P5+P7, transformation 5 of 6: the floor (honest
SKIP-with-notice gates for bot-less adopters) and the ceiling (the
operator's one-button preset) — one resolution mechanism read from
opposite ends. After this, only P6 remains.

## Context you must not lose

- **One resolver**: the preset layer replaces the stub inside
  KIT-0053's `resolve` function in `scripts/local/bootstrap`. Do not
  create a second resolution path anywhere — preflight reads the
  RECORDED `bots:` line (via the `_doctor_install` family), never the
  preset.
- **One region, one reader**: the `bots:` declaration joins
  shape/profile in the `kit-install` KIT-LOCAL region. Writer stays
  the consumer engine (the door resolves, the engine writes — the
  KIT-0053 invariant). Reader extensions go into `_doctor_install`'s
  family, and the partial-record rule binds: an unreadable region
  poisons dependent fields together (patterns.yml
  `intersection_names_drops`, record-reader face).
- **Absent = today's behavior, everywhere** (N1): no `bots:` line →
  gates behave exactly as now; no preset file → door behaves exactly
  as now. Characterize first (door prompt surface + Gates 2/3), the
  KIT-0048/0050/0053 precedent.
- **Preflight is shell + gh** (N3): Gates 2/3 read the declaration by
  extracting the region with `kit_markers.py` (it has a CLI) or an
  equally simple call — no Python imports into the gate script beyond
  what exists.
- **Secrets discipline (F6)**: `env-source` copies 0600 and is never
  echoed, staged, or logged. Test with a fixture secret, assert
  absence from all output and git status.
- **HOME-override in every preset test** — never read or write the
  real `~/.config` from the suite.
- **The one-button demo is the acceptance bar (N4)**: full preset →
  `bootstrap --new <scratch>` → zero prompts → doctor + preflight
  consistent with declarations. Record the transcript in the PR.

## Implementation guidance

- Suggested order: characterization (door prompts + gates) → F1 bots
  question/flag + region write → F2 gate SKIPs (harness fixtures) →
  F5 preset reader in `resolve` → F6 env-source → F7 example +
  `--no-preset` → F8 doctor `--against-preset` → F3/F9 docs.
- Gate SKIP lines follow the exact `GATE:N:Name:SKIP:<detail>` format
  (KIT-0042's F1.1 precedent for detail text that names the cause).
- The evaluator invocation for your Phase 7:
  `echo y | ADVERSARIAL_UNATTENDED=1 adversarial …` (belt-and-braces —
  three builds coexist; see the KIT-0053 retro's corrected Surprising
  #1). **Check the log file exists with a verdict; never trust
  exit 0.** `git status` after every run.
- Self-review items that bite here: 8 (exit codes), 10 (the preset
  example is a shipped hint — verify every key it shows against what
  `resolve` actually reads), 13 (bots × shape × preset cells — which
  combinations share a path?).

## Test approach

- Ordering rule: local tests green → evaluator trio → PR open.
- `tests/test_preflight_check.py` (declaration fixtures),
  `tests/test_setup_door.py` (resolve chain, preset precedence,
  unknown-key WARN, malformed fail-loud, env-source), doctor
  `--against-preset` in `tests/test_doctor.py`.
- `pytest` directly; `./scripts/core/ci-check.sh` before pushing.

## Evaluation summary

`arch-review-fast`: REVISION_SUGGESTED — flat-format boundary
documented (accepted), single-resolver named (accepted, already
satisfied by KIT-0053's structure), team presets declined (ADR's
second-operator revisit trigger). Disposition in the task file; log:
`.adversarial/logs/KIT-0056-degraded-modes-and-presets--arch-review-fast.md`.
No outstanding blockers.

## Out of scope

- P6 (the arc's last task), KIT-0054/0055, downstream migration
- Team/shared presets; bot-app installation automation
- Any gate changes beyond Gates 2/3 SKIP handling

## PR sizing

Single PR (< 500 lines: door question + region line + gate SKIPs +
preset reader + env-source + example + doctor flag + tests); split on
the P5/P7 boundary only if it balloons — pre-approved. Branch
`feature/KIT-0056-degraded-modes-presets` (already created).
