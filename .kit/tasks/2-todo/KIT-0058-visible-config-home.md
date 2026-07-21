# KIT-0058: Relocate the operator config to a visible sibling folder

**Status**: Todo
**Priority**: high (fast-follow — must land BEFORE the operator creates
their real preset; nobody has one yet, so relocation is free now)
**Assigned To**: unassigned
**Estimated Effort**: 2-3 hours
**Created**: 2026-07-21
**Linear ID**: (automatically backfilled after first sync)

## Related Tasks

**Parent**: KIT-ADR-0027 P7, amended 2026-07-21 (operator review:
invisible dotfolders are a threshold; visibility + guardrails beat
obscurity)
**Related**: KIT-0056 (shipped the preset reader this relocates),
KIT-0057 (arc finale, in flight — do NOT fold this in; it lands as its
own small PR after)

## Overview

Move the operator config home from `~/.config/agentive-kit/` to a
**visible sibling of the kit checkout**:
`<parent-of-kit-primary-clone>/agentive-config/` (for this operator,
`~/Github/agentive-config/`). Simpler: one visible folder next to
where the user already works. Safer: seeded `.gitignore` + README on
first use, 0600 secrets by reference, and a doctor check asserting a
git-init'd config repo is private with `env.source` untracked —
guardrails instead of obscurity.

## Requirements

- **F1 — resolution**: the preset reader (inside the door's
  `resolve()` — still the only resolver) locates the config home as
  the parent of the kit's PRIMARY clone (`git rev-parse
  --git-common-dir`-based, worktree-safe) + `/agentive-config/`.
  `AGENTIVE_KIT_CONFIG_DIR` overrides it (tests, unusual layouts) —
  an override, never a search chain. The loaded preset path is NAMED
  in door output (existing loudness rule).
- **F2 — defensive seeding on first use** (*in `orchestrate`, not
  `resolve` — accepted evaluation finding: resolve locates paths and
  writes nothing; orchestrate performs the seeding as a distinct,
  independently-testable step*): when the door first
  creates (or first reads an empty) config home, it seeds
  `.gitignore` (`env.source`, `*.env`) and a one-paragraph `README.md`
  (what this folder is; private-repo pattern welcomed; secrets stay in
  `env.source`, 0600, never committed). Seeding is idempotent and
  never overwrites existing files.
- **F3 — doctor `config-home` check** (rides `doctor.d/`): if the
  config home has a git remote → assert visibility `private` via
  `gh repo view --json visibility` (WARN on public or on gh failure,
  naming the risk); assert `env.source` is untracked/ignored (FAIL if
  tracked — that's a secret in git). No remote / no git = PASS with
  the path named. Incident citation per the lifecycle rule.
- **F4 — legacy migration notice**: if `~/.config/agentive-kit/preset`
  exists, door and doctor emit a one-line named notice ("legacy
  preset location found — move it to <new path>"); it is NEVER read as
  a fallback. Remove the notice at 0.9.0 (join the removal set).
- **F5 — docs + example**: `docs/preset.example`, the door's help, and
  the P7 setup docs all point at the new home; `doctor
  --against-preset` reads the new location.

### Non-Functional Requirements

- **N1**: HOME/`AGENTIVE_KIT_CONFIG_DIR`-override in every test —
  never the real sibling folder.
- **N2**: no behavior change when no config home exists (stranger
  path byte-identical; characterize).
- **N3**: the folder itself is never created unless the user engages
  the preset flow (no drive-by dirs on every door run).

## Acceptance Criteria

- [ ] Preset read from `<kit-parent>/agentive-config/preset`;
      override honored; loaded path named in output
- [ ] First-use seeding: `.gitignore` + README appear once,
      idempotently, never overwriting
- [ ] Doctor: private-remote assertion (WARN public), env.source
      tracked = FAIL, no-git = PASS; fixtures for all three
- [ ] Legacy location: notice only, never read (test both)
- [ ] Stranger path characterization green (N2)
- [ ] One-button demo re-run from the new location (transcript in PR)

## Notes

- Source: ADR-0027 P7 amendment 2026-07-21 (in the ADR, with the full
  rationale). Sequenced after KIT-0057 as its own small PR — the arc
  finale is not scope-creeped.
- Operator's create-your-preset step WAITS for this task.

## Evaluation (2026-07-21)

`arch-review-fast` (gemini-2.5-flash): **REVISION_SUGGESTED** — three
findings. Log:
`.adversarial/logs/KIT-0058-visible-config-home--arch-review-fast.md`.
Planner disposition:

- **Accepted — seeding out of `resolve()`**: folded into F2; resolve
  locates, orchestrate seeds (KIT-0053's decomposition already has the
  slot).
- **Declined — `SourceControlService` abstraction over `gh`**: the
  forge-abstraction suggestion, declined twice already in ADR-0027
  ("Explicitly not proposed"); `gh` is the kit's declared backbone and
  F3 already degrades to WARN when `gh` fails.
- **Acknowledged, no change — git-based resolution**: the kit is a git
  clone by construction (its entire machinery assumes it); the
  evaluator itself rated an abstraction premature. Documented here as
  the deliberate choice it is.
