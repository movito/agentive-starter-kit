# KIT-0092 — Evaluator Review Record

**Task**: Shim removal + monolith test shrinkage (agentive-kit 0.3.1)
**Branch**: `feature/KIT-0092-shim-removal`
**Commit reviewed**: `dfca585`
**Date**: 2026-08-08
**Input**: `.adversarial/inputs/KIT-0092-code-review-input.md`
(22 files, 9,857 lines, `--format full`) — generated via `agentive
review-input`, dogfooding the retargeted CLI (handoff requirement).

**Ordering**: trio run BEFORE PR open, per the KIT-0035/KIT-0046
ordering rule. Round 1 of a max 2.

## Verdicts

| Evaluator | Model | Verdict | Cost class |
|---|---|---|---|
| `code-reviewer-fast` | gemini-2.5-flash | FAIL | ~$0.01 |
| `code-reviewer` | o3 | FAIL | ~$0.33 |
| `claude-code` | claude-sonnet-4-6 | **APPROVED** | ~$0.05 |

## The central disposition fact

This PR's changes to `preflight.py` and `review_input.py` are
**100% docstrings, comments, and user-facing strings** — verified by
`git diff HEAD~1` over both files: not one line of logic changed. The
`--format full` input handed the evaluators whole modules, so the two
FAIL verdicts reviewed the *modules*, not the *change*. Every finding
below that targets module logic is therefore pre-existing behavior,
unmodified by this PR.

`claude-code` reached the same conclusion independently: "The issues
identified are primarily structural… appropriate to address in
follow-up work, not blockers for this cleanup PR."

## Disposition table

| # | Evaluator | Finding | Disposition |
|---|---|---|---|
| 1 | o3 | Unbalanced closing fence in `_file_section` — "always produced" | **REFUTED — hallucination.** `review_input.py:240` is `f"````{lang}\n{content}````\n\n"`: four backticks BOTH sides. Empirically confirmed against the generated artifact — 40 four-backtick lines, an even number (20 balanced pairs; 22 files less 2 pure deletions). Not a bug. |
| 2 | o3 | Gate 3 treats `completed:skipped` BugBot runs as failure | Pre-existing `_gate_3_bugbot` logic; untouched by this PR. Plausible and worth a task — NOT actioned here (out of scope, and gate-semantics changes need their own parity evidence). |
| 3 | o3 | CI event filter ignores `pull_request_target` / `merge_group` | Pre-existing `_gate_1_ci` logic; untouched. Same disposition as #2. |
| 4 | o3 / fast | Target repo path may escape root (`../../../etc`) | Pre-existing `review_input.main` validation; untouched. Real hardening candidate for a follow-up. |
| 5 | fast | `git log` failure ⇒ empty `code_sha` ⇒ bot gates false-PASS | Pre-existing `main`/gate logic; untouched. Legitimate latent; follow-up. |
| 6 | fast | Unhandled `OSError` on output dir/file write | Pre-existing `review_input.main`; untouched. Follow-up. |
| 7 | fast | Whitespace-in-`target.path` checked in `review_input` but not `preflight` | Pre-existing asymmetry; untouched. Follow-up. |
| 8 | claude-code | GraphQL interpolation safe but call-order-fragile (2× HIGH) | Explicitly assessed by the evaluator itself as "currently safe", "not blockers". Validators run before every interpolation on all live paths. No action. |
| 9 | claude-code | `os.chdir` in harnesses not thread-safe under `pytest-xdist` | **In my diff's blast radius — verified.** `pytest-xdist` is neither installed nor configured (`addopts` has no `-n`), so it cannot bite today. The pattern predates this PR (the python half always used `os.chdir`). No action; noted for whoever introduces parallel runs. |
| 10 | claude-code | Gate 5 `rglob` vs Gate 6 `glob` asymmetry | Pre-existing; undocumented but intentional. Follow-up doc nit. |
| 11 | claude-code | `_parse_args` stdout/stderr asymmetry | Pre-existing, inherited verbatim from the bash original. Changing it would break the output contract the (surviving) matrix pins. No action. |
| 12 | claude-code | Manifest count tests are brittle magic numbers | Working as designed — a "did you mean to change the count?" gate. The evaluator agrees. This PR updates them (29→26, 50→47) with reasons in comments. No action. |
| 13 | claude-code | `review_input.py` holds two unrelated entry points | Acknowledged in the module docstring; the evaluator marks it "not a blocker for this PR". Follow-up refactor candidate. |

**Actioned in this PR: none.** One finding refuted outright (#1); one
verified as inert in this repo (#9); the rest are pre-existing module
behavior outside a docs-and-strings diff.

## Adjacent defect found while dogfooding (not actioned)

`agentive review-input`'s "Next steps" hint prints
`ADVERSARIAL_UNATTENDED=1`. Grepped the actual install
(`~/.local/share/uv/tools/adversarial-workflow/`, not the repo venv —
`adversarial` is a separate uv tool): **the flag does not exist.**

This is the *exact* defect `self-review/SKILL.md` lesson #10 records
from KIT-0044 — a shipped hint about another tool's interface that was
never verified against the installed version. It regressed, or was
never fully removed from the "Next steps" tail. Harmless in practice
(an unknown env var is ignored; the `echo y |` pipe does the real
work), but it is a false runtime claim in shipped output.

Not actioned: outside this PR's scope. Worth a small task.

## Deep rounds used

1 of 2 permitted. No round 2 — nothing was actioned, so a re-run would
review an unchanged diff.
