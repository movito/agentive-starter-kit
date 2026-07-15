# KIT-0050 Evaluator Review — language profiles

**Date**: 2026-07-15
**Input**: `.adversarial/inputs/KIT-0050-code-review-input.md` (full-file
context, 9,509 lines) — branch `feature/KIT-0050-language-profiles`
vs `main`.
**Trio**: code-reviewer-fast-v2 (gemini-3-flash) → CONCERNS ·
code-reviewer (o3) → FAIL · claude-code (sonnet-4-6) → APPROVED.
**Working tree after each run**: clean (`git status` verified — no
evaluator mutations).

Note: the trio initially auto-cancelled on the large input in non-TTY
context. `ADVERSARIAL_UNATTENDED=1` is now the supported unattended
opt-in (upstream added it — the CLI's own message names it; the older
`echo y |` pipe no longer satisfies the non-TTY guard).

## o3 (code-reviewer) — FAIL, all four bug claims refuted empirically

The verify-before-believing pass ran each claim against the real
scripts before touching anything:

1. **"Unconditional shift breaks `--no-kit` and all `--flag=value`
   forms"** — REFUTED. The post-case `shift` removes the *current*
   token (the flag itself, never yet shifted for boolean/`=` forms).
   Scratch runs: `--no-kit <dir>` → rc 0, provisioned;
   `--shape=planning --profile=none <dir>` → rc 0, region written.
   o3 misread the loop (this is the unchanged KIT-0048 parser).
2. **"Valid symlinked hook mis-detected as broken"** — REFUTED.
   `test -f` follows symlinks (POSIX); a symlink to an executable
   dispatched fine in a scratch run (rc 0, hook ran with `--mode ci`).
3. **"Planning+python combo still returns profile='python'"** —
   REFUTED by reading the code: the illegal branch records the error
   and leaves `profile=None` (full set runs, maximally diagnostic,
   doctor exits 1). Exactly the KIT-0048 malformed-record pattern.
4. Finding 4's remedy ("hard-fail and block ci-check") would couple
   the dispatcher to the record — the ADR keeps the dispatcher
   record-blind by design.

**Test gaps accepted** (real, though the bugs weren't):
- `--no-kit` had no functional run in the suite → added
  `test_no_kit_flag_still_seeds_hook_and_record`.
- `=`-form flags had no functional run → added
  `test_equals_form_flags_parse`.
- Executable-symlink hook dispatch unpinned → added
  `test_executable_symlink_hook_dispatches`.
- planning+python: full-set-still-runs not asserted → extended
  `test_planning_python_combination_fails_loud`.

## fast-v2 (CONCERNS) — dispositions

1. **Non-executable hook blocks the built-in fallback** — BY DESIGN
   (spec/handoff verbatim: a present-but-broken hook is a loud error,
   never a silent fallback — the intersection-masking class). Tested.
2. **`none` profile exits 0 → green CI** — BY SPEC (F3: "a no-op hook
   that says so loudly and exits 0"; acceptance criterion: "loud
   no-op, exit 0"). The loudness is the mitigation; a docs-only repo
   with no toolchain SHOULD pass.
3. **Misspelled `profile:` key defaults silently** — inherent to
   back-compat: an absent profile line MUST default (pre-KIT-0050
   regions), and a typo'd key is indistinguishable from absent. An
   empty *value* (`profile:` with nothing) DOES fail loud — pinned
   with `test_empty_profile_value_fails_loud` (was a genuine gap).
4. **kit_markers.py sync dead-end** (seeded to consumers, rides no
   sync tier, so reader logic can drift from `project`) — REAL but
   pre-existing since KIT-0048 (planning shape has always shipped it
   seeded-not-synced; scripts/local is the consumer-owned layer, and
   KIT-0049 v1 says additions/updates to it arrive via re-bootstrap).
   Moving it to `core/` is an architectural call touching KIT-0048's
   ship-list decisions — **flagged for the planner as a follow-up
   candidate**, not changed unilaterally here.

## claude-code — APPROVED

No findings.

## Outcome

No production-code changes required; five test additions/extensions.
Full suite green after triage.
