# KIT-0093: The door switches to package-install mode — Implementation Handoff

**You are the feature-developer. Implement this task directly. Do not delegate or spawn other agents.**

**Date**: 2026-08-08
**From**: planner-f5
**To**: feature-developer (f5 variant recommended — multi-PR, judgment-heavy removal decisions)
**Task**: `.kit/tasks/5-done/KIT-0093-door-package-install-mode.md`
**Status**: Ready — ADR-0028 phase 2; the only active work item
**Evaluation**: arch-review-fast APPROVED 2026-08-08, first pass —
`.adversarial/logs/KIT-0093-door-package-install-mode--arch-review-fast.md`

**Target Codebase**: This repo (agentive-starter-kit) — single-repo mode
(the repo split, not your working directory — see Session topology).

## Session topology (read before anything else)

- Worktree: `~/Github/ask-worktrees/KIT-0093`, branch
  `feature/KIT-0093-door-package-install-mode` — created and
  provisioned by the planner; task file already `3-in-progress`
- VERIFY, never create: `git branch --show-current` must show the
  branch above before your first edit; if not, STOP and ask
- 3 PRs per the spec's PR plan; stacked per STACKED-PR-WORKFLOW.md
  (CI triggers natively on stacked bases now; CodeRabbit still skips
  feature-branch bases and its "pass — Review skipped" is NOT a green
  gate — real round lands post-retarget)
- Force-push fallback: relay via `!` prefix; `gh pr create --head`

---

## Mission

Make `bootstrap --new` produce content + pins + records and verify (or
instruct) two installs — never copy scripts or agents again. Spec F1–F6
is authoritative and carries four absorbed tasks' requirements; their
full source records live in `6-canceled/` (KIT-0078, KIT-0087,
KIT-0081, KIT-0082) — read all four before PR 1.

## Verified anchors (2026-08-08 — re-grep before relying)

- **The door today**: `scripts/local/bootstrap` 1,118 lines;
  `engine-consumer.sh` 1,004 (writes the CLAUDE.md kit-install record —
  it remains the ONLY writer of that record; seeds the four marker
  agents at ~`:592`; first-session region ~`:921`; refuses pyproject to
  planning shape at ~`:294`); `engine-export.sh` 271 (the `git archive`
  copy path — most of what it ships stops shipping).
  `tests/test_setup_door.py` 1,546 lines is the existing behavior net;
  `TestEnvSeedingE2E` is the reuse target for F5's .env invariants.
- **Two absorbed findings verified STILL LIVE today**:
  - `packages/agentive-kit/src/agentive_kit/evaluators.py:520` prints
    `GOOGLE_API_KEY - Gemini evaluators` — the kit standard is
    `GEMINI_API_KEY` (`.env.template`, doctor `20-env-keys`). The wrong
    name survived the KIT-0090 port. Fix in the package (F4 item;
    releases with 0.3.x).
  - `create-project.md:180` and `:317` still instruct
    `pipx install adversarial-workflow` (F3/F2 — dies with whatever
    verdict F2 reaches on that agent).
- **Plugin verification pattern**: `scripts/core/doctor.d/
  50-plugin-source.sh` already reads the local plugin registry (and
  knows the marketplace-must-be-GitHub rule from KIT-0030). The door's
  verify-or-instruct step for the plugin should reuse its detection
  approach, not invent one. The doctor on THIS machine currently
  reports the marketplace not installed — your acceptance runs must
  handle both present and absent states (absent → clear printed
  install instruction, never a hard failure).
- **`agentive` CLI verification**: `command -v agentive` +
  `agentive --version`; absent → print `uv tool install agentive-kit`
  and continue (the KIT-0083 degradation pattern, now house style).
- **KIT-0092 coordination**: if your release lands as agentive-kit
  0.3.x, KIT-0092 (shim removal + preset-guard retightening + monolith
  test shrinkage) rides the SAME release — read its spec; either
  execute it in your PR 3 (closing it by reference) or state in the PR
  body why it ships separately.

## The one rule above all others

This task deletes distribution surfaces. **KIT-0067's lesson is the
governing law: enumerate a file's FUNCTIONS before de-shipping it** —
that incident deleted the operator's daily launcher because the
decision was directory-shaped. F1's per-artifact decision table
(ships-in-repo / package / plugin, with rationale) is not paperwork; it
is the mechanism that prevents launcher-class regressions. The
`.kit/launchers/launch` file itself is an open decision in that table
(KIT-0075 F4 cross-ref — the operator uses it daily; whatever you
decide, it must keep working or improve).

## Test approach

- **PR 1 lands the F5 acceptance test RED against today's door** —
  proving it detects the copies — plus the F4 quick fixes. The KIT-0082
  source record lists the assertions; reuse `TestEnvSeedingE2E`.
  Red-first is the acceptance bar for the test itself (a test born
  green against the old world proves nothing — house falsifiability
  rule).
- **PR 2 flips the door**; the acceptance test turns green; the
  journey replays (F2 — the KIT-0078 record names the transcripts and
  the ev-fast-charging-loads intake) run against the NEW door.
- Full suite per push (door changes touch delegation surfaces —
  TESTING-WORKFLOW rule); evaluator trio before each PR opens;
  disposition tables; deep rounds capped ~2.
- Environmental claims: this handoff's anchors carry their file:line
  sources — re-grep each before building on it; where the spec or the
  absorbed records assert runtime behavior, probe it (the KIT-0080
  inversion lesson).

## Out of scope — do not touch

- Phase 3 (existing-consumer migration — upgrader's spec, next)
- Phase 4 (sync-machinery retirement: `.core-manifest.json`,
  `sync_from_manifest.py` stay untouched even though they look
  adjacent)
- Plugin CONTENT (agent behavior) beyond distribution wiring
- Linear sync, evaluator library contents

---

**Task File**: `.kit/tasks/5-done/KIT-0093-door-package-install-mode.md`
**Absorbed source records**: `6-canceled/KIT-0078-*`, `KIT-0087-*`, `KIT-0081-*`, `KIT-0082-*`
**Evaluation Log**: `.adversarial/logs/KIT-0093-door-package-install-mode--arch-review-fast.md`
**ADR**: `.kit/adr/KIT-ADR-0028-versioned-packages-not-file-copies.md` (Accepted; this is phase 2)
