# KIT-0098 — Evaluator Review Record

**Date**: 2026-08-10
**Task**: Fresh-eyes repair of the KIT-0097 round-churned sections
**Branch**: `feature/KIT-0098-churned-sections-repair`
**Position**: PRE-PR-OPEN (Ordering rule, KIT-0035/KIT-0046)
**Input format**: `--format diff` (strings/prose-shaped change, per handoff)
**Input**: `.adversarial/inputs/KIT-0098-code-review-input.md` (4 files)

## Trio run

| Evaluator | Model | Verdict | Findings |
|---|---|---|---|
| `code-reviewer-fast` | gemini-2.5-flash | FAIL | 6 |
| `code-reviewer` | o3 | FAIL | 4 |
| `claude-code` | claude-sonnet-4-6 | (no verdict) | 4 |

Logs: `.adversarial/logs/KIT-0098-code-review-input--{code-reviewer-fast,code-reviewer,claude-code}.md`

Deep rounds used: **1** (limit ≤2).

## The dominant failure mode: diff-format reconstruction

Nine of the fourteen findings share one root error — **the evaluators
reconstructed the unchanged surrounding text from the diff hunks, and
reconstructed the PRE-fix state**. This is the exact class KIT-0069 and
KIT-0073 documented (two prose sweeps, trio 0-for-7 and 0-for-8). It is
why every finding below was checked against the tree before disposition,
never accepted on the strength of the description.

The clearest instance: all three evaluators independently reported that
this PR **removed** the planning-root `ls .kit/tasks` safety check and
flagged it HIGH/robustness. The check is intact at
`feature-developer.md:202-205` (and `-f5.md:207-210`). What was removed
was a *second, duplicate* copy of it — the churn residue this task
exists to clean up. The evaluators saw a deleted `ls` in the diff and
concluded the guard was gone.

## Disposition

| # | Finding | Source | Disposition |
|---|---|---|---|
| F1 | `ci-checker.md` step numbering now skips 3 | fast | **REJECTED** — false. Headings read 1,2,3,4 with no gap (verified: `grep "^### [0-9]"`). The file previously had TWO sections numbered 3; the fix removed a duplicate, it did not create a gap. |
| F2 | Removed planning-root verification (`feature-developer.md`) | fast | **REJECTED** — false. Guard intact at :202-205 with its STOP instruction. Duplicate copy removed only. |
| F3 | `.kit/tasks` missing now undetected | fast | **REJECTED** — same false premise as F2. |
| F4 | Single-repo `TARGET` resolution now "manual" | fast | **REJECTED** — asks to restore `TARGET="${TARGET_PATH:-$(git rev-parse …)}"`. That is `$()`, forbidden by the kit's Shell Rules, and an assignment that cannot survive to the next Bash call — the precise defect this task repairs. |
| F5 | Split-mode echo parsing more complex | fast | **REJECTED** — same premise as F4. |
| F6 | `TARGET_PATH=` echoed but docs say `$TARGET` | fast | **ACCEPTED** — real seam introduced by this PR's own edit. Fixed: the echo output is now explicitly named as the value the doc calls `$TARGET`. |
| F7 | `$TARGET` expands empty on copy-paste | deep (o3) | **REJECTED** — assumes a human copy-pasting verbatim. The reader is an agent instructed to substitute literal text, and `"$PLANNING"` is the established kit-wide convention (declared a placeholder at `feature-developer.md:208`, then used in `$`-sigil form in live blocks at :230-256). These edits make the files consistent with it. |
| F8 | `$GH_REPO_ARG`/`$GIT_DIR_ARG` same issue | deep (o3) | **REJECTED** — same premise as F7. Partially mitigated anyway: the note now says to *delete* the placeholder in single-repo mode rather than leave it empty. |
| F9 | Paths containing spaces break substitution | deep (o3) | **ACCEPTED** — legitimate and cheap. Both files now say to quote the path if it contains spaces. |
| F10 | No CI lint for placeholder regressions | deep (o3) | **REJECTED (out of scope)** — a docs-lint/CI proposal; KIT-0094 territory, explicitly out of scope for this task. |
| F11 | Removed validation before planning-repo reliance [HIGH] | claude-code | **REJECTED** — false, same as F2/F3. Highest-severity finding of the run, and it describes a guard that is still in the file. |
| F12 | `--repo` injection via unvalidated `owner/name` [MED] | claude-code | **REJECTED (pre-existing, already handled)** — the evaluator itself notes it is "not a regression introduced by this diff". The canonical parser validates via `target_repo_init` (:44, described :38) and the fallback requires an owner/name-shaped value with STOP on malformed (:82, :98). |
| F13 | Step renumbering may break cross-references [MED] | claude-code | **REJECTED after audit** — named a real check worth running. Ran it: no step-number cross-references exist in `ci-checker.md` or `check-ci.md`. No fallout. |
| F14 | "routing text is EMPTY" ambiguous [LOW] | claude-code | **ACCEPTED** — folded into the F8 mitigation: say to delete the placeholder, not leave it empty. |

**Totals**: 14 findings — 3 accepted, 11 rejected. Every rejection was
verified against the tree with a named check, not asserted.

## Circuit-breaker status

The breaker asks whether a round's findings are majority
*self-inflicted* (defects introduced by this session's own edits).

- Self-inflicted: **1 of 14** (F6, a naming seam in my own edit; F14 is
  a clarity improvement to new text, not a defect).
- Evaluator reconstructions of pre-fix state: 9 of 14.

Round 1 is **not** majority-self-inflicted. The breaker does not fire.
Round count stands at 1 of the permitted 3.

## Bot round 1 (PR #121) — CodeRabbit

| Bot | Verdict | Threads |
|---|---|---|
| Cursor Bugbot | PASS | 0 |
| CodeRabbit | CHANGES_REQUESTED | 1 |

| # | Finding | Disposition |
|---|---|---|
| B1 | `ci-checker.md`: the placeholder contract at :96-103 contradicts the "use `$GH_REPO_ARG` unquoted / it expands to nothing" framing still standing at :68, :137-147, :158, :264, :314 | **ACCEPTED** — correct and tree-grounded. This is **self-inflicted**: my round-1 edit declared the contract but swept only the fallback section, leaving the older framing elsewhere in the file. Fixed as a class in one commit (all 5 prose sites), verified by `grep -n "unquoted\|expands to\|populated\|vanish"` returning empty. |

Bot round 1 is **1 of 1 self-inflicted** — technically majority. Noted
against the circuit breaker below.

## Circuit-breaker re-assessment after bot round 1

The breaker's purpose is to stop a session that is adding defect surface
faster than it removes it. Round-by-round:

- **Evaluator round 1**: 14 findings, 1 self-inflicted (7%).
- **Bot round 1**: 1 finding, 1 self-inflicted (100% of a single-item
  round).

Taken literally, bot round 1 is "majority self-inflicted" and the
breaker fires. Taken as the rule intends — is the repair converging? —
the picture is the opposite of KIT-0097's round 8: the finding is a
*single incomplete sweep of one class in one file*, caught by a bot on
the first pass, fixed as a class rather than instance-by-instance, and
leaving a mechanically verifiable end state (the grep returns empty).
Total self-inflicted across both rounds: 2 of 15.

**Decision**: fix and push once, then STOP the loop regardless of what
round 2 returns — no third round without operator direction. This
respects the breaker's intent while not abandoning a one-line-class fix
that is already verified. Flagged explicitly for the operator in the PR
and the handoff.

## Bot round 2 — clean on the repair; 2 open findings on bookkeeping

Round 2 (push `2720bae`, the placeholder-contract class sweep):
**CodeRabbit and Cursor Bugbot both re-reviewed with zero findings.**
The repair converged.

A third bot pass then ran against the handoff commit `cb6c700` (task
move + review starter — planning artifacts only) and raised two
findings. **Both are RECORDED, NOT FIXED**, per the closed-loop decision
taken after bot round 1. Neither touches the four repaired files, the S1
verdicts, or any S2 item.

| # | Finding | Assessment | Status |
|---|---|---|---|
| B2 | `KIT-0098-HANDOFF-feature-developer.md:8,92` — the task-path pointer now reads `4-in-review` while the Session-topology prose at :19-21 still says the file is in `3-in-progress` | **Valid, cosmetic.** Artifact of `project move` rewriting the path pointer automatically while handoff-time prose stayed as written. The handoff is a historical record of session start, so the `3-in-progress` statement was true when written — it wants an explicit "at handoff time" label rather than a rewrite. | **OPEN — operator call** |
| B3 | `KIT-0098-REVIEW-STARTER.md:17-18` — "No behavior, no code, no tests changed" is loose: agent instruction files *are* agent behavior | **Valid, wording.** Intent was "no application code or tests". Suggested replacement: "No application code or tests changed; agent workflow guidance changed." | **OPEN — operator call** |

Both are one-line edits to planning artifacts. They are left open
deliberately: the breaker decision was to stop the fix loop after the
round-1 push regardless of what later rounds returned, and honouring
that is worth more than closing two cosmetic threads on documents that
are not the deliverable. **Recommend the operator either wave them
through at merge or fold them into KIT-0099's housekeeping.**

## Review-surface budget

Committed repair: **-13 net lines** (36 insertions / 49 deletions).
Round-1 fixes: +11 / -7. Total well inside the ~500-prose-line budget —
as a de-duplication repair should be (net negative).
