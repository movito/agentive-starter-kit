# KIT-0100: Canon fixes round 2 — the 2.0.1 follow-ups + plugin 2.0.2

**Status**: Backlog
**Priority**: medium-high (six verified advisory defects, two
pair-rule-bound; promote as the next canon cycle — after the
operator's new-project test, or sooner if a defect bites)
**Type**: Content fixes + patch release
**Estimated Effort**: 0.5 day
**Created**: 2026-08-11
**Source**: `.kit/context/KIT-0099-KIT-FOLLOWUPS.md` — the finding
list IS the spec (six items, each verified against kit canon before
filing, with suggested fixes; CodeRabbit independently endorsed the
fix-here-then-release routing twice)
**Evaluation**: skipped (planner) — enumerated fixes with verified
anchors and suggested shapes; the KIT-0092/0099 precedent class

## Scope

- **F1–F6**: the six items in the follow-ups file, verbatim — stale
  Phase-6 refs (pair rule), `gh run watch` timeout wrapper, the
  `--allow-empty` dirty-index guard (cite the self-review scoped-
  staging rule), evaluator fallback tier containment, Step 2 snippet
  pointing at the tier rule (pair rule), wrap-up's unverified
  review-starter path. Re-verify each anchor before fixing (files
  have moved before).
- **F7 — commands self-explain before acting (operator feedback,
  2026-08-11, live during /setup-preset)**: "I'm just typing a command
  and seeing stuff happen … the interaction requires me to be fully
  aware of what the command contains." Every USER-INVOCABLE command
  (setup-preset, new-project, start-task, status, preflight, retro,
  wrap-up, …) opens its first response with a standard transparency
  header: one line of what-this-does, what it will read/write and
  where, and a link to the explainer — the command's own source on
  GitHub plus the relevant docs page (e.g. STARTING-A-PROJECT for
  door-adjacent commands). Pattern definition + sweep across the
  user-invocable set; internal skills (user-invocable: false) are out
  of scope. KIT-0078-family finding (cold-start transparency).
- **F8 — interview-first agent launches carry the opening prompt
  (operator hit live, 2026-08-11, native /new-project test)**: a
  session cannot speak first, so every instruction that sends the
  operator to an interview-first agent (project-intake, any
  FIRST-TURN-CONTRACT agent) must include the initial message in the
  launch command — `claude --agent project-intake "Begin the
  intake."` — or state "the agent waits for your first message; type
  begin". Sweep: new-project.md's session-handoff instructions, any
  starter/handoff text that says "open a session with <agent>", and a
  note in the FIRST-TURN CONTRACT blocks themselves acknowledging the
  contract fires on the first USER message (the launch instruction
  owns the gap). This is the KIT-0075 2026-07-29 silent-start
  incident reproduced under native launch — the launch-instruction
  fix shape is now confirmed; cross-reference it there.
- **F9 — justify or collapse the new-session hop (operator, same
  test)**: "it isn't clear why I can't just keep working in the
  session that I ran /new-project in." The hard reason (launcher-era
  persona fragility) died with native --agent; what remains is
  fixed-at-launch agent identity + role isolation. Decide per hop:
  where the current session CAN do the next step, the flow does it
  inline; where a fresh session is genuinely required, the
  instruction says WHY in one sentence (identity is per-session;
  fresh context for a different contract). new-project.md is the
  primary surface. KIT-0078-family (cold-start journey); the journey
  replays must be re-run against the fix.
- **F10 — the intake must not end "ready" while the door left
  outstanding instructions (operator hit live, 2026-08-11, first real
  packaged intake)**: the door correctly printed "install the
  lifecycle CLI" (agentive-kit was never globally installed — the kit
  repo's in-tree source masked the gap), but the intake's completion
  summary said "Next action: open a planner tab … start from the
  backlog" with no mention of it — two true statements reading as a
  contradiction, and the missing CLI silently cascaded (evaluator
  install couldn't run; TASK_PREFIX unset). Fixes: (a) the intake's
  Step 5 summary must RELAY the door's doctor tail + any printed
  install commands verbatim (the kit-side spec already says this —
  verify the plugin body kept it) and must not print a
  ready-to-plan next action while the doctor has FAILs — instead:
  "resolve these, re-run `agentive doctor`, THEN open the planner";
  (b) the door's final tail should elevate a missing `agentive` CLI
  from an inline notice to the headline next step (it is the one gap
  that cascades). Resolved live: CLI installed, evaluators
  provisioned, prefix set, doctor 10/0/0.

  **Output format (operator-specified, 2026-08-11)** — the completion
  summary is ONE checklist ending in ONE command:

  ```
  ✓ Read the handoff brief
  ✓ Created the repo (+ GitHub: movito/<name>)
  ✓ Seeded .env from your preset
  ✓ Installed the evaluator library
  ✓ Verified the agentive CLI
  ✓ Verified the agentive-workflow plugin
  ✗ <anything outstanding> — run: <exact remedy command>

  You can now start working on <PROJECT NAME>. Open a new terminal
  tab in <path> and paste:

  claude --agent planner-f5 "Triage the backlog and recommend what to start."
  ```

  Binding rules for the format: every ✓ line is a VERIFIED claim
  (checked at print time, never assumed — the
  displayed_commands_are_contracts widening applies: any printed fact
  is a claim); failed/outstanding items appear IN the same list as ✗
  with the exact remedy, so "done" and "still needed" can never
  contradict across two messages; the closing command includes the
  opening prompt (F8) and appears ONLY when the doctor has no FAILs —
  otherwise the last line is the re-run instruction instead.
  (drift guard red-by-design between kit merge and tag — the
  established rhythm). The follow-ups' "also noted" README item is
  ALREADY handled (agentive-skills#6, 2026-08-11).

## Ground rules (all now standing policy — cited, not restated)

Review-surface budget (small — this is well under); fast-tier-only +
`--format diff` (prose-shaped); circuit breaker; pair-identity test
enforces the pair rule mechanically; every fix's end state
grep-verified (the sweep-completeness class).

## Acceptance Criteria

- [ ] Six fixes landed in canon (or declined with rationale), pair
      test green, anchors re-verified in the PR body
- [ ] 2.0.2 live; drift guard green; `claude plugin list` shows 2.0.2
- [ ] Follow-ups file marked closed with pointers (it stays as the
      record)
