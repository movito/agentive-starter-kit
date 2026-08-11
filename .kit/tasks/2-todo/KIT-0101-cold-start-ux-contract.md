# KIT-0101: The cold-start UX contract — transparency headers, session-hop audit, completion checklist

**Status**: Todo
**Priority**: high (every finding operator-reported from live use,
2026-08-11; runs immediately after KIT-0100's mechanical cycle)
**Type**: UX design pass (canon prose + door tail + intake contract)
**Estimated Effort**: 1 day
**Created**: 2026-08-11
**Source**: split from KIT-0100 at promotion (review-surface budget) —
the FULL finding texts live in KIT-0100's spec as the source record:
its **F7** (commands self-explain before acting), **F9** (justify or
collapse the new-session hop), **F10** (completion is ONE verified
checklist + ONE command, with the operator-specified format and
binding rules)

> **Evaluation**: arch-review-fast REVISION_SUGGESTED 2026-08-11,
> three minor findings, all dispositioned DECLINED-as-designed — gate
> passed per the Oscillation protocol: (1) naming
> `test_scaffold_acceptance.py` concretely is the house
> verified-anchor style (anchors locate, the re-grep rule guards
> drift); (2) the Ground Rules block is citation-of-standing-policy,
> not inlined duplication — the pattern every post-#120 spec uses;
> (3) referencing KIT-0100's F7/F9/F10 text is the source-record
> split pattern (KIT-0099-FOLLOWUPS precedent) chosen at the
> review-surface split — self-containing would duplicate 60 lines of
> operator-authored finding text. Log:
> `.adversarial/logs/KIT-0101-cold-start-ux-contract--arch-review-fast.md`

## Requirements

- **R1 (= KIT-0100 F7)** — transparency-header pattern defined once,
  then swept across ALL user-invocable commands: first response opens
  with what-this-does, what it reads/writes where, and links to the
  command's GitHub source + relevant docs page. Internal skills
  (`user-invocable: false`) out of scope.
- **R2 (= KIT-0100 F9)** — session-hop audit of the /new-project →
  intake → planner journey: for each "open a new session" hop, either
  collapse it (the current session does the work inline) or keep it
  WITH a one-sentence stated reason (per-session agent identity; a
  different contract needs fresh context). The launcher-era
  persona-fragility rationale is dead (native --agent); do not cite it.
- **R3 (= KIT-0100 F10)** — the completion contract: the intake's
  Step 5 output becomes the operator-specified checklist (every ✓
  verified at print time; ✗ items inline with exact remedies; the
  single closing launch command carries the opening prompt and prints
  ONLY when doctor has no FAILs). Door side: a missing `agentive` CLI
  elevates to the headline next step in the tail. NOTE: the door tail
  and its contract strings are pinned by
  `tests/test_scaffold_acceptance.py` — changed strings update the
  pins in the same commit (the test header's own rule).
- **R4 — journey replay as acceptance** (the KIT-0078/0093
  tradition): re-run the cold-start journey — /setup-preset →
  /new-project → intake → first planner session — against the fixed
  surfaces; the 2026-08-11 friction points (silent starts, unexplained
  hops, contradictory endings) must be structurally impossible, not
  just absent.
- **Release**: rides the next plugin release after KIT-0100's 2.0.2
  (2.0.3, or bundled if 0100 hasn't shipped when this lands — the
  drift guard arbitrates as usual).

## Ground rules (standing policy, cited)

Review-surface budget (~500 prose lines — if the sweep exceeds it,
STOP and report for a further split); fast-tier-only + `--format
diff` (prose-shaped); circuit breaker; pair-identity test; every ✓/✗
claim and swept site grep-verified.

## Acceptance Criteria

- [ ] Header pattern documented once + present in every user-invocable
      command (grep-proven list in the PR)
- [ ] Every session hop in the journey either collapsed or reasoned
      in-text; no bare "open a new session with X"
- [ ] Completion checklist implemented per the F10 format + binding
      rules; scaffold-acceptance pins updated with it
- [ ] Journey replay recorded in the PR (transcript or step log)
- [ ] Budget held; release shipped per the drift-guard rhythm
