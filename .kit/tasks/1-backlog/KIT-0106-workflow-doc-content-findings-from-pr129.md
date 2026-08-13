# KIT-0106: Workflow-doc content findings from PR #129's bot round

**Status**: Backlog
**Priority**: low — doc accuracy debt, none of it introduced by KIT-0104
**Type**: Documentation
**Estimated Effort**: 2-3 hours (one prose PR, tree-grounded verification per the prose-sweep rule)
**Created**: 2026-08-13
**Source**: CodeRabbit review on PR #129 (KIT-0104 PR 1) — the door's
packaged data store mirrors `.kit/context/workflows/` byte-identically,
which put the whole doc set in front of a reviewer for the first time
in a while. Every finding below is against PRE-EXISTING kit-tree
content; PR #129 only copied it. The sync guard
(`tests/test_door_data_sync.py`) means each fix lands in BOTH homes in
the same commit.

## Findings (thread-by-thread, from PR #129)

1. **COMMIT-PROTOCOL.md** — claims `ci-check.sh` runs "the same checks"
   as GitHub Actions with "100% confidence"; it deliberately runs a
   SUPERSET and GitHub verification stays required.
2. **TESTING-WORKFLOW.md** (two spots) — pre-commit fast-test command
   documented without `-v --tb=short -x --maxfail=3`; same
   superset/duration claim as above (15-30s vs measured 213-238s).
3. **STACKED-PR-WORKFLOW.md** (two spots) — close/reopen CI-nudge advice
   contradicts the later incident note; state ONE current retry rule
   (manual `gh workflow run --ref` dispatch). Branch replacement listed
   as a preferred fallback in one place and last-resort in another —
   state one order: operator relay → double merge → replacement last.
4. **TEMP-THEN-COMMIT-PATTERN.md** (two spots) — "every file or none"
   overclaims (staging-failure atomicity only; a failed `mv` mid-loop
   still partially commits); `rm -f "$DST/"*.tmp` sweeps unrelated
   temp files — scope cleanup to a run-specific prefix.
5. **ADR-CREATION-WORKFLOW.md** — three filename conventions
   (`NNNN-`, `ADR-NNNN-`, `KIT-ADR-NNNN-`) without a rule for which
   applies where.
6. **AGENT-CREATION-WORKFLOW.md** + **TASK-STARTER-TEMPLATE.md** —
   reference builder-only templates (AGENT-TEMPLATE.md,
   OPERATIONAL-RULES.md) that consumer scaffolds never receive.
7. **REVIEW-FIX-WORKFLOW.md** — MD040: ASCII-diagram fence has no
   language (` ```text `). Rides naturally with KIT-0094's
   markdownlint gate (KIT-0104 PR 3).
8. **checks-none.sh template** — "declares no local toolchain" is wrong
   for `single --profile none` (toolchain files may exist); say "this
   profile configures no project checks".
9. **checks-python.sh template** — unquoted `$PY_FILES` expansion into
   pattern_lint (whitespace/glob splitting); use an array. NOTE:
   portability rule applies — bash 3.2 has no `mapfile -d`; use a
   `while read -d ''` loop or `find -exec`.
10. **spec-compliance-input-template.md** — hardcodes
    `.kit/tasks/3-in-progress/`; review-time specs live in
    `4-in-review/` — reference the current status folder.
11. **adversarial config.yml comment block** — CodeRabbit flagged the
    pin-propagation commentary (thread on
    `door/data/adversarial/config.yml`); verify the comment matches
    `agentive install-evaluators`' actual pin resolution, and the
    EVALUATOR-LIBRARY-WORKFLOW.md description with it.

## Acceptance

- [ ] Each finding fixed in the kit-tree source AND its packaged copy
      (`agentive_kit/door/data/...`) in the same commit — the sync
      guard enforces this
- [ ] Prose-sweep review rule applies (fast evaluator only; planner
      tree-grounded verification is the gate)
- [ ] PR #129 threads cited in the PR body

## Notes

- Do NOT fold into KIT-0104 PR 3 wholesale: PR 3's scope is the
  factory-clone language sweep (F5/F6) + KIT-0094. Item 7 (MD040)
  lands there naturally; the rest is content correction with its own
  review surface. Planner sequences.
