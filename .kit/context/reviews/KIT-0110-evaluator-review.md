# KIT-0110 — Evaluator Review Record (PR 1, kit repo)

**Date**: 2026-08-14
**Agent**: feature-developer-f5
**Diff shape**: logic (new tool + tests) → full trio, `--format full`
**Input**: `.adversarial/inputs/KIT-0110-code-review-input.md`
(commit `1426ec3`)

## Verdicts

| Evaluator | Model | Verdict |
|---|---|---|
| code-reviewer-fast | gemini-2.5-flash | CONCERNS |
| code-reviewer | o3 | FAIL |
| claude-code | claude-sonnet-4-6 | APPROVED |

Logs: `.adversarial/logs/KIT-0110-code-review-input--{code-reviewer-fast,code-reviewer,claude-code}.md`

## Dispositions (every finding verified against code before acting)

### Actioned

1. **`_entry_bounds` unanchored matching** (claude-code, LOW —
   CONFIRMED latent): a `why: >-` continuation line beginning
   `- name:` could open/close an entry early. Fixed: both start and
   end matches are now anchored to the roster's 2-space list indent;
   regression test `test_entry_bounds_ignores_lookalike_in_why_text`.
2. **Missing `git` binary → raw traceback** (kernel of o3 F2):
   `subprocess.run` raises `FileNotFoundError` uncaught. Fixed: both
   `_git()` and `merge_three_way()` convert it to a named
   `ResyncError` ("git is not on PATH"), caught by the `main()`
   wrapper → clean `EXIT_INTEGRITY`.
3. **`_spec is None` on the guard import** (claude-code, LOW): now an
   explicit `ImportError` naming the path.
4. **`ResyncError` escaping `main()` as traceback** (self-review,
   pre-trio): `main()` wraps `_main()` and converts to
   `EXIT_INTEGRITY`.

### Refuted (with reason)

1. **o3 F1 "indented `version:` frontmatter silently ignored"** — an
   indented `version:` is not a top-level YAML key; the zero-indent
   regex matches the only legal form. The cited "legal YAML with
   optional indentation" is not legal YAML for a mapping key.
2. **o3 F2 as stated ("merge-file rc=1 with empty stdout classified as
   conflict")** — rc 1 means exactly 1 conflict by the documented
   contract, and conflict output always carries the merged content;
   the only real failure shape (missing git binary) is fixed above.
3. **o3 F3 "spaces/control chars in source reach git"** — list-arg
   subprocess, no shell; git receives the pathspec literally. A
   nonexistent path fails the rev walk → loud base-not-found, never
   silent.
4. **fast F1 `plugin_body_relpath` KeyError** — `name` is guaranteed
   by the guard's `_validate_components` before any call.
5. **fast F4 / claude-code "YAML injection via set_entry_field"** —
   evaluator self-refuted: hashes are hex-only, `kit_version` is
   quoted, the version regex excludes quotes/newlines.

### Declined (out of contract, recorded)

1. **CRLF preservation on roster rewrite** (o3) — the roster is
   LF-committed in movito/agentive-skills; newline-convention
   detection is speculative surface.
2. **History-walk depth limit** (claude-code) — infrequent local tool;
   walk length is bounded by per-file commit count.
3. **4-space field indent assumption** (claude-code) — the roster's
   established format is the tool's documented contract; the guard's
   parser and this tool share it.
4. **Import-time `exec_module` of the guard** (claude-code, MEDIUM) —
   the guard is `__main__`-guarded with no module-level side effects;
   the pattern is the kit's established scripts/local convention
   (same load in `tests/test_plugin_drift.py`).

## Known blind spot note

No CSS/dual-render surface in this diff; the known evaluator blind
spot does not apply.

---

# PR 2 (marketplace repo, movito/agentive-skills) — Gate 5 record

**Date**: 2026-08-14
**Diff shape**: logic (new verify script + first CI workflow + roster
column/header) → fast + deep, hand-assembled full-content input
(`.adversarial/inputs/KIT-0110-pr2-code-review-input.md`; the
marketplace repo has no helper infra)

## Verdicts

| Evaluator | Model | Verdict |
|---|---|---|
| code-reviewer-fast | gemini-2.5-flash | CONCERNS |
| code-reviewer | o3 | FAIL |

Logs: `.adversarial/logs/KIT-0110-pr2-code-review-input--{code-reviewer-fast,code-reviewer}.md`
claude-code tier skipped: the script's security surface (local file
hashing, no network, no subprocess) is a strict subset of PR 1's,
which claude-code APPROVED the same day.

## Dispositions

### Actioned

1. **Narrow globs let extra files ship undetected** (o3 + fast,
   CONVERGENT — CONFIRMED): `agents/*.md` / `skills/*/SKILL.md` missed
   `skills/x/HOWTO.md`, `agents/notes.txt`. Fixed: the unrostered scan
   now walks `agents/`, `commands/`, `skills/` recursively and flags
   EVERY non-rostered file. Falsified live: planted
   `skills/self-review/HOWTO.md` + `agents/.evil.md` → both flagged,
   exit 1; removed → 27 verified, exit 0.
2. **Leading-dot component names produce hidden shipped files** (o3 —
   CONFIRMED latent): `_SAFE_NAME` tightened to forbid a leading dot,
   in the marketplace script AND kit-side `plugin_resync.py` (fix the
   class, not the instance).

### Refuted (with reason)

1. **o3 headline "dot-prefixed bodies escape `Path.glob`"** — verified
   empirically: `pathlib.Path.glob('*.md')` DOES match `.evil.md`
   (dotfile-skipping is the `glob` module's behavior, not pathlib's).
   The FAIL's stated mechanism is wrong; the surviving kernel is the
   extra-file gap actioned above.
2. **fast "`body_relpath` implicitly returns None on unknown kind"** —
   it cannot: the final branch is an unconditional return, and
   `load_components` rejects unknown kinds for shipped entries before
   any call.
3. **fast "missing `ships` silently treated as false"** — intentional;
   identical semantics to the kit guard's parser.

### Declined (out of contract, recorded)

1. **Hard-coded plugin dir breaks forks** (o3) — this repo IS the
   single-plugin marketplace; a fork edits one constant.
2. **2 GB body OOM / streamed hashing** (o3) — repo-controlled
   markdown bodies; speculative surface.
3. **Duplicate ships:false entries abort** (o3) — strictness is
   deliberate: the roster is a decision record; duplicates in it are a
   defect worth loudness.
4. **Unit-test gaps** (o3) — the marketplace repo has no test infra by
   design (KIT-0109 retro item 3 notes the tradeoff); the falsification
   runs above are the test story, recorded in the PR body.
