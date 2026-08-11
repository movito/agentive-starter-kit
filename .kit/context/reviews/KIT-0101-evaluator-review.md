# KIT-0101 — Evaluator Review Record (PR 1: R1–R4)

**Date**: 2026-08-11
**Input**: `.adversarial/inputs/KIT-0101-code-review-input.md`
(`--format diff` — prose-dominated sweep per the handoff's policy)
**Tier**: `code-reviewer-fast` ONLY — the deep tier
(`code-reviewer`, `claude-code`) is **skipped by planner policy**
(handoff "Test approach": fast-tier-only on this journey's
prose-shaped diffs; KIT-0069/KIT-0073 precedent — the deep tier's
spend buys nothing on prose sweeps). This record IS the Gate 5
artifact; tree-grounded verification before merge is the real gate
for this PR shape (bots + the R4 journey replay in the PR body).
**Log**: `.adversarial/logs/KIT-0101-code-review-input--code-reviewer-fast.md`
**Verdict**: CONCERNS — 3 findings, all dispositioned below.
Per the prose-sweep rule, each was reproduced against the tree
before disposition; none survived.

## Findings and dispositions

1. **[ROBUSTNESS] "intake infers doctor pass/fail by grepping
   [PASS]/[FAIL] strings — brittle"** — **DECLINED (misreads
   unchanged code)**. Verified against the tree: `run_doctor_tail`
   derives its verdict from doctor's EXIT CODE
   (`case "$doctor_exit"`, `scripts/local/bootstrap:924` — the
   KIT-0046 F3 exit contract), not from output strings, and the
   intake reads the relayed `Doctor verdict:` line the door prints
   from that code. The evaluator reconstructed the unchanged
   function from a diff-only input — the exact KIT-0069 failure
   mode this record's tier policy anticipates.

2. **[ROBUSTNESS] "printed install instructions might fail when the
   user runs them"** — **DECLINED (by design)**. The KIT-0083
   degradation pattern: when a dependency is absent the door cannot
   execute the remedy, so it verifies-or-instructs, never assumes
   and never hard-fails. A door that tried to run `uv tool install`
   on the operator's behalf is out of scope and contrary to the
   pattern the tests pin.

3. **[TESTING] "no pytest coverage of the intake agent's composed
   Step 5 output"** — **DECLINED (not machine-testable; covered by
   R4)**. `project-intake` is an agent prose body — its composed
   LLM output cannot be asserted in pytest. The task designates the
   journey replay (R4) as the acceptance mechanism for exactly this
   surface; the replay step log is recorded in the PR body. The
   door-side halves of the contract ARE pinned
   (`test_scaffold_acceptance.py` headline assertion,
   `test_setup_door.py` forced-missing-CLI test).

## Notes

- One deliberate deviation from the F10 mock, flagged (not silent):
  the closing launch command uses `claude --agent planner` (the
  journey's consistent agent name across `new-project.md`,
  `STARTING-A-PROJECT.md`, and scaffold seeds) where the operator's
  mock showed `planner-f5`. Same opening prompt, same format rules.
  Planner may override.
