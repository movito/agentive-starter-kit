## KIT-0053 — The One Setup Door, ADR-0027 P3 (PR #81 + stacked #82)

**Date**: 2026-07-16
**Agent**: feature-developer-f5
**Mode**: single-repo
**Scorecard**: 19 threads (all resolved), 0 strict regressions (2 new-code
instances of the known masking class — see Surprising #3), 5 fix rounds
(+1 decline-only round), 13 commits on `feature/KIT-0053-one-setup-door`
(PR #82 adds 1 docs commit on the stacked branch)

### What Worked

1. **Characterize-first found a shipping crash before any refactor** —
   the very first characterization run exposed that `create-project.sh`'s
   flagless export dies on macOS (`tr -d '-_ '`: BSD tr parses the
   leading dash as an option). Every flagless export had been broken on
   the primary platform; fixed in `8c97bb3` before the entrances were
   touched. The KIT-0048 precedent (goldens as a commit boundary) paid
   for itself in the first hour.
2. **Frozen-surface shims + `--legacy-shim` fidelity channel** — letting
   the shims own their historical parse/validation verbatim (instead of
   thin passthroughs) was the only design under which the entire
   KIT-0048/0050 characterization suite (69 tests incl. all error paths,
   exit codes, messages) passed UNMODIFIED through shim → door → engine.
   Thin shims + a validating door cannot reproduce historical usage
   errors byte-for-byte.
3. **Evaluator-before-PR (F3 ordering) + refute-with-evidence** — the
   trio ran pre-PR; o3's three accepted findings (git-identity
   fail-fast, preset empty-output guard, door pipefail) landed before
   any bot saw the code. Empirically refuting hallucinations (scratch
   `find` tree for the `-o` scoping claim) took ~30 seconds and kept two
   "Critical"-labeled non-bugs out of the diff.
4. **Door-level (not engine-level) placement of the record-conflict
   check** — only the door knows whether a value was operator-given or
   defaulted; an engine-side comparison would have false-positived on
   every flagless re-adopt of a non-default record. Getting the layering
   right the first time meant CodeRabbit's follow-up round only asked
   for a stronger test, not a redesign.

### What Was Surprising

1. **`ADVERSARIAL_UNATTENDED` EXISTS in adversarial-workflow 1.0.1** —
   runtime evidence, resolving the KIT-0052 contradiction: in non-TTY
   with a large input and the flag unset, 1.0.1 prints "Non-TTY context
   detected and ADVERSARIAL_UNATTENDED is unset — auto-cancelling" and
   **exits 0 without running anything**. `echo y |` cannot work there —
   the auto-cancel fires before stdin is read. With
   `ADVERSARIAL_UNATTENDED=1` it auto-confirms and runs. The KIT-0050
   retro was right; the 2026-07-15 "zero matches in venv AND system"
   re-verification was wrong. Memory (Key Gotchas) corrected this
   session. Corollary: the documented `echo y |` guidance in
   prepare-review-input.sh 1.5.1 is dead weight for agents.
2. **The pre-approved PR split was structurally impossible to execute
   green** — door-first/shims-second orphans the old entrance paths at
   the PR-1 boundary, and the characterization suite doesn't FAIL — it
   **module-skips silently** (`pytest.skip` when the script is absent).
   Main would have looked green with the regression net switched off.
   Restructured: PR 1 = characterization + door + engines + shims +
   removal task; PR 2 = docs only. Lesson: module-skip guards that
   protect consumer checkouts double as a silent-disable hazard for
   kit-side refactors.
3. **The masking class appeared twice more in brand-new code** — a
   fresh-export `--profile none` recording `none` next to the kit's
   python Project Rules (BugBot), and `--no-kit` being silently
   unhonorable on the materials path (BugBot). Both were written by an
   agent that had the "intersections must name what they drop" pattern
   in context. The class is evidently easy to re-create whenever two
   configuration axes meet a copy step; validators only got added after
   a bot pointed at the seam.
4. **Bot rounds converged cleanly but slowly**: 19 threads over 6
   scan rounds (11 → 3 → 1 → 1 → 1), each push triggering a fresh scan
   with a genuinely new find. Every post-batch find was small but real
   (short-option swallow, name+email identity). Batch-by-category kept
   it to 5 fix rounds, but a ~500-line new bash surface simply takes
   several passes to settle.

### What Should Change

1. **Update the unattended-evaluator guidance** (KIT-0052 scope):
   replace `echo y |` with `ADVERSARIAL_UNATTENDED=1` in
   `prepare-review-input.sh`'s next-steps output and the
   code-review-evaluator skill; add "exit 0 does not mean it ran —
   check the log file" to the gotcha. The auto-cancel-exits-0 behavior
   is the worst kind of silent skip for an agent pipeline.
2. **Pre-run black on new/edited Python files before committing** —
   three commits aborted mid-hook this session because black reformatted
   brand-new test files during pre-commit (stash-restore cycle, then
   re-stage + recommit). One `black <files>` before `git add` removes
   the whole failure mode. Candidate for COMMIT-PROTOCOL.md.
3. **Add a masking-class self-review question** to the self-review
   skill: "where do two configuration axes meet a copy/preserve step,
   and does each such seam either honor both axes or reject the
   combination loudly?" Two of this session's four real bot finds were
   exactly that question.
4. **Note the module-skip hazard in TESTING-WORKFLOW.md**: when a
   refactor moves/renames a file that a test module-skips on, the suite
   goes green-by-absence. A rename PR must grep for
   `allow_module_level=True` guards referencing the moved paths and
   keep them exercised in the same PR.

### Permission Prompts Hit

One: `rm -rf /tmp/kit0053-find-test && mkdir ...` (the find `-o` scoping
refutation) was denied by the sandbox; immediately rerouted to `$TMPDIR`
without the `rm -rf` prefix — no meaningful stall, no allow-list change
needed (the `$TMPDIR` form is already permitted).

### Process Actions Taken

- [ ] KIT-0052: swap `echo y |` → `ADVERSARIAL_UNATTENDED=1` in
      prepare-review-input.sh next-steps + code-review-evaluator skill;
      document exit-0-without-running
- [ ] COMMIT-PROTOCOL.md: pre-run black on new/edited Python files
      before staging
- [ ] self-review skill: add the two-axes-meet-a-copy-step masking
      question
- [ ] TESTING-WORKFLOW.md: module-skip guards + renames = silent
      green; grep `allow_module_level` on any file-move PR
- [ ] Planner: merge #81 → retarget #82 to main (CodeRabbit only
      reviews it then) → merge; then the post-P3 downstream checkpoint
      opens (ADR-0027 sequence)
- [ ] KIT-0054 stays pinned to 0.9.0 (shim removal; carries the
      record-conflict divergence erasure + materials setup-dev
      hardening notes)

### Incident Closure

1. **ADVERSARIAL_UNATTENDED auto-cancel exits 0 without running** —
   **triage-guide entry** (belongs in the KIT-0052 fix: the
   symptom→cause line "evaluation 'succeeded' but no log verdict =
   auto-cancelled non-TTY large input" goes where the evaluator-run
   docs live). Not doctor-checkable cheaply: the behavior only
   manifests at run time with a large input.
2. **BSD tr option-parse crash in the prefix fallback** — **not
   re-checkable note not needed**: closed by the fix itself plus a
   permanent characterization test (`test_export_e2e_defaults` runs the
   flagless export on every CI run — the regression net IS the check).
3. **Silent module-skip on renamed scripts** — **triage-guide entry**
   (TESTING-WORKFLOW.md action above); a doctor check can't know which
   skips are legitimate consumer-checkout skips vs refactor holes.
