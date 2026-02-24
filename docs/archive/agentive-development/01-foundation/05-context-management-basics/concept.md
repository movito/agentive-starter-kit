# Context Management Basics: Concept

**Layer:** Foundation
**Topic:** 1.5 Context Management Basics
**Estimated Reading Time:** 3-5 minutes

---

## What is Context Management?

Context management is the practice of documenting just enough shared understanding so work can resume across session boundaries without information loss. When you end a work session, you capture current state, decisions made, blockers encountered, and next steps planned. When you or another collaborator returns, they read the context document and continue without re-discovering what you already learned.

Context management transforms "What was I doing?" into "Read handoff, continue work." Instead of relying on memory or conversation history that degrades and disappears, you maintain persistent documentation that survives context windows, session ends, and agent handoffs.

In agentive development, context management is the shared memory that enables coordination. Agents don't have memory between sessions, so documented context is their only way to maintain continuity. Human collaborators benefit equally—six weeks later, you'll have forgotten the details that seemed obvious today.

## Why Does This Matter?

### Problems Solved

- **"What was I doing?" after session gaps** - Memory fades over days or weeks; undocumented context requires re-learning decisions
- **Repeated explanations across agents** - Without persistent context, every new agent asks the same questions you already answered
- **Lost insights from failed experiments** - When you don't document why approaches failed, others repeat the same mistakes
- **Context loss at handoff boundaries** - When work moves between people or agents, undocumented assumptions cause misalignment

### Value Provided

Context management preserves your expensive learning. When you spend three hours discovering that "approach A fails because of DaVinci Resolve API limitation X," documenting that insight saves the next person three hours. Multiply this across dozens of tasks and multiple agents, and context management becomes a massive time multiplier.

This practice enables asynchronous collaboration. When context is documented, you don't need to be online simultaneously to hand off work. The agent completes a task, documents state and decisions, and the next agent picks up seamlessly. Without context documentation, handoffs require synchronous meetings to transfer tribal knowledge.

Context management also supports your future self. The you of three months from now is effectively a different person who doesn't remember today's decisions. Documented context answers "why did we do it this way?" without requiring archaeological investigation through git history and slack threads.

## How It Fits in Agentive Development

Context management is the connective tissue between all other practices. Structured tasks define what to do; context management preserves why and how. TDD validates correctness; context management explains which tests matter and why. Git safety preserves code history; context management preserves decision history.

Later layers depend on context management even more. External evaluation requires context to review plans meaningfully. Specialized agents need context to understand task background. Multi-agent coordination requires shared context to prevent duplicate work or conflicting approaches. CI/CD systems reference context to understand test failures.

Without context management, every practice becomes isolated. With it, they compose into a coherent system where learning accumulates instead of evaporating.

## Key Principles

### 1. Document Current State at Session End

Before closing a session, capture where things stand right now. What's working? What's broken? What tests pass? What's deployed? "All tests passing except 3 precision tests marked xfail" is concrete state. "Making progress" is useless. Future you or the next agent needs to know exactly what exists, not vague status updates.

**Example:** "Implemented timecode conversion using Fraction. Tests pass for 23.976fps, fail for 29.97fps. Need to verify NTSC frame rate calculation."

### 2. Capture Blockers and Next Steps

Document what's preventing progress and what should happen next. Blockers might be technical ("DaVinci API doesn't expose timeline metadata"), environmental ("need access to production database"), or decisional ("unclear which export format to support"). Next steps should be concrete actions: "Add 29.97fps test cases" not "finish timecode work."

**Example:** "BLOCKED: GPT-4o API key expired, need to renew. NEXT: Once unblocked, run evaluation on TASK-2025-0078-B implementation plan."

### 3. Link to Related Work

Context doesn't exist in isolation. Link to task specifications, related tasks, relevant documentation, and previous decisions. "See TASK-2025-0012 for precision requirements" saves readers from searching. Links create a knowledge graph where context connects to other context, building organizational memory.

**Example:** "This approach differs from TASK-2025-0034 (file-based export). Related decision in ADR-0041 (API over file system)."

### 4. Minimal but Sufficient

Document what preserves understanding, not what can be inferred. Don't transcribe the entire git history or copy-paste code. Do capture non-obvious decisions, failed attempts, and key insights. If someone could figure it out in 5 minutes by reading code, don't document it. If it would take 30 minutes of investigation, document it.

**Example:** Good: "Used Fraction instead of float to prevent cumulative rounding errors." Bad: "Changed line 47 from 24.0 to Fraction(24000, 1001)." (visible in git diff)

### 5. Resumable by Others

Write context for someone who wasn't present during the work. Your colleague, a future agent, or your future self should be able to read the context and continue without asking clarifying questions. Avoid references to "earlier today we discussed..." because the reader wasn't there. Make context self-contained.

**Example:** Instead of "Fixed that issue we talked about," write "Fixed FileNotFoundError when export directory missing by creating it in process_media()."

## What's Next

See [Example: Context Management](./example.md) for a real handoff between agents where context documentation enabled seamless continuation across a week-long gap.

Then practice documenting session handoffs yourself in [Practice Exercise](./practice.md) to build this crucial habit.

---

**See also:**
- [Example: Context Management](./example.md)
- [Practice Exercise](./practice.md)
- [1.1 Structured AI Collaboration](../01-structured-ai-collaboration/concept.md)
- [1.6 Documentation Discipline](../06-documentation-discipline/concept.md)
- [3.6 Handoff Documentation](../../03-delegation/06-handoff-documentation/concept.md)
