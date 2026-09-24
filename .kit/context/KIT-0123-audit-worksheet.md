# KIT-0123 Audit Worksheet — Phases 1 + 2

**Date**: 2026-09-24 (all native-feature claims verified against the
live harness THIS session — source: Claude Code tool/skill
documentation as served 2026-09-24 — or against live platform docs
where noted. Bins below are PRELIMINARY; final verdicts are Phase 3,
after the evaluation gate and operator ruling.)
**Companion**: `.kit/context/FLEET-INVENTORY-2026-09-24.md`

## Phase 1 — Census + native-feature baseline

### Shipped surface (counts)

- **Agents**: 16 in kit `.claude/agents/`; 11 exposed by plugin 2.1.1;
  roster.yaml additionally carries legacy `feature-developer-v6`/`v7`
  entries (roster `type:` fields not yet inspected — VERIFY in Phase 3);
  `architecture-reviewer` (KIT-0116) and `feature-developer-o55`
  (2026-09-24) not yet released.
- **Commands**: 14. **Skills**: 5. **Workflow docs**: 15.
- **scripts/core**: 12 entries; **scripts/optional**: 4;
  **scripts/local** (kit-only, not shipped): 9.
- **Templates**: 4 (`.kit/templates/`) + task template.
- **Door/packaging**: `agentive-kit` PyPI 0.4.0 (door + engines) +
  plugin marketplace — two distribution channels, both audit rows.
- **Evaluator layer**: `.adversarial/` config + evaluator library
  integration (pin in pyproject `[tool.adversarial]`).

### Native Claude Code baseline (dated 2026-09-24, live harness)

Present natively in the current harness: ScheduleWakeup (with its own
pacing/cache guidance — **1-hour prompt-cache TTL**), Monitor,
background Bash + task notifications, TaskStop/TaskOutput; Agent tool
(background subagents, `isolation: "worktree"`, forks, SendMessage
continuation) + Workflow orchestration (opt-in); native skills
`/code-review` (effort levels, `--fix`, `--comment`, ultra),
`/security-review`, `/simplify`, `/loop`, `/schedule` (cloud cron),
`/run`, `/init`; EnterWorktree/ExitWorktree; auto-memory (MEMORY.md) +
CLAUDE.md hierarchy; plugin marketplace + skills system;
`update-config` (hooks/settings), `fewer-permission-prompts`;
`claude-code-guide` agent; `claude-api` skill (model IDs/migration);
Artifact publishing for reports/dashboards.

### Census with preliminary bins

Legend: DIFF = differentiated, COMM = commodity, SUP = superseded
candidate, MIX = split verdict likely. Evidence column cites dated
facts; PRELIMINARY throughout.

| Artifact | Bin (prelim) | Evidence / notes |
|---|---|---|
| feature-developer (+f5, o55) | DIFF (trim within) | Gated process = the moat. BUT Phase 7 cache guidance now **contradicts** the live harness: agent teaches 5-min-TTL pacing ("300 s is the worst choice"); ScheduleWakeup docs (2026-09-24) state 1-h TTL, no cache cliff. Dated divergence, not just duplication → body trim required whatever else happens. |
| planner (+f5) | DIFF (trim within) | Same trim class (Shell Rules / polling refs). Process content differentiated. |
| bot-triage skill | DIFF | Nine faces = recorded institutional knowledge; no native equivalent. Still accreting (KIT-0115). |
| Task lifecycle (specs/folders/`project`) | DIFF (form open) | No native equivalent. Form contested by stratum A itself: ixda ships ONE script (`project`); DTL dropped it for the global `agentive` CLI. Convergence decision needed (CLI likely — kills #142/#143 drift class). |
| TASK-STARTER-TEMPLATE + handoff/starter/review-record practice | DIFF | Heavily used in both stratum-A projects (handoffs, starters, review starters, retros throughout `.kit/context/`). |
| preflight, retro, wrap-up, start-task, status, triage-threads, commit-push-pr, check-spec | DIFF | Process commands; live usage: retro corpus mentions /wrap-up ×14, /retro ×6, /preflight ×2 (ID2). (Retro mentions are a weak lower bound — silent use invisible.) |
| babysit-pr, wait-for-bots, check-bots, check-ci commands + check-bots/wait-for-bots.sh | MIX→COMM | Polling layer. Native ScheduleWakeup/Monitor/`/loop` cover the mechanics; fd Phase 7 already inlines the loop. Candidate: collapse to one thin command citing native tools. |
| ci-checker agent | COMM | `gh` + native monitoring; thin value over a command. |
| test-runner / powertest-runner | COMM | Current models run test suites competently unaided; powertest's Task-tool delegation predates current rules. |
| code/security/document/architecture-reviewer agents | MIX | Overlap: native `/code-review`+`/security-review` (both already used in stratum A). BUT KIT-ADR-0036 Tier 2 spawns these as read-only background reviewers — the *delegation shape* is differentiated even if review content overlaps. Split verdict expected. |
| code-review-evaluator skill + `.adversarial` trio | MIX — decide with data | ACTIVE in both stratum-A projects (operator-confirmed; logs through ID2-0158, DTL-0036). Usage skews cheap tier (fast-v2, arch-review-fast-v2, claude-code; DTL also deep code-reviewer). Misses on record: trio 0-for-17 deletion-heavy vs bots 11-for-14; two prose-sweep shutouts; KIT-0118 third-axis (argv seams bot-favourable). Native /code-review in live use ×4 across both. Phase 3 question: does the trio earn its keep on logic-shaped diffs specifically? |
| pre-implementation, self-review, review-handoff skills | DIFF | Cheap prose discipline; no native equivalent; low carry cost. |
| WORKTREE-WORKFLOW.md | SUP (partial) | Native EnterWorktree/ExitWorktree + Agent `isolation:"worktree"` (2026-09-24). The ORDERING rule (`project start` on main → worktree) survives as process; mechanics go native. |
| COMMIT-PROTOCOL, REVIEW-PIPELINE (KIT-0116), REVIEW-FIX, TASK-COMPLETION, PR-SIZE, STACKED-PR, TESTING, COVERAGE, ADR-CREATION, TEMP-THEN-COMMIT, WORKFLOW-FREEZE, COMMAND-UX, AGENT-CREATION, EVALUATOR-LIBRARY | DIFF mostly | Process canon; audit row-by-row in Phase 3 for harness-workaround content (same trim class as agent bodies). REVIEW-PIPELINE is current (KIT-0116) and load-bearing. |
| bootstrap agent | SUP? | Door (`agentive new/adopt`) is the one setup entrance (KIT-ADR-0030); project-intake handles graduation. Verify no remaining niche. |
| project-intake agent | DIFF | Current door companion. |
| agent-creator agent + create-agent.sh + AGENT-TEMPLATE | MIX | Harness has native agent-creation affordances; kit template carries house conventions (frontmatter versioning, extension points). Likely: keep template, retire agent. |
| upgrader agent | DIFF — evolves | Seed of the reconciler in the target architecture (baseline capture, prune-shadowing, overlay recording). |
| feature-developer-v6/v7 roster entries | SUP | Legacy lineage; canonicalized into V2 (2026). Retire from roster at next release. |
| ci-check.sh, pattern_lint.py, validate_task_status.py, logging_config, lib/ | DIFF (project-side) | Repo hygiene, hook-wired; per-repo copies are the #142/#143 drift class → distribution question, not existence question. |
| check_cross_repo_config.py | DIFF (split-mode only) | Known bugs filed (#140-ish class from DTL-0026). |
| scripts/optional (linear sync, setup-dev, create-agent) | MIX | Linear sync dormant by operator choice; keep-as-optional vs archive. |
| new-project, setup-preset commands + door engines (PyPI) | MIX — channel decision | Two channels (plugin + PyPI door) both under audit; KIT-0107/0108 already queued. DTL pattern (global CLI) vs ixda pattern (vendored script) is the live experiment. |
| OPERATIONAL-RULES, PROTOTYPE-HANDOFF templates | DIFF (cheap) | Row-audit in Phase 3. |

## Phase 2 — Stratum-A empirical cross-check

**Corrections to prior understanding:**

1. **`ixda-services-planning` IS the ID2 project** (task prefix ID2,
   retros through ID2-0190, `AUDIT-IMPORT-2026-09-09.md`). Memory's
   "ID2 dormant" note is STALE — ID2 migrated into this pair and is the
   fleet's most active project. (Memory pointer updated this session.)
2. `.adversarial` is ACTIVE current-gen practice (operator-confirmed;
   fresh logs both projects), organized differently per project (ixda:
   per-provider dirs incl. mistral/openai; DTL: v1+v2 yml files).

**Usage signals:**

- ixda (ID2): `scripts/core/` = `project` ONLY — the empirical minimal
  core. No `.claude/` dir (user-level plugin). Full process-layer use:
  handoffs, starters, review starters, retros, analysis reports.
- DTL: no `project` script — lifecycle via global `agentive` CLI
  (KIT-0118); fuller scripts/core retained (ci-check, pattern_lint,
  validate_task_status, bot scripts); process layer in full use.
- Native `/code-review` already invoked in BOTH projects' recent retros.
- Divergence datum: the two current-gen projects solved "lifecycle
  tooling" two different ways (vendored single script vs global CLI) —
  the audit's convergence decision, not new machinery, resolves it.

## Open items for Phase 3

1. Roster `type:` fields for v6/v7 entries (verify before "retire" verdict).
2. Per-project plugin version pinning support (verify against Claude
   Code docs — determines where the overlay concept can live).
3. Trio verdict: segment the evidence by diff shape (logic vs prose vs
   deletion-heavy) and by tier (fast vs deep); weigh active usage.
4. Operator interview: commands/skills used silently (retro mentions
   are a lower bound); which optional layers they'd mourn.
5. Keep-list draft + KIT-ADR "ASK v2 scope" + eval gate
   (arch-review-fast, then arch-review o3 — `architecture` flag).
