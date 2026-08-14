# KIT-0105 — Evaluator Review Record (PR 1 of 3)

**Date**: 2026-08-14
**Scope**: PR 1 (kit) — project-intake becomes location-agnostic
(commit `49045fc` + polish commit)
**Tier**: normal (code + prose — the trio), per the handoff's process
citations
**Input**: `.adversarial/inputs/KIT-0105-code-review-input.md`
(full format — the diff carries a new test class, so logic-shaped)

## Verdicts

| Evaluator | Verdict | Log |
|-----------|---------|-----|
| code-reviewer-fast | FAIL (7 findings) | `.adversarial/logs/KIT-0105-code-review-input--code-reviewer-fast.md` |
| code-reviewer | CONCERNS (7 findings) | `.adversarial/logs/KIT-0105-code-review-input--code-reviewer.md` |
| claude-code | APPROVED (6 findings) | `.adversarial/logs/KIT-0105-code-review-input--claude-code.md` |

## Dispositions

### code-reviewer-fast (all 7: no action — verified against the tree)

1. **Prefix re-derivation can produce invalid prefix** — refuted: the
   project name is validated `^[a-z][a-z0-9-]{0,60}$` before derivation;
   uppercase-strip-hyphens-truncate of such a name always yields a
   valid `^[A-Z][A-Z0-9]{0,5}$` prefix. Pre-existing prose besides.
2. **Long slug after derivation** — pre-existing prose, untouched by
   this diff; "drop filler words until it fits" IS the recovery path.
3. **Step 5 planner launch lacks `printf %q`** — refuted: the path in
   Step 5's closing block is display prose ("open a new terminal tab
   in <path>"), not a shell argument; the pasted command's argument is
   a fixed string. Pre-existing text besides.
4. **Git <2.28 detection** — pre-existing prose; the fallback is
   already instructed and an LLM agent reads the command's error.
5. **Empty prototype folder** — speculative/low; Step 0's "skim its
   top level" is pre-existing and unchanged.
6. **Symlink obfuscation of the kit-checkout guard** — the Inputs
   discipline already requires canonicalizing paths to absolute form;
   the guard is LLM-interpreted prose, pre-existing class.
7. **`_REF_PATTERN` too narrow** — the helper is PRE-EXISTING
   (unchanged by this diff); the full-format input made it look new —
   the known KIT-0092 full-contents artifact.

### code-reviewer (CONCERNS — no action; 5 of 7 target pre-existing code)

1–4. **Regex/link styles, case-sensitive extensions, placeholder
   breadth, Windows paths** — all in `_REF_PATTERN` /
   `_is_placeholder` / `_referenced_paths`, which predate this PR
   (KIT-0093-era helpers). Out of this diff's scope; widening them is
   its own task if ever warranted.
5. **`git init -b main` in the fixture assumes git ≥2.28** — the
   existing suite pins the same assumption (`make_adopt_dir` in
   `test_setup_door.py`); diverging in one fixture would be
   inconsistent, and CI images satisfy it.
6. **TASK_PREFIX replace could no-op and false-pass** — refuted:
   `test_prefix_and_backlog_seeded` re-reads `.env` and demands the
   exact `TASK_PREFIX=PROTO` line, so any no-op or double-fill fails
   loudly. Fail-closed, not false-pass.
7. **60 s subprocess timeouts brittle** — three local git ops on a
   tmpdir; 60 s is generous and matches suite norms.

### claude-code (APPROVED — 4 cheap fixes applied, 2 accepted as-is)

1. **HIGH: hardcoded date in `_TASK_STUB`** — comment added ("frozen,
   not asserted — shape, not freshness").
2. **MEDIUM: dependent tests confusing on door failure** — accepted:
   identical shape to the existing `single_scaffold`/
   `planning_scaffold` fixtures; the first test reports rc + output.
3. **MEDIUM: `_BRIEF` omits template sections** — comment added
   (deliberately minimal: the mechanical spine's inputs only; prose
   extraction is LLM work CI cannot exercise).
4. **LOW: no `capture_output` on fixture git calls** — applied.
5. **LOW: `_text()` re-reads per test** — accepted (three cheap reads).
6. **LOW: exact-string pointer assertion** — comment added (deliberate
   format-contract pin).

## Note for the planner

The pre-existing-helper findings (deep-reviewer 1–4) are the familiar
full-format artifact: evaluators treat appended unchanged file contents
as new code. If `_referenced_paths` breadth ever matters, it is a
backlog item, not a rider on this train.
