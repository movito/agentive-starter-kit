# KIT-ADR-0035: Native Claude Code primitives supersede dispatch-kit — and the review gap closes on them

**Status**: Accepted (operator decision 2026-08-18; documented 2026-08-20)
**Type**: Strategic / platform — records a make-vs-adopt reversal and the
obligation it creates. Enforcement is KIT-0116's acceptance criteria and
KIT-0117's teardown checklist; its failure mode is the review gap
persisting silently, which is why the revisit trigger is usage-counted.
**Date**: 2026-08-20 (decision 2026-08-18)
**Deciders**: Fredrik Matheson (operator), Claude Code (planner-f5)
**Related**: KIT-ADR-0034 (this work is demand-generated, see Compliance),
KIT-ADR-0004 (adversarial workflow — the spec-time half of the review
ladder), KIT-0116 (automated review pipeline — the implementation),
KIT-0117 (dispatch-kit salvage + archive), KIT-0114 (executable logic in
markdown — the same defect class as the live `dispatch emit` steps),
KIT-ADR-0036 (reserved: read-only reviewer delegation carve-out, authored
within KIT-0116)

## Context

### The problem dispatch-kit set out to solve

When multiple agent sessions work a project, the human is the router:
deciding when a phase is done, which agent runs next, and carrying
context between terminal tabs by copy-paste. dispatch-kit
(`~/Github/dispatch-kit`, DSP prefix, ~6,150 LOC Python, 945 tests, 94%
coverage) attacked this with an append-only event bus (`bus.jsonl`),
declarative transition rules, gates (human/CI/evaluator/compound), trust
modes (approve/notify/auto), and a spawner that launched agents via
`tmux send-keys`. The design was clean — tmux was quarantined in exactly
two of its modules. But the operator never got along with tmux, usage
stopped, and the repo has been dormant since 2026-03-21.

### What changed underneath it

Landscape research (2026-08-18, verified against code.claude.com docs and
live GitHub API — evidence in KIT-0116 References):

- **Claude Code shipped the mission natively.** Cross-session messaging
  (v2.1.224+, on by default, Unix sockets, macOS/Linux): any two sessions
  in ordinary tabs discover and message each other — with safety
  semantics a `send-keys` router cannot have (sender identity, inbound
  hold/refuse, loop throttling, messages can never approve permissions).
  Plus: background subagents with completion notifications, Agent Teams
  (experimental flag: shared file-locked task list + mailboxes), Agent
  View (dispatch/monitor dashboard, auto-worktrees), Workflow tool
  (deterministic fan-out with verification stages).
- **The market reached the same verdict.** Dedicated tmux orchestrators
  are dead or stale since mid-2025; the MCP message-bus category never
  exceeded single-digit stars; the projects still alive (claude-squad,
  Vibe Kanban, Conductor) solve parallel-isolation UX, not message
  routing. "Software factories" (Factory.ai, Devin, OpenHands) are a
  different paradigm — hosted autonomy replacing local sessions, not
  connecting them. The niche became a platform feature.

### The lesson under the lesson

The kit's own workflow (starter messages, new tabs, human as gate) was
partly a *value* — operator sovereignty — and partly a *workaround* for
the sub-agent permission trap. Native messaging separates the two: the
operator keeps spawning and judging; the copy-paste courier role
disappears. Meanwhile the courier cost had a measurable casualty: the
kit's three reviewer agents (`code-reviewer`, `security-reviewer`,
`document-reviewer`) were defined and **never once invoked**, because
invocation meant another tab and another pasted starter. Review coverage
is strong at the ends (adversarial evaluators at spec time; BugBot +
CodeRabbit + human verdict at PR time) and hollow in the middle —
no dedicated code-review pass, no implementation-level architecture
review, no security pass, docs written opportunistically.

### What survives from dispatch-kit

Concepts, not code (canonical mapping: KIT-0116 Appendix A):

| dispatch-kit concept | Fate |
|---|---|
| Transition rules (when X → spawn Y) | Salvaged as gate wiring in agent bodies |
| Trust modes (approve/notify/auto) | Salvaged as review tiering (default-on / flag-triggered / opt-in) |
| Event bus | Superseded by harness task notifications |
| Spawner/sessions (tmux) | Obsolete |
| Gates, starters | Already lived in the kit |

## Decision

1. **The kit's coordination transport is native Claude Code primitives.**
   Background subagents, task notifications, cross-session messaging, and
   (when it leaves the experimental flag) Agent Teams. No homegrown
   routing layer — not on tmux, not on MCP, not on a file bus. Vendor
   coupling is accepted deliberately; the required capabilities are
   enumerated in KIT-0116 ("Platform capability mapping") so a platform
   change means remapping a list, not re-architecting.

2. **dispatch-kit retires: salvage, then archive** (KIT-0117). Its
   concepts land as configuration shape in the kit; its repo is archived
   with a retrospective; the five live `dispatch emit`/`dispatch log`
   steps still shipping in agentive-workflow plugin commands (and kit
   twins) are stripped on a release train. No dispatch-kit code is
   reused.

3. **The review gap MUST close on those primitives — this is an
   obligation, not an option.** The kit's setup is fine-tuned so that
   code review actually runs going forward (KIT-0116): a dedicated
   `/code-review` pass on every non-trivial task by default;
   architecture / security / docs dimensions flag-triggered at spec time
   from written heuristics; reviewer agents runnable as background
   read-only subagents (carve-out ADR reserved as KIT-ADR-0036); an
   opt-in deep-review workflow for high-risk work. "Defined but never
   invoked" is the failure state this ADR exists to prevent recurring.

## Known constraint: DTL still writes `.dispatch/`

design-theory-timeline's upgrade (2026-08-19, DTL-0026) **retained**
`.dispatch/` because a live dispatch-kit 0.4.2 writer exists there —
an operator choice. Consequence: the globally-installed `dispatch` CLI
is NOT to be uninstalled as a reflex. KIT-0117's teardown step must
first resolve DTL's dependency (migrate DTL off the writer, or
explicitly scope the CLI as DTL-local) before removing the binary.
Archiving the dispatch-kit *repo* is independent of this and can proceed.

## Compliance with KIT-ADR-0034

This work is demand-generated, not audit-generated: the operator hit the
friction in real usage (tmux abandonment; reviewer agents unused because
invocation cost a tab) and initiated the investigation. The plugin
survey that found the live `dispatch emit` steps was scoped verification
of an operator question, not a sweep.

## Consequences

- KIT-0116 (2-todo, three-eval-round gate passed) implements the review
  pipeline; KIT-0117 (backlog) executes salvage + teardown + archive.
- The reserved reviewer-delegation ADR shifts to **KIT-ADR-0036**
  (KIT-0116 spec updated in the same commit as this ADR).
- Plugin release-train pairing: KIT-0117's command-stripping should ride
  the same release as KIT-0115 (and KIT-0111 if sequenced next).
- A live demo of cross-session messaging is deferred by operator choice;
  it can ride KIT-0117's close-out session.
- The kit's "never delegate via Task" guidance stays intact for
  implementation agents; KIT-ADR-0036 will define the read-only
  exception precisely.

## Revisit triggers

- Reviewer-agent invocation count is still ~0 two months after KIT-0116
  ships → the fine-tuning failed; reopen.
- Agent Teams leaves the experimental flag → evaluate as orchestration
  layer (potentially replacing starter-paste launches).
- A platform change breaks any capability in KIT-0116's mapping →
  remap or reconsider decision 1.
- DTL migrates off its `.dispatch/` writer → complete KIT-0117's CLI
  teardown.
