# KIT-ADR-0036: Read-only reviewer delegation — the carve-out to the no-Task-delegation rule

**Status**: Proposed (authored within KIT-0116 Phase 2; ratification =
operator merge of the Phase-2 PR — the human verdict IS the acceptance)
**Type**: Workflow / safety boundary — narrows a standing prohibition
by exactly one verified class and pins the boundary mechanically
**Date**: 2026-08-24
**Deciders**: Fredrik Matheson (operator, via PR verdict), Claude Code
(feature-developer-f5, KIT-0116 Phase 2)
**Related**: KIT-ADR-0035 (the obligation this discharges — its
Decision 3 review gap closes on native primitives), KIT-0116 (FR-4…FR-6,
FR-8), `.kit/context/workflows/REVIEW-PIPELINE.md` (Tier 2 in the
review ladder), the planner/fd "Sub-agent permission trap" footgun
(this ADR is now its cited exception), KIT-ADR-0014 (the interactive
review workflow this supersedes for spawned reviews)

## Context

The kit has had a standing rule since its earliest agent bodies:
**never delegate via the Task/Agent tool**. Two reasons, both real:

1. **The permission trap.** Sub-agents launched via the Task tool do
   not inherit `.claude/settings.json` allow patterns. An agent whose
   work needs Bash blocks on permission prompts it cannot answer —
   and a *background* sub-agent cannot prompt at all, so it fails or
   hangs silently. This is why the workflow made the operator the
   courier: paste a starter into a new tab, where permissions resolve
   interactively.
2. **Mutation risk.** An implementation agent holds Write/Edit/Bash.
   Delegating implementation multiplies the surfaces that can mutate
   the tree outside the gated workflow.

KIT-ADR-0035 named the cost: the three reviewer agents were **never
invoked once** — review labor priced at one operator tab each was
review labor that never happened. It also named the resolution path:
the tab-courier workflow was partly a *value* (operator sovereignty)
and partly a *workaround* (the permission trap). Native background
subagents with completion notifications separate the two — IF the
spawned agent cannot hit the trap and cannot mutate.

Both reasons are toolset-shaped. An agent whose declared tools are
pure reads has no permission surface to trap on and no way to mutate
the tree. The prohibition can therefore be narrowed by a *verifiable*
class rather than by trust.

## Decision

### 1. The rule stands for implementation agents

Delegation via the Task/Agent tool remains **banned** for any agent
holding mutating tools (Write, Edit, NotebookEdit, unrestricted Bash)
or needing permission-gated operations. The permission-trap rationale
is unchanged. Implementation agents are invoked by the operator in
new tabs, exactly as before.

### 2. The carve-out: read-only reviewer agents

A feature-developer session MAY spawn the kit's **reviewer agents**
(`code-reviewer`, `architecture-reviewer`, `security-reviewer`,
`document-reviewer`) as **background subagents via the Agent tool**,
after local tests pass, per REVIEW-PIPELINE.md's Tier 2 — provided
each spawned agent's declared toolset satisfies the read-only
condition in §3. The spawn is fire-and-continue: the fd keeps working
(docs, changelog) and triages findings on the completion notification
with the same fix-or-defer discipline as bot threads, persisting the
outcome in the task's review-pass record.

### 3. The toolset condition (what "read-only" means, exactly)

A reviewer agent is delegation-eligible iff every declared tool is on
this ruled roster:

| Tool | Ruling | Rationale |
|------|--------|-----------|
| Read, Grep, Glob | Permitted, all reviewers | Pure reads |
| TodoWrite | Permitted (code-reviewer) | Session-scoped scratch state; touches neither filesystem nor repo |
| WebSearch | Permitted (security-, document-reviewer) | Network read, no repo mutation; needed for CVE and docs verification. Accepted residual risk: a reader that can also query the web is an exfiltration surface — acceptable on this trusted codebase; revisit before pointing reviewers at untrusted diffs |
| WebFetch | Permitted (document-reviewer) | Link verification; same residual-risk note as WebSearch |
| Serena MCP (read/navigation tools) | Permitted | Semantic navigation; bodies must not instruct `execute_shell_command` (none do — audited 2026-08-24) |
| **Write, Edit, NotebookEdit** | **Forbidden** | Findings RETURN as the subagent's final message; the CALLER persists them (review-pass record). A reviewer that cannot write cannot corrupt the tree, and the KIT-ADR-0014-era "write your report file" flow is superseded for spawned reviews |
| **Bash** | **Removed from all reviewers** (FR-6 default remedy) | No reviewer demonstrated necessity: the diff scope arrives IN the spawn prompt (branch, changed-file list, or inline diff — the spawning fd already has it), so no reviewer needs git. Retention would require demonstrable necessity PLUS the exact commands enumerated under a `Permitted Bash commands` heading in BOTH the agent body and this ADR — `tests/test_review_pipeline_contracts.py` pins that mechanically. As of this ADR: **no agent enumerates any; the heading intentionally does not exist here** |

### 4. The spawn contract

The spawning session provides, in the prompt: the task ID, the review
dimension, and the **diff scope** (branch name + changed-file list at
minimum; inline diff for small changes). The reviewer never derives
the diff itself — it has no git. Findings return as the final
message; the fd triages fix-or-defer and persists into
`.kit/context/reviews/<TASK-ID>-review-pass.md`. Reviewer findings
**inform**; the human verdict (planner Phase 7) remains the merge
gate — operator sovereignty is untouched by this ADR.

### 5. The verified boundary

Recorded from the KIT-0116 Phase-2 live smoke (the gate for codifying
this — spec Risk 1: "the ADR records the verified boundary, not the
hoped-for one"):

- VERIFIED 2026-08-24: `code-reviewer` (toolset per §3) spawned as a
  background subagent via the Agent tool from an fd session completed
  its review and returned findings with **zero permission prompts**.
  Evidence: KIT-0116 Phase-2 PR + `KIT-0116-review-pass.md`.

## Consequences

- The operator stops being the courier for review labor; reviewer
  invocation cost drops from one tab + one pasted starter to one
  background spawn. (KIT-ADR-0035's success metric: reviewer agents
  invoked ≥ 1× per applicable task, from 0.)
- The no-delegation footgun text in planner and fd bodies now cites
  this ADR instead of stating an absolute — the absolute was
  load-bearing, so the exception lives in exactly one place (this
  file) and everywhere else points here.
- Enforcement is mechanical: `tests/test_review_pipeline_contracts.py`
  arms its reviewer-toolset and citation checks on this file's
  existence (`KIT-ADR-0036*.md` glob). A future reviewer agent that
  declares Bash without enumeration fails CI.
- The KIT-ADR-0014 interactive review flow (reviewer writes its own
  report file) is superseded for spawned reviews; report persistence
  is caller-side. KIT-ADR-0014 remains valid history for the
  interactive path.

## Revisit triggers

- A reviewer demonstrates genuine need for a git read (e.g. blame
  archaeology): add the enumeration to §3's table AND the agent body,
  under the pinned heading, in one PR.
- Reviewers pointed at untrusted diffs: re-rule WebSearch/WebFetch
  (exfiltration surface).
- Agent Teams leaves the experimental flag: re-evaluate whether the
  spawn contract migrates.
