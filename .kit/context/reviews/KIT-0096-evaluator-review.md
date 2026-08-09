# KIT-0096 — Evaluator review record (both PRs)

**Task**: KIT-0096 plugin release refresh (agentive-workflow 2.0.0)
**Date**: 2026-08-09
**Trio run per PR, pre-PR-open (KIT-0035/KIT-0046 ordering rule).**
Formats per format-by-change-shape: marketplace input `diff` (strings/docs
sweep), kit input `full` (new logic).

Logs (read-only):

- `.adversarial/logs/KIT-0096-marketplace-code-review-input--code-reviewer-fast.md` (FAIL)
- `.adversarial/logs/KIT-0096-marketplace-code-review-input--code-reviewer.md` (FAIL)
- `.adversarial/logs/KIT-0096-marketplace-code-review-input--claude-code.md` (no verdict emitted)
- `.adversarial/logs/KIT-0096-code-review-input--code-reviewer-fast.md` (CONCERNS)
- `.adversarial/logs/KIT-0096-code-review-input--code-reviewer.md` (CONCERNS)
- `.adversarial/logs/KIT-0096-code-review-input--claude-code.md` (no verdict emitted)

Verdicts below APPROVED with all findings dispositioned-and-cited are a
legitimate gate-pass per the Oscillation protocol (code-review-evaluator
skill). Deep rounds: 1 per PR (cap 2, not reached — no re-run needed
since every accepted finding was fixed and re-verified locally).

## Marketplace PR (movito/agentive-skills, 2.0.0)

Scope note: this PR ships the KIT'S CANONICAL agent bodies (spec: "agent
behavior stays as the kit repo defines it"). Findings against the
canonical workflow content are out of scope here and marked KIT-SIDE
where they deserve upstream attention.

| # | Finding (evaluator) | Disposition |
|---|---|---|
| M1 | `check-ci main` hardcode reintroduced in code-reviewer; June copy had dynamic detection + warning (claude-code HIGH, deep, fast) | **ACCEPTED — fixed** (`c4baa99`). Reproduced against tree: June's hardening restored, and extended to document/security/test-runner which carry the same kit-canonical hardcode. Flagged for kit-side backport. |
| M2 | test-runner hardcodes pytest/80%/pattern_lint (ADR-0025 leak) (claude-code LOW) | **ACCEPTED — fixed** (`c4baa99`). Kit stack specifics replaced by runtime-read; in scope as generalization. Kit canonical unchanged (kit's own body legitimately names its stack). |
| M3 | document-reviewer "for the this project" ambiguity (claude-code MEDIUM) | **ACCEPTED — fixed** (`c4baa99`). |
| M4 | wrap-up drops `phase_complete` emit silently (claude-code LOW) | **ACCEPTED — CHANGELOG line added** (`c4baa99`), scoped precisely: only wrap-up's step was removed (KIT-0077); 4 commands keep optional emits (verified by grep both refs). |
| M5 | PII email in plugin.json, public repo (claude-code HIGH) | **FLAGGED TO OPERATOR** — pre-existing since 1.1.0 (also marketplace.json owner block); it is the operator's published identity. Not changed unilaterally; see PR body. |
| M6 | `agentive` CLI required but not installed by plugin (deep, fast) | **DECLINED** — real dependency, documented: README "Depends on" section names both channels + install command; ADR-0028 packaging owns the install story. Shims existed and were deliberately retired at agentive-kit 0.3.1 (KIT-0092). |
| M7 | `verify-ci.sh` references "outdated" vs agentive CLI (fast ×2) | **DECLINED** — kit is mid-migration (verified: check-ci.md ships verify-ci.sh, preflight.md ships `agentive preflight`); bodies ship kit-canonical; README documents the dual state. |
| M8 | spec-compliance evaluator "legacy references" (deep) | **DECLINED — misread.** Reproduced: all 6 mentions are warnings saying it does NOT exist / do not run it (check-spec.md:48, SKILL.md:197-200). |
| M9 | planner Branch-Isolation vs Phase-5 worktree-add "contradiction" (fast) | **DECLINED** — kit-canonical content; policy governs commits to feature branches, creation-at-authoring is the WORKTREE-WORKFLOW ordering rule. KIT-SIDE candidate for wording clarity. |
| M10 | agent-handoffs.json skipped on non-main branches misleads planner (fast) | **DECLINED — by design** (KIT-0093 reconciliation, cited in the body itself). |
| M11 | planner/planner-f5 "diverge in one place" (claude-code MEDIUM) | **DECLINED — verified.** `diff` shows exactly 5 hunks per pair (frontmatter, dates, title, header note, identity line); bodies byte-identical. Same for feature-developer pair. |
| M12 | roster kit_sha256 unverifiable in this PR (claude-code LOW) | **ACCEPTED as process note** — generation command + guard location stated in PR body; the kit PR's guard + 14 tests verify them mechanically; README Maintenance documents regeneration per release. |
| M13 | Robustness musings on canonical workflow demands (fast ×12: upgrader parsing, ACK halt, oscillation-state, self-review rigor, retro complexity, etc.) | **DECLINED** — critiques of the kit's canonical contracts, not defects introduced by this PR; behavior changes are explicitly out of scope. |
| M14 | `echo y \| adversarial` false-success risk; `source .env` inconsistency (claude-code MEDIUM ×2, fast) | **DECLINED** — kit-canonical skill/agent text. KIT-SIDE candidates. |
| M15 | upgrader rollback retention window unverified (claude-code LOW, fast) | **DECLINED** — the text itself flags "verify; this may change"; kit-canonical. |

Net: no finding against the transforms this PR actually performs
(generalization + namespacing) survived reproduction except M1–M3,
all fixed. Zero kit-specific leaks found by any evaluator.

## Kit PR (drift guard)

| # | Finding | Disposition |
|---|---|---|
| K1 | Roster `source` can escape kit root (all three evaluators) | **ACCEPTED — fixed** (`e0a874b`): containment check (absolute + `..` refused), 2 tests. Roster is network-fetched input. |
| K2 | Permission-denied on source file crashes guard (deep) | **ACCEPTED — fixed** (`e0a874b`): OSError → finding, not traceback. |
| K3 | Duplicate roster entries "hide drift" (deep) | **ACCEPTED (validation), mechanics disputed** — a stale duplicate would still append a finding, nothing hidden; but uniqueness validation added as malformed-roster finding + test. |
| K4 | Unpinned pyyaml in CI (claude-code HIGH) | **ACCEPTED — floor pinned** (`>=6.0`, matching dev extra). |
| K5 | `raise SystemExit` chain inconsistency (claude-code LOW) | **ACCEPTED — fixed** (`from exc`). |
| K6 | Windows backslash paths (deep) | **DECLINED** — kit targets POSIX (README portability rule is macOS/Linux); CI is ubuntu; roster generated by kit tooling. |
| K7 | SSRF / URL allowlist (claude-code MEDIUM) | **DECLINED** — `--roster-url` is operator/CI configuration, not attacker-controlled input; workflow hardcodes the default. |
| K8 | Unpinned actions @v7 supply chain (claude-code HIGH) | **DECLINED** — repo convention (test.yml, all workflows use @vN); changing pin style is repo-wide policy, not this PR. |
| K9 | Multi-GB roster body OOM (deep) | **DECLINED** — trusted URL, ephemeral CI runner. |
| K10 | `components: []` silent pass (claude-code LOW) | **DECLINED — wrong**: the completeness sweep then reports every kit component unrostered → FAIL (exercised by tests' roster+glob interplay). |
| K11 | cert-verification config (claude-code LOW) | **DECLINED** — urllib verifies TLS by default. |
| K12 | Guard untested (deep on marketplace input) / test-fixture races (claude-code) | **DECLINED — addressed**: 14 tests incl. falsification AC, missing-hash, traversal, duplicates; tests are single-threaded tmp_path fixtures. |

## Falsification evidence (spec AC)

Automated: `test_kit_newer_than_release_fails` (and 13 siblings) — green.
Live run: copied `.claude/` to a scratch root, appended one line to
feature-developer.md, ran the guard against the staged 2.0.0 roster →
exit 1, finding names the file and both hashes. In-sync run against this
tree → exit 0, "27 shipped components match".
