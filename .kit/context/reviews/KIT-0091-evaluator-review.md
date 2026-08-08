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

**Verdict**: FAIL (o3). Dispositioned below; per the Oscillation
protocol this is the final deep round — remaining verdict-weight rests
on the dispositions, the parity matrix, and CI/bots.

| # | Finding | Disposition |
|---|---------|-------------|
| R2-1 | CRLF line endings break `## Target Repository` header matching | **FIXED — real parity bug**: bash `awk /...[[:space:]]*$/` swallowed a CR; the port's `[ \t]*$` did not. `\r?` added; CRLF + LF unit tests in tests/agentive_kit/test_preflight_pkg.py. Writing those tests ALSO exposed a second real port bug the matrix cannot see (cross-repo is not harness-modeled): the bullet-value regex let `[^`]*` cross newlines, capturing garbage between bullets — bullet parsing is now per-line, mirroring sed exactly. |
| R2-2 | Negative `PREFLIGHT_CI_POLL_DELAY` reaches `time.sleep` → ValueError | **FIXED**: clamp extracted into `_poll_delay()` (non-numeric → default, negative → 0), unit-tested on all four edges. |
| R2-3 | `target.path` path traversal | **DECLINED — repeat** of round-1 finding #5 (same disposition: bash parity, CLAUDE.md is the trusted agent-instruction file). |
| R2-4 | `run_gh(capture=False)` stdout is None | **DECLINED — morph** of the round-1 refuted ValueError claim; no caller passes capture=False. run_gh docstring now states the constraint. |
| R2-5 | No test for duplicate bot tokens | **FIXED (test only)**: matrix scenario pins duplicate-token semantics (no NOTICE, declared set unchanged) against reader drift. |

---

## PR 2 — review_input + worktree + target_repo + F5 (+ shims, 0.2.0)

**Input**: regenerated via the freshly-shimmed `prepare-review-input.sh`
(its first production run), `--base feature/KIT-0091-port-gate-scripts`
(16 files). **Date**: 2026-08-07.

| Evaluator | Model | Verdict |
|-----------|-------|---------|
| code-reviewer-fast | gemini-2.5-flash | CONCERNS |
| code-reviewer | o3 | FAIL → 1 real fix, 2 refuted, 3 declined |
| claude-code | claude-sonnet-4-6 | 14 findings → 1 hardening fix, rest dispositioned |

### Disposition table — PR 2 round 1

| # | Source | Finding | Disposition |
|---|--------|---------|-------------|
| 1 | o3 | `resolve_primary_root` `.resolve()` collapses symlinked primaries to physical paths | **FIXED — real parity divergence**: bash `cd`+`pwd` kept the LOGICAL path (plain pwd prints $PWD), despite its own comment claiming physical. `.resolve()` dropped; symlinked-primary test added (worktree lands beside the logical parent). |
| 2 | o3 | helper `threads` GraphQL has unbalanced braces | **REFUTED empirically**: all three query builders (threads, summary, preflight) count to balance 0 (verified in-session). The stub-blindness concern is fair; the count was wrong. |
| 3 | o3 | `_looks_binary` labels unreadable files binary | **DECLINED — parity**: bash `grep -Iq . file 2>/dev/null` fails on unreadable files and classified them binary identically. |
| 4 | o3 | reply body allows shell injection via backticks/`$()` | **REFUTED**: no shell exists anywhere on the path — ghio uses `subprocess.run` with list args (`shell=False`), and the bash original quoted `-f body="$body"` too. |
| 5 | o3 | `../` rename paths escape the project root | **DECLINED**: git repo-relative paths cannot contain `..` (git refuses to track them), and bash joined `$TARGET_PATH/$file_path` equally unchecked. |
| 6 | o3 | `target_repo` warning fires on every worktree (`not`-precedence claim) | **REFUTED**: `not X and not Y` parses as `(not X) and (not Y)` — warn only when NEITHER exists; the passing cross-repo parity test (a `.git` dir target, no warning) is the evidence, and a `.git` FILE satisfies `is_file()`. |
| 7 | claude-code MED | helper interpolates OWNER/NAME into GraphQL with only the loose shape check | **FIXED as documented divergence**: bash had the same exposure; the port now applies preflight's strict charset validation (KIT-0043) to every slug before any query string; refusal test added. |
| 8 | claude-code MED | target.path traversal | **DECLINED — repeat** of the PR 1 disposition (trusted CLAUDE.md, bash parity). |
| 9 | claude-code MED | raw content in output markdown | **DECLINED — parity**: bash `cat`'d raw; the 4-backtick fence is the containment, pinned by the fence-integrity test. |
| 10 | claude-code LOW ×5 | shim env vars, symlink refs, base_branch to git, worktree anchor env, sys.path insert | **DECLINED**: all are list-arg subprocess paths (no shell); the shim sets its own env vars immediately before exec; an attacker controlling env already controls PATH/python3. |
| 11 | fast | `_file_section` trailing newline | **REFUTED**: content gets `\n` appended when missing (both diff and file blocks). |
| 12 | fast | empty `--base=` / `--format=` untested | **FIXED (tests)**: both refusal edges added to the matrix. |
| 13 | fast | `_git_out` hides git stderr | **REFUTED**: it re-emits captured stderr on failure by design. |
| 14 | fast | `_detect_helper_repo` empty-slug handling | **DECLINED — already handled**: empty slug exits 2 with the gh-repo-set-default remedy (same as bash). |

### PR 2 round 2 — deep re-run after fixes (cap reached)

**Verdict**: FAIL (o3) — all five findings refuted or parity-declined;
per the Oscillation protocol this closes the deep rounds, and the
verdict-weight rests on the dispositions, the three parity matrices,
and CI/bots.

| # | Finding | Disposition |
|---|---------|-------------|
| R2-1 | Indented CLAUDE.md bullets not parsed ("legacy sed matched `[[:space:]]*-`") | **REFUTED — misquotes the source**: lib/target_repo.sh's sed patterns are column-0 anchored (`^- \*\*GitHub\*\*`), no whitespace tolerance; the port matches the real grammar exactly. |
| R2-2 | Backtick in filename corrupts the `### Source:` header | **DECLINED — parity**: bash emitted the identical header (`echo "### Source: \`$file_path\`"`). |
| R2-3 | `~` in target Path not expanded | **DECLINED — parity**: bash used quoted `"$TARGET_PATH"` — no tilde expansion there either; same failure mode. |
| R2-4 | GraphQL braces unbalanced (repeat, new confabulated detail: "two repository opens") | **REFUTED — second empirical pass**: run_gh mocked at the boundary, actual sent queries captured — threads 8 opens/8 closes, summary 5/5, both exit 0. The repeat of a refuted finding with shifting details is the oscillation the protocol caps. |
| R2-5 | Windows symlink privilege breaks provisioning | **DECLINED — parity + platform scope**: bash `ln -s` had the identical constraint; the kit targets macOS/Linux sessions (WORKTREE-WORKFLOW). |

**Full logs**: `.adversarial/logs/KIT-0091-code-review-input--*` (regenerated per run; verdicts summarized above).
