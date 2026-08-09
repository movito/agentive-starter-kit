## KIT-0092 — Shim removal + monolith test shrinkage, agentive-kit 0.3.1 (PR #118)

**Date**: 2026-08-08
**Agent**: feature-developer
**Mode**: single-repo (worktree `~/Github/ask-worktrees/KIT-0092`, branch `feature/KIT-0092-shim-removal`)
**Scorecard**: 1 thread, 0 regressions, 0 fix rounds, 3 commits

Bot rounds: 1 (a single push cycle; the one finding was declined, so no
fix round followed). Evaluator deep rounds: 1 of 2 permitted.

### What Worked

1. **Re-grepping instead of trusting the handoff's caller list caught a
   shipping defect.** The handoff named 8 files in `.claude/` and said
   the 8 was a snapshot. The sweep found four more live surfaces, and
   one mattered: `preflight.py` and `review_input.py` printed
   `./scripts/core/*.sh` in their own `--help`/usage text. Without that
   fix, 0.3.1 would have shipped a CLI instructing users to run the
   three files the same release deleted. Running all three help
   surfaces post-change (`agentive preflight/review-input/review-helper
   --help`) is what confirmed it, not reading the diff.

2. **Verify-before-believing killed a confident-sounding hallucination.**
   o3 reported an "always produced" unbalanced markdown fence in
   `review_input._file_section` as a must-fix blocker. `review_input.py:240`
   is `f"````{lang}\n{content}````\n\n"` — four backticks on both sides.
   Confirmed twice: reading the line, then counting the generated
   artifact (40 four-backtick lines, evenly paired). ~2 minutes of
   checking prevented a "fix" that would have broken working output.

3. **Checking whether harness plumbing was really bash-only, rather
   than deleting everything the bash touched.** The `sleep` stub was
   genuinely bash-only and went. The `dispatch` stub looked identical
   but `preflight._emit_dispatch_event` does `shutil.which("dispatch")`
   and shells out — and the module now runs **in-process**, so deleting
   the stub would have let a developer's real `dispatch` binary fire
   live progress events from a test run. Kept, with the reason written
   into the comment.

4. **Inverting the shipset contract instead of dropping it.** The three
   paths moved from `PLANNING_MUST_SHIP` to `PLANNING_MUST_NOT_SHIP`
   and the seeded-manifest test now asserts their absence. A deletion
   PR that merely removes assertions leaves nothing pinning the new
   state; this way a regression that re-ships them fails.

### What Was Surprising

1. **The handoff's Part C table was wrong on two of its four rows.** It
   earmarked `tests/test_project_script.py` (2,006 lines) and
   `tests/test_doctor.py` (2,645) for shrinkage. Neither file contains
   a single reference to the three removed shims — their bulk is
   `project`-shim and doctor coverage, both explicitly out of scope.
   ~4,650 lines were never in scope. The handoff's own judgment rule
   ("a test dies with the shim it tests… nothing-tests-deleted-code,
   not a target number") resolved it correctly, but the table's
   specificity read as verified fact when it was a prediction.

2. **`--format full` made two of three evaluators review the modules
   instead of the change.** This PR's package edits are 100%
   docstrings, comments, and strings — zero logic (verified with `git
   diff` over both files). Both FAIL verdicts consisted entirely of
   pre-existing behavior findings. `claude-code` was the only one to
   scope correctly ("not blockers for this cleanup PR"). Full-file
   context remains right for logic changes; for a strings-only diff it
   inverted the signal-to-noise ratio.

3. **The pre-commit `pytest-fast` hook aborted the first commit with
   `pytest: command not found`.** The hook is `language: system` and
   calls bare `pytest`; a worktree shell where the venv is used via
   explicit `.venv/bin/python` paths has no `pytest` on PATH. The
   staged tree was intact and `PATH="$PWD/.venv/bin:$PATH" git commit`
   fixed it — but the failure text says "Fast tests failed!", which
   reads as a test failure rather than a missing binary. A literal
   reading invites `SKIP_TESTS=1`, silently dropping the guard.

4. **Zero substantive bot findings on a 22-file diff.** BugBot clean;
   CodeRabbit's single finding was MD029 on a line my diff never
   touched (it appeared as context adjacent to a changed hunk), flagged
   against a "configured style" that does not exist — there is no
   `.markdownlint*` config in the repo and markdownlint runs in neither
   pre-commit nor CI. Declined with reasoning; CodeRabbit then flipped
   to "Review approved".

### What Should Change

1. **Handoff tables that predict file contents should be marked as
   predictions or verified before writing.** The Part C table read as
   surveyed fact. A one-line grep per row at handoff time would have
   caught it. Suggested convention: cite the grep that produced each
   row, or label the row "predicted — verify".

2. **Match evaluator input format to diff kind.** A strings-and-docs
   diff fed as `--format full` produces module-wide findings that are
   all out of scope. Consider: for diffs with no logic changes, prefer
   `--format diff`, or state the diff's nature in the input header so
   evaluators scope correctly. This is the third recorded instance of
   input format distorting evaluator output (cf. KIT-0069/KIT-0073
   prose-sweep shutouts) — the general lesson is that the trio's value
   depends on input shape matching change shape.

3. **Fix the `pytest-fast` hook's missing-binary message.** Distinguish
   "pytest not found" from "tests failed", and prefer a venv-aware
   resolution (`.venv/bin/pytest` when present) over bare `pytest`, so
   worktree sessions do not hit a false failure whose suggested remedy
   is to skip the guard.

4. **`agentive review-input` advertises a flag that does not exist.**
   Its "Next steps" tail prints `ADVERSARIAL_UNATTENDED=1`; grepping
   the actual install (`~/.local/share/uv/tools/adversarial-workflow/`
   — a separate uv tool, not the repo venv) shows no such flag. This is
   the exact class `self-review/SKILL.md` lesson #10 records from
   KIT-0044, regressed or never fully removed. Harmless (unknown env
   var ignored; the `echo y |` pipe does the work) but a false runtime
   claim in shipped output. Deserves a small task.

### Permission Prompts Hit

None. Every command used this session resolved against the existing
allow list (`Bash(pytest *)`, `Bash(black *)`, `Bash(adversarial *)`,
git/gh porcelain). No new patterns needed.

### Process Actions Taken

- [ ] Feed back to planner: Part C table rows 3–4 (`test_project_script.py`,
      `test_doctor.py`) were unverified predictions; ~4,650 lines never in scope
- [ ] Adopt a "predicted vs verified" convention for handoff file tables,
      or cite the grep behind each row
- [ ] Guidance: choose evaluator input format by diff kind (logic → full,
      strings/docs-only → diff or an annotated header)
- [ ] Fix `pytest-fast` hook: distinguish missing-binary from test failure;
      resolve `.venv/bin/pytest` when present
- [ ] New task: remove the `ADVERSARIAL_UNATTENDED=1` hint from
      `agentive review-input`'s "Next steps" output (verify against the
      installed tool first — self-review lesson #10)
- [ ] Consider: adopt a markdownlint config with an `ol-prefix` style
      permitting sequential numbering, or accept MD029 noise on
      adjacent-hunk context lines as a known false-positive class

### Incident Closure

Two environment incidents this session:

1. **`pytest` absent from PATH in a worktree shell, aborting the first
   commit with misleading "Fast tests failed!" text.** → **Doctor check
   (extend)**: `scripts/core/doctor.d/55-worktree-provisioning.sh` is
   the right home — it already audits worktree venv correctness
   (KIT-0065 symlink destruction, KIT-0044 stale-venv split-brain) with
   per-incident header notes. Add a `worktree-hookpath` concern: WARN
   when a real `.venv/` exists in the worktree but `pytest` does not
   resolve on PATH, since `language: system` pre-commit hooks call bare
   binary names and will abort commits with a message that reads as a
   test failure. Cite KIT-0092. (Filed as a process action; not
   implemented in this PR, which is scoped to shim removal.)

2. **`adversarial` CLI lives outside the repo venv
   (`~/.local/share/uv/tools/adversarial-workflow/`), so grepping
   `.venv/lib/.../site-packages/` for `ADVERSARIAL_UNATTENDED` returned
   a false "not present" before I re-checked the real install.** →
   **Triage-guide entry**: this is diagnosable only at failure time and
   belongs where the verification step is documented —
   `.claude/skills/self-review/SKILL.md` lesson #10 already teaches
   "grep the installed package", but does not say **how to locate it**
   when the tool is a uv tool install rather than a venv dependency.
   Add one sentence to that lesson: resolve the binary first (`which
   <tool>`, read its shebang) and grep THAT tree, because a repo-venv
   grep will report a false negative for uv/pipx-installed CLIs.
