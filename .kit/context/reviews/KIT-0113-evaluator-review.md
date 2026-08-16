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
| HIGH | `BEGIN [A-Z ]*PRIVATE KEY` lacks the PEM `-----` delimiters, false-positiving on docs | **DECLINED**, same fail-closed reasoning — the evaluator itself concedes the cost is "annoying but not a security regression." ⚠️ **But see the bot round below**: the claim originally recorded here — that this pattern was "strictly broader" than the `BEGIN .* PRIVATE KEY` it replaced — was WRONG, and CodeRabbit caught it. Corrected there. |
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

## Bot round 1 — PR #135 (BugBot 3 + CodeRabbit 3)

Bot truth taken from the `reviewThreads` GraphQL query with
`hasNextPage` fail-closed counting, **not** the check statuses: the
Cursor BugBot check reported `skipping` while its three threads were
already posted — another face of the lying-status class.

All six threads accepted. Two of CodeRabbit's were convergent with
BugBot's, so the substantive findings are four:

| # | Bot(s) | Finding | Fix |
|---|--------|---------|-----|
| 1 | BugBot High + CodeRabbit Major | Step 4c ran `add` → scan → `commit` as one pasteable block with no gate. Under the inverted reading, a hit exits 0 — which *looks* like success — so a faithful run commits the staged secret. | Replaced the block with a shell-level `case $?` gate. **Prose cannot stop a pasted sequence** (CodeRabbit's phrasing, and it is right); the gate now lives in the shell. `case` not `if`: an `if`/`else` sends both "clean" (1) and "scan errored" (128) down the same branch and commits on a scan that never ran. |
| 2 | BugBot High | The Step 2.1 pre-existing-repo scan was switched to `-l` but never got the inverted-exit / fail-closed rules, so a hit could read as success and the push proceed. | Gave it the exit contract by explicit reference to Step 2.3, plus a note that it takes no `--cached` (it scans tracked files, not an index). |
| 3 | BugBot Medium + CodeRabbit Major | The "re-scan after remediation" instruction — added in evaluator round 2 — could itself false-pass: `--cached` sees only the index, so a scan run right after *unstaging* the offender passes vacuously while the secret sits in the working tree, ready to be re-`add`ed behind a green scan. | Rewrote the sequence to: remediate in the working tree → stage everything to be committed → scan → commit, with "nothing may be staged after the authorizing scan". |
| 4 | CodeRabbit Minor | The review record's claim that the new PEM pattern was "strictly broader" than the old one was **false**. | Correct, and it exposed a real regression — see below. |

### Finding 4 corrected a regression, not just a claim

CodeRabbit's point: `BEGIN .* PRIVATE KEY` also matched labels with
lowercase or punctuation, which `[A-Z ]*` rejects. Neither pattern was
a superset of the other — so the change had *narrowed* coverage for
those labels while widening it for the bare form.

Re-tested over an 8-fixture PEM set (bare, RSA, OPENSSH, EC, DSA,
ENCRYPTED, lowercase `rsa`, `X-509`):

| Pattern | Matches |
|---------|---------|
| `BEGIN .* PRIVATE KEY` (original) | 7/8 — misses bare `BEGIN PRIVATE KEY` |
| `BEGIN [A-Z ]*PRIVATE KEY` (this PR, round 1) | **6/8** — misses lowercase `rsa` and `X-509` |
| `BEGIN [A-Za-z0-9 -]*PRIVATE KEY` (adopted) | **8/8** |

Both scan sites now carry the 8/8 form, and the "strictly broader"
claim above is retracted — the adopted pattern is a genuine superset
of both predecessors, which the original was not.

### Gate verified live

The `case` gate was executed against all three exit classes rather
than assumed, and the first run **found a bug in the test, which is
how the fixture caught a real subtlety**: a directory nested inside
another git repo returns exit 1 (empty index for that path), not 128.
Against a true non-repo:

| Case | Result |
|------|--------|
| staged secret present (exit 0) | BLOCKED (credential found) |
| clean index (exit 1) | COMMIT would run |
| not a git repository (exit 128) | BLOCKED (scan failed to run) |

## Bot round 2 — PR #135 (CodeRabbit 1)

One new thread; the six from round 1 stayed resolved.

| Bot | Finding | Fix |
|-----|---------|-----|
| CodeRabbit Major | `git add -A` was unchecked in the Step 4c gate. A partially-failed stage leaves a stale/partial index; the scan then validates *that*, and exit 1 authorizes a commit that is not the tree meant to be seeded. | **ACCEPTED.** Wrapped the gate in `if ! git -C "$PLANNING" add -A`. Classified correctly by the bot as data integrity rather than credential leak — the scan still examines exactly what would be committed, so this cannot leak a secret; what it can do is ship a silently incomplete seeding commit. |

**Simplified from the suggested fix.** CodeRabbit's diff captured the
scan status into a `scan_status` variable via an `if`/`else` before
branching. That is unnecessary here: `case $?` already follows the
`git grep` directly, with no intervening command, so `$?` is the
scan's status. Adopted the guard, dropped the extra variable — same
behavior, one less moving part.

Re-tested across four paths after the change:

| Case | Result |
|------|--------|
| staged secret present | BLOCKED (credential found) |
| clean index | COMMIT would run |
| not a git repo (add fails first) | BLOCKED (staging failed) |
| path does not exist | BLOCKED (staging failed) |

Note the abort ordering shifted: a non-repo now fails at `add` rather
than reaching the scan's 128 branch. Both block, so the invariant
holds either way — but the `*)` scan-error branch is still load-bearing
for the case where staging succeeds and the scan itself breaks.
