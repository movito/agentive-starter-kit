# KIT-0048 — Adversarial Evaluator Review

**Date**: 2026-07-14
**Input**: `.adversarial/inputs/KIT-0048-code-review-input.md` (full-file, 17 files)
**Ordering**: trio ran BEFORE PR open (the KIT-0046-widened rule — now all tasks)
**Post-run `git status`**: caught one real anomaly — not an evaluator mutation, but my own incomplete re-staging after the GIT_DIR incident reset (the KIT-0027 deletion had been lost; fixed in `5cabcdc`). The rule pays for itself in a way nobody predicted.

| Evaluator | Model | Verdict |
|-----------|-------|---------|
| code-reviewer-fast-v2 | gemini-3-flash-preview | CONCERNS |
| code-reviewer | o3 | FAIL |
| claude-code | claude-sonnet-4-6 | CHANGES_REQUESTED |

## Disposition — accepted (fixed pre-PR)

| # | Finding (source) | Fix |
|---|------------------|-----|
| 1 | **Non-zero kit_markers exit silently read as "no region"** — a crashed reader would silently fall back to single, violating fail-loud (o3, the FAIL driver) | rc≠0 now distinguishes the documented "region not found" stderr (absent → single) from every other failure (→ `DOCTOR:shape-record:FAIL` + full set); crashing-reader test |
| 2 | **Empty `# shapes:` header → empty set → check skipped in EVERY shape forever** (o3) | Empty declaration → run everywhere; test. Fixing this exposed a second bug: `\s*` in the regex slurped the newline and captured the next line as tokens — horizontal-whitespace class now |
| 3 | **Case-sensitive header** (o3) | `re.IGNORECASE`; test with `# SHAPES:` |
| 4 | **600-byte header window** misses declarations after long banners (o3 + claude-code convergent) | First 30 lines scanned; 20-line-banner test |
| 5 | **Heredoc injection via `--target-path`/`--target-github`** — `$(...)` in operator values would shell-execute when written to CLAUDE.md (claude-code, HIGH) | All value-carrying writes now `printf '%s'`; hostile-value test proves `$(touch …)` lands literally and executes nothing |
| 6 | **`--target-github` format unvalidated** (claude-code) | `owner/repo` regex (the preflight slug pattern); rejection test |
| 7 | **IFS could affect the GIT_* scrub loop** (claude-code, part of its compgen finding) | `IFS=$' \t\n'` reset at script top |

## Disposition — declined (with evidence)

| # | Finding (source) | Why declined |
|---|------------------|--------------|
| 8 | ARG_MAX exceeded by thousands of GIT_* vars (fast-v2) | Speculative scale; no environment ships thousands of GIT_ vars; the loop is the shipped 70-core-bare pattern |
| 9 | `_doctor_shape` timeout → full set + FAIL is "confusing" (fast-v2) | Working as specified — F3's accepted evaluation finding IS "malformed/unreadable = full set + fail loud, never silently fall back" |
| 10 | `python3` vs `sys.executable` version mismatch (fast-v2 + claude-code) | N2 pins the requirement (system python3 ≥ 3.11); `sys.executable` is correct for driver-spawned subprocesses — the driver and reader must agree, and do |
| 11 | `# shapes:` false positive on doc strings (fast-v2) | Requires a line-anchored `# shapes:` comment above the real header within 30 lines — convention places the header at line 2; first-match wins |
| 12 | `compgen` not POSIX-portable (claude-code, HIGH) | Script is `#!/usr/bin/env bash` by shebang; compgen is a bash builtin; POSIX sh is out of contract (and the same pattern shipped in 70-core-bare.sh, KIT-0046) |
| 13 | Test references "undefined BASH" (claude-code) | Module-level names resolve at call time, not def time; the suite passes 114/114 — empirically defined |
| 14 | Manifest timestamp sensitivity in the identity test (claude-code) | The planning manifest heredoc has a FIXED `synced_at` constant — byte-identical across runs by construction |
| 15 | Session fixture mutates os.environ without monkeypatch (claude-code) | monkeypatch is function-scoped and cannot serve a session fixture; explicit save/restore is the standard pattern |
| 16 | Hardcoded core_version in planning manifest (claude-code) | Mirrors the existing consumer-manifest precedent (2.0.0, unchanged since KIT-0033); `project sync` updates it |

## Incident note (for the retro)

Between the feature commit and this review, the **KIT-0043-class GIT_DIR
corruption recurred and was root-caused**: a class-scoped fixture in the
new test module escaped the function-scoped conftest GIT_* isolation
under the pytest-fast pre-commit hook; bootstrap's git calls hit the real
worktree repo (scaffold commit onto the feature branch, `core.bare`
flipped on the primary). Recovered (branch reset, config restored) and
closed with three layers (session-scoped conftest scrub; scrubbed helper
envs; bootstrap scrubs GIT_* itself + `-e .git` worktree guard), verified
by re-running the suite under the exact hostile GIT_DIR. This pins the
vector KIT-0043 never conclusively identified.
