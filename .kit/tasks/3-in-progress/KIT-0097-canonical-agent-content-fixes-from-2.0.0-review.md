# KIT-0097: Canonical .claude/ content fixes from the 2.0.0 plugin-release review

> **Evaluation**: arch-review-fast REVISION_SUGGESTED 2026-08-09 with a
> single minor finding (PII-rider placement), accepted via rationale in
> R2 — gate passed with disposition. (First run was an empty-response
> model flake; rerun succeeded.) Log:
> `.adversarial/logs/KIT-0097-canonical-agent-content-fixes-from-2.0.0-review--arch-review-fast.md`

**Status**: In Progress
**Priority**: high — operator requested asap follow-up (2026-08-09); every
finding below is live in the kit's canonical agents/commands/skills, and the
2.0.0 plugin ships them verbatim (behavior-parity rule, KIT-0096)
**Type**: Content / defect sweep
**Estimated Effort**: 0.5 day
**Created**: 2026-08-09
**Source**: Bot review of the 2.0.0 marketplace PR
(movito/agentive-skills#4 — 4 BugBot + 19 CodeRabbit findings, all
targeting kit-canonical content, zero targeting the release transforms)
plus 2 evaluator-round backport candidates. KIT-0096 correctly declined
to fix these in the plugin copies (spec out-of-scope: "behavior stays as
the kit repo defines it"; divergent marketplace edits re-create the
drift the release ended). Fix here, in the source, then cut plugin
2.0.1 — the KIT-0096 drift guard will go red on the first merged fix
and force the release, which is the designed flow.

## The fix-here-then-release contract

Every fix lands in the kit's canonical `.claude/` tree. NEVER patch
`movito/agentive-skills` directly (its README Maintenance section
forbids divergent edits). After merging: refresh the changed files into
the plugin per the release process (generalization transforms +
roster.yaml hash update + version bump 2.0.1).

## Findings, by file (thread links = movito/agentive-skills#4)

### .claude/agents/feature-developer.md + feature-developer-f5.md (edit BOTH — bodies stay in sync)

- [x] **F1 — Ordering contradiction (BugBot HIGH + CR ×2, threads T1/T9/T12)**:
      the Workflow Overview table (Ship=5, CI+Bots=6, Evaluator=7) and the
      task-flow line (`… → PR → bots → evaluator → …`) contradict the
      Phase-7 ordering rule (KIT-0035/KIT-0046: trio BEFORE PR open).
      Renumber/reorder the table and flow line to the pre-PR order and fix
      the phase cross-references (preflight/handoff). This is the
      highest-value fix: agents that follow the table burn bot rounds.
- [x] **F2 — "Never push without verifying CI" restriction (CR, T11)**
      literally forbids the initial Phase-5 push. Requalify: no completion /
      follow-up push without green CI; the initial PR push is the thing CI
      runs ON.
- [x] **F3 — Phase 7 still documents `scripts/core/*review*` probing + raw
      `GIT_TARGET diff` input (BugBot T3, CR T13)** while the canonical path
      is `agentive review-input` (full-file context, cross-repo aware).
      Also note T13's point: `git diff main...HEAD` misses uncommitted
      changes — state that the tree must be committed before input
      generation (or use the helper, which enforces it).
- [x] **F4 — Split-mode routing gaps (CR T7/T10)**: Phase 1's verification
      and KIT-0057 post-hook checks use bare `git` (fine for the worktree
      the session sits in — but say so explicitly); planning-repo commands
      (`cat .kit/tasks/...`, `./scripts/core/project start`) use relative
      paths that break from a target-repo worktree in split mode — derive a
      planning-repo path from the handoff/CLAUDE.md and use it.
- [x] **F5 — Ship-phase black/isort mandate (CR T8)** conflicts with the
      project-owned-stack principle: scope the pre-format instruction to
      "the project's own formatter (read from CLAUDE.md)" and keep the
      portable mutating-hook warning.
- [x] **F6 — Phase 9 `project move` wording (BugBot T4)**: clarify the
      single-repo worktree case (branch-safe, KIT-0093) vs split mode
      (planning repo owns `.kit/tasks/` — the move never runs via
      GIT_TARGET).

### .claude/agents/document-reviewer.md + security-reviewer.md

- [x] **F7 — `tools:` frontmatter omits Bash and Write (CR Major, T6)**
      while the bodies mandate running `adversarial`/CI commands and
      writing reports/handoffs. Either add the tools or trim the
      instructions — decide deliberately (adding Bash to review agents
      widens their blast radius; the ci-checker header shows the
      Task-tool/Bash permission interaction to consider).

### .claude/agents/ci-checker.md

- [x] **F8 — Backport the plugin's Cross-Repo Mode section** (present in
      plugin 1.1.0 AND 2.0.0, absent from kit canonical — KIT-0096
      evaluator round).
- [x] **F9 — Skip the origin/default-repo mismatch check in split mode
      (CR T5)**: detect `## Target Repository` first; the planning-repo
      origin legitimately differs (check-ci.md already documents this).

### .claude/agents/code-reviewer.md, test-runner.md, document-reviewer.md, security-reviewer.md

- [x] **F10 — Backport the `check-ci` de-hardcode** (KIT-0096 evaluator
      round; fixed in plugin copies only): `/check-ci main` verifies the
      base branch, not the change — restore dynamic branch detection +
      warning comment (the pre-KIT-0067 plugin had it; kit canonical
      regressed). Also ASK-XXXX → TASK-ID and the Serena hardcode in
      code-reviewer/test-runner if the kit wants parity with the shipped
      genericization.

### .claude/agents/test-runner.md

- [x] **F11 — Unconditional `project start` as first action (CR T14)**:
      check task status + session topology first; only start from the
      planning repo on main when the task is still in 2-todo (mirror the
      feature-developer verify-never-create discipline).

### .claude/agents/upgrader.md

- [x] **F12 — CHANGELOG/ref resolution (CR T15)**: Phase 2a fetches
      `ref=main` for "the new version's CHANGELOG" and the 404 fallback
      always prepends `v` to refs; resolve/validate the target ref once and
      reuse it for both paths.
- [x] **F13 — Rollback cannot pin the previous version (CR T16)**:
      `claude plugin update` resolves marketplace-latest, not `<previous>`;
      make the rollback section verify `claude plugin list` shows the
      previous version before restamping Provenance, and state plainly when
      rollback requires cache restoration / operator intervention.

### .claude/commands/

- [x] **F14 — check-ci.md (BugBot T2 + CR T18)**: the manual-dispatch
      recovery (`gh workflow run test.yml --ref`) ignores cross-repo mode
      (needs `--repo <target>`) and hardcodes `test.yml` (resolve the
      workflow at runtime or take it as an argument).
- [x] **F15 — check-spec.md (CR T19)**: route changed-file discovery
      through the target repo in split mode (`git -C <target_path>`, real
      merge base instead of assumed local `main`).
- [x] **F16 — preflight.md (CR T20)**: the override example omits the
      required `--task` flag: `agentive preflight --repo owner/name --pr
      PR_NUMBER --task TASK-ID`.
- [x] **F17 — retro.md (CR T21)**: "let the planner decide" is an
      unclassified-incident escape hatch; either block completion until one
      of the three closure outcomes exists or define planner escalation as
      a persisted closure state.
- [x] **F18 — wrap-up.md (CR T22)**: the summary block prints
      `Task … — COMPLETE` unconditionally, contradicting the
      unmerged-stays-in-review rule; add merged/unmerged variants.
- [x] **F19 — babysit-pr.md (CR Minor, T17)**: MD029 ordered-list prefix
      (`6.` in a `1.`-style file) — reconcile with the KIT-0094 MD029
      decision before changing; if the decision says keep, record decline.
      → **DECLINED, no change.** Verified against the file: the list is
      correctly sequential `1.`–`7.` (babysit-pr.md:94-110). CodeRabbit
      was linting numbering that only *looked* wrong inside the diff hunk
      — precisely the false-positive class KIT-0094 F1 says to decide
      once, centrally, rather than per-thread. Renumbering to satisfy it
      would break the actual sequence.

### .claude/skills/code-review-evaluator/SKILL.md

- [x] **F20 — No-API-key path bypasses the gate (CR T23)**: the
      degraded-mode text lets a session proceed to human review on a
      documented failure; require an explicit failed/skipped record +
      coordinator approval, or stop.
- [x] **F21 — Ordering-language sweep (CR T12 second half)**: remove stale
      post-bot phrasing so the skill states the single pre-PR order.

## Acceptance Criteria

- [x] All checkboxes above fixed in kit canonical `.claude/` (or
      explicitly declined with rationale in the PR — e.g. F19 per the
      KIT-0094 decision)
- [x] feature-developer and planner pairs re-synced (bodies identical,
      versions bumped)
- [x] `tests/test_agent_contracts.py` still green; new contract pins added
      where a fix creates a sentinel worth pinning (e.g. F1 ordering)
- [ ] Plugin release 2.0.1 cut afterward (separate release step): changed
      files refreshed into movito/agentive-skills, roster.yaml hashes
      updated, drift guard back to green — thread replies on PR #4
      reference this task as the closure path

## Second checklist — found in review on PR #120 (the pre-filed path)

Per the handoff: new findings on the fixed text append HERE as a second
checklist, not a new task. All in scope (each is a defect in a fix this
task made). Evaluator trio + 2 bot rounds; 30 findings total, 23
accepted, 7 declined. Full disposition:
`.kit/context/reviews/KIT-0097-evaluator-review.md`.

**Evaluator round (pre-PR, `--format diff`)**

- [x] **E1** — upgrader `TARGET_REF` probe left the version's dots
      unescaped, so a probe for `1.2.3` also accepted `"1X2X3"` (o3).
      Verified by hand before and after the fix.
- [x] **E2** — `$PLANNING` written as a shell variable, but each Bash
      tool call is a fresh shell: `"$PLANNING"/scripts/…` would silently
      become `/scripts/…` (claude-code HIGH).
- [x] **E3–E5** — ordering-pin hardening: at-most-one-match per phase
      prefix, whitespace-tolerant heading regex, cell-scoped table row.
- [x] **E16** — check-spec's new `git fetch` not routed through
      `-C "$TARGET"`, leaving the target's `origin/main` stale.
- [x] **E17** — upgrader rollback said "restore from that cache" with no
      command an agent could run, while its own rules forbid editing the
      cache. Now probes for a supported form, else operator intervention.
- [x] **E18** — pair duplication was a drift hazard enforced only by
      prose → new `test_agent_pair_bodies_stay_identical` contract test.

**Bot round 1 — the runnable-vs-prose class (BugBot ×2 + CodeRabbit)**

Both bots independently found that the *prose* said route through the
target repo while the *runnable snippet beside it* was bare — so the
F14/F15 fixes reproduced the bug they were fixing.

- [x] **B1** — check-spec: all code-side commands now `git -C "$TARGET"`;
      `TARGET` set in single-repo mode too, so one form is correct in
      both topologies. Default branch resolved, not assumed.
- [x] **B2** — upgrader `$CURRENT_REF` used but never set (F12 left the
      CURRENT side as prose). One `resolve_ref()` helper, called twice.
- [x] **B3** — upgrader ref probe ran BEFORE the idempotence gate, so a
      no-op re-run could halt on a network error.
- [x] **B4** — check-ci: explicit single-repo and cross-repo variants for
      `gh workflow list` and `gh workflow run`.
- [x] **B5** — ci-checker classified split mode from heading presence
      alone; now requires Path + GitHub, and stops on a malformed section.
- [x] **B6** — **F7 was half-applied**: both read-only reviewers still
      told the agent to run `adversarial` (needs Bash) and author handoff
      files + `agent-handoffs.json` (needs Write). Reworked to
      request-don't-run and supply-content-don't-author.
- [x] **B7** — `source .env` → worktree-safe POSIX-dot form (KIT-0091).
- [x] **B8** — Phase 5's "ALL tasks" contradicted the skill's skip
      policy. Ordering governs *when*, skip governs *whether*, and a skip
      needs its persisted record.
- [x] **B9** — retro said "one of three ways" while offering four.
- [x] **B10** — MD029 (retro, via the restructure) + MD040 fence.
- [x] **B11 — DECLINED ×2**: both wrap-up comments carried a severity
      header and analysis scripts but no finding body. Nothing stated to
      act on; recorded rather than guessing.

**Bot round 2 — BugBot on round 1's own fix**

- [x] **B12** — the new skip-record guidance used a relative
      `.kit/context/reviews/…` path, but Gate 5 reads the PLANNING repo:
      in split mode the record lands in the target worktree, is never
      found, and fails a gate the work satisfied. Same F4 class. Skip
      record AND Step 3 evaluator record routed through `"$PLANNING"`;
      Quick Reference now names the owning repo per artifact.

## Riders (KIT-0096 retro, added at promotion 2026-08-09)

- **R1 — Phase 9 move+stage recipe**: while fixing the workflow docs
  (F1's family), add the concrete recipe to feature-developer Phase 9:
  `project move <ID> in-review` relocates the task file, so the
  follow-up `git add` must name the NEW path — verify the staged set
  with `git status --short` before committing (the planner footgun,
  now needed implementer-side since moves ride PRs).
- **R2 — PII decision at the 2.0.1 release step**: `plugin.json` /
  `marketplace.json` carry the operator's personal email in `author`.
  Surface the choice in the release PR (keep, or switch to a
  noreply/org address) — operator decides, don't choose silently.
  Kept HERE rather than in a governance task because 2.0.1 IS this
  task's release step — the decision has exactly one natural moment,
  and a separate task for one field would be ceremony (evaluation
  finding, accepted via this rationale).
- (The planner bot-presence convention example was applied directly at
  KIT-0096 completion — no action here.)

## Out of Scope

- Editing plugin copies in movito/agentive-skills directly (release-only)
- The drift guard / release machinery (KIT-0096's, already shipped)
- Behavioral redesign beyond the cited findings
