# KIT-0056: Degraded modes + operator presets — the floor and the ceiling (ADR-0027 P5+P7)

**Status**: In Review
**Priority**: high
**Assigned To**: unassigned
**Estimated Effort**: 4-6 hours
**Created**: 2026-07-18
**Target Completion**: TBD
**Linear ID**: (automatically backfilled after first sync)

## Related Tasks

**Parent**: KIT-ADR-0027 P5 + P7 (Accepted; the ADR sequences them
together — "the same resolution mechanism read from opposite ends")
**Related**: KIT-0053 (the door + the preset stub this fills; the
kit-install region P5's declaration joins), KIT-0046/0048 (doctor +
declaration mechanics), KIT-0034/0042/0043 (the preflight gates P5
extends)

## Overview

P5 is the floor: a new adopter without CodeRabbit, BugBot, or three
model-provider keys gets honest SKIP-with-notice gates instead of
false FAILs. P7 is the ceiling: the kit's primary operator gets
`bootstrap --new <dir>` as a genuine one-button full-stack project via
a preset file that pre-answers exactly the door's questions. One
resolution mechanism (the KIT-0053 chain), read from opposite ends;
the kit itself stays neutral in both directions.

## Requirements

### P5 — Degraded modes (the floor)

- **F1 — bots declaration in the kit-install region**: a `bots:` line
  (e.g. `bots: coderabbit bugbot` | `bots: none` | subsets), written
  by the door (a new door question, flag `--bots`), read via the
  existing `_doctor_install` family — one region, one reader library
  (ADR evaluation finding: no ad-hoc regex over CLAUDE.md). **Absent
  line = both bots expected** — today's behavior; zero migration for
  existing repos.
- **F2 — preflight Gates 2/3 honor the declaration**: a declared-absent
  bot → `GATE:N:<bot>:SKIP:<declared absent in kit-install>` — never
  FAIL, never silent PASS. Declared-present (or absent line) keeps
  every existing behavior including the KIT-0034 fallbacks. Extend the
  stub-`gh` harness with declaration fixtures.
- **F3 — degraded evaluation mode, documented not gated**: the
  code-review-evaluator skill gains a "single-key mode" section — with
  one provider key, run one evaluator + the self-review checklist and
  NAME the mode in the persisted review record. Gate 5 is unchanged (a
  record is still required; a degraded record satisfies it). No gate
  logic changes for this half.
- **F4 — loud everywhere**: every degraded surface names its mode in
  output (`intersection_names_drops` applied to service presence).

### P7 — Operator presets (the ceiling)

- **F5 — the preset reader fills the KIT-0053 stub**:
  `~/.config/agentive-kit/preset` (simple `key: value` lines, same
  parse family as the kit-install region — no YAML/JSON dependency;
  flat-keys-only is a documented, conscious boundary of the format —
  richer needs are a revisit trigger, not a v1 concern). **All
  resolution logic lives in the door's existing `resolve` function**
  (KIT-0053's decomposition) — the preset layer replaces its stub;
  no second resolver anywhere (evaluation finding, satisfied by the
  existing structure).
  Resolution stays CLI > preset > kit defaults > prompt. A preset may
  answer ONLY questions the door asks (shape, profile, bots, evaluator
  install yes/no, venv setup yes/no, target-repo fields for planning
  shape) — unknown keys are a loud WARN and are ignored, never an
  error (forward compatibility), and never invent new behavior.
- **F6 — secrets by reference**: an optional `env-source: <path>` key
  naming an operator-owned template (chmod 600 expected). On `--new`,
  the door copies it to the target's `.env` (mode 0600) — never
  printing contents, never staging it (`.env` is gitignored in the
  export already; verify). No key material ever lives in the preset
  itself.
- **F7 — never distributed**: the preset path is outside every repo;
  nothing in any sync tier, rsync, or export may touch
  `~/.config/agentive-kit/`. The kit ships ONE commented example
  (`docs/preset.example` or door `--help` text — implementer's call)
  and the door gains `--no-preset` to bypass for a stranger-mode run.
- **F8 — doctor `--against-preset`** (small): compares the project's
  kit-install record against the preset and reports divergence as
  INFO lines — never WARN/FAIL (a deliberately-lean project is not
  wrong; ADR P7).
- **F9 — docs**: preset setup documented where the door's docs live,
  including the org-wide bot-app installation note (documented as an
  operator step, never automated — GitHub App installs are an auth
  surface the kit does not drive).

### Non-Functional Requirements

- **N1**: no preset present + no `--bots` flag = byte-identical
  current behavior everywhere (characterization: door, preflight,
  doctor).
- **N2**: preset parsing is stdlib/shell only; malformed preset =
  loud error naming the line, never a silent partial read (the
  record-reader face of the masking class — partial records poison
  dependent fields together).
- **N3**: preflight stays shell + `gh` (KIT-0034 N-series stands).
- **N4**: the one-button demo is the acceptance bar: with a full
  preset, `bootstrap --new <scratch>` asks ZERO questions and the
  resulting project's doctor + preflight reflect the preset's
  declarations.

## Acceptance Criteria

- [ ] Gates 2/3 SKIP-with-notice under `bots: none`; unchanged
      behavior with no declaration (harness fixtures both ways)
- [ ] Door writes the `bots:` line from flag/preset/prompt; region
      round-trips via kit_markers
- [ ] Single-key degraded mode documented; a degraded review record
      names its mode
- [ ] Preset chain: CLI beats preset beats defaults beats prompt
      (unit-tested in the door's resolve function); unknown keys WARN
      and skip; malformed preset fails loud
- [ ] `env-source` copies 0600, never prints, never stages
- [ ] One-button demo (N4) recorded in the PR: full preset → zero
      prompts → doctor/preflight consistent with declarations
- [ ] `--no-preset` gives the stranger path; no-preset machines are
      byte-identical to today (N1 characterization)
- [ ] `doctor --against-preset` reports INFO-only divergence
- [ ] Nothing under `~/.config/agentive-kit/` is touched by sync,
      rsync, or export paths (test the exclusion)

## Test Plan

- Characterize door prompts + preflight gates with no preset/flags
  first (N1 net).
- Preset fixtures via `HOME`-override in tests (tmp HOME with a
  preset; never the real `~/.config`).
- Gates 2/3 declaration fixtures ride `tests/test_preflight_check.py`;
  door resolve-chain tests ride `tests/test_setup_door.py`.

## Notes

- Source: KIT-ADR-0027 P5 + P7 (incl. the P7 amendment's full
  mechanism: pre-answered-questions-only, git-config resolution
  order, projects record resolved choices, doctor validates the
  record not the preset).
- After this task the operator creates their real preset (an operator
  step, not a PR): `~/.config/agentive-kit/preset` with full-stack
  answers — at that point "make another project for Fredrik with his
  usual prefs" is literally one command.
- Out of scope: P6 (homes + prune — the arc's last task), downstream
  migration, bot-app automation, KIT-0054/0055, team/shared presets
  (declined — the ADR's "second operator" revisit trigger is exactly
  that scenario; presets stay personal and undistributed).

## Evaluation (2026-07-18)

`arch-review-fast` (gemini-2.5-flash): **REVISION_SUGGESTED** — three
findings, design judged "largely sound... solid foundation". Log:
`.adversarial/logs/KIT-0056-degraded-modes-and-presets--arch-review-fast.md`.
Planner disposition:

- **Accepted — flat-format boundary documented** (the evaluator itself
  rated the choice acceptable for scope); folded into F5.
- **Accepted (already satisfied) — explicit resolver**: KIT-0053's
  `resolve` function IS the single resolution home; F5 now names it
  and forbids a second resolver.
- **Declined — team/shared presets**: single-operator reality; the
  ADR's "second operator" revisit trigger covers the scenario
  precisely. Folded into Out-of-scope.
