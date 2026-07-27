# KIT-0071 — Evaluator Review Record

**Task**: Worktree provisioning correctness (F1–F7)
**Date**: 2026-07-27
**Input**: `.adversarial/inputs/KIT-0071-code-review-input.md`
(full-file context, base `origin/main`, commit `86d2e0c`)
**Ordering**: trio run BEFORE PR open (KIT-0035/KIT-0046 rule). This
is a code+doc mixed diff — the normal ordering applies, NOT the
prose-sweep exception.

## Verdicts

| Evaluator | Verdict | Log |
|-----------|---------|-----|
| code-reviewer-fast (gemini-2.5-flash) | CONCERNS | `.adversarial/logs/KIT-0071-code-review-input--code-reviewer-fast.md` |
| code-reviewer (deep) | FAIL | `.adversarial/logs/KIT-0071-code-review-input--code-reviewer.md` |
| claude-code | APPROVED | `.adversarial/logs/KIT-0071-code-review-input--claude-code.md` |

`git status` clean after every run (no evaluator mutations).

## Triage — every finding reproduced or refuted

1. **fast: empty `project_name` in worktree Serena config passes
   silently** — CONFIRMED. Fixed: unnamed config now WARNs
   (`no name/project_name`); test `test_serena_unnamed_config_warns`.
2. **fast: `new-worktree.sh` pre-existence guard untested** —
   DECLINED (out of scope): the guard predates this PR (KIT-0068
   A69); this diff does not touch that path, and the helper has no
   shell test harness (it fetches origin). Noted for a future task if
   the helper grows one.
3. **deep: collision detector ignores the `name:` key** — CONFIRMED
   against `scripts/core/project:429` (the reconfigure reader accepts
   `name:` OR `project_name:`). Fixed: `serena_name()` now mirrors the
   Python reader (both keys, first non-empty wins, surrounding-quote
   strip only); test `test_serena_short_name_key_collision_detected`.
4. **deep: symlink guard misses legacy `venv/`, `--force` would
   rm -rf the primary through it** — REFUTED with reproduction:
   `cmd_setup` only ever manages `.venv` (`venv/` is never rebuilt or
   removed by it), and `shutil.rmtree` on a symlink refuses outright
   with `[Errno None]` — the exact KIT-0065 symptom, proving rmtree
   cannot follow the link. The claimed destruction path does not
   exist. The doctor-side kernel of value kept: the check now also
   WARNs on a symlinked `venv/` (the alternate layout
   40-version-skew supports); test
   `test_alternate_venv_layout_symlink_warns`.
5. **deep: quote-stripper mangles apostrophes** — CONFIRMED (minor):
   `sed "s/[\"']//g"` stripped internal apostrophes, enabling a
   false collision between `operator's-toolkit` and
   `operators-toolkit`. Fixed by the same rewrite as (3); test
   `test_serena_apostrophe_name_not_mangled`.
6. **deep: GIT_COMMON_DIR survives when the check is *sourced*** —
   REFUTED for the actual execution model: the doctor driver executes
   checks as subprocesses (never `source`), and bash `unset` removes
   exported variables from the environment of every child the check
   spawns. `compgen -A variable | grep '^GIT_'` matches
   `GIT_COMMON_DIR`. Belt added anyway: hostile-env test now covers
   `GIT_COMMON_DIR` (`test_hostile_git_common_dir_cannot_redirect_audit`).

## Known blind spots / not executed

- The Serena `activate_project("<absolute path>")` LAUNCH advice is
  codified from KIT-0069's in-session verified fix; it was not
  re-executed here (no Serena use this session).
- The fresh-worktree demo invoked the checkout's own `project setup`,
  which is origin/main's copy until this PR merges — the old copy
  ignores `--no-hooks` (its hook install attempt failed
  non-critically). Post-merge provisioning uses the new script.
