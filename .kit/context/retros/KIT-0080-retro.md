## KIT-0080 — Portable git resolution (Apple git 2.30.1) (PR #107)

**Date**: 2026-08-06
**Agent**: feature-developer
**Mode**: single-repo
**Merged**: squash → `2f64ac2`
**Scorecard**: 1 thread, 1 regression, 1 fix round, 4 commits

### What Worked

1. **Checking whether the "gone" repro was actually gone** — the spec and
   handoff both said the local reproduction had vanished (operator upgraded
   to git 2.55) and that stub fixtures were therefore the ONLY proof
   mechanism. Probing `/usr/bin/git` first thing found **Apple git 2.30.1
   still installed** — Homebrew shadowed it via PATH, it did not remove it.
   The spec's own "Reproduction after the upgrade" section says exactly
   this; two handoff layers had already read it as unavailable. Cost: one
   command. Payoff: the whole task was verified against the real broken
   binary instead of an emulation, including reproducing S1/S3/S4 live and
   confirming the untruncated 8-failure baseline.

2. **Falsifying every guard against `git show HEAD~1:<file>` rather than a
   hand-edit** — the first falsification attempt used a scripted string
   replacement that mangled the file into a syntax error. That "failure" was
   worthless: the test failed for the wrong reason. Re-running against the
   pristine pre-fix blob produced the real signal — the exact
   `dirname: illegal option -- -` from the spec. A guard-test is only proven
   by the ORIGINAL defect, not by any breakage.

3. **The new tests caught two bugs I wrote** — `test_non_repo_still_skips`
   caught that `cd ""` is a silent no-op (an empty rev-parse result would
   have made "not a repo" resolve to a confident wrong path), and the
   existing `test_derivation_without_override_names_the_sibling` caught an
   off-by-one when I collapsed the double `dirname` to one. Both are the
   same silent-wrong-answer class the task exists to kill — the fix nearly
   reintroduced the bug in a new costume.

4. **Verify-before-believing on evaluator findings** — o3 returned CONCERNS
   with 5 findings; 4 were refuted by direct measurement in ~10 minutes
   total. `../.git` breaking the worktree comparison: false, git returns
   absolute paths from a linked worktree. ERR trap swallowing the exit code:
   false, measured exit 1. Filesystem-root `dirname` math: unchanged
   pre-existing code AND the arithmetic claim was wrong. Accepting these
   would have meant churning working code and burning bot rounds.

### What Was Surprising

1. **A two-hop handoff amplified a wrong environmental claim into a
   constraint** — the spec correctly recorded that Apple git lives on at
   `/usr/bin/git`, then its own summary line said "the local repro is GONE",
   the planner handoff hardened that into "**You cannot manually reproduce
   anything**", and the task starter repeated it in bold. Each hop was a
   faithful summary; the aggregate inverted a fact present in the source
   document. The instruction to distrust a clean local run was right for the
   right reason — it just wasn't the only option available.

2. **`cd ""` succeeds silently** — the portable recipe live-verified in
   KIT-0083 F1 (`cd <dir> && cd "$(git rev-parse --git-common-dir)" && pwd`)
   is correct on the happy path and quietly wrong on failure: the empty
   substitution makes `cd ""` a no-op, `pwd` returns the starting dir, and
   the whole thing exits 0. A recipe can be "live-verified" and still carry
   a failure-path hazard the verification never touched.

3. **`cd`+`pwd` vs string-joining is a semantic choice, not a style one** —
   `cd`+`pwd` resolves symlinked ancestors and returns PHYSICAL paths
   (`/var` → `/private/var` on macOS). That broke the door/doctor
   equivalence invariant, which is pinned by a test. Resolvers that get
   COMPARED must join by string; `new-worktree.sh`, whose value creates
   files rather than being compared, correctly keeps `cd`+`pwd`. Same bug,
   opposite correct answers, two lines apart.

4. **My first "Apple git" test harness was the artifact, not the bug** —
   stripping PATH to `/usr/bin:/bin` to force Apple git also forced
   `/usr/bin/python3` (3.9), which cannot parse `X | None` in
   `scripts/core/project`. That produced 8 setup-door failures I briefly
   read as real 2.30.1 breakage. A shim dir containing only a `git` symlink,
   prepended to the real PATH, isolates the one variable — the stripped-PATH
   approach changes several.

### What Should Change

1. **`patterns.yml` `displayed_commands_are_contracts` should widen to
   generated scripts** — the rule already mandates `%q`/`shlex.quote` for
   interpolated values, but scopes it to commands *printed for a human to
   paste*. CodeRabbit's one finding was the same defect in a *generated
   bash script* (a test fixture interpolating `shutil.which("git")` into an
   unquoted `REAL=` assignment; a spaced git path makes the stub exit 127).
   Counted as a regression because the underlying rule exists — it just
   didn't reach this shape. Suggest renaming the concept to "interpolated
   paths in emitted shell" and listing both faces.

2. **Handoffs should cite the source line for environmental claims, not
   restate them** — "the local repro is GONE" would have been
   self-correcting as "local repro: see spec §Reproduction after the
   upgrade". A pointer forces the reader to the primary source; a summary
   lets a factual error propagate with increasing confidence at each hop.

3. **Add a "check the failure path" beat to the fix-recipe convention** —
   both `cd ""` and the physical-path divergence were hazards in the
   *recipe*, not in the diagnosis. When a task hands over a live-verified
   one-liner, the implementer should be told to verify it on the FAILING
   input too, not just the working one.

4. **The narrowed fetch refspec breaks worktree PR creation** — this repo's
   `remote.origin.fetch` is `+refs/heads/main:refs/remotes/origin/main`
   only, so from a worktree `git push -u` cannot create a tracking ref and
   `gh pr create` refuses with "you must first push the current branch".
   Worked around with `--head`, deliberately not changed since it looked
   intentional. It will bite every future worktree session identically —
   needs a decision: widen the refspec, or document `--head` in
   `WORKTREE-WORKFLOW.md`.

5. **`project move` edits `agent-handoffs.json`, which KIT-0086 forbids on a
   branch** — the move auto-updated two `details_link` fields; I reverted
   them per the handoff's explicit instruction, which leaves the file
   pointing at `3-in-progress` for the planner to fix by hand. The script
   and the discipline contradict each other. Either `project move` needs a
   `--no-handoff-update` flag (or should skip the edit when not on `main`),
   or KIT-0086 needs an explicit carve-out for this script's own writes.

### Permission Prompts Hit

Three denials, each cheap to route around (seconds, no user wait — I
switched approach rather than requesting approval):

1. `rm -rf "$SP/p2"` inside a scratchpad probe — the `rm -rf` deny is
   settled policy (WORKTREE-WORKFLOW.md). Reused a differently-named probe
   dir instead. Working as intended.
2. A compound `cd … && mkdir && git init && env …` probe with an inline
   `rm -rf` tail — same cause.
3. A `ln -s`/`env PATH=…` compound in `/private/tmp` for the git-absent FAIL
   branch. Covered it in pytest instead, which was the better home anyway.

None are new patterns worth allowlisting; the `rm -rf` denials are the
policy doing its job.

### Process Actions Taken

- [ ] Widen `patterns.yml` `displayed_commands_are_contracts` to cover
      interpolated paths in GENERATED shell scripts, not only displayed
      commands (cite KIT-0080 / CodeRabbit PR #107)
- [ ] Decide the fetch-refspec question: widen `remote.origin.fetch`, or
      document the `gh pr create --head` workaround in
      `WORKTREE-WORKFLOW.md`
- [ ] Resolve the `project move` vs KIT-0086 contradiction (flag, branch
      guard, or explicit carve-out)
- [ ] Update `agent-handoffs.json` `details_link` for KIT-0080 → merged
      (left stale on purpose per KIT-0086)
- [ ] Consider a handoff-template line: cite the source §/line for
      environmental claims rather than restating them
- [ ] Consider adding "verify the recipe on its FAILING input" to the
      fix-recipe handoff convention

### Incident Closure

Four incidents this session; each routed:

1. **Apple git 2.30.1 below the portability floor** → **doctor check
   added**: `scripts/core/doctor.d/15-git-version.sh` WARNs below the floor,
   with the incident cited in its header comment and the floor pinned to the
   README Requirements row by
   `test_floor_agrees_with_the_readme_requirements_row`. This is the F4
   deliverable and the standing canary for the class.

2. **`cd ""` silently resolving to the starting directory** → **guarded and
   tested, not checkable by doctor**: it is a code-shape hazard, not
   environment state. Closed as inline comments at all five resolver sites
   plus `test_non_repo_still_skips_under_old_git`, and as the repo-wide
   `test_no_script_still_uses_the_unportable_flag` guard that keeps the
   whole class from returning.

3. **Narrowed fetch refspec breaking worktree PR creation** →
   **triage-guide entry needed** (action item above): diagnosable only at
   failure time, and the symptom (`gh pr create` saying "you must first push
   the current branch" *after* a successful push) does not name its cause.
   Belongs in `WORKTREE-WORKFLOW.md` next to the launch steps. Not filed by
   me — it is a repo-config decision for the planner.

4. **`project move` writing a file the branch discipline forbids** →
   **triage-guide entry / process fix needed** (action item above). Not
   doctor-checkable: doctor cannot know whether a given edit was intended.
   The contradiction lives between a script and a rule, so it needs one of
   them changed rather than a check.
