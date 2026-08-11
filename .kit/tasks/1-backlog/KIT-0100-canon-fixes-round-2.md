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
- **Release 2.0.2**: the mechanical resync per the KIT-0099 recipe
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
