# KIT-0091 — Evaluator Review Record

**Task**: Port the bash gate surfaces into agentive-kit (phase 1b)
**Branch**: `feature/KIT-0091-port-gate-scripts`
**Ordering**: trio run BEFORE PR open (KIT-0035/KIT-0046 rule).

---

## PR 1 — preflight + ghio (+ markers, shim)

**Input**: `.adversarial/inputs/KIT-0091-code-review-input.md` (10 files, full format)
**Date**: 2026-08-07

| Evaluator | Model | Verdict |
|-----------|-------|---------|
| code-reviewer-fast | gemini-2.5-flash | CONCERNS (0 correctness, 5 robustness) |
| code-reviewer | o3 | FAIL → fixed/refuted, see round 2 below |
| claude-code | claude-sonnet-4-6 | CHANGES_REQUESTED → dispositioned below |

### Disposition table — round 1

| # | Source | Finding | Disposition |
|---|--------|---------|-------------|
| 1 | o3 | Gate 3 false-FAILs when multiple cursor check-runs are all green (multi-line jq output vs whole-string compare) | **FIXED** as documented divergence: bash original had the identical latent bug (and the embedded newline corrupted the GATE line format). Port now applies Gate 2's all-green rule; fail-closed preserved; 2 matrix tests added (all-green PASS, mixed FAIL naming first non-green). |
| 2 | o3 | `ghio.run_gh(capture=False)` raises ValueError (`text=True` without capture) | **REFUTED** empirically: `subprocess.run(["true"], capture_output=False, text=True)` runs clean (verified in-session, Python 3.14). No such ValueError exists. |
| 3 | o3 | Duplicate bot tokens accepted silently (`bots: coderabbit coderabbit`) | **DECLINED** — parity-exact with bash; duplicates change no semantics (declared set is unchanged); dedup would be cosmetic churn on a fail-closed path. |
| 4 | claude-code HIGH/MED | Slug validation regex weaker in `_parse_target_repo` than in `main()` | **DECLINED (comment added)** — both layers are faithful ports (target_repo.sh's shape check + the script's strict charset re-check); the strict check provably runs before GraphQL interpolation (evaluator concedes). Cross-reference comment added so a future refactor cannot silently bypass the strict layer. |
| 5 | claude-code MED | `target.path` from CLAUDE.md used unsanitized (path traversal) | **DECLINED** — parity with bash (`git -C $TARGET_PATH` used the same value raw) and threat model: CLAUDE.md is the trusted project-instruction file; an attacker editing it controls the agent outright, not just this path. |
| 6 | claude-code MED | bots reader first-line-wins vs docstring "last wins" confusion | **FIXED (comment)** — first-wins is deliberate (bash `head -1`); comment added distinguishing it from flag parsing. |
| 7 | claude-code MED | `cli.py` `return` after `preflight.main()` looks like a swallowed exit | **FIXED (comment)** — exit codes propagate via SystemExit (evaluator confirmed); unreachable-return comment added. |
| 8 | claude-code LOW | `fetch_ok` sticky across poll attempts non-obvious | **FIXED (comment)** — stickiness is intended (one success proves connectivity); comment added. |
| 9 | claude-code LOW | `_parse_args` errors split stdout/stderr inconsistently | **DECLINED** — byte-for-byte parity with bash (which sent `--repo` errors to stderr and the rest to stdout); matrix asserts the streams. |
| 10 | claude-code LOW | NOTICE lines on stdout alongside GATE lines | **DECLINED** — parity; evaluator itself marks acceptable. |
| 11 | fast | `cli.py` unguarded `from agentive_kit import preflight` | **DECLINED** — sibling module of the same installed dist; consistent with the existing top-level `lifecycle` import. |
| 12 | fast | `_first_nonempty_file` swallows OSError silently | **DECLINED** — parity: bash `find ... 2>/dev/null` was equally silent on unreadable candidates. |
| 13 | fast | Invalid `PREFLIGHT_CI_POLL_DELAY` silently falls back | **DECLINED** — test-seam variable; fail-safe default; a NOTICE would pollute the machine-parsed stdout contract. |
| 14 | fast | Shim not-installed error goes to stdout | **DECLINED** — consistent with `scripts/core/project`'s identical error and with the bash script's stdout ERROR convention. |
| 15 | fast | GATE detail may contain colons | **DECLINED** — inherent to the inherited contract (details have always contained colons); consumers parse with the 4-field split/regex. |

### Round 2 — code-reviewer re-run after fixes (deep rounds capped at 2)

See "Round 2 verdict" appended below.

**Full logs**: `.adversarial/logs/KIT-0091-code-review-input--code-reviewer-fast.md`,
`--code-reviewer.md`, `--claude-code.md` (regenerated per run; round-1
verdicts summarized above).
