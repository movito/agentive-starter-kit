## KIT-0033 — Make planner + feature-developer truly portable downstream (PR #58)

**Date**: 2026-06-27
**Agent**: feature-developer
**Mode**: single-repo
**Scorecard**: 9 threads, 0 regressions, 5 fix rounds (1 evaluator + 4 bot), 7 commits

### What Worked

1. **Extracting the merge logic into a stdlib Python helper** — putting the
   marker merge in `scripts/local/kit_markers.py` (functions + thin CLI) instead
   of inline `sed`/`awk` in bash made the N2/F4 core directly unit-testable. Every
   subsequent bot finding (CRLF, malformed-marker fail-fast, duplicate regions)
   landed as a 3-line function change plus a focused test, not a bash rewrite.
2. **Scratch-consumer end-to-end verification via `mktemp`** — running the real
   `bootstrap-consumer.sh` against throwaway dirs caught behaviors unit tests
   can't: the `.kit/` skeleton, lifecycle `project start`/`complete`, the stale-
   orphan sweep, and the atomicity abort all proven against actual filesystem
   state before and after each fix.
3. **Running the Phase-7 evaluator while CI was pending** — code-reviewer-fast
   returned FAIL and surfaced the `rm -f`-on-source footgun and duplicate-region
   bug *before* the bots did, so those were already fixed in `40f732d` by the time
   the bots posted.
4. **`gh-review-helper.sh` for thread triage** — `threads`/`reply`/`resolve`
   subcommands made the reply-and-resolve loop mechanical across all 9 threads;
   no hand-rolled GraphQL for thread node IDs.

### What Was Surprising

1. **The bots found a real bug I'd shipped, not just nitpicks** — both BugBot and
   CodeRabbit independently flagged that `tests/test_kit_markers.py` was rsynced
   to consumers while its `scripts/local/kit_markers.py` import was not, breaking
   consumer `pytest`/`pytest-fast` at collection. The marker design was sound but
   the *delivery* of its test was not — a blind spot pure-LLM self-review missed.
2. **Five fix rounds for a "4–8 hour" task** — each push surfaced exactly one new
   edge case (orphan sweep → CRLF → merge atomicity → arg guard). All were
   legitimate; the cadence was "fix, push, bot finds the next layer." The fail-fast
   I added on CodeRabbit's advice is what made the *atomicity* bug reachable, which
   BugBot then caught — a fix exposing the next finding.
3. **flake8 E501 noise vs. actual gate** — bare `flake8` flagged 79-char overflows,
   but the repo's CI and pre-commit both use `--select=E9,F63,F7,F82` (no E501) with
   `--max-line-length=88`. Several minutes spent reconciling before reading
   `.github/workflows/test.yml` showed line length isn't even checked.
4. **The coverage gate, not a test, was the first CI failure** — adding 100%-tested
   library functions still dropped total coverage to 78% because the *CLI* layer
   (`_cmd_*`, `main`) was uncovered. Easy to forget the gate is on the whole file.

### What Should Change

1. **Add a "does this test ship downstream?" check to self-review** — any new test
   that imports from `scripts/local/` (not synced to consumers) must be excluded
   from the consumer `tests/` rsync. This was the highest-severity miss and is a
   recurring structural hazard for the kit's dual ASK-dev / consumer audience.
2. **Bootstrap mutations should be temp-then-commit by default** — the atomicity
   bug (per-item `mv` inside a `set -e` loop) is a general bash pattern worth
   codifying: stage all outputs to temp files, then move them only after every
   step succeeds. Worth a note in a bootstrap/scripting guideline.
3. **Run the evaluator AND a quick `git grep` for "what gets synced" before first
   push** — the consumer-import bug was discoverable by asking "the test file lands
   in consumers; does its import?" A pre-push checklist item for files that cross
   the ASK→consumer boundary would have saved 2 bot rounds.
4. **Document the Gate-2 SHA-matching quirk in preflight** — CodeRabbit APPROVED
   and its check-run is green, but `preflight-check.sh` Gate 2 still FAILs because
   no `coderabbitai[bot]` review event is tied to the exact head SHA after a docs-
   only or trivial push. The gate should accept "check-run passed + latest review
   APPROVED + zero unresolved threads" as equivalent.

### Permission Prompts Hit

1. **`cd … && chmod … && rm -rf … && bash …`** (chained, with `rm -rf`) — denied
   immediately at the first scratch-dir setup. Worked around by splitting into
   separate calls and using `mktemp -d` instead of `rm -rf` on a fixed path.
2. **`rm -rf /tmp/kit-consumer-test; mkdir …; echo`** — denied (the `rm -rf`).
   Switched to `mktemp -d` for all scratch consumers thereafter.

Both are general sandbox guards (destructive `rm -rf` + command chaining), not
project allowlist entries — no `.claude/settings.json` change warranted. Lesson:
reach for `mktemp -d` from the start for throwaway dirs.

### Process Actions Taken

- [ ] Add self-review checklist item: tests importing `scripts/local/` must be
      excluded from the consumer `tests/` sync in `bootstrap-consumer.sh`
- [ ] Codify the temp-then-commit (two-pass) pattern for multi-file bootstrap
      mutations in a scripting guideline
- [ ] Relax `preflight-check.sh` Gate 2 to accept check-run-pass + latest review
      APPROVED + zero unresolved threads (avoid SHA-exact false negatives)
- [ ] Consider shipping `kit_markers.py` test coverage expectations as part of the
      consumer manifest contract (so the dual-audience boundary is explicit)
