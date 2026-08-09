## KIT-0093 — The door switches to package-install mode, ADR-0028 phase 2 (PRs #115, #116, #117)

**Date**: 2026-08-08
**Agent**: feature-developer-f5
**Mode**: single-repo
**Scorecard**: 26 threads (8 + 13 + 5), 0 regressions, 13 fix rounds (5 + 5 + 3), 53 PR commits (7 + 17 + 29 — the #116/#117 counts include stack merge-forward commits) — stacked series, all three squash-merged same-day; **released agentive-kit 0.3.0** (tag `agentive-kit-v0.3.0`, publish workflow succeeded)

### What Worked

1. **Strict-xfail as the red-first mechanism** — landing the acceptance test's packaged-world contract as `xfail(strict=True)` proved it RED against the copying door while keeping CI green, and made PR 2 structurally unable to flip the door without consciously removing the markers (an xpass fails the suite). Zero CI cost, full falsifiability.
2. **Contract strings defined by the test first** — the door's verify-or-instruct lines were authored in `tests/test_scaffold_acceptance.py` (PR 1) and implemented to spec in PR 2; the final hermetic missing-deps test (PR 3) then pinned them under a restricted PATH. No drift at any point.
3. **Verify-before-believing killed four verdict-driving evaluator claims across three trios** — `GOOGLE_API_KEY` runtime claim (refuted via every `evaluator.yml` + the CLI resolver), `install-evaluators` exit-masking (refuted via the 8 `sys.exit` paths), sed pin extraction (refuted empirically against the real config), and PR 3's "residual create-project block" (refuted by a no-match grep — the evaluator reconstructed the pre-fix state, the KIT-0069 pattern exactly).
4. **The post-retarget CodeRabbit round earned its keep** — 11 findings on #116 once it faced main, including two genuine bugs my tests missed: `_doctor_install` silently defaulting without `kit_markers.py` (BugBot) and the `--name`/basename identity split across CLAUDE.md vs README/current-state. The handoff's "CodeRabbit skips feature-branch bases — the real round lands post-retarget" warning was exactly right; plan babysitting time for it.
5. **Stacked PRs + `merge --no-edit` forward propagation** — thirteen fix rounds across a three-PR stack with two squash-merge base rotations, no lost work; the two add/add conflicts (acceptance test, review record) resolved predictably by taking the downstream superset.

### What Was Surprising

1. **bash 3.2 mis-parses apostrophes inside heredocs within `$( )`** — a heredoc body containing `repo's` broke `engine-consumer.sh` with "unexpected EOF" on stock macOS bash. Cost ~20 minutes of bisection; the fix was rephrasing one word. The pre-existing heredocs had (apparently accidentally) avoided apostrophes.
2. **The dangling-reference check was red on the SINGLE shape too** — KIT-0081 F2 had only named the planning scaffold, but the single export's agent copies cited `KIT-ADR-0014/0019`, which `engine-export.sh` deleted. The acceptance test found a live defect before the switch made it moot.
3. **A fix round landed on the wrong branch once** — after a merge-forward I stayed on the pr3 branch and committed a #116 fix there; recovered with a cherry-pick, but the stack's branch-switching cadence makes this a real hazard. Adding `git branch --show-current` before every commit to the loop prompts fixed it for the rest of the session.
4. **The scaffold got ~8× faster as a side effect** — dropping `git archive` + full-tree rsync for the enumerated content scaffold cut a `--new` run from ~8s to ~1s and the acceptance suite from ~14s to ~2s.
5. **Bot rounds on instruction prose converge serially, not in batches** — #115's rename block took five rounds because each finding only existed after the previous fix (rename → main-collision → probe-failure → deletion-gating → owner-derivation). Batching by category cannot compress this shape.

### What Should Change

1. **patterns.yml candidate: no apostrophes in heredocs inside `$( )`** — stock-macOS bash 3.2 quote-tracks heredoc bodies within command substitution. One line in the defensive-coding patterns saves the next bisection; the engines are full of this construct.
2. **KIT-0092 Parts A+C need their own slot as 0.3.1** — Part B (guard retightening) shipped inside #116 where the old probe became blocking; the shim removal + monolith-test shrinkage were deliberately kept off the release PR. The promise window is 0.3.x — schedule promptly.
3. **Phase 3 spec should anchor on the `--packaged` seam** — `engine-consumer.sh --packaged`, the packaged region bodies, and `agentive_kit.doctor._parse_install_record` are exactly the machinery the consumer migration needs.
4. **Feature-developer Phase 9 vs the worktree ordering rule** — the agent spec still says `project move <ID> in-review`, which contradicts the never-move-from-a-feature-branch rule for worktree sessions. One reconciling sentence in the spec removes the ambiguity.
5. **Babysit-loop rule: verify the branch before every commit** — codify `git branch --show-current` as a pre-commit step in the stacked-PR/babysit workflow docs (see Surprising #3).

### Permission Prompts Hit

All were sandbox auto-refusals with immediate adaptation (no user-wait stalls):

1. `source …` in compound commands (worktree sandbox) — adapted to `.venv/bin/python -m …` and `bash -c` wrappers; recurring, ~5 occurrences.
2. `git reset --hard <branch>` — denied; `merge --ff-only` used instead.
3. `rm -rf <scratchpad-subdir>` — denied even inside the scratchpad; fresh subdirectory used.
4. `for … done` loops over `gh api graphql` — command-complexity refusal; split into separate calls.

None are allow-list candidates — they are worktree-isolation guardrails; the adaptations are cheap.

### Process Actions Taken

- [ ] patterns.yml entry: apostrophes in heredocs inside `$( )` break bash 3.2 (cite this retro)
- [ ] Schedule KIT-0092 Parts A+C as agentive-kit 0.3.1 (Part B done in #116; break-once proof in the PR body)
- [ ] Phase 3 spec: anchor on `engine-consumer.sh --packaged`, packaged region bodies, `_parse_install_record`
- [ ] feature-developer agent spec: reconcile Phase 9's `project move` with the worktree ordering rule
- [ ] Stacked-PR/babysit workflow docs: `git branch --show-current` before every fix commit
- [ ] Planner: commit this retro main-side; move task to 5-done; remove the KIT-0093 worktree + merged branches

### Incident Closure

1. **bash 3.2 heredoc/apostrophe parse failure** — triage-guide entry proposed as a patterns.yml defensive-coding rule (action item above); not doctor-checkable (a source-authoring hazard, not an environment state).
2. **Installed agentive CLI predating `agentive doctor`** — closed in-code: the door's tail detects a pre-0.3 CLI and prints `uv tool upgrade agentive-kit` instead of a misleading FAILURES verdict (#116).
3. **Packaged doctor silently defaulting without `kit_markers.py`** — closed in-code with tests (in-package record reader shared parser, unbalanced/lone markers fail loud, prose mentions exempt); the doctor's own unit tests now pin the behavior.
4. **Wrong-branch fix commit during stack babysitting** — triage-guide entry: the branch-verify step added to the loop prompts this session; durable home is the STACKED-PR-WORKFLOW doc (action item above).
