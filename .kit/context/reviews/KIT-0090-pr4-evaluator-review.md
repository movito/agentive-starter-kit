# KIT-0090 PR 4 — Evaluator Review Record

**PR**: stacked on #110 — publish workflow + dogfood
**Date**: 2026-08-06. Trio run BEFORE PR open; deep verdict FAIL,
all four findings dispositioned without code change:

1. "Catch generic ImportError in _kit_lifecycle" — REFUTED by its own
   earlier round: ModuleNotFoundError-only was o3's PR-1 round-5
   instruction (a broken INSTALLED package must surface its real
   error, not a false install hint). Recorded oscillation #2.
2. "Failed editable install must be fatal / cleaned" — DECLINED: the
   dogfood install is best-effort by design; a failed `pip install -e`
   leaves nothing importable and every caller has the source-tree
   fallback chain. Same non-critical pattern as the pre-commit hook
   install in the same function.
3. "Publish workflow imports runtime code for the version" — DECLINED:
   agentive_kit/__init__.py is a docstring plus __version__ (stdlib-
   only, no side effects), and setuptools' own dynamic-attr mechanism
   performs the equivalent read at every build.
4. "Tests for the dogfood block" — DECLINED with honesty: the block is
   non-critical glue; the live proof is this venv running
   installed-first with the full suite green (1033 passed, and
   test_missing_package_fails_loud auto-skipping via its guard exactly
   as designed in PR 1).

fast: CONCERNS, repeats of prior dispositions. Full suite green before
and after the dogfood install flip.
