# KIT-0118 — Evaluator review record

**Task**: KIT-0118 — Packaged-door fresh-install fixes + agentive-kit 0.4.0
**Branch**: `feature/KIT-0118-packaged-door-fixes`
**Reviewed commit**: a19b397
**Run**: 2026-08-24, BEFORE the PR opened (KIT-0035 ordering rule)
**Input**: `.adversarial/inputs/KIT-0118-code-review-input.md`
(`--format full` — logic-shaped change; 19 files, ~174k tokens)

## Tier selection

Logic-shaped diff (control flow, new flag plumbing, a parser field, an
early-return reorder), so the FULL trio ran — not the prose-sweep
fast-only path.

| Evaluator | Model | Verdict | Log |
|---|---|---|---|
| `code-reviewer-fast` | gemini-2.5-flash | CONCERNS | `.adversarial/logs/KIT-0118-code-review-input--code-reviewer-fast.md` |
| `claude-code` | claude-sonnet-4-6 | **APPROVED** | `.adversarial/logs/KIT-0118-code-review-input--claude-code.md` |
| `code-reviewer` | o3 | FAIL | `.adversarial/logs/KIT-0118-code-review-input--code-reviewer.md` |

## Dispositions

Every finding was verified against the tree before being believed or
dismissed (the verify-before-believing reflex). 3 actioned, 5 refuted,
3 out of scope.

### Actioned

1. **fast-gate: `evaluators: yes # comment` is read as invalid.**
   Correct as-is — the record format has no comment syntax and no
   reader strips one (`shape:`/`profile:` compare identifiers, `bots:`
   tokenizes over a fixed vocabulary, so a trailing comment is invalid
   for all of them). Silently stripping would be the near-miss cousin
   of #145. **Pinned as a contract test**:
   `test_trailing_comment_in_the_value_fails_loud`.
2. **claude-code LOW: `sed` comment-strip could truncate a path whose
   directory name contains `" #"`.** Real if remote. Initially
   dispositioned as "document the tradeoff" — **CodeRabbit raised the
   same finding on the PR and asked for a fix rather than a note, which
   was the better call**: the expression now matches only the literal
   legacy `# TODO` marker, so every tree the old engine produced still
   migrates while a real `../target #1` survives untouched. See the bot
   round below.
3. **o3 INTERACTION: `--no-kit` never resolves the evaluator offer.**
   Deliberate, not an oversight. **Added the rationale as a comment**
   at the `resolve_evaluator_offer` call site: rung-0 targets carry no
   `.adversarial` config and no record, so there is nothing to install
   and nothing to record; the door already acknowledges an explicit
   `--with-evaluators` out loud on that path.

### Refuted (verified false against the tree)

4. **o3 CORRECTNESS: `GIT_CONFIG_*` leaks through `_scrubbed_env`.**
   FALSE. The filter is `not k.startswith("GIT_")`, and
   `"GIT_CONFIG_KEY_0".startswith("GIT_")` is `True` — the variables
   the finding names are stripped. Verified by executing the
   comprehension. (Also untouched by this PR.)
5. **o3 CORRECTNESS: `--with-evaluators=YES` records mixed case, then
   conflicts on re-run.** FALSE. `--with-evaluators` is a BOOLEAN flag
   whose value is hardcoded lowercase in the flag table; the `=VALUE`
   form is refused at parse (`unknown argument`, exit 2 — verified by
   running `parse_args`). `evaluators_declared` can only ever hold
   exactly `"yes"` or `"no"`.
6. **o3 CORRECTNESS: duplicate `evaluators:` lines accumulate on every
   re-adopt.** FALSE. The append is gated on the flag being GIVEN, and
   a preserved region is never reseeded. **Pinned as a regression
   test** anyway (the claim is cheap to close permanently):
   `test_re_adopt_without_the_flag_does_not_duplicate` — three adopts,
   one line.
7. **o3 TESTING gaps ×2** — the restatements of findings 5 and 6; both
   now have tests.

### Out of scope

8. **fast-gate: relative-vs-absolute `target_path` conflict comparison
   is not path-normalized.** Pre-existing check, untouched by this PR;
   normalizing would change established conflict semantics.
9. **fast-gate: `_get_adversarial_cli_version` parses YAML by regex.**
   Untouched code the `--format full` input dragged in; the tradeoff is
   already documented at the call site (`project` runs on bare Python,
   PyYAML is not guaranteed).
10. **o3: `copy_env_into_target` uses `os.O_NOFOLLOW` (Windows).**
    Untouched by this PR, and the kit's engines are bash + rsync — the
    whole door is Unix-targeted.

## Post-disposition state

Two tests added on top of the reviewed commit; full suite re-run green
(1198 passed, 13 skipped). No behavior changed as a result of the
review — the two source edits are comments, the rest is coverage.

## Bot round (PR #147, one substantive round)

CI: all six checks green. **Bot truth was read from `reviewThreads`
GraphQL, not the check statuses** — CodeRabbit's *check* showed `pass`
while `reviewDecision` was `CHANGES_REQUESTED` with 2 unresolved
threads. That is the eighth recorded face of the lying-check-status
class (bot-triage skill); the trio had passed the same diff.

Both findings were real, both reproduced against the tree, both fixed:

1. **Major — `--evaluators=` skipped validation entirely.** Validation
   was keyed on `[ -n "$EVALUATORS" ]`, so an empty value read as "flag
   never passed": the engine would complete an install having silently
   dropped a flag the operator explicitly gave. Reproduced directly
   (`--evaluators= --shape single` fell through to the usage error).
   Fixed with an `EVALUATORS_GIVEN` presence sentinel driving
   validation; emptiness now means only "not declared". The `--bots`
   flag shares the original shape — noted, not changed here (pinned by
   many tests; KIT-0108 owns that engine's consolidation).
2. **Minor — the legacy-prose strip was a general `" #"` comment
   opener.** Narrowed to the literal `# TODO` marker the old engine
   actually wrote. `../target #1` and `../my project # notes` now
   survive; all three legacy forms still migrate.

Regression tests added for both, including one asserting the sed
expression in the test still matches the literal in the engine — a
migration test that drifts from its source proves nothing.

Suite after the bot round: **1210 passed, 13 skipped**.
