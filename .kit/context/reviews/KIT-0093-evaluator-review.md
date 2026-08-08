# KIT-0093 — Evaluator review record

## PR 1: scaffold acceptance test RED + F4 quick fixes

**Date**: 2026-08-08
**Input**: `.adversarial/inputs/KIT-0093-code-review-input.md` (full format, 5,782 lines — diff + full contents of changed files, so the evaluators also saw ~2,800 pre-existing lines of `scripts/core/project`)
**Trio**: code-reviewer-fast (FAIL) · code-reviewer (FAIL) · claude-code (APPROVED)
**Logs**: `.adversarial/logs/KIT-0093-code-review-input--{code-reviewer-fast,code-reviewer,claude-code}.md`

### Disposition table

| # | Evaluator | Finding | Disposition |
|---|-----------|---------|-------------|
| 1 | fast | `--ref` value not validated in `scripts/core/project` install-evaluators fallback (no `_is_tag_like`) | CONFIRMED, pre-existing, out of diff (this PR changed one print line in that file). The canonical package implementation HAS the validation (`evaluators.py:_is_tag_like`); the legacy inline copy is recorded duplication that retires with the script (ADR-0028 phase 3). Not fixed here. |
| 2 | fast | `git rev-parse` not wrapped in try/except in the same fallback | Same as #1 — pre-existing legacy divergence, canonical copy handles it, dies with the shim. |
| 3 | fast | Intake branch check only handles `master`, silent on `dev` etc. | ACCEPTED — fixed: any non-main/non-master branch now routes to "ask the user; never silently rename". |
| 4 | fast | `gh repo create` generic failures read as deferral | Pre-existing instruction text, untouched by this diff. Declined here; candidate for a later intake polish. |
| 5 | fast | `_referenced_paths` extension filter too narrow | ACCEPTED — broadened to `md/json/yaml/yml/sh/py`. Extensionless refs (e.g. `.kit/launchers/launch`) stay out: that file's fate is PR 2's decision table. |
| 6 | fast | `_is_placeholder` could mask a real file named `*-XXXX-*` | Declined — no such file exists or is plausible in the kit's naming scheme; documented heuristic. |
| 7 | fast | Contract-string assertions brittle to rewording | Declined by design — the door's printed lines ARE a contract (`displayed_commands_are_contracts`); the test is the contract's origin and PR 2 implements to it. |
| 8 | fast | `test_no_copied_agent_bodies` only checks `*.md` | Declined — agent/skill/command bodies are `.md` by definition; non-md `.claude/` content (settings.json) is a PR 2 decision-table row, not a copy-of-agent-bodies question. |
| 9 | deep | **Headline FAIL**: runtime allegedly reads `GOOGLE_API_KEY`, so the rename breaks Gemini | **REFUTED against the tree**: every installed evaluator declares `api_key_env: GEMINI_API_KEY` (`.adversarial/evaluators/google/*/evaluator.yml`) and the adversarial CLI resolver maps `gemini → GEMINI_API_KEY` (`resolver.py:118`). `GOOGLE_API_KEY` in the installer tail was the misnomer (KIT-0081 F4); the fix direction is correct. Classic verify-before-believing catch. |
| 10 | deep | Package/legacy text duplication risks re-divergence | Known, recorded duplication (`scripts/core/project` header notes it); retires with the script in phase 3. Declined. |
| 11 | deep | No test asserts the key-name happy path | Declined — key-name membership is pinned by `doctor.d/20-env-keys.py` (`RECOMMENDED_KEYS`) and its tests; an install-then-evaluate integration test would spend real API keys in CI. |

### Verdict handling

claude-code APPROVED. Both FAIL verdicts rest on findings triaged above: the deep FAIL's sole correctness claim is refuted with tree evidence (#9); the fast FAIL's correctness claims are pre-existing out-of-diff legacy code (#1/#2) plus the intake wording gap, which is fixed (#3). Deep rounds capped at 1 — no re-run needed: the two accepted fixes are test-scope and agent-doc wording, both re-verified locally (module green, 14 passed / 12 strict-xfail unchanged).

---

## PR 2: the door switch (packaged-install mode)

**Date**: 2026-08-08
**Input**: `.adversarial/inputs/KIT-0093-code-review-input.md` (full format, 12,146 lines, base = PR 1 head)
**Trio**: code-reviewer-fast (CONCERNS) · code-reviewer (findings list) · claude-code (CHANGES_REQUESTED)

### Disposition table (round 1)

| # | Evaluator | Finding | Disposition |
|---|-----------|---------|-------------|
| 1 | deep+claude | `agentive install-evaluators` wrapper masks failures with `sys.exit(0)` | **REFUTED against the tree**: every failure path in `cmd_install_evaluators` calls `sys.exit(1)` (grep: 8 sys.exit sites; returns only on success/no-op), so SystemExit propagates through the wrapper — identical to the legacy dispatcher's pattern at `scripts/core/project:2501`. |
| 2 | deep | sed pin extraction breaks on quoted values with trailing comments | **REFUTED empirically**: the smoke scaffold's config.yml carries `adversarial_cli_version: "1.0.1"` / `evaluator_library_version: "v0.10.0"` extracted from the kit's real quoted+commented lines. Shape-gates added anyway (see accepted #5). |
| 3 | deep | bots duplicate line when record uses commas | REFUTED by trace: `EXISTING_BOTS` sed captures the full value regardless of commas (non-empty), `_canon_bots` normalizes both sides. Also pre-existing code, untouched here. |
| 4 | fast+deep | README heredoc interpolates unsanitized `PROJECT_NAME` (backticks/`$()` execute in the expanding heredoc) | **ACCEPTED — fixed**: name+prefix stripped of backticks/$/quotes/newlines before heredoc use (fill_env_identity precedent); hostile-name e2e regression test added (PWNED probes + README/state assertions). |
| 5 | claude | validate extracted pins before writing them into scaffolds | ACCEPTED — fixed: CLI pin must start with a digit, library pin must be tag-charset-only; malformed captures fail loud at scaffold time. |
| 6 | deep | doctor checks trust `-x scripts/core/project`; exec-bit-less copies get the agentive remedy | Declined — `-x` is the standard probe; the agentive remedy still works globally (degradation, not a dead end). |
| 7 | deep | `fill_env_identity` temp-file leak on disk-full | Pre-existing KIT-0084 code, untouched; temp lives inside `.git/` via mktemp — not a predictable path. Declined. |
| 8 | fast | unreadable-but-present pyproject silently skips the black-pin preflight | Pre-existing warn-never-fail design of that preflight; an unreadable pyproject fails the Black step loudly one step later. Declined. |
| 9 | fast | linear_sync task-ID edge-case tests missing | Comment-only change to that file in this PR. Declined. |
| 10 | deep | 55-worktree remedy misleads inside packaged-repo worktrees | REFUTED by read: the remedy keys on the DIAGNOSED root's own `scripts/core/project`; a packaged worktree takes the plain-venv branch. |

### Verdict handling (round 1)

The two verdict-driving claims (#1, #2) are refuted with tree/empirical evidence; the two accepted hardenings (#4, #5) are fixed and covered by a new e2e test. Deep rounds capped at 2 per the handoff; round 2 not spent — the remaining findings are declines with recorded rationale.
