# KIT-0113 Retro — project-intake hardening

**Date**: 2026-08-17
**Agent**: feature-developer (opus)
**Shipped**: `project-intake` 1.2.0 → 1.3.2 across kit PRs #135, #136,
#137; plugin release **2.1.1** (agentive-skills#12, `d0800f3`); drift
guard verified GREEN on kit main (run 31980414599 at `e75de7c`).

## What the task turned out to be

Filed as two fixes to one markdown file, estimated ~1h + release leg.
Delivered as three kit PRs and one release, because the first fix
introduced a shell gate and every subsequent round found a defect in
*that gate* rather than in the original scope.

| Round | Found | Class |
|-------|-------|-------|
| Evaluator (pre-PR) | non-0/1 exits undefined; doctor exit 1 overloaded | fail-open |
| Bots on #135 | ungated commit after scan; rescan false-pass; PEM claim false | fail-open |
| Bots on #136 | `add -A` unchecked; blocked branch returns 0; `set -e` kills CLEAN path | fail-open |
| Planner gate-check | 2.3 twin re-derived, inherited grep's INVERTED status | fail-open |
| Bots on #12 | `-I` skipped binaries; prose contradicted the gate | fail-open |

Fifteen findings, fourteen real. One declined (roster update requested
in the kit PR — roster is marketplace-side and resync must read kit
main first).

## What worked

- **Running commands instead of reasoning about them.** Every claim
  written into the agent body was executed first: the quiet scan, the
  inverted exit reading, the PEM fixture set, the `set -e` matrix, the
  binary bypass. Each measurement changed what got written; several
  contradicted what I was about to assert.
- **reviewThreads GraphQL as bot truth.** Check statuses lied three
  times this task — BugBot read `skipping` twice while its threads
  were already posted, and CodeRabbit's check read "Review in
  progress" after its review at head had landed.
- **Holding the release open.** All three kit PRs folded into one
  2.1.1 cut rather than shipping 2.1.1/2.1.2/2.1.3. Possible only
  because the release PR was held rather than merged at first green.
- **Not merging on inference at the end.** The drift guard does not
  re-run on kit main when the marketplace merges; its last recorded
  result was stale-red. Dispatching it explicitly is the only thing
  that produced a real green.

## What went wrong (mine)

1. **Dismissed a correct finding because of its framing.** The
   security evaluator raised binary-file coverage pre-PR; I filed it
   under "deployment policy question" in the unverifiable list rather
   than spending one `git grep` on it. It was a fail-open in the
   credential gate, and it shipped through two PRs before a bot
   re-found it. *A finding phrased as a question is still a finding.*
2. **Simplified away a reviewer's guard.** CodeRabbit proposed
   `|| scan=$?` on the first release round; I declined it as "a moving
   part without a job", reasoning that `case $?` immediately after the
   grep was equivalent. It is — except under `set -e`, which is
   exactly what it existed for. Restored two PRs later.
3. **Tested only the abort paths.** My `set -e` check asserted that
   blocked gates abort. It never asserted that a CLEAN gate proceeds —
   which was the path being broken. A test that only checks failures
   fail will pass while success is broken.
4. **Claimed evidence stronger than what I ran.** The twin-symmetry
   test stubbed the commit out, so it could not have caught a gate
   that returned the right status and committed anyway — yet I cited
   it as proof of equivalence. Re-run against real fixtures at
   repository-state level after a reviewer said so.

## Pattern recorded

`harden_twins_by_copy_not_rederivation` (patterns.yml), sibling of
`fix_by_class_not_instance`. Two clauses beyond the sibling:

- Port the hardened form **verbatim**; re-derivation silently drops
  properties nobody restated. This applies to a **reviewer's suggested
  form** too — "simplify the redundant-looking part" is re-derivation
  in a tidier hat.
- Verify by running both twins in isolated fixtures and comparing exit
  status, stdout, stderr **and the state the gate protects**, across
  every environment the snippet runs in. Status parity is not
  equivalence; side-by-side reading catches nothing.

## Recommendation (not filed — planner's call)

**Extract the gate into a small tested script the agent invokes.**
The polarity contradiction was a documentation-drifted-from-code
failure, which is the failure mode when executable logic lives in
prose across three sites that must agree by hand. A script gives the
contract one home and a test. If this construct needs touching again,
that is the fix, not more prose.

## Process notes

- **Bot budget**: baseline is one substantive round; this took five
  across two repos. Not churn — each round found real defects — but
  the cost is real and traceable to hardening executable logic inside
  markdown.
- **Ninth lying-status face** for bot-triage: `reviewDecision` stays
  CHANGES_REQUESTED indefinitely when the bot clears findings via
  COMMENTED rather than APPROVED. Not filed — bot-triage is a rostered
  component and editing it would open another drift cycle mid-release.
- **Stale relays**: one planner gate-check arrived anchored to a head
  four commits old, describing already-fixed work as pending. Suggest
  gate-checks carry the head SHA they were computed against.
- **Version-field trap**: `roster.yaml` records the `planner`
  component's own `kit_version` as `"2.1.0"` — identical to the plugin
  version being bumped. A blind find-and-replace would have falsified
  it with no test to catch it. Matched by anchored regex on
  `plugin_version:` and verified untouched.
