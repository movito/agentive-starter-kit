## KIT-0105 — project-intake ships in the plugin (kit #133 + #134, agentive-skills #11)

**Date**: 2026-08-15
**Agent**: feature-developer-f5
**Mode**: single-repo (kit) + marketplace repo via `git -C` (the KIT-0109/0110 precedent)
**Scorecard**: 13 threads (2 + 6 + 5), 1 regression, 5 fix rounds (1 + 3 + 1), 12 commits (4 + 6 + 2)
**Shipped**: agentive-workflow **2.1.0** (merge `3848b64`), 28 components (+project-intake); drift guard GREEN on kit main post-release; KIT-0110's open AC closed (first `plugin_resync.py` cut); passengers KIT-0112 complete + KIT-0103 R1 done.

### What Worked

1. **The tooled cut earned its keep on release one** — `plugin_resync.py` computed the 7-component delta exactly (matching my hand-derived version list), surfaced the 3 published-adaptation conflicts loudly instead of clobbering them, and left the roster hash columns machine-true (`verify_plugin_integrity.py`: 28/28 before the PR even opened). The KIT-0110 design (surface-never-solve conflicts) was validated by real divergent bodies.
2. **Falsify-both-arms before shipping the query** — running retro.md's new fail-closed jq against live PRs (clean page → count, forced truncation → REFUSED + exit 1) caught nothing the first time but made BugBot's endCursor-placeholder finding a 5-minute fix with instant re-verification. This retro itself then dogfooded the shipped query for its own scorecard.
3. **Widened class grep beat the original class definition** — the planner's gate caught self-review item 8's dead anchors because my R1 grep keyed on command names only; re-defining the class as "contract-anchor citations" and re-sweeping found item 9's two dead references the planner's own grep had ALSO missed. The class-definition iteration is where the value was.
4. **Evaluator-before-PR held the bot-round budget** — every PR came in at exactly one substantive bot round (PR 2's extra rounds were sequential single-finding rounds, not sieges); claude-code's PR 1 polish items (capture_output, comment pins) pre-empted plausible bot threads.
5. **reviewThreads-first discipline paid out four face-sightings** — fourth face (CodeRabbit `pass` over CHANGES_REQUESTED) and sixth face (BugBot `skipping` while posting a Medium) both reproduced live ON THE PR THAT DOCUMENTS THE FACES; SHA-matching caught two stale APPROVEDs that check-status alone would have accepted.

### What Was Surprising

1. **The drift guard passed on PR 1** — `ships: false` files don't count toward drift, so the expected-red window only opened at PR 2's rostered-file edits, not at the agent rewrite. The three-PR plan had budgeted justification lines for both kit PRs; only one needed it.
2. **CodeRabbit enforced this PR's own rule against its own records** — the round-3 finding on the review starter ("gate table reads fully cleared while planner verification was pending") is the KIT-0112 completeness spirit applied to our process artifacts. Bots reviewing the bookkeeping is a real second gate.
3. **`npm install` walked out of the repo** — with no package.json in the marketplace checkout, npm resolved the OPERATOR'S HOME `~/package.json` and installed there. Caught immediately (ls of expected outputs), uninstalled the exact addition, re-ran with an explicit manifest. A repo without a Node manifest is not a safe npm CWD.
4. **A stale roster column corrected itself by accident, then almost got un-corrected** — the global `2.0.4→2.1.0` perl swept planner's `kit_version` column; I "restored" it before checking, then hash-verification showed the swept value was actually RIGHT (the column had been stale since a prior release; resync only refreshes columns on merged entries). Verify before reverting, not just before applying.
5. **The published adaptations made three-way merge conflicts structural, not incidental** — any kit edit inside a region the published copy replaces (fd project-context, self-review's dropped item) will conflict on EVERY future resync. That's by design (the tool surfaces them), but the resolver must know the adaptation layer to resolve correctly.

### What Should Change

1. **`plugin_resync.py` should refresh stale kit_version columns on `--hashes-only`** — it recomputes `plugin_sha256` for all shipped entries but leaves `kit_version` untouched unless the entry merges, which is how planner's column sat wrong across a release. One-line widening; cite this retro.
2. **Publish-adaptation manifest** — the three adapted components (fd, fd-f5, self-review) should be listed somewhere machine-readable (roster field or a comment block) naming WHAT the adaptation is, so a future resolver doesn't rediscover it from conflict markers. Could ride the resync tool's conflict message ("this component carries a known adaptation: …").
3. **review-input helper needs `--repo-root`/`--output`** — third hand-assembled marketplace review input in three releases (KIT-0109, KIT-0110, now KIT-0105). Already filed as the KIT-0103 rider; this is the third data point raising its priority.
4. **The R1-class lesson generalizes**: retirement sweeps must grep for *citations of the retired thing's internals* (function names, file paths, docstring references), not just its invocation names. Candidate patterns.yml widening under `fix_by_class_not_instance` or a sibling key.
5. **npm in manifest-less repos**: write the package.json BEFORE any `npm install` (or use `--prefix .`). Candidate one-liner for patterns.yml; the incident closure below records the class.

### Permission Prompts Hit

None that blocked work — the worktree's allowlist plus operator pre-approvals covered the full three-repo flow (kit worktree, marketplace via `git -C`, GraphQL mutations).

### Process Actions Taken

- [ ] Planner: cherry-pick kit-side commits from the worktree branch `feature/KIT-0105-pr2-canon-bundle` — `3fdceee` (PR 3 evaluator record) and the retro commit that follows — onto main at closeout
- [ ] Planner: file the ready-to-paste **project-intake hardening task** (quiet credential scan — CodeRabbit Critical on agentive-skills#11 thread `PRRT_kwDOSj0O5s6ZiCNh` — + post-seeding doctor; body in my gate report)
- [ ] Planner: widen **KIT-0103 R3** to pagination fail-closed in `review_input.py` / `check-bots.sh` / `preflight.py` (CodeRabbit on kit #134; all three verified bare `first: 100`)
- [ ] Planner: consider `plugin_resync.py` stale-column refresh + adaptation manifest (Should-Change 1–2)
- [ ] Planner: patterns.yml candidates — retired-internals citation grep; npm-needs-a-manifest
- [ ] Operator: update the local plugin install to 2.1.0
- [ ] Task moves: KIT-0105 → done; KIT-0112 → done (completed in PR 2); KIT-0103 stays backlog with R1 checked off (planner owns all moves)

### Incident Closure

1. **npm home-directory pollution** (marketplace, PR 3): `npm install --save-dev` in a manifest-less repo walked up to `~/package.json` and installed there. Undone same-minute (exact uninstall, verified clean). Closure: **triage-guide entry** — recorded HERE and proposed for patterns.yml (Should-Change 5): *in a repo without package.json, write the manifest first; npm resolves ancestor manifests silently.* Not doctor-checkable (the hazard is an action pattern, not environment state).
2. **Stale roster `kit_version` column** (planner entry, 2.0.4-recorded vs 2.1.0-actual): drift guard and integrity check both key on hashes, so a wrong version column is invisible to every existing check. Closure: **escalated — awaiting planner classification**. (a) What happened: planner's `kit_version` sat one version behind its own body across ≥1 release; found only by an accidental sed sweep + hash verification. (b) Why not 1–3: a kit doctor check can't see the marketplace roster (cross-repo, network); a not-checkable note has no natural home kit-side; a triage guide entry doesn't prevent recurrence. (c) Question for the planner: should `verify_plugin_integrity.py` (marketplace CI, already reads both columns) additionally assert `kit_version` == the version frontmatter INSIDE the published body it already hashes — closing the column-drift class in the required check — or is that the resync tool's job (Should-Change 1)?
3. **Kit-side record commit re-created a deleted remote branch** (my push of `3fdceee` post-merge): self-caught, remote branch re-deleted, commit held locally for cherry-pick. Closure: **triage-guide entry** — recorded here: *after a train PR merges, the worktree branch is a dead end for pushes; kit-side artifacts produced during a later PR belong to the planner's main-side bookkeeping (hand them off, don't push them).*
