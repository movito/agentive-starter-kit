# Review Insights Index

Distilled knowledge from code reviews. Updated by planner during task completion.

**Reference**: KIT-ADR-0019 (Review Knowledge Extraction)

---

## How to Use This File

**For Agents Starting Work**:
1. Check relevant module sections before implementation
2. Review "Patterns & Anti-Patterns" for established conventions
3. Note any integration requirements that affect your work

**For Planner Completing Tasks**:
1. After moving task to `5-done/`, read the review file
2. Extract high-signal insights (not everything, just what's reusable)
3. Append entries under appropriate sections
4. Always include task ID for traceability

---

## Index by Module

### Sync & Manifest (`scripts/.core-manifest.json`, `.github/workflows/`)

- **KIT-0024**: Shell variable expansion in YAML (GitHub Actions) is vulnerable to backtick injection — always quote `$()` subshells in workflow files
- **KIT-0024**: Guard against missing directories before `cp` in sync workflows — downstream repos may not have `.claude/commands/` yet
- **KIT-0024**: o3 code-reviewer can produce false positives about basic shell behavior (`$()` strips trailing newlines, GitHub Actions empty outputs are `""` not `null`, `_core$` regex anchoring). Always verify shell-related findings with one-liner tests before accepting.

### Scripts (`scripts/`)

- **ASK-0043**: Root-resolution preamble (`SCRIPT_DIR`/`PROJECT_ROOT`/`cd`) is now standard in all shell scripts. Future scripts must include it. Scripts with `set -e` already handle `cd` failure; scripts without it need `|| exit 1` on the `cd` line.
- **ASK-0044**: Launcher scripts (`launch`, `onboarding`) must self-test `PROJECT_ROOT` resolution — when a script moves to a different directory depth, `dirname` chains silently resolve to the wrong root. Add guard: `[[ -f "$PROJECT_ROOT/pyproject.toml" ]] || exit 1`.

- **ASK-0025**: Inline Python via `-c` in bash scripts follows `teams` command pattern - acceptable for smaller scripts
- **ASK-0025**: For large inline scripts (185+ lines), consider extracting to separate module (e.g., `scripts/check_sync_status.py`) for testability
- **ASK-0027**: Support multiple YAML field names (e.g., both `name:` and `project_name:`) with first-match-wins logic
- **ASK-0027**: Watch for path resolution bugs in `project_dir` handling - use `Path.resolve()` consistently

### CLI (`scripts/core/project`)

- **ASK-0025**: User-friendly output should include actionable next steps (e.g., "Run ./scripts/core/project linearsync to sync")
- **ASK-0025**: Limit verbose output lists (e.g., show max 5 missing tasks, then "and N more...")
- **ASK-0027**: Progress reporting pattern - show status for each file/item processed
- **ASK-0027**: Idempotent commands - safe to run multiple times without unintended side effects
- **ASK-0028**: Subprocess calls should use `capture_output=True, text=True` for proper error capture
- **ASK-0028**: Truncate long error output (e.g., `stderr[-500:]`) with manual remediation instructions
- **ASK-0028**: Detect corrupted state (e.g., missing venv python) and suggest `--force` flag
- **ASK-0029**: Library installers should track version + commit hash in `.installed-version` for auditability
- **ASK-0029**: Pin external content installers to specific versions (tags), not just "latest"
- **ASK-0029**: Support `--force` for reinstallation and `--ref <tag>` for version override
- **ASK-0032**: Use `shutil.which()` for tool detection - simple and reliable
- **ASK-0032**: Provide primary recommendation with alternatives in error messages (uv → pyenv → manual)
- **ASK-0032**: Use generous timeouts (600s) for operations that may download large files

### Tests (`tests/`)

- **ASK-0025**: CLI entry points excluded from coverage (pyproject.toml), but core logic should be extractable into testable functions
- **ASK-0025**: Consider extracting comparison/validation logic from CLI commands into utility modules for unit testing
- **ASK-0032**: Use `conftest.py` for shared fixtures - improves test maintainability
- **ASK-0032**: MockVersionInfo class pattern: handle both tuple comparison (`>=`) and attribute access (`.major`)

---

## Patterns & Anti-Patterns

### Recommended Patterns

- **Idempotent CLI**: Design commands to be safe for repeated execution (ASK-0027)
- **Actionable Output**: Include specific next-step commands in error/status messages (ASK-0025)
- **Output Limiting**: Cap verbose lists with "and N more..." to avoid overwhelming users (ASK-0025)
- **Dual Config Support**: Accept multiple field names for config values, take first match (ASK-0027)
- **Robust Error Handling**: Graceful handling of missing files without swallowing errors (ASK-0027)
- **Type Hints + Docstrings**: Include for maintainability in all new code (ASK-0027)
- **Progress Reporting**: Show per-item status for batch operations (ASK-0027)
- **Optional Dependencies**: Use `GQL_AVAILABLE` flag pattern instead of `sys.exit(1)` at import time (ASK-0028, KIT-ADR-0005)
- **Subprocess Error Capture**: Always use `capture_output=True, text=True` and check return codes (ASK-0028)
- **Provider-Agnostic Design**: Avoid hard-coded model/provider names in documentation; use generic terms with "see docs for options" (ASK-0029)
- **Version Pinning for External Content**: Pin to tags by default, record commit hash for auditability (ASK-0029)
- **Non-Intrusive Feature Flags**: New features should only activate for relevant scenarios (e.g., Python 3.13+ only) (ASK-0032)
- **Tiered Error Messages**: Primary recommendation → alternatives → manual fallback (ASK-0032)
- **Data-Shape Verification Before Coding**: When implementing against a bot/CI/API signal, capture real output first — KIT-0034's spec said "CodeRabbit check-run" but reality is a commit status; coding to the paraphrase would have shipped a fallback that never fires (KIT-0034)
- **PATH-Stubbed Binary for Shell-Script Testing**: A fake `gh` shim on PATH running the *real* script against canned states is the cheapest credible verification for shell+CLI gate logic with no test harness — re-runs in seconds per fix round (KIT-0034; codification tracked in KIT-0040)
- **Single Shared API Snapshot Across Related Checks**: One GraphQL fetch feeding preflight Gates 2/3/4 eliminated the race where the fallback and thread gate could disagree mid-run, and cut 3 API calls to 1 (KIT-0034)
- **Mutation-Test a New Test Harness**: after building a harness, deliberately break one condition in the system under test and confirm a test fails — turns "the harness passes" into "the harness detects breakage" for ~10 minutes of work (KIT-0040)
- **Stub Every External Touchpoint, Not Just the Obvious One**: the preflight harness stubbed `sleep` (instant poll loops) and `dispatch` (no fire-and-forget event leakage) alongside `gh`; module-scoped fixtures cut runtime 5.3s → 1.8s, inside the pre-commit fast-hook budget (KIT-0040)
- **Two Consistent Detection Paths for Parse-or-Reject Logic**: pair a tolerant parse regex with a deliberately *looser* malformed-input detector so no input falls between "parses fine" and "detected as broken" — the gap between the two is where silent data loss lives (KIT-0040, kit_markers.py)
- **Grep-Before-Deciding on Optional Lint Rules**: a 30-second grep for would-be violations settled the DK005 implement-or-skip decision with evidence (5 legitimate fixture hits, and the real incident surface was shell-in-YAML the rule couldn't see) instead of taste (KIT-0037/38/39)
- **A Convention Spec Must Verify Its Own Wording Against the Code It Cites**: KIT-0037 codified an exit-code convention while its own text carried a wrong exit code copied from retro shorthand — check the convention's claims against the reference implementation, not just the implementation against the convention (KIT-0037/38/39)

### Anti-Patterns to Avoid

- **Massive Inline Scripts**: Inline Python >100 lines in bash scripts hurts maintainability and testability (ASK-0025)
- **Untestable CLI Logic**: Embedding all logic in CLI entry points prevents unit testing - extract core logic (ASK-0025)
- **Silent Failures**: Operations that can fail silently (like Linear sync) need verification commands (ASK-0025)
- **Trusting Evaluator Verdicts Without Triage**: o3 code-reviewer can return FAIL based on false positives — always verify individual findings before accepting the overall verdict (KIT-0024)
- **Blanket rm+copy in Sync Actions**: Use manifest-driven file-by-file copy to preserve local/unowned files in downstream repos (KIT-0024, KIT-ADR-0022)
- **Splitting structural migrations into multiple PRs**: Mass directory moves + path rewrites create a half-migrated codebase between PRs that agents cannot navigate. Agents depend on hardcoded paths in prompts, handoff files, and CLAUDE.md — stale paths cause silent failures. Structural migrations must land atomically in a single branch/PR, even if large. The evaluator (arch-review) does not assess intermediate state viability — it only reviews the target architecture. The planner must catch this. (ASK-0044)
- **Grep verification with only full-path patterns**: `grep -r 'old/path/'` misses bare directory name references (e.g., `"decisions"` in array literals, `exclude_path_parts`). Structural renames must also grep for bare directory names. (ASK-0047)
- **Test fixtures with hardcoded paths**: `test_project_script.py` constructs fixtures with literal path strings (`docs/decisions`). When the real paths change, fixtures break. Consider deriving from constants. (ASK-0047)
- **Merged PRs as stable verification fixtures**: retro-referenced PRs are snapshots, not fixtures — PR #58 drifted (2 new unresolved BugBot threads) and could no longer serve as the canonical Gate-2 false-negative case; PR #63 had to substitute. Verify a referenced PR still has the assumed shape before building a test plan on it. (KIT-0034)

---

## Integration Notes

- **Grep False Positives**: `settings.local.json` (gitignored) contains auto-generated permission allow-list entries with old paths — these trigger grep matches during path audits but are not runtime code. Exclude from path-consistency checks. (ASK-0044)
- **CI Verification**: `verify-ci.sh` only checks push-triggered workflows but the Tests workflow triggers on `pull_request`. Fall back to `gh run list` for comprehensive status. (ASK-0044)
- **Linear Sync**: Use `./scripts/core/project sync-status` after commits to verify Linear is updated (ASK-0025)
- **Upstream Merges**: Run `./scripts/core/project reconfigure` after pulling upstream changes to update agent files (ASK-0027)
- **New Project Setup**: Run `./scripts/core/project setup` to create venv and install dependencies (ASK-0028)
- **Evaluator Installation**: Run `./scripts/core/project install-evaluators` to add additional evaluation providers (ASK-0029)
- **adversarial-workflow CLI requires `.adversarial/` at repo root**: The CLI (v0.9.9) hardcodes `.adversarial/` as its working directory. ASK-0044 moved it to `.kit/adversarial/` but this broke the CLI. Reverted: `.adversarial/` now lives at repo root again. Future move requires ADV-0053 (configurable dir) — tracked upstream at movito/adversarial-workflow#58. (ASK-0044 post-mortem)
- **CodeRabbit reports via the legacy commit-status API (`context: "CodeRabbit"`), BugBot via check-runs**: any gate or tooling querying bot review state must hit the right surface for each bot — statuses primary for CodeRabbit, check-runs for BugBot. (KIT-0034)
- **CodeRabbit re-flags stale bookkeeping paths on every task-status move**: `project move` changes the task folder but not `details_link` in agent-handoffs.json or handoff-file metadata; update them in the same commit as the move to preempt a bot round. FIXED in KIT-0040 (PR #70): `project start|move|complete` now rewrites the metadata in the same operation. (KIT-0034 → KIT-0040)
- **`gh pr checks` is stale immediately after a push**: it reports the *previous* head's checks for a window after pushing — an all-green snapshot taken seconds after a push is not proof; disambiguate with a SHA-scoped GraphQL query. (KIT-0040)
- **External-finding yield concentrates on fresh code**: across 8 evaluator/bot findings on PR #70, the 2 real ones were both in code written that session, none in pre-existing code under review. Weight triage attention accordingly. (KIT-0040)
- **Preflight Gates 5/6 assume one task ID per PR**: exact-name match on `<TASK-ID>-REVIEW-STARTER.md` (`preflight-check.sh:487`) and single-ID evaluator artifacts — bundled PRs need lead-task naming + per-task pointer files (KIT-0037/38/39 session files are the reference shape) until KIT-0042 lands. (KIT-0037/38/39)
- **CodeRabbit substantively reviews factual claims in prose**: it ran its own verification scripts against `resolve_source()` to check exit codes claimed in a docs-only diff — bot rounds add value even when the adversarial evaluator is skipped for docs-only changes. (KIT-0037/38/39)
- **DK005 (scoped-staging lint rule) deliberately not implemented**: grep showed it would noqa-spam test fixtures while missing the shell-in-YAML incident surface; decision in PR #71's body. Revisit trigger: a scoped-staging violation recurring in *production* code, not test fixtures. (KIT-0037/38/39)
- **The evaluator trio runs BEFORE PR open for ALL tasks** (adopted KIT-0035 for doc-dominated; widened KIT-0046): evidence spans three tasks — zero-noise first bot rounds twice on docs, and on a code task all three substantive round-1 bot findings were evaluator-convergent. Local tests green first; defer only when the diff can't be assembled pre-PR. (KIT-0035 → KIT-0046)
- **The F4 Incident Closure rule worked on its first outing**: KIT-0046's own retro closed seven incidents as doctor-check / hardening / triage-entry / not-checkable — the doctor grew four hardenings *during its own build* because the rule forced the mapping. (KIT-0046)
- **An activated venv can blind venv-vs-system comparisons**: both probe sides resolve to the venv; system-side probes must skip venv bin dirs explicitly. (KIT-0046, doctor skew check)
- **`.adversarial/inputs/` is now gitignored** (regenerable; review records live in `.kit/context/reviews/`) — clean evaluator sessions leave clean worktrees; preserve-then-force is the fallback, not the routine. (KIT-0046 retro, planner decision; validated at KIT-0048 closeout — plain `worktree remove` worked)
- **Autouse isolation has a scope boundary**: function-scoped autouse fixtures don't reach class/session-scoped fixtures — wider-scoped fixtures that shell out need explicit env scrubbing (`_scrubbed_env()`; self-review item 11, TESTING-WORKFLOW caveat). Third appearance of the GIT_* leak class, each one scope-level deeper. (KIT-0048)
- **Refuse-loudly beats partial-apply for shape mismatches**: KIT-0048's sync stopgap (planning repo + full manifest → exit 2 with a pointer to KIT-0049) is the template — when a tool can't yet honor a new constraint, a loud refusal with a tracked successor beats a partially-correct application. (KIT-0048; successor delivered in KIT-0049)
- **The intersection-masking class**: five reviewers independently found five faces of one design risk in subset-selection code — silence about what got dropped. Now a patterns.yml rule (`intersection_names_drops`): intersections/filters name their exclusions; empty selections never claim completeness. (KIT-0049)
- **Consistency bugs live in the seams BETWEEN N readers of one contract, not inside any one reader** — every KIT-0056 reviewer's real find was a divergence between the three bots-declaration readers (raw-vs-normalized compares, whitespace tolerance, empty-value handling). Pairwise pins keep leaking; the closure is a conformance harness: one fixture table, all readers, assert agreement. (KIT-0056; harness lands in P6)
- **Duplicate record keys: first-wins is now blessed contract** (patterns.yml `record_duplicate_keys_first_wins`) — lenient for the machine-written record, strict for the hand-authored preset; the conformance fixture pins the policy so leniency is tested, not accidental. (KIT-0056 retro item 4, planner decision)
- **o3 calibration, final form: the verdict alone carries no signal — the code check is mandatory.** Arc totals: 3 real-blocker FAILs (KIT-0046/0048/0049) vs 2 fully-refuted FAILs (KIT-0050/0057, line-citation refutations). Full triage attention either way; its test-gap findings retain value even in refuted rounds. (KIT-0046→0057)
- **A conformance harness that passes first-run is still the finding**: KIT-0057's 13×3 reader table agreed immediately because KIT-0056's pairwise pins had already converged the readers — the harness converts that state into a ratchet. Green-on-arrival ≠ wasted work. (KIT-0057)
- **Directory-level symlinks are invisible to `rglob()+is_file()` walkers**: the sync engine would have read a dir-symlinked path as empty and deletion-pruned consumer copies; real dirs holding file-level symlinks are the working shape, pinned by `test_sync_engine_reads_content_through_old_path`. Check walker semantics before symlinking anything a machine reads. (KIT-0057, self-review catch)
- **A retro is testimony; and even verification generalizes badly across installs — the three-installs lesson.** The ADVERSARIAL_UNATTENDED saga (KIT-0044 → 0050 → 0053, three conflicting "verified" conclusions) resolved 2026-07-17: THREE coexisting installs all claiming "1.0.1" — PyPI builds (venv, system python: plain `input()`, `echo y |` works) and an **editable dev install of the operator's upstream checkout on PATH** (implements the flag, auto-cancels exit 0 without it). Every session's observation was correct *for its binary*; every generalization to "the library" was wrong, including the planner's "exists nowhere" (a failed `/opt/homebrew` glob went unchased). Rules distilled: (1) verify against `command -v <tool>` — the binary the session actually runs — not against whichever package `pip` shows; (2) editable installs make version strings lie (doctor check filed, KIT-0055); (3) when two verifications conflict, suspect the environment before either verifier; (4) never trust the adversarial CLI's exit 0 — cancelled runs exit 0; the log file's verdict is the proof. Standing invocation: `echo y | ADVERSARIAL_UNATTENDED=1 adversarial …` (robust on every build). (KIT-0044/0050/0053, planner empirical matrix)
- **A script cannot export into its caller's shell** — surface, don't fake-set. (KIT-0035) **Superseded detail**: the surfaced `ADVERSARIAL_UNATTENDED` flag turned out never to exist in the installed adversarial-workflow library (KIT-0044); the working pattern is `echo y |` piping (prepare-review-input.sh 1.5.1). Verify shipped hints against installed tools — now self-review item 10.
- **`adversarial list-evaluators` exists** for evaluator discovery (with `ls .adversarial/evaluators/*/` as fallback; prefer `-v2` variants). (KIT-0035)
- **isort's pin is a floor (`>=`), not exact** — version-drift warnings comparing "active vs pinned" only make sense for exact pins like Black's. (KIT-0035)
- **Evaluator-before-PR round-collapse is measured, not theoretical**: PR #72 (six items, 8 files) ran the trio pre-open and got a ZERO-thread first bot round with CodeRabbit APPROVED — vs KIT-0032's four post-open rounds on one doc file. (KIT-0035 retro)
- **Test rejection cases, not just acceptance, for detection patterns**: live-output testing only exercises the happy path; the marketplace-source bypass (`Directory (/Users/alice/github/movito/...)`) passed every live test. Now codified in TESTING-WORKFLOW.md. (KIT-0035 retro)
- **Existence checks should require non-empty regular files**: zero-byte pointer files satisfied preflight Gates 5/6's bare `find -name`; `-type f -size +0c` closes it. Audit any gate that equates "file exists" with "artifact provided". (KIT-0042, o3's one real catch)
- **Write the route decision before the code**: KIT-0042's convention-vs-glob reasoning written first let TDD prove the chosen route needed zero gate-logic change — the mechanism collapsed to a string change plus docs. (KIT-0042)
- **Count your declines — convergent repeated evaluator findings are a follow-up signal**: o3 + fast-v2 flagged the identical Gate 1/2/7 edge set three runs running; individually declinable, collectively they earned KIT-0043. Decline tables are where recurring findings go to be forgotten unless someone counts them. (KIT-0042)
- **Triple convergence is a priority filter, not just a severity flag**: o3 + fast-v2 + BugBot hit the Gate 1 cap flaw from three different angles, and the merged fix was strictly better than any single reviewer's suggestion — convergence count beats any one reviewer's own severity rating. (KIT-0043)
- **Reproduce-or-decline as a spec clause for evaluator-sourced requirements**: KIT-0043 F4's "verify first" gate turned an unverified o3 claim into two green pinning tests plus a documented decline instead of a speculative rewrite. Make this the standing convention whenever a requirement originates from an unverified reviewer claim. (KIT-0043)
- **Verify-before-believing applies to your OWN inferences, not just reviewers' claims**: the "operator converted the repo to bare" reading was checkable in one command (an intact working tree inside a "bare" repo) and went unchecked for a whole closeout. (KIT-0043)
- **Weight fast-v2 findings by specificity, not placement**: its self-hedged headline claim was structurally impossible while its secondary finding was the best of the round — twice now. (KIT-0042/0043)
- **Committable ≠ compilable**: a CodeRabbit committable suggestion was a bash syntax error (heredoc body swallowed the `&&`-chained `mv`/`then` lines) — auto-applying would have broken `seed_config_home`. Syntax-verify (`bash -n` / scratch execution) any committable shell suggestion before applying; rule now in the bot-triage skill. (KIT-0058)
- **BugBot check-run conclusion "skipping" is NON-TERMINAL, and preflight Gate 3 masks it as reviewed-clean**: BugBot said "skipping" on three commits of PR #91, then reviewed a later commit and filed a Medium; meanwhile Gate 3 reported the skip as `PASS: no findings`. Neither face is safe to assume — gate fix folded into KIT-0062 F6. (KIT-0058)
- **`git archive` ships HEAD, not the working tree**: a door demo run from a kit tree with uncommitted files silently exported N-1 doctor checks. Any export/demo from a dirty source tree exercises the last commit; one-line notice filed as KIT-0064. (KIT-0058)
- **Cross-language "two can never disagree" pins don't need imports**: the door↔doctor path-equivalence test compares sourced-bash `config_home` against Python `_config_home` via doctor's own "no preset found at <path>" output line — no importlib gymnastics on an extensionless script, and the contract is enforced where it's observable. (KIT-0058)
- **o3 calibration, sixth data point**: FAIL decomposed as 2 real / 2 refuted / 1 pre-existing — including a "missing test" that existed in the very diff under review. Verdict-carries-no-signal holds. (KIT-0058)

### Empirically Disproven Reviewer Claims (decline-by-reference)

- **"`sed -n '/^## X/,/^## /p'` terminates on its own start line" — FALSE.** POSIX sed searches the end address from the line AFTER the addr1 match. Asserted identically by o3, Gemini fast-v2, AND CodeRabbit in one session — model-diverse review does not protect against shared training-data folklore about classic tools. BSD-sed repro pasted in `.kit/context/reviews/KIT-0035-evaluator-review.md`; decline by linking there. (KIT-0035)
- **"`grep -o` extracts the shortest match" — FALSE** (leftmost-longest; `26.3.1` extracts fully, not `26`). Tested live, repro in the same review record. (KIT-0035)
- When declining any reviewer claim, paste the repro in the review record — it turns later re-litigation (bots repeating an evaluator's false claim) into a one-reply copy-paste. (KIT-0035)
- Decline-by-reference is proven end-to-end: shown this section plus a fresh repro, fast-v2 *retracted* its prefix-collision claim in the next round. (KIT-0042)
- **"`gh` rejects full remote URLs as repo arguments" — FALSE** (o3, rated high-risk): three live `gh repo view` calls proved HTTPS, HTTPS+`.git`, and scp-style SSH forms all work. Repro in `.kit/context/reviews/KIT-0058-evaluator-review.md`. (KIT-0058)
- **CodeRabbit operational facts**: "Internal error occurred during review" can mean *quota exhaustion* (detail text says "Prepaid credits exhausted" only after several crash rounds — check it before re-triggering); the wrong handle `@coderabbit` (no `-ai`) is silently ignored. Outage substitution pattern documented in check-bots.md. (KIT-0042)
- **Preflight Gate 1 at-cap semantics (since PR #75)**: when `gh run list` returns a full page (raw count = limit), the gate reports PENDING, never PASS — a matrix-heavy repo hitting this should raise `CI_RUN_LIMIT`, not suspect a preflight bug. (KIT-0043)
- **Worktree tests can MUTATE the real repo, not just fail**: pre-commit exports an absolute `GIT_DIR` in worktrees; a leaked subprocess flipped `core.bare=true` on the primary clone (second occurrence of the KIT-0036 class, this time state-corrupting). Suite-wide `GIT_*` isolation now lives in `tests/conftest.py` (7ef104d); after pre-commit runs in a worktree, `git -C <primary> config core.bare` staying `false` is the canary. (KIT-0043)
- **Fresh worktrees are missing every gitignored install artifact**: `.venv`, `.env`, AND `.adversarial/evaluators/` (the CLI's "invalid choice" error means no evaluators installed). Provision all three at creation. (KIT-0043)
- **Stale-venv drift, second incident — this time it MUTATED files**: `.venv` carried adversarial-workflow 0.9.7 (aider-era transport, applies SEARCH/REPLACE edits to the working tree during review) while the system had the aider-free 1.0.1. Venv-context runs got the mutating engine; shell runs didn't — split-brain behavior identical in shape to the KIT-0032 stale-Black phantom. Venv upgraded to 1.0.1 (2026-07-14). Defense in depth stays: `git status` after every evaluator run (code-review-evaluator skill, Step 3). Candidate follow-up: generalize KIT-0035 F1's version-drift warning beyond Black. (KIT-0044 diagnosis)
- **Harness cwd-reset in worktree sessions is unresolved**: the shell cwd resets to the primary clone between Bash calls even in a worktree-launched session; `cd`/`git -C` prefixes persist. One more session of data, then document as standing pattern in WORKTREE-WORKFLOW.md or escalate. (KIT-0044)

---

## ADR Candidates

*None currently - insights above are implementation patterns rather than architectural decisions*

---

*Last updated: 2026-07-24 by planner-f5 (KIT-0058 extraction: committable≠compilable, BugBot skipping non-terminal, git-archive-ships-HEAD, cross-language output-line pins, gh-URL refutation)*
