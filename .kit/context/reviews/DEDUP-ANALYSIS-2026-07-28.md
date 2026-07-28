# Deduplication & Dead-Code Analysis — 2026-07-28

**Repo**: agentive-starter-kit @ main `1dc3f0c`
**Method**: 3-layer (mechanical inventory → taxonomy/conceptual judgment → verification + operator-split). Read-only.
**Operator question answered**: *"the project root and the .kit folder contain many of the same things"* — see §2, the taxonomy/mirror table. The short answer: they mostly do **not** duplicate; the apparent overlap is the deliberate product/planning split (canonical homes live under `.claude/` and `scripts/core/`; `.kit/` is the builder layer). The few real duplications are already claimed by pinned 0.9.0 removals.

---

## 1. Executive summary

| Metric | Count |
|---|---|
| Tracked files | 609 |
| Exact content-duplicate groups | 4 (only 1 non-trivial: the `.kit/skills` symlinks, already KIT-0059) |
| Provably-dead files | 4 (stale tracked evaluator inputs in a now-gitignored dir) |
| Operator-must-confirm items | 6 (questions, not deletions) |
| Done-task handoff/starter accumulation | 74 files / 7,516 lines in `.kit/context/` flat |
| Files untouched since before 2026-06-01 | 269 (mostly legitimate historical + stable-reachable) |
| Multi-home artifact categories | 4 (skills, ADRs, templates, docs) — all explained in §2 |

**Two prior audits already cover the "bugs/currency" axis** and are complementary, not overlapping, with this one:
- `.kit/context/reviews/PRE-090-CRUFT-AUDIT-2026-07-24.md` (589L, 92 findings: stale-doc/version-drift/contradiction — e.g. `project linearsync`/`create-agent` pointing at pre-v0.4.0 paths).
- `.kit/context/reviews/DOC-CURATION-AUDIT-2026-07-28.md` (33 docs; audience/currency). Its two deletion targets (`docs/prd/`, `.kit/docs/TESTING.md`) are **already actioned** — both gone from the tree; do not re-report.

This analysis intentionally targets a different axis: **duplication, dead code, and the multi-home taxonomy** feeding a future planning/product split.

---

## 2. Taxonomy / mirror map (the centerpiece)

For each artifact category: every directory home, which is canonical, and what each home holds. Canonical-homes principle is KIT-ADR-0027 P6 (skills/commands/agents live under `.claude/`).

| Category | Homes | Canonical | What each home holds / verdict |
|---|---|---|---|
| **Agents** | `.claude/agents/` (15) | `.claude/agents/` | Single home. Harness-reachable by definition; all 15 have live citers. No duplication. Not synced downstream (no `agents_core` tier — KIT-0026 backlog tracks that). |
| **Commands** | `.claude/commands/` (14) | `.claude/commands/` | Single home. 11 shipped downstream (6 core + 5 optional); **3 builder-only, not in manifest**: `new-project`, `setup-preset`, `wrap-up` (correctly local — they drive project creation / session finalize). Taxonomy note, not dead code. |
| **Skills** | `.claude/skills/` (5 real) **+ `.kit/skills/` (3 symlinks)** | `.claude/skills/` | **REAL DUPLICATION — already claimed.** `.kit/skills/{code-review-evaluator,review-handoff,self-review}/SKILL.md` are relative symlinks into `.claude/skills/` (read-both deprecation cycle). **KIT-0059 removes them at 0.9.0.** Exclude from new findings. Hashes see them as exact dups (§3). |
| **ADRs** | `docs/adr/` (2) + `.kit/adr/` (31) | both (distinct roles) | **NOT duplication — the product/planning split by design.** `docs/adr/` = the *consumer project's own* ADRs (holds only `about-adr.md` + `TEMPLATE-FOR-ADR-FILES.md`, i.e. scaffolding for downstream). `.kit/adr/` = kit reference ADRs (KIT-ADR-*). Quirk (documented, not a finding): `.kit/adr/` also holds `ADR-0007`/`ADR-0008` (non-KIT prefix, promoted); `about-kit-adr.md:58` explicitly explains the naming collision. |
| **Templates** | `.kit/templates/` (4) + `.kit/context/templates/` (2) + `.kit/tasks/9-reference/templates/` (1) + `.adversarial/templates/` (2) | split by purpose | **Multi-home but role-separated** (see §4 for the one conceptual-overlap pair). `.kit/templates/` = agent/task authoring (AGENT-TEMPLATE, TASK-STARTER-TEMPLATE, OPERATIONAL-RULES, PROTOTYPE-HANDOFF). `.kit/context/templates/` = review-artifact templates. `9-reference/templates/` = task-template shipped as consumer reference. `.adversarial/templates/` = evaluator input templates. |
| **Docs** | `docs/` (10) + `docs/archive/` (92) + `.kit/docs/` (3) | split by audience | `docs/` = consumer-facing product docs. `.kit/docs/` = builder docs (migration playbook, linear-sync behavior, UPGRADE-0.4.0). `docs/archive/` = historical (the agentive-development curriculum). No cross-home duplication found. |
| **Workflows** | `.kit/context/workflows/` (13) | single | Single home; all cited by agents/CLAUDE.md. No duplication. |
| **Scripts** | `scripts/core/` (27) + `scripts/local/` (10) + `scripts/optional/` (6) | tiered by distribution | core = synced downstream; local = ASK-only (engines, bootstrap door, kit_markers); optional = opt-in. All reachable (§5). 4 shim files here are pinned removals. |
| **Adversarial** | `.adversarial/` (config, templates, inputs) + `.adversarial/evaluators` (symlink) + `.kit/adversarial/` (operator untouchable) | — | `config.yml` + `config.yml.template` (template ships in `kit_builder`). `inputs/` is **gitignored yet has 5 tracked files** (§5 dead). `.kit/adversarial/` = operator-owned, untracked — not analyzed. |
| **Launchers** | `.kit/launchers/launch` (1) | single | Deliberately kept (restored 2026-07-28; KIT-0075 owns modernization). Not a finding. |
| **Tests** | `tests/` (27) | single | Reachable via pytest. No duplication. |
| **Task-lifecycle records** | `.kit/tasks/{1-backlog…9-reference}/` (113) + `.kit/context/` flat handoffs/starters (§7) | — | Task specs by status = live state. Flat handoffs/starters for *done* tasks = accumulation (§7). |

**Bottom line for the operator:** root vs `.kit` overlap is real for exactly **one** category (skills, already being removed) and **apparent-but-intentional** for ADRs/docs/templates (product side vs builder side). There is no sprawling duplication to clean up — the split is largely clean already.

---

## 3. Exact-duplicate pairs (MD5 of whitespace-normalized content)

| Group | Verdict |
|---|---|
| `.kit/skills/*/SKILL.md` ↔ `.claude/skills/*/SKILL.md` (3 pairs) | **Symlinks** — KIT-0059 removes at 0.9.0. Not new work. |
| 44 × empty `.gitkeep` + 3 × empty `__init__.py` (all zero/near-zero content) | Trivial structural placeholders; identical because empty. **Ignore** — deleting `.gitkeep`s would drop tracked empty dirs. |

No non-trivial exact duplicates of real content exist outside the symlinks.

---

## 4. Conceptual duplicates (two surfaces, one job)

| Pair | Assessment | Recommendation |
|---|---|---|
| `.kit/context/templates/review-starter-template.md` (67L) ↔ `.kit/templates/TASK-STARTER-TEMPLATE.md` | Overlapping intent (both scaffold a review/starter handoff) but different granularity — the context one is the review-starter body, the kit one is the task-starter. **Low-confidence overlap.** | Operator confirm whether both are still authored-from; if the review-starter is auto-generated by an agent from the review-template, one may be redundant. **Question, not a merge order.** |
| `docs/STARTING-A-PROJECT.md` ↔ `new-project` skill/command ↔ `create-project` agent | Three surfaces teach project creation, but at different layers (human doc vs slash-command vs agent). This is intentional layering, **not** duplication. | Keep. |
| `docs/UPDATING-YOUR-PROJECT.md` ↔ `docs/MANIFEST-UPGRADE-GUIDE.md` ↔ `docs/PLUGIN-UPGRADE-GUIDE.md` | Three update surfaces; UPDATING is the index that points at the other two by surface (scripts vs plugin). Doc-curation audit already flagged MANIFEST-UPGRADE-GUIDE for a **trim** (stale inline example manifest), not a merge. | Defer to doc-curation audit's trim disposition; no new merge. |

No hash-invisible helper-pair duplication found in scripts (each engine/helper has a distinct role).

---

## 5. Provably dead (no consumer of any kind; evidence trail)

| File | Evidence | Recommendation |
|---|---|---|
| `.adversarial/inputs/ASK-0039-code-review-input.md` (631L) | `.adversarial/inputs/` is **gitignored** (`.gitignore:141`) yet this file is tracked (committed pre-ignore). Only citer is the completed ASK-0039's own historical review under `.kit/context/reviews/`. A stale run-artifact for a done task. | **Delete (git rm).** Directory is meant to be ephemeral/ignored. |
| `.adversarial/inputs/ASK-0039-spec-compliance-input.md` (449L) | Same as above. | **Delete.** |
| `.adversarial/inputs/ASK-0043-code-review-input.md` (125L) | Same; done task ASK-0043. | **Delete.** |
| `.adversarial/inputs/KIT-0024-code-review-input.md` (70L) | Same; done task KIT-0024. | **Delete.** |

Total: 4 files / 1,275 lines. All are evaluator *inputs* (regenerated per run by `prepare-review-input.sh`), for long-done tasks, in a directory the repo already declares gitignored. The `.gitkeep` in that dir should stay (holds the tracked empty dir). This is the only provably-dead code — everything else has at least a plausible operator consumer.

---

## 6. No visible consumer — OPERATOR MUST CONFIRM (questions, never deletions)

*(The launch-incident lesson: citation greps cannot see manual operator usage. Each of these has no programmatic consumer but may be invoked by hand or is deliberately-kept.)*

1. **`.dispatch/config.yml` (64L, untouched since 2026-03-30)** — cited only by docs/agents that *describe* dispatch, not by any live script. Is the `.dispatch/` dispatch-kit compatibility layer still in use, or superseded by the current sync engine? (ASK-0038 verified it long ago; may now be vestigial.)
2. **Three builder-only commands `new-project` / `setup-preset` / `wrap-up`** — reachable by the harness locally but absent from the manifest, so they never reach consumers. Intended (builder-only)? If so, this is correct-as-is; confirming closes the taxonomy gap.
3. **`.serena/claude-code/USE-CASES.md` (912L, 2026-03-30)** — large Serena usage doc cited by test-runner/powertest-runner agents and engine copy-lists. Still current for the Serena workflow, or reference cruft? (Kept if agents genuinely point operators here.)
4. **`.kit/context/templates/review-starter-template.md` vs review-template.md** — see §4. Are both still the source templates agents copy from, or has one been superseded by an agent generating starters inline?
5. **`.kit/docs/UPGRADE-0.4.0.md`** — a version-pinned migration doc for the v0.4.0 scripts restructure; live citers are all historical/handoff. Keep as migration history, or move to `docs/archive/`? (Analogous to the doc-curation audit's archive dispositions.)
6. **`.kit/templates/OPERATIONAL-RULES.md` (199L, 2026-03-30)** — cited by KIT-ADR-0023 and the migration playbook and TASK-STARTER-TEMPLATE. Confirm it's still the operational-rules source injected into task starters (if so, keep; it looked stable, not stale).

None of these are deletion recommendations. They are the "operator knows something greps can't" set.

---

## 7. Done-task handoff accumulation (quantified)

`.kit/context/` holds **104 flat files / 12,009 lines** of session artifacts. Of those, **74 files / 7,516 lines** are HANDOFF / REVIEW-STARTER / TASK-STARTER / SESSION artifacts whose task ID is in `5-done` / `6-canceled` / `7-blocked`:

- 46 `*-HANDOFF-*` files
- 38 `*-REVIEW-STARTER*` files (overlap in totals; combined 74 tie to done tasks)
- plus SESSION-HANDOFF/INVENTORY/SPIKE/DEMO one-offs

These are historical (not live citers, not cleanup candidates individually) — **but their accumulation is the finding**, as a recent gate flagged. `.kit/context/` root is now a 111-entry directory mixing live coordination files (`patterns.yml`, `agent-handoffs.json`, `current-state.json`, `workflows/`) with 74 dead per-task handoffs.

**Recommendation:** relocate completed-task handoffs/starters to a `.kit/context/archive/` (or `.kit/tasks/8-archive/handoffs/`) subtree — mirrors the existing `docs/archive/` pattern. Keeps history, de-clutters the working directory, and makes the live-vs-historical boundary legible. A move (not delete) preserves the record. This is the single largest legibility win available and is low-risk (pure `git mv`).

---

## 8. What this means for a future planning/product repo split

Mapping each `.kit/` subtree (and its root-side counterparts) to where it lands post-split:

| Subtree | Post-split home | Notes |
|---|---|---|
| `.kit/context/` (handoffs, retros, reviews, workflows, patterns.yml, current-state) | **Planning repo** | Pure coordination state. The §7 archive cleanup should happen *before* a split so the planning repo starts clean. |
| `.kit/tasks/` | **Planning repo** | Task lifecycle is planning. Except `9-reference/` (consumer-facing template) → could stay in product as an example. |
| `.kit/adr/` (KIT-ADR-*) | **Product repo** (as shipped reference) | These are the *kit's* decisions; consumers inherit them read-only. Ship with product. |
| `.kit/templates/`, `.kit/docs/` | **Product repo** | Authoring templates + builder docs distribute downstream (they're in the `kit_builder` manifest tier). |
| `.kit/skills/` | **gone** (KIT-0059) | Symlinks removed at 0.9.0; canonical `.claude/skills/` ships with product. |
| `.kit/launchers/` | **Planning repo** | Operator tooling for driving the kit. |
| `.claude/` (agents, commands, skills) | **Product repo** | Canonical homes; the distributable payload. |
| `scripts/core/` | **Product repo** | Synced downstream. |
| `scripts/local/` (engines, bootstrap door, kit_markers) | **Planning/product-factory repo** | ASK-only; the "project factory" tooling. Not distributed. |
| `scripts/optional/` | **Product repo** | Opt-in consumer scripts. |
| `.adversarial/` (config, templates) | **Product repo**; `inputs/` **ephemeral** | Config template ships; inputs are per-run and gitignored (§5). |
| `docs/` + `docs/archive/` | **Product repo** | Consumer-facing. |

**The split is already ~80% clean** thanks to KIT-ADR-0027's canonical-homes work. The three things that would make it cleaner *before* splitting: (a) finish the pinned 0.9.0 symlink/shim removals (already scheduled), (b) archive the 74 done-task handoffs (§7), (c) delete the 4 stale evaluator inputs (§5). None require new architecture.

---

## Appendix — reachability confirmations (Layer 3)

- All 15 agents, all 14 commands, all 27 core scripts, all 10 local + 6 optional scripts have ≥3 live citers (path-basename greps, excluding historical dirs). No orphaned scripts.
- Manifest `kit_builder` tier ships `.kit/skills/` (symlinks) — KIT-0059 retargets to `.claude/skills/`; already tracked, not a new finding.
- `.aider.chat.history.md` is **not tracked** (only done/canceled task specs mention aider; KIT-0065 purged aider-era scripts).
- `docs/prd/` and `.kit/docs/TESTING.md` (doc-curation audit targets) are **already removed** from the tree — do not re-report.
