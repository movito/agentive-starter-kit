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
