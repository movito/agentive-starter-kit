# KIT-0097 — Evaluator Review Record

**Mode**: full trio (all three provider keys present)
**Input**: `.adversarial/inputs/KIT-0097-code-review-input.md` —
`agentive review-input KIT-0097 --format diff`, 15 files, 1961 lines
**Format rationale**: `diff`, per the KIT-0092 shape rule and the handoff.
This PR is strings/docs-shaped (markdown agent definitions); `full` would
have handed the evaluators ~7000 lines of unchanged agent prose and
invited findings about text the diff never touched.
**Round**: 1 (deep rounds used: 1 of the ~2 cap)
**Raw logs**: `.kit/context/reviews/KIT-0097-evaluator-review-logs.md`

| Evaluator | Model | Verdict |
|---|---|---|
| `code-reviewer-fast` | gemini-2.5-flash | CONCERNS |
| `code-reviewer` | o3 | CONCERNS |
| `claude-code` | claude-sonnet-4-6 | (no verdict token emitted; findings only) |

## Disposition table

| # | Finding | Source | Disposition |
|---|---|---|---|
| E1 | `TARGET_REF` probe grep leaves version dots unescaped — `1.2.3` also matches `1X2X3` | o3 | **ACCEPTED** — real bug I introduced in F12. Fixed: `TARGET_RE="${TARGET//./\\.}"` + `grep -qE` with `[[:space:]]*`. Verified by hand: `1.2.3` matches, `1X2X3`/`1.2.30`/`11.2.3` do not. o3's stated repro (`1.2.30`) was itself wrong — the closing quote already anchored that — but the underlying defect was real. |
| E2 | `$PLANNING` does not persist across tool calls; `"$PLANNING"/scripts/…` silently becomes `/scripts/…` | claude-code (HIGH) | **ACCEPTED** — correct and specific to this harness: each Bash call is a fresh shell. Added an explicit warning that `$PLANNING` is a value to carry, not a variable that survives, plus a `ls <planning-root>/.kit/tasks` confirmation step. |
| E3 | Order test could silently pass with duplicate phase headings (e.g. a later "Evaluator Notes" section) | o3 + claude-code | **ACCEPTED** — plausible as the file grows. `find()` now asserts at most one heading matches each prefix and names the collisions. Falsified once. |
| E4 | Heading regex brittle to `###`, extra spaces | o3, claude-code | **ACCEPTED (partial)** — relaxed to `^\s*##\s+Phase\s+(\d+):\s*(.+?)\s*$` and the title is stripped. Deliberately still requires `##`: a phase demoted to `###` is a real structural change the pin should catch, not tolerate. |
| E5 | Table-row regex breaks on indentation | o3 | **ACCEPTED** — allowed leading whitespace and constrained the match to the row's own cell (`[^|]*`). Falsified once. |
| E6 | Table-row regex breaks on smart quotes | o3 | **DECLINED** — the pattern matches the literal phrase `before PR open`, which contains no quote characters. Nothing to break. |
| E7 | `re.findall` two-group unpacking may be an indexing error | claude-code (LOW) | **DECLINED** — evaluator checked and self-retracted in the same finding ("This is fine. *(No issue)*"). |
| E8 | ci-checker: missing/empty `CLAUDE.md`, empty Target Repository section, `gh` not installed | fast | **DECLINED** — out of scope (F9 is "skip the origin check in split mode") and the fallbacks are already correct: absent file/section → `SINGLE_REPO_MODE`, which is the right default. Pre-existing behavior this task did not touch. |
| E9 | Topology probe prints matched lines rather than using exit status, so a caller testing for non-empty output mis-classifies | o3 | **DECLINED for this PR** — the `grep -A 5 … \|\| echo SINGLE_REPO_MODE` idiom is repo-wide and pre-existing (feature-developer, wrap-up, check-spec all use it); the agent reads the output rather than branching on it in shell. Changing the idiom in one file would make the fleet inconsistent. Worth a dedicated sweep; noted rather than half-applied here. |
| E10 | Agents might not obey the new instructions (uncommitted-tree, wrong wrap-up variant, ignoring the API-key STOP, incomplete retro escalation, mixed `--format` choice) | fast (majority of its findings) | **DECLINED as a class** — these restate the instruction and assert the agent might not follow it. That is true of every line in every prompt file; it is not a defect in the change. The prose-sweep pattern the handoff predicted (KIT-0069/0073). Where a mechanical guard was possible and in scope, one exists (the F1 contract pin). |
| E11 | `test-runner`: project may not define test commands anywhere | fast | **DECLINED** — that is the ADR-0025 contract working as designed: the distributed body must not carry kit stack specifics. A project with no documented test command is a project-setup gap the agent should surface, not something this agent should paper over with a pytest default. |
| E12 | `check-spec`: detached HEAD, missing `origin/main`, `main` named `master` | fast | **DECLINED (noted)** — pre-existing in the command's other git calls; F15's scope was split-mode routing and merge-base correctness, both delivered. A general git-preconditions pass across the commands is a separate change. |
| E13 | `preflight`: auto-detection of `--task`/`--pr` can be wrong and pass silently | fast | **DECLINED** — this is exactly what the F16 edit now tells the operator (pass them explicitly when auto-detection could be wrong). Already addressed. |
| E14 | Shell-injection surface via `$PLANNING` / `<TASK-ID>` metacharacters | claude-code (MEDIUM/LOW) | **DECLINED** — operator-supplied local paths and framework-generated task IDs, inside an interactive developer session; every path in these docs is already double-quoted. The trust boundary the finding itself calls "acceptable for this trust model". |
| E15 | `set -a; source .env` exports more than the three keys | claude-code (LOW) | **DECLINED for this PR** — pre-existing idiom, documented in the evaluator skill with a worktree-permission rationale (KIT-0091) for the exact `. ./.env` form. Narrowing it is a change to the evaluator-invocation convention, not a content fix from the #4 review. |

| E16 | `check-spec`: the added `git fetch origin main` isn't routed through `-C "$TARGET"` in split mode | claude-code (LOW) | **ACCEPTED** — correct, and my own F15 edit introduced it: fetching in the planning repo leaves the target's `origin/main` stale, defeating the point of the fix. Both calls now show the split-mode form, plus a note for projects whose default branch isn't `main`. |
| E17 | `upgrader` rollback says "restore from that cache" with no command | claude-code (LOW) | **ACCEPTED** — a step an agent cannot execute is not a procedure. Rather than invent a cache-path edit (which the agent's own hard rules forbid), the step now directs it to probe `claude plugin --help` for a supported pinned-install form and to fall through to the operator-intervention case when none exists. |
| E18 | ~130 duplicated lines across the feature-developer pair are a drift hazard; add sync comments or extract | claude-code (MEDIUM) | **ACCEPTED, stronger than proposed** — the diagnosis is exactly what this task was cleaning up. Added the suggested SYNC comment AND a new contract test, `test_agent_pair_bodies_stay_identical`, which compares both pairs' bodies below `## Workflow Overview` (normalizing the identity header) so drift fails a test instead of relying on a comment being read. Falsified once. Extraction to an include was not done: the plugin distribution model ships each agent as a standalone file. |
| E19 | Removing CI sections from the reviewer agents is a behavioral contract change worth a migration note | claude-code (MEDIUM) | **ACCEPTED (as release note)** — recorded for the 2.0.1 plugin CHANGELOG rather than the agent bodies; that is where a consumer reads what changed. |
| E20 | Shared test over both pair halves gives false confidence if the F5 variant intentionally diverges | claude-code (LOW) | **DECLINED** — inverted. Divergence is precisely what the pair rule forbids and what E18's new test now enforces. An intentional future divergence would need that contract changed deliberately, which is the correct amount of friction. |

**Net**: 9 accepted (1 real bug, 2 real harness/routing defects, 1
unexecutable step, 4 test hardenings incl. a new pair-identity pin, 1
release note), 11 declined with reasons. All accepted items are in the
follow-up commit; the review round is closed at one deep round (cap ~2).
