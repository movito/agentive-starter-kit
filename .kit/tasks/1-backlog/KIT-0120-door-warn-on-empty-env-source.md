# KIT-0120: Door warns when preset env-source is empty (silent bare-.env seeding)

**Status**: Backlog
**Priority**: low (one loud line at seed time; doctor already catches the downstream symptom)
**Type**: Infrastructure / UX
**Estimated Effort**: 1-2 h (warning + test; docs line in /setup-preset guidance optional)
**Created**: 2026-09-09
**Source**: Field observation, ixda-services-planning creation 2026-09-09 (planner-f5 session "2026-09-09 F5 New IxDA Services Planning repo")
**Related**: KIT-0084 (introduced .env seeding), KIT-0108 (`--bots=` empty-value hole — same "present but empty" defect class)

## Overview

KIT-0084's seeding precedence is: preset `env-source` wins over the
`.env.template` fallback. `apply_env_source()` validates that the source
file **exists and is readable** and warns on loose permissions — but
never checks that it is non-empty.

Observed live (2026-09-09, `agentive new` → ixda-services-planning,
agentive-kit v0.4.0): the operator preset declared
`env-source: ~/Github/agentive-config/env.source`, which was a **0-byte
file** (created at `/setup-preset` time 2026-07-24, never populated).
The door printed its normal success line —
"Seeded .env from preset env-source (mode 0600, gitignored; contents
never printed)" — and produced a 2-line `.env`
(PROJECT_NAME/TASK_PREFIX only). Doctor then FAILed on env-keys, which
names the **symptom** (keys missing) but not the **cause** (empty
env-source), and nothing points the operator at the file they need to
fill. The operator's natural next move — hand-editing the project's
`.env` — leaves env.source empty, so every future `agentive new`
repeats the failure.

This is the same defect class as KIT-0108's `--bots=` rider: a
present-but-empty value passing a presence check and silently defeating
the mechanism it configures. (`flag_presence_is_not_flag_emptiness`,
patterns.yml.)

## Requirements

- **F1 — warn at seed time on empty env-source.** In
  `apply_env_source()` (`packages/agentive-kit/src/agentive_kit/door/__init__.py`),
  when the resolved source is 0 bytes (or whitespace/comment-only —
  decide at implementation; 0-byte check is the minimum), print a
  warning to stderr naming the source path and the consequence, e.g.:
  `Warning: env-source <path> is empty — .env seeded with no API keys;
  fill <path> so future projects start with working keys (agentive
  doctor will FAIL env-keys until then)`. Do NOT die: an empty source
  may be a deliberate stranger/demo setup, and the doctor gate already
  blocks real work. Do NOT print file contents (existing discipline).
- **F2 — the success line stops overclaiming.** On the empty path,
  suppress or reword the "Seeded .env from preset env-source" success
  message so the transcript does not read as a working seed.
- **F3 — test coverage.** Unit test: preset with 0-byte env-source →
  warning emitted, exit 0, `.env` exists 0600 with identity lines only.
  Existing non-empty-source tests unchanged.
- **F4 (optional, decide at implementation) — /setup-preset guidance.**
  Where the preset-authoring flow creates or records an env-source
  path, if the named file is empty at authoring time, say so then too —
  the 2026-07-24 authoring is where this instance was actually born.

## Out of Scope

- Validating env-source *contents* (key names/formats) — doctor's
  env-keys check owns that, post-seed.
- Any change to seeding precedence or the `.env.template` fallback.
- Auto-falling-back to `.env.template` when env-source is empty —
  precedence is the operator's recorded intent; warn, don't override.

## Acceptance Criteria

- [ ] `agentive new` with an empty preset env-source prints a warning
      naming the env-source path and the fix; exit status unchanged
- [ ] Success line no longer claims a working seed on the empty path
- [ ] Non-empty env-source behavior byte-identical to today
- [ ] Test for the empty-source path passes; existing seeding tests green

## Success Metrics

- **Quantitative**: 0 recurrences of "bare .env with green seed line";
  the empty-source path has a dedicated test.
- **Qualitative**: an operator hitting this learns the cause (fill
  env.source) from the seed transcript alone, without diagnosing
  doctor's env-keys FAIL back to the preset.

## Reproduction (verified 2026-09-09)

```
$ wc -c ~/Github/agentive-config/env.source
       0 /Users/broadcaster_three/Github/agentive-config/env.source
$ agentive new .../ixda-services-planning --shape planning ...
# → "Seeded .env from preset env-source ..." (no warning)
# → resulting .env: PROJECT_NAME=... / TASK_PREFIX=  (2 lines, no keys)
# → DOCTOR:env-keys:FAIL:ANTHROPIC_API_KEY missing in .env; ...
```
