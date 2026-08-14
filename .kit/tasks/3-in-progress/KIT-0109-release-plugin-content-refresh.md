# KIT-0109: Plugin release — resync the 20-component drift set, guard to green

**Status**: In Progress
**Priority**: high — the drift guard has been red on kit main since
2026-08-12; the cadence rule adopted 2026-08-14 (`plugin-drift.yml`
header) makes this a standing release obligation, already past its
same/next-day window
**Type**: Release (mechanical)
**Estimated Effort**: 1-2 h + bot rounds
**Created**: 2026-08-14
**Source**: KIT-ADR-0034 release obligation (the legitimate generator
class); KIT-0104 PR 3 retro escalation → operator posture ruling
2026-08-14 (guard stays required; cadence is the remedy)
**Evaluation**: skipped (planner) — mechanical release; mechanics are
the KIT-0099 recipe verbatim, precedent twice-run (2.0.0, 2.0.1)

## Scope

The KIT-0099 release recipe, run against today's canon
(kit main `1cb8c52`):

1. **R1 — the work list is the guard's own output, re-derived at
   session start.** `python3 scripts/local/check_plugin_drift.py` on
   kit main listed **20 stale components** on 2026-08-14 (10 agents:
   feature-developer ×2 variants, planner ×2, ci-checker,
   code-reviewer, test-runner, document-reviewer, security-reviewer,
   upgrader; 5 commands: babysit-pr, check-ci, retro, triage-threads,
   wrap-up; 5 skills: bot-triage, code-review-evaluator,
   pre-implementation, review-handoff, self-review). Re-run before
   starting — kit main may have moved. **Derive the delta from
   roster.yaml's recorded hashes, never from `git diff`** (KIT-0099
   method note: git-only derivation would have shipped two stale
   agents).
2. **R2 — refresh into `~/Github/agentive-skills`
   `plugins/agentive-workflow/`** per the KIT-0096 transforms
   (KIT-LOCAL regions don't ship). Membership is UNCHANGED — 20
   refreshes, zero additions/removals (verify this claim against the
   drift output at session start).
3. **R3 — roster.yaml hashes updated; ALL version fields bumped
   consistently** (KIT-0099 outcome: four version fields). Expected
   bump: **patch** (membership-identical resync, the 2.0.1
   precedent) — verify the published version and the roster header's
   versioning rule before choosing; a membership change would mean
   minor.
4. **R4 — marketplace PR** (CodeRabbit reviews there — verified on
   agentive-skills#4/#5). **Fix-here-then-release contract
   (KIT-0097)**: any bot finding against canonical CONTENT is filed
   kit-side (follow-ups file, like KIT-0099's 6), never patched
   plugin-side — a plugin-only edit re-opens drift. Fixes to the
   TRANSFORM itself are in-scope on the branch. Operator merges.
5. **R5 — verify end-to-end**: drift guard GREEN on kit main
   (`gh workflow run` "Plugin Drift Guard" `--ref main`, cite the
   run); `claude plugin marketplace update agentive-skills` +
   `claude plugin update agentive-workflow@agentive-skills` lands the
   new version (`claude plugin list` output quoted); closure noted on
   the release PR.

## Acceptance Criteria

- [ ] Delta derived from roster hashes at session start; count and
      membership claim verified against the live guard output
- [ ] All stale components resynced; roster hashes match the shipped
      content; all version fields consistent
- [ ] Release PR merged (operator); every bot thread replied +
      resolved; content findings routed kit-side, not patched in place
- [ ] Drift guard green on kit main — run link in the completion note
- [ ] New version installed and verified locally (`claude plugin list`
      quoted)

## Notes

- **Release PRs get reviewed as freshly-authored content** (KIT-0096
  insight: 42 findings, all on canonical text) — budget bot rounds for
  content findings and route them per R4; CodeRabbit has twice
  independently endorsed the kit-side routing.
- CHANGELOG: keep explicit empty categories — the `upgrader` agent
  fetches it to compute reconcile diffs (KIT-0099, fixed on #5).
- This release does NOT wait for KIT-0105/KIT-0103-R1 — they get their
  own train per the cadence rule (two small releases beat one late
  one; deliberate planner sequencing 2026-08-13/14).
- The drift set includes today's planner-pair checklist contract
  (template v2.1.0) and the bot-triage sixth face — consumer projects
  get both on update.
