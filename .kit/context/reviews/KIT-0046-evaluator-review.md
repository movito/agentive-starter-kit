# KIT-0046 — Adversarial Evaluator Review

**Date**: 2026-07-14
**Input**: `.adversarial/inputs/KIT-0046-code-review-input.md` (full-file, 19 files)
**Ordering**: code-dominated task — trio ran after PR open (#77), in parallel with the bot round
**Post-run `git status`**: clean after all three runs (adversarial-workflow 1.0.1, aider-free — no working-tree mutations, unlike the KIT-0044 incident)

| Evaluator | Model | Verdict |
|-----------|-------|---------|
| code-reviewer-fast-v2 | gemini-3-flash-preview | CONCERNS |
| code-reviewer | o3 | FAIL |
| claude-code | claude-sonnet-4-6 | APPROVED |

Raw logs: `.adversarial/logs/KIT-0046-code-review-input--*.md`

## Disposition — accepted (fixed in the batch commit)

| # | Finding (source) | Fix |
|---|------------------|-----|
| 1 | **Duplicate-key false-fail**: commented template line before the real key returns "commented" on first match (o3, blocker — **reproduced before fixing**: `DOCTOR:env-keys:FAIL` on a template+real .env) | `key_state` scans the whole file; present wins over commented; regression test |
| 2 | **Push-trigger grep tied to two-space indent** silently SKIPs on other formats (o3, blocker) | Regex now matches block style at any indent, flow style (`on: [push,…]`), and scalar (`on: push`); 4 parametrized style tests + commented/parked cases. Errs toward checking, never toward SKIP |
| 3 | **GIT_DIR leak can blind the checks** — incl. the core-bare canary itself (fast-v2, high) | Driver scrubs `GIT_*` from every check's env; `70-core-bare.sh` also unsets locally (standalone runs); hostile-GIT_DIR decoy-repo test proves the canary can't be redirected |
| 4 | **grep-over-JSON PR-number extraction** (convergent: all three evaluators) | `gh pr list --json number --jq '.[0].number // empty'` |
| 5 | **PASS-then-crash masks lost concerns** (fast-v2) | Driver synthesizes an extra FAIL when a check exits non-zero after emitting lines; test |
| 6 | **tomllib absent on bare 3.10 → drift silently SKIPped** (o3) | `tomli` fallback, then regex scan of the pin string as last resort |
| 7 | **`export KEY=` unrecognized** (fast-v2) | Supported + test; spaces-around-`=` stays strict per claude-code's own analysis, now documented in the docstring |
| 8 | **black version regex unanchored** (claude-code) | Anchored to `black[,\s]+` |
| 9 | **Stray files in doctor.d (.DS_Store) cause spurious FAILs** (claude-code) | Dotfiles skipped by the driver; test. Non-dot stray files still FAIL by design (contract) |
| 10 | **verify-setup shim lacks set -e** (claude-code) | `set -euo pipefail` added |
| 11 | **gh-auth negative paths untested** (o3) | PATH-stub tests: missing gh → FAIL, unauthenticated → FAIL |

## Disposition — declined (with evidence)

| # | Finding (source) | Why declined |
|---|------------------|--------------|
| 12 | `wc -l` leaves a newline in `COUNT` breaking the PASS line (o3) | **Disproven live**: `COUNT=$(ls … \| wc -l \| tr -d ' ')` → `COUNT=[6] len=1` — command substitution strips trailing newlines by definition |
| 13 | Driver output flood from a misbehaving check (o3) | Speculative for kit-authored checks; the 30s timeout bounds runtime; buffering a pathological check's output is not a correctness issue |
| 14 | `--dir <path>` space form unsupported (o3) | Documented contract is `--dir=`; the space form exits 3 with usage printed — exactly the F3 "driver/usage error" path, loud and instructive |
| 15 | `KEY = value` (spaces around `=`) unrecognized (fast-v2) | Working as intended — standard .env parsers reject it too; claude-code's review independently reached the same conclusion; now documented in the docstring |
| 16 | Check stderr passthrough could leak sensitive data (claude-code) | Reviewer's own remediation: "No code change needed" — check-author contract, noted in the driver docstring's read-only clause |
| 17 | `ls \| wc` count inflated by filenames with newlines (claude-code) | Cosmetic count in a PASS detail; existence/non-emptiness already decided the verdict |
| 18 | `--limit 1` returns most-recently-updated PR, old PR possible (claude-code) | Acknowledged by the reviewer as acceptable per the WARN-max design |

## Notes

- o3's FAIL verdict rested on findings 1 and 2 — both real, both reproduced/accepted, both fixed with regression tests. The verdict did its job.
- Three-way convergence on finding 4 (grep-over-JSON) — the convergence-counting rule from REVIEW-INSIGHTS applied within a single round.
