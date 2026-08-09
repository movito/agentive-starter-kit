# KIT-0097: Canonical .claude/ content fixes from the 2.0.0 plugin-release review

**Status**: Backlog
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

- [ ] **F1 — Ordering contradiction (BugBot HIGH + CR ×2, threads T1/T9/T12)**:
      the Workflow Overview table (Ship=5, CI+Bots=6, Evaluator=7) and the
      task-flow line (`… → PR → bots → evaluator → …`) contradict the
      Phase-7 ordering rule (KIT-0035/KIT-0046: trio BEFORE PR open).
      Renumber/reorder the table and flow line to the pre-PR order and fix
      the phase cross-references (preflight/handoff). This is the
      highest-value fix: agents that follow the table burn bot rounds.
- [ ] **F2 — "Never push without verifying CI" restriction (CR, T11)**
      literally forbids the initial Phase-5 push. Requalify: no completion /
      follow-up push without green CI; the initial PR push is the thing CI
      runs ON.
- [ ] **F3 — Phase 7 still documents `scripts/core/*review*` probing + raw
      `GIT_TARGET diff` input (BugBot T3, CR T13)** while the canonical path
      is `agentive review-input` (full-file context, cross-repo aware).
      Also note T13's point: `git diff main...HEAD` misses uncommitted
      changes — state that the tree must be committed before input
      generation (or use the helper, which enforces it).
- [ ] **F4 — Split-mode routing gaps (CR T7/T10)**: Phase 1's verification
      and KIT-0057 post-hook checks use bare `git` (fine for the worktree
      the session sits in — but say so explicitly); planning-repo commands
      (`cat .kit/tasks/...`, `./scripts/core/project start`) use relative
      paths that break from a target-repo worktree in split mode — derive a
      planning-repo path from the handoff/CLAUDE.md and use it.
- [ ] **F5 — Ship-phase black/isort mandate (CR T8)** conflicts with the
      project-owned-stack principle: scope the pre-format instruction to
      "the project's own formatter (read from CLAUDE.md)" and keep the
      portable mutating-hook warning.
- [ ] **F6 — Phase 9 `project move` wording (BugBot T4)**: clarify the
      single-repo worktree case (branch-safe, KIT-0093) vs split mode
      (planning repo owns `.kit/tasks/` — the move never runs via
      GIT_TARGET).

### .claude/agents/document-reviewer.md + security-reviewer.md

- [ ] **F7 — `tools:` frontmatter omits Bash and Write (CR Major, T6)**
      while the bodies mandate running `adversarial`/CI commands and
      writing reports/handoffs. Either add the tools or trim the
      instructions — decide deliberately (adding Bash to review agents
      widens their blast radius; the ci-checker header shows the
      Task-tool/Bash permission interaction to consider).

### .claude/agents/ci-checker.md

- [ ] **F8 — Backport the plugin's Cross-Repo Mode section** (present in
      plugin 1.1.0 AND 2.0.0, absent from kit canonical — KIT-0096
      evaluator round).
- [ ] **F9 — Skip the origin/default-repo mismatch check in split mode
      (CR T5)**: detect `## Target Repository` first; the planning-repo
      origin legitimately differs (check-ci.md already documents this).

### .claude/agents/code-reviewer.md, test-runner.md, document-reviewer.md, security-reviewer.md

- [ ] **F10 — Backport the `check-ci` de-hardcode** (KIT-0096 evaluator
      round; fixed in plugin copies only): `/check-ci main` verifies the
      base branch, not the change — restore dynamic branch detection +
      warning comment (the pre-KIT-0067 plugin had it; kit canonical
      regressed). Also ASK-XXXX → TASK-ID and the Serena hardcode in
      code-reviewer/test-runner if the kit wants parity with the shipped
      genericization.

### .claude/agents/test-runner.md

- [ ] **F11 — Unconditional `project start` as first action (CR T14)**:
      check task status + session topology first; only start from the
      planning repo on main when the task is still in 2-todo (mirror the
      feature-developer verify-never-create discipline).

### .claude/agents/upgrader.md

- [ ] **F12 — CHANGELOG/ref resolution (CR T15)**: Phase 2a fetches
      `ref=main` for "the new version's CHANGELOG" and the 404 fallback
      always prepends `v` to refs; resolve/validate the target ref once and
      reuse it for both paths.
- [ ] **F13 — Rollback cannot pin the previous version (CR T16)**:
      `claude plugin update` resolves marketplace-latest, not `<previous>`;
      make the rollback section verify `claude plugin list` shows the
      previous version before restamping Provenance, and state plainly when
      rollback requires cache restoration / operator intervention.

### .claude/commands/

- [ ] **F14 — check-ci.md (BugBot T2 + CR T18)**: the manual-dispatch
      recovery (`gh workflow run test.yml --ref`) ignores cross-repo mode
      (needs `--repo <target>`) and hardcodes `test.yml` (resolve the
      workflow at runtime or take it as an argument).
- [ ] **F15 — check-spec.md (CR T19)**: route changed-file discovery
      through the target repo in split mode (`git -C <target_path>`, real
      merge base instead of assumed local `main`).
- [ ] **F16 — preflight.md (CR T20)**: the override example omits the
      required `--task` flag: `agentive preflight --repo owner/name --pr
      PR_NUMBER --task TASK-ID`.
- [ ] **F17 — retro.md (CR T21)**: "let the planner decide" is an
      unclassified-incident escape hatch; either block completion until one
      of the three closure outcomes exists or define planner escalation as
      a persisted closure state.
- [ ] **F18 — wrap-up.md (CR T22)**: the summary block prints
      `Task … — COMPLETE` unconditionally, contradicting the
      unmerged-stays-in-review rule; add merged/unmerged variants.
- [ ] **F19 — babysit-pr.md (CR Minor, T17)**: MD029 ordered-list prefix
      (`6.` in a `1.`-style file) — reconcile with the KIT-0094 MD029
      decision before changing; if the decision says keep, record decline.

### .claude/skills/code-review-evaluator/SKILL.md

- [ ] **F20 — No-API-key path bypasses the gate (CR T23)**: the
      degraded-mode text lets a session proceed to human review on a
      documented failure; require an explicit failed/skipped record +
      coordinator approval, or stop.
- [ ] **F21 — Ordering-language sweep (CR T12 second half)**: remove stale
      post-bot phrasing so the skill states the single pre-PR order.

## Acceptance Criteria

- [ ] All checkboxes above fixed in kit canonical `.claude/` (or
      explicitly declined with rationale in the PR — e.g. F19 per the
      KIT-0094 decision)
- [ ] feature-developer and planner pairs re-synced (bodies identical,
      versions bumped)
- [ ] `tests/test_agent_contracts.py` still green; new contract pins added
      where a fix creates a sentinel worth pinning (e.g. F1 ordering)
- [ ] Plugin release 2.0.1 cut afterward (separate release step): changed
      files refreshed into movito/agentive-skills, roster.yaml hashes
      updated, drift guard back to green — thread replies on PR #4
      reference this task as the closure path

## Out of Scope

- Editing plugin copies in movito/agentive-skills directly (release-only)
- The drift guard / release machinery (KIT-0096's, already shipped)
- Behavioral redesign beyond the cited findings
