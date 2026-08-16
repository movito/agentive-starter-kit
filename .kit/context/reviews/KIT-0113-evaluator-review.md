# KIT-0113 — Evaluator Review Record

**Date**: 2026-08-16
**Agent**: feature-developer
**Change**: `.claude/agents/project-intake.md` — R1 quiet credential
scans, R2 post-seeding doctor, component 1.2.0 → 1.3.0
**Input**: `.adversarial/inputs/KIT-0113-code-review-input.md`
(`--format diff` — a prose/contract diff; `full` would have fed the
evaluators ~550 lines of unchanged agent body and invited findings
about text the diff never touched, KIT-0092)

## Tiers run

| Evaluator | Verdict | Log |
|-----------|---------|-----|
| `code-reviewer-fast` | CONCERNS | `.adversarial/logs/KIT-0113-code-review-input--code-reviewer-fast.md` |
| `claude-code` (security) | CHANGES_REQUESTED | `.adversarial/logs/KIT-0113-code-review-input--claude-code.md` |
| `code-reviewer` (deep, ~$0.33) | **SKIPPED** | — |

**Deep-tier skip reason**: the diff is a single markdown agent body —
no executable surface, no logic paths to trace. The security tier was
run *instead* because the change is entirely about credential
handling, which is where the real risk sits. The ordering rule was
honoured: both tiers ran before the PR opened.

## Round 1 — `code-reviewer-fast` (CONCERNS)

Five findings, four of them one class (unhandled non-0/1 exit codes on
the scan commands) plus one on overloaded doctor exit codes.

| # | Finding | Disposition |
|---|---------|-------------|
| 1–4 | Scans define behavior only for exit 0/1; `git` exits 128 on bad path / missing repo / permission error, leaving behavior undefined | **ACCEPTED** — real. A scan that did not run has proven nothing. Added an explicit fail-closed clause: any exit other than 0/1 is a broken scan, report and stop, never commit on it. Commit `c8ee531`. |
| 5 | `agentive doctor` exit 1 is ambiguous | **ACCEPTED** — and verified against the implementation: exit 1 genuinely IS overloaded. The driver's contract (`doctor/__init__.py:539–543`) uses 1 for "at least one FAIL" (0 = PASS/SKIP, 2 = warnings only, 3 = driver error), while `_project_root()` (`cli.py:74–80`) also exits 1 when it finds no project root. Step 5 now gates on the `DOCTOR:` verdict lines, not the exit code alone. Commit `c8ee531`. |

## Round 2 — `claude-code` security (CHANGES_REQUESTED)

Two accepted, five declined. The two blocking findings were both
proposals to *narrow* the credential regex — declined on fail-closed
grounds, reasoning recorded below.

| Severity | Finding | Disposition |
|----------|---------|-------------|
| HIGH | `eyJ[A-Za-z0-9_-]{20,}` is structurally incomplete (no `.` separator) and false-positives on any base64 JSON; tighten to require three JWT segments | **DECLINED.** For a *detection* scan, matching the header segment is sufficient to flag the file — the `.` is needed to parse a JWT, not to spot one. Requiring three segments would narrow detection, i.e. fail open, which is the wrong bias for a credential gate. False positives here cost one user glance at a filename; false negatives cost a leaked credential. The `eyJ` shape is also inherited from the pre-existing prose pattern ("long `eyJ` JWT blobs"), which this change merely made executable. |
| HIGH | `BEGIN [A-Z ]*PRIVATE KEY` lacks the PEM `-----` delimiters, false-positiving on docs | **DECLINED**, same fail-closed reasoning — and the evaluator itself concedes the cost is "annoying but not a security regression." Note the new pattern is already strictly *broader* than the one it replaces: verified live, `BEGIN [A-Z ]*PRIVATE KEY` matches 3/3 PEM header forms where the old `BEGIN .* PRIVATE KEY` matched 2/3 (it missed bare `BEGIN PRIVATE KEY`). |
| HIGH | `git grep --cached` on an empty index exits 1, indistinguishable from clean | **DECLINED** — self-limiting. Nothing staged means `git commit` fails on its own, so the "scan passed but nothing was committed" state cannot ship a credential. The evaluator concedes an empty commit is harmless. |
| MEDIUM | Pattern set duplicated across two sites, manual sync is fragile | **DECLINED** — already mitigated in-document with an explicit "change it in both" instruction, and the two literals are byte-identical (verified by grep count = 2). A markdown agent body has no DRY mechanism; the suggested line-number cross-references would themselves drift. |
| MEDIUM | A failed `cd` short-circuits `&&` so the doctor never runs; the fail-closed posture should cover it | **ALREADY ADDRESSED** in `c8ee531` (the evaluator read the pre-fix hunk). Wording sharpened from "wrong directory" to "a `cd` that failed" for precision. |
| LOW | Exit 2 (warnings only) not addressed in the launch gate — agent must infer | **ACCEPTED.** Added one line: a warnings-only re-run still prints the launch command, WARNs listed as informational rather than ✗. |
| LOW | No instruction to re-scan after remediation | **ACCEPTED** — genuinely good catch. Removing one offending file does not clear hits in the others. Added: the post-remediation scan, not the original, is the pass that authorizes the commit. |

### Note on the evaluator's "unverifiable" list

`claude-code` flagged the `agentive doctor` exit-code contract as
unverifiable from the diff and warned "if the contract differs, the
gate logic is wrong." It was verified directly against the
implementation before the claim was written into the agent body —
see the round-1 finding 5 row for file and line anchors.

## Verification performed beyond the evaluators

The scan command was executed live in a scratch repo rather than
reasoned about, since displayed commands are contracts:

- planted `ghp_…` in a staged file → printed `leak.py` and nothing
  else (filename only, zero secret bytes), exit 0
- unstaged it → no output, exit 1

This is what established the inverted-exit reading now documented at
both scan sites.
