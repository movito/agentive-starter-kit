## KIT-0032 — Build the `upgrader` Agent (PR #56)

**Date**: 2026-06-27
**Agent**: feature-developer-v6 (claude-opus-4-8)
**Mode**: single-repo (planning-repo exception — `**Target Codebase**: This repo`)
**Scorecard**: 7 threads, 0 regressions, 4 fix rounds, 6 commits

### What Worked

1. **Inline `ScheduleWakeup` polling (Phase 6)** — never busy-waited through CI or
   bot scans. Cache-aware delays (270s while warm, holding commits to bundle with
   in-flight scans) kept the loop cheap across ~8 wake-ups.
2. **Verify-before-believing caught three false findings** — o3's two "break-now"
   bugs (`tools:` lists Claude tools not shell binaries; "indented `model:`")
   evaporated on a 10-second grep, and claude-code's "`claude-sonnet-4-6` is a
   typo" was the very staleness the agent fixes. Declining these with evidence
   avoided pointless churn.
3. **Full-file-context evaluator input** — feeding the whole agent + the guide it
   automates let the trio find real consistency bugs a diff would have hidden: the
   `! git push` exit-code footgun and the Phase 2a run-vs-reason contradiction.
4. **Root-causing the phantom Black failure** instead of "fixing" formatting — the
   markdown-only change could not have broken Black; chasing it to a stale `.venv`
   (Black 23.12.1 vs pinned 26.x) avoided a bogus edit to an unrelated test file.

### What Was Surprising

1. **Stale-venv Black drift produced a phantom CI failure** on a zero-Python
   change. `black --check .` (system 26.1.0) was clean while `ci-check.sh` (venv
   23.12.1) failed on `tests/test_pattern_lint.py` — a confusing, time-consuming
   split until the venv version was compared.
2. **Bot follow-on cascades** — each wording fix spawned the next finding: Phase 8
   "N versions behind" → Phase 3/7 normalization+reconcile consistency. Four review
   rounds for a single documentation file, all valid, none regressions.
3. **`ANTHROPIC_API_KEY` was commented out in `.env`**, silently blocking the third
   evaluator until the operator uncommented it mid-session — the trio ran 2-of-3
   first, then completed.
4. **preflight Gate 1 flapped on timing** — it reported "no CI runs found" twice
   immediately after a push, before GitHub registered the runs; both were false
   alarms, not failures.

### What Should Change

1. **Guard against venv tool-version drift** — `ci-check.sh` could warn when local
   `black --version` differs from the `pyproject.toml` pin, turning a confusing
   phantom failure into a one-line "your venv is stale, reinstall dev extras."
2. **Surface `ANTHROPIC_API_KEY` for the evaluator trio** — onboarding / Phase 7
   docs should note the `claude-code` evaluator needs it uncommented, so it isn't
   discovered as a mid-run blocker.
3. **For doc-heavy deliverables, run the evaluator trio (Phase 7) before opening
   the PR** — the evaluator-driven rewrites here each triggered fresh bot rounds;
   doing Phase 7 first would collapse several bot cycles into one.
4. **preflight should distinguish "CI pending/unregistered" from "CI failed"** —
   a timing guard (or a short re-poll) would stop Gate 1 from reading as a failure
   seconds after a push.

### Permission Prompts Hit

None. All `git`, `gh`, `./scripts/*`, and `adversarial` calls were already covered
by `.claude/settings.json`. (`ADVERSARIAL_UNATTENDED=1` was needed for large-input
auto-confirm, but that is an env flag, not a permission prompt.)

### Process Actions Taken

- [ ] Add a venv Black-version-drift warning to `ci-check.sh` (local vs pinned)
- [ ] Document the `claude-code` evaluator's `ANTHROPIC_API_KEY` requirement in onboarding / Phase 7
- [ ] Evaluate running Phase 7 (evaluator trio) before PR open for doc-heavy tasks
- [ ] preflight Gate 1: distinguish "CI not yet registered" from "CI failed"
- [ ] File guide follow-up: harden the brittle greps in `docs/PLUGIN-UPGRADE-GUIDE.md` (agent mirrors them; guide wins)
