## KIT-0096 — Plugin release refresh: agentive-workflow 2.0.0 (kit PR #119 + agentive-skills PR #4)

**Date**: 2026-08-09
**Agent**: feature-developer-f5
**Mode**: single-repo (kit) + second repo for the release (movito/agentive-skills — cloned, branched, PR'd per handoff)
**Scorecard**: 30 threads (7 kit + 23 marketplace), 3 regressions, 5 fix rounds (2 kit bot + 1 marketplace bot + 2 evaluator), 11 commits (8 + 3)
**Released**: agentive-workflow 2.0.0 (installed 1.1.0 → 2.0.0 verified; drift guard red → green around the release, live)

### What Worked

1. **Diffing fresh kit copies against the 1.1.0 plugin copies as a transform map** — one `git diff` per file surfaced BOTH directions: the transforms to re-apply (namespacing, ASK-XXXX→TASK-ID, Serena de-hardcode) AND plugin-side hardening the kit canonical had lost (`check-ci` dynamic-branch warning, ci-checker's Cross-Repo Mode section). Two real consumer regressions prevented before any reviewer saw them; claude-code's HIGH finding confirmed the first one independently.
2. **Bulk edits as scripts with exact-match assertions** (`generalize_fd.py` etc., count-asserted `str.replace` + region replace) — the asserts caught two would-be silent failures pre-write: the kit-name leak in the CROSS-REPO parenthetical, and my own `"ASK-" not in "TASK-ID"` substring bug. Twenty-seven files transformed with zero transform findings from 6 evaluator runs + 2 bot fleets.
3. **Sha-anchored roster + drift guard proved itself same-day** — falsified twice pre-merge (pytest AC + live scratch-tree run), then the real release exercised the full designed loop: guard red on 404 → marketplace merge → local exit 0 → PR check green. The June→August staleness class now has a machine answer.
4. **Out-of-scope discipline on 42 content findings** (19 evaluator + 23 bot, ALL targeting kit-canonical text) — declining to patch them into plugin copies and routing them to KIT-0097 preserved the sha-anchor invariant on day one; CodeRabbit's own "fix in agentive-starter-kit first" learnings endorsed the routing on five threads.

### What Was Surprising

1. **The handoff's "no bots are configured on that repo" was false** — BugBot + CodeRabbit both ran on agentive-skills#4 and produced 23 threads. An environmental claim shipped unverified in the same handoff that carries the cite-don't-restate rule; one `gh api` call would have caught it.
2. **Kit canonical had regressed BEHIND the 1.1.0 plugin in two places** — drift ran both directions, not just plugin-stale. The task's framing ("plugin is two generations behind") was true but incomplete; the 1.x distribution genericizations (7bf230a era) never made it back upstream.
3. **Zero of 42 content findings hit the actual change** — on a refresh PR, evaluators and bots review the CONTENT as if newly authored, not the delta semantics; `--format diff` reduced noise but cannot stop content-shaped review of a content-shaped diff. Plan for it: the review budget on release PRs is spent on upstream defects.
4. **pre-commit pytest-fast runs 213–234 s in this worktree** (docs say ~11 s; KIT-0057 measured ~70 s) — my first commit attempt died on the Bash tool's 2-minute default timeout mid-hook, exactly the KIT-0057 aborted-commit shape; the verify-after-hook reflex (`git log -1` + `git status`) caught it. Suite has grown ~1,141 fast-marked tests.
5. **`claude plugin update agentive-workflow` (bare name) errors** — only the full `agentive-workflow@agentive-skills` form resolves. The upgrader agent's runbook already uses the full form everywhere, so the docs were right and my shortcut was wrong; worth one gotcha line so nobody re-learns it.

### What Should Change

1. **Bot-presence claims in handoffs must cite a query** — extend planner.md Phase 4's environmental-claims rule with bot presence as a named example (`gh api repos/<o>/<n>/... | check for coderabbit/cursor activity`); "no bots there" changed this session's whole Phase 6 plan for PR #4 and was wrong.
2. **Fix the pytest-fast duration story** — either re-scope the fast marker set back toward the documented budget or update the stack-notes/COMMIT-PROTOCOL numbers, and state the agent-side rule: Bash timeout ≥ 360 s for any kit commit. Three commits this session each cost ~3.5 min of hook wall-clock.
3. **Release PRs should pre-file the upstream-findings task** — KIT-0097 was created reactively after 23 threads landed; the next content refresh (2.0.1) should open with an empty "found-in-review → fix-at-source" task referenced in the PR body, so triage is one reply per thread from minute one.
4. **Phase 9 move+stage needs a single sequence** — the `project move` old-path deletion landed unstaged despite the documented footgun (planner footgun list, item "project move invalidates…"); I only caught it in the post-commit status check. One helper (`project move --commit`) or an explicit two-line recipe in the feature-developer Phase 9 would end the recurrence. (Candidate rider for KIT-0097's feature-developer edits.)

### Permission Prompts Hit

None. All git/gh/python calls ran without permission stalls in this session (worktree + scratchpad flows).

### Process Actions Taken

- [ ] KIT-0097 evaluated and scheduled (planner; task filed on merged main, operator wants it asap; then plugin 2.0.1 — first merged fix flips the drift guard red by design)
- [ ] planner.md Phase 4: add bot-presence to the environmental-claims examples (can ride KIT-0097's planner edits)
- [ ] pytest-fast duration: re-scope markers or correct the documented budget; record the ≥360 s Bash-timeout rule for kit commits
- [ ] Phase 9 move+stage recipe (candidate rider on KIT-0097 F6)
- [ ] PII email in plugin.json/marketplace.json: operator decision at 2.0.1
- [ ] KIT-0075 F4: interactive launch-habit observation pending the operator's first real session in a plugin-only project (headless resolution evidence posted on agentive-skills#4)
- [ ] chmod 600 the kit worktree's .env (door warned during the F5 test run)

### Incident Closure

1. **False "no bots" handoff claim** → **triage-guide entry**: planner.md Phase 4 environmental-claims bullet gains the bot-presence example (rides KIT-0097's planner-adjacent edits; the kit-repo doctor's `80-bot-presence.sh` can't see other repos, so the check belongs at handoff-authoring time).
2. **pytest-fast 213 s vs documented ~11 s (timeout-killed commit)** → **triage-guide entry**: COMMIT-PROTOCOL.md / kit stack-notes get the real duration + the ≥360 s tool-timeout rule; symptom→cause: "commit appears to hang / tool timeout mid-hook → pytest-fast tail, verify with git log -1 + git status" (extends the existing KIT-0057 note with current numbers).
3. **Bare `claude plugin update <name>` fails without `@marketplace`** → **triage-guide entry**: docs/PLUGIN-UPGRADE-GUIDE.md § Gotchas one-liner (upgrader agent already uses the full form; the guide is its spec).
4. **Kit worktree .env at mode 755** → closed by existing check: the setup door's mode warning fired and named the exact remedy — no new check needed, operator action listed above.
