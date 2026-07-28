# KIT-0046 Review Starter — `project doctor` (ADR-0027 P4)

**PR**: https://github.com/movito/agentive-starter-kit/pull/77
**Branch**: `feature/KIT-0046-project-doctor` (worktree: `../ask-worktrees/KIT-0046`)
**Task**: `.kit/tasks/4-in-review/KIT-0046-project-doctor.md`
**Date**: 2026-07-14
**Agent**: feature-developer-f5 (third worktree session)

## What shipped

| Req | Deliverable |
|-----|-------------|
| F1 | `cmd_doctor` driver in `scripts/core/project` — iterates `doctor.d/` without short-circuiting; strict 4-field `DOCTOR:<name>:<verdict>:<detail>` records (mirrors `GATE:`); `--dir=`/`--root=` seams (empty values are usage errors); GIT_* scrubbed from check env; dotfiles skipped; crash-after-output synthesizes FAIL; `TODO(P2)` per-shape seam |
| F2 | Eight checks, each citing its incident: gh-auth (backbone-first), env-keys (never prints values; present-wins scan; quote/comment normalization), evaluators, venv-skew + black-pin (activation-proof system probe, .venv/+venv/ layouts, tomli/regex fallback; isort deliberately unchecked), plugin-source (hardened guide grep), push-sync-token (on:-block-scoped, comment-tolerant, style-complete; SKIPs while parked → KIT-0045), core-bare (full GIT_* scrub incl. GIT_CONFIG_* override; resolves primary via git-common-dir), bot-presence (WARN-max; quota recorded not-checkable) |
| F3 | Exit contract: 0 ok / 1 fail / 2 warn-only / 3 driver-or-usage error |
| F4 | Retro skill: Incident Closure lifecycle rule (doctor check \| not-checkable note \| triage-guide entry) |
| F5 | `verify-setup.sh` → deprecation shim; **exit contract changes 0/1 → 0/1/2/3**; removal filed as KIT-0047 (backlog) |
| — | Core scripts **3.2.0**; manifest +8 `doctor.d/` entries, count tests updated |

## Review state

- **CI**: green. **CodeRabbit**: approved. **BugBot**: pass, no findings.
- **Threads**: 17 over 6 rounds — **all real, zero noise, all fixed** (round 1: dup-key + black-pin-3.10 [evaluator-convergent] + `--dir` resolve + DK comment, backlog-placement declined with precedent; round 2: quoted-empty values, TOML comment fallback, on:-block awk scoping, full GIT_* scrub + GIT_CONFIG_* override proof, strict 4-field records; round 3: trailing-comment triggers; round 4: **activated-venv skew masking** [real design gap], venv/ layout, on:-line comment; round 5: combined-matrix test; round 6: empty-flag cwd degeneration, version assertions)
- **Evaluators** (trio ran in parallel with round 1): fast-v2 CONCERNS / **o3 FAIL** / claude-code APPROVED — 11 accepted (o3's dup-key blocker **reproduced live before fixing**), 7 declined with pasted evidence (2 o3 claims disproven). Disposition: `.kit/context/reviews/KIT-0046-evaluator-review.md`
- **Tests**: 63 in `tests/test_doctor.py` (driver contract, env/skew/core-bare/push-sync/gh-auth fixtures, hostile-GIT_DIR decoy, GIT_CONFIG override, activation-masking)
- **Real runs**: 7 pass / 0 fail / 2 skip from the worktree AND via `--root=` against the primary (4.7s, N2 met). During the session the bot-presence check correctly emitted a transient WARN while CodeRabbit was mid-re-review — the WARN-max design observed live.

## Reviewer attention points

1. `scripts/core/` syncs downstream — consumers receive doctor via `project sync` once 3.2.0 lands
2. `verify-setup.sh` exit-contract change (0/1 → 0/1/2/3) — downstream callers scripting binary exits need review at sync time
3. `awk` is now a check dependency (60-push-sync-token) — POSIX-standard, but note it
4. Driver home is Python-in-`project` (CLI-layer conventions) rather than a shell driver — stated rationale: verdict aggregation + arg parsing + env scrubbing are cleaner in Python, and the checks themselves stay shell/stdlib

## Post-merge planner actions

- `git worktree remove ../ask-worktrees/KIT-0046` (plain remove — created after the .gitignore symlink fix)
- `./scripts/core/project complete KIT-0046`; delete branch
- Retro: `.kit/context/retros/KIT-0046-retro.md` (first retro using the Incident Closure section)
