# KIT-0069 — Implementation Notes for the Planner

**Task**: audit truth sweep (prose cluster of the pre-0.9.0 cruft audit)
**Written**: 2026-07-27, during implementation (not retrospectively)
**Purpose**: process findings the planner should act on, separate from the
per-A-number dispositions that live in the PR body.

---

## 1. `rg` is not trustworthy in this repo — two distinct failure modes

This is the most important finding, because it nearly invalidated the
whole task in the first ten minutes.

**Mode A — hidden directories are skipped by default.** Nearly every kit
surface lives in a dot-directory (`.kit/`, `.claude/`, `.adversarial/`,
`.serena/`). A class grep without `--hidden` searches almost nothing that
matters and returns a *false all-clear*. My first ghost-citation sweep
returned zero hits across four patterns; the class actually had 20+ live
citations. Had I trusted it, the PR would have claimed a class was
"already fixed by #93/#94" while leaving every instance in place.

**Mode B — false-empties even with `--hidden`.** Later in the session,
`rg --hidden` with a multi-pattern `-e` set plus several `-g '!...'`
exclusions returned zero matches on a pattern that `grep -Rn` matched in
four files immediately. I did not fully diagnose the interaction; the
operational point stands regardless.

**Rule adopted (now self-review item 16):** use `grep -Rn` for any
class-closure evidence. An under-reporting grep in a truth-sweep task is
worse than no grep, because it manufactures false confidence and the
failure is silent.

**Planner action**: this affects every future class-sweep task, and the
audit itself was produced by agents running greps. Worth asking whether
any of the audit's own "not found" claims are Mode-A artifacts.

## 2. Serena's project root follows the *registered project*, not the cwd

`activate_project("agentive-starter-kit")` resolved to the **primary
clone**, while all work was happening in `../ask-worktrees/KIT-0069`.
`replace_in_files` would therefore have written every bulk edit into the
primary tree — which was sitting on `main`. Caught before use, by testing
the root with a string that existed only in the worktree.

Fix: `activate_project("<absolute worktree path>")` registers a separate
project (here: `KIT-0069`). Safe — `.serena/project.yml` is gitignored and
`.serena/` in a worktree is a real directory, not a symlink. It does write
`.serena/project.local.yml`, which was neither tracked nor ignored; a
`.gitignore` line was added.

**Planner action**: fold into KIT-0071. See §3.

## 3. KIT-0071 is scoped too narrowly — this is a worktree-provisioning class

KIT-0071 is specced around the `.venv` symlink. This session hit **four**
instances of the same underlying pattern — worktree provisioning that
shares or misdirects state with the primary clone:

| # | Surface | Nature |
|---|---------|--------|
| 1 | `.venv` | symlink to primary's venv (destructive on rebuild) |
| 2 | `.adversarial/evaluators` | symlink to primary's install tree |
| 3 | Serena project root | resolves to primary clone, not worktree |
| 4 | `rm -rf` permission | blocks temp-dir cleanup in worktree sessions |

Recommend widening KIT-0071 from "venv symlink" to "worktree
provisioning: what is shared, what is copied, what is misdirected" with a
doctor check that enumerates them.

## 4. Never bulk-edit the audit record

The `AGENT-TEMPLATE.md` path sweep matched **26 occurrences in 10 files**;
only **6** should change. Among the 20 that must not: the cruft-audit
record itself, which quotes the stale paths as evidence. A blind
`sed -i` repo-wide would have rewritten the evidence base and inverted its
before/after quotes — silently, and in a way that would survive review
because the resulting text still reads plausibly.

**What saved it**: `replace_in_files` with `dry_run=true` plus
`occurrence_ids` selection. For any class that spans both live surfaces
and historical records, dry-run-then-select is the correct tool, not a
cleverer regex.

**Planner action**: worth a standing rule — evidence files (audit records,
retros, review records) are append-only during the task that consumes
them.

## 5. "Broken command" was actually "orphaned capability" (A35)

`/check-spec` called an evaluator that ships nowhere. The obvious readings
were "fix the name" or "retire the command". Both were wrong.

Tracing the origin showed the evaluator is real and works — it is a
dispatch-kit **project-local custom** evaluator
(`.adversarial/evaluators/custom/spec-compliance.yml`, Gemini Flash,
~$0.004/run) that `facbb4b` left behind when porting the command, because
the kit installs from a library that has no `custom/` tier. The library has
never shipped one across 18 tags. The `-fast` suffix never matched the
evaluator's real name (`spec-compliance`) even in dispatch-kit, so the
command was likely broken at source.

**Generalisable lesson**: when a live surface cites a tool that does not
exist, trace *where the citation came from* before choosing fix-vs-retire.
A missing dependency and an orphaned one look identical from the citing
surface, and they have opposite correct dispositions.

**Also**: the adversarial-evaluator-library repo is itself kit-derived and
has inherited the same broken `check-spec.md`. Downstream propagation of
kit bugs is real and worth a periodic check.

Filed as KIT-0072.

## 6. Ownership-by-A-number cuts across files — say so explicitly

The binding ownership rule assigns *findings*, not *files*. Several files
are jointly owned:

- `COVERAGE-WORKFLOW.md` — A41 (KIT-0067) governs its `thematic_cuts`/53%
  content; A42 (this task) governs the dead PROCEDURAL pointer inside it.
  I fixed the pointer and left the rest, which will read as inconsistent
  until 0067 lands.
- `EVALUATION-WORKFLOW.md` — A71 (mine) covers one dead link; A68
  (KIT-0067) covers its `delegation/` tree and the other seven dead
  cross-references.
- `onboarding.md` — A33 (KIT-0067) is structural; its ghost template paths
  are A42-class and were fixed here.

This worked, but only because each split was reasoned about explicitly.
**Planner action**: when a future task splits an audit by finding, flag
jointly-owned files in the handoff so the implementer expects the seam
rather than discovering it.

## 7. Class-wide grep beats the audit's instance list — F1 was correct

The spec's "fix by class, grep the class repo-wide" instruction paid off
concretely: `.env.template:41,63` carried the pre-v0.4.0 `./scripts/project`
path and appears nowhere in the 92-finding audit. Similarly, the project
script's own help text used a bare `./project <cmd>` form that the audit's
`scripts/project` pattern did not match, and prose mentions of "procedural
index" (no filename) were invisible to a filename-only grep.

**Lesson for future audits**: an audit enumerates *instances*; only a class
grep closes a *class*. Budget for the delta — it was roughly +15% more
sites than the audit listed.

## 8. Verify model IDs against the live Models API, not any cached list

Three sources disagreed:

- the harness environment block: newest is Opus 4.8 / Sonnet 4.6
- the bundled `claude-api` skill catalog (cached 2026-06-04): same
- project memory: `claude-opus-5` / `claude-sonnet-5` are valid and
  supersede those

`GET /v1/models` settled it: **`claude-opus-5` and `claude-sonnet-5` are
real and newest**, and `claude-sonnet-4-20250514` / `claude-3-5-haiku-20241022`
are absent entirely (retired). Memory was right; both cached sources were
stale.

**Rule**: for any task that pins a model, curl `/v1/models` — it takes one
call and every static list ages. This is now written into AGENT-TEMPLATE's
model section so the next agent does not re-litigate it.

Corollary: hardcoded per-token pricing was removed from AGENT-TEMPLATE
rather than guessed. I could verify IDs but not 5-series pricing, and an
invented price is worse than a link.

## 9. Confirmations that held

- **Pre-commit output tail is not proof** (KIT-0057). Both commits ended
  with a passing pytest tail; both were verified with `git log -1` +
  `git status` before proceeding. No aborts occurred, but the check cost
  nothing.
- **Pre-formatting before commit** (KIT-0057 Phase-5 note) avoided any
  mutating-hook abort across two commits touching 5 Python files.
- **Self-review item 15** (grep the file for the token you just fixed)
  caught residual "procedural index" prose mentions in two files after the
  filename-level fix looked complete.

## 10. Two audit findings were REFUTED by direct measurement

Both survived the audit's adversarial verification. Both are wrong. This
is the strongest argument for the verify-before-believing reflex — a
verified finding is still a claim.

**A74 — evaluator verdict vocabulary. Refuted, and backwards.** The audit
said the doc's `APPROVED / NEEDS_REVISION / REJECT` vocabulary "will never
match a current evaluator verdict" because the library emits
`PASS / CONCERNS / FAIL`. Measured across the installed tree (25
evaluators declaring verdicts):

| Vocabulary | Count |
|---|---|
| `APPROVED` / `NEEDS_REVISION` / `REJECT` (and `REVISION_SUGGESTED`, `APPROVED`/`REJECT`) | 22 |
| `PASS` / `CONCERNS` / `FAIL` | 3 |

The audit generalised from the single evaluator it sampled
(`openai/code-reviewer`). Rewriting the doc as suggested would have broken
it for 22 of 25 evaluators.

**But there is a real bug underneath, which the audit missed**: the kit's
own recommended trio spans both vocabularies —
`code-reviewer-fast` and `code-reviewer` emit PASS/CONCERNS/FAIL while
`claude-code` emits APPROVED/REJECT. An agent grepping one fixed token
across the trio silently misses a verdict. The doc now says vocabulary is
per-evaluator, tabulates the variants, and tells agents to read the log
rather than pattern-match.

**A48 (part) — "the 3.5.0 manifest has no tiers at all".** Refuted. The
manifest groups files under `files.{scripts_core, commands_core,
commands_optional, kit_builder}`; `kit_builder` has 13 entries and does
sync `.kit/` contents. The playbook sentence the audit flagged is true and
was left alone. A48's *skills* claim was valid and was fixed.

**Planner action**: when a sweep task is derived from an audit, budget for
findings that are wrong, and require measured evidence in the disposition
rather than "as the audit says".

## 11. New findings surfaced while sweeping (not in the audit)

1. ~~**The manifest still syncs the retired `.kit/skills/`.**~~
   **WITHDRAWN — I over-claimed this as a new finding; it is already
   tracked.** `files.kit_builder` does contain `.kit/skills/`, but
   KIT-0059's Requirements already name the exact remedy ("Retarget the
   manifest: the `kit_builder` tier's `.kit/skills/` entry in
   `scripts/.core-manifest.json` becomes `.claude/skills/` … keep
   `tests/test_core_manifest.py` counts in sync in the same commit") and
   its Acceptance Criteria include "Manifest + manifest tests updated
   together". Nothing to file.

   Worth keeping as a process data point: `code-reviewer-fast` returned
   **FAIL** on this PR resting entirely on this item, calling it an
   "active correctness bug" causing "sync failures for consumer projects".
   Two independent checks refute that: (a) `.kit/skills/` **exists today**,
   so the manifest entry resolves and sync works — the hazard only appears
   *after* KIT-0059 deletes it; and (b) 0.9.0 removals are explicitly out
   of this task's scope per the handoff. The evaluator also could not see
   `scripts/.core-manifest.json` (not in the diff) and inferred its content
   from a doc — it reasoned about a file it had not read. **An evaluator
   verdict is a claim; check it the same way you check a doc citation.**
2. **Three documented releases were never tagged.** `v0.5.1`, `v0.6.0`,
   `v0.7.0` have CHANGELOG headings but no git tags, so no compare link
   can exist for them (the `[0.8.0]` link now spans `v0.5.0...v0.8.0`).
   Adding links for them would have manufactured broken URLs — the same
   class this task exists to remove. Cutting the tags retroactively, or
   accepting the gap, is a release-hygiene call for the 0.9.0 cut.
3. **`.env.template` carried a pre-v0.4.0 path** and appears in no audit
   finding — found only by the class grep (see §7).

## 12. Evaluator trio: both verdicts were FAIL, and both were wrong

Run pre-PR per the standing ordering rule. Outcome:

| Evaluator | Result | Findings | Survived verification |
|---|---|---|---|
| `code-reviewer-fast` (Gemini Flash) | **FAIL** | 1 blocking | 0 |
| `claude-code` (Sonnet) | **did not run** | — | — |
| `code-reviewer` (o3) | **FAIL** | 6 | **0 of 6** |

**`claude-code` could not run**: `litellm.BadRequestError … credit balance
is too low`. No log file was written — which is exactly why the standing
rule is "the log file with a verdict is the proof, never the exit code".
**Operator-owed: top up the Anthropic API balance.**

**`code-reviewer-fast`'s FAIL** rested entirely on the manifest still
listing `.kit/skills/`, called an "active correctness bug" causing
"sync failures for consumer projects". Refuted twice over: `.kit/skills/`
exists today so the entry resolves, and the remedy is already an explicit
named requirement in KIT-0059. The evaluator reasoned about
`scripts/.core-manifest.json`, which was **not in the diff** — it inferred
file contents from a doc that mentioned it.

**`code-reviewer` (o3) produced six findings; all six are fabricated.**
Each was checked against the tree:

| Claim | Measured reality |
|---|---|
| `scripts/core/project` hard-codes `delegation/tasks/` | 0 occurrences of `delegation`; 8 `.kit/tasks` references |
| `linear_sync_utils.py` scans `delegation/` | 0 occurrences; `sync_tasks_to_linear.py:517` reads `.kit/tasks` |
| `create-agent.sh` copies `.claude/agents/AGENT-TEMPLATE.md` | line 42 reads `.kit/templates/AGENT-TEMPLATE.md` |
| Tests still use `@pytest.mark.integration` / `.unit`, so `--strict-markers` breaks collection | 0 usages; the full suite passed **799/12s after** the markers were removed |
| Helper error text still prints `./scripts/<name>.sh --help` | every one prints `./scripts/core/...` |
| Two `AGENT-TEMPLATE.md` copies now diverge silently | `.claude/agents/AGENT-TEMPLATE.md` does not exist — its absence *was* finding A21 |

**The common failure mode across both evaluators**: reasoning confidently
about files **not present in the input**. A diff-only input invites the
model to reconstruct the unchanged side from assumption, and it reconstructs
the *pre-fix* state — so a truth-sweep PR reads as "the old paths are still
there". This is the same hazard the code-review-evaluator skill already
warns about ("diff-only input causes models to hallucinate missing
symbols"), now observed for whole files rather than symbols.

**Planner actions:**
1. For sweep-shaped PRs, either supply full-file context (cost permitting)
   or state in the input that unchanged regions must not be reasoned about
   — and expect FAIL verdicts that are artifacts of the input form.
2. **Never action an evaluator finding without reproducing it.** Two FAILs,
   seven findings, zero real. The verdict carries no signal on its own;
   this is now the tenth recorded o3 data point in that direction.
3. Consider whether the trio is the right gate for prose-only PRs at all,
   or whether a class-grep + full test suite is the stronger evidence.

## 13. Operator-owed items hit again

- **`rm -rf` allowlist** — blocked the F3 scratch-generation test; worked
  around with `mktemp -d`. Memory says this is the fifth consecutive task
  to hit it.
- **Sweep owed**: `/tmp/kit0069-gen.ZZga30/` (F3 artifact, could not be
  removed for the same reason).
