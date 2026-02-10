# Nuum Memory Architecture (Sanity.io)

**Source**: https://www.sanity.io/blog/how-we-solved-the-agent-memory-problem
**Date Captured**: 2026-02-05
**Relevance**: Critical for KIT-ADR-0021 - informs agent lifecycle decisions

---

## The Problem: "Agentic Burn-Out"

As context windows fill during extended sessions, agents:
- Lose coherence
- Forget earlier decisions
- Repeat questions
- Gradually become less capable

Sanity calls this the **"Goldfish Problem"** - agents with no long-term memory.

---

## Their Solution: Distillation (Not Summarization)

**Key insight**: Summarization loses operational intelligence. Distillation preserves it.

> "Instead of summarizing a grab bag of unrelated material, we look for sequences in the context window that are related."

For each conversation segment, create two outputs:

| Output | Purpose | Example |
|--------|---------|---------|
| **Narrative** | 1-3 sentence summary of what happened | "Discussed auth strategy, decided on JWT" |
| **Retained Facts** | Actionable details | File paths, config values, decision rationales |

---

## Three-Tier Memory Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  TIER 1: Temporal Memory                                    │
│  - Full-fidelity message history                            │
│  - Full-text searchable                                     │
│  - Most recent, highest detail                              │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼ (background distillation)
┌─────────────────────────────────────────────────────────────┐
│  TIER 2: Distilled Memory                                   │
│  - Narrative + Retained Facts                               │
│  - Recursive: summaries get summarized                      │
│  - Gradient from detailed → abstract                        │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼ (curator agent extraction)
┌─────────────────────────────────────────────────────────────┐
│  TIER 3: Long-Term Memory                                   │
│  - Durable knowledge                                        │
│  - Persists across sessions                                 │
│  - Extracted by separate curator agent                      │
└─────────────────────────────────────────────────────────────┘
```

---

## Key Mechanisms

### Background Distillation
- Runs invisibly while agent works
- Compresses older segments automatically
- Targets ~40-60% context window saturation

### "Reflect" Tool
- Enables perfect recall
- Searches original Tier 1 messages
- Agent can retrieve exact details when needed

### Recursive Compression
- Tier 2 summaries themselves get summarized
- Creates natural gradient: recent=detailed, old=abstract
- Preserves decision rationale while discarding noise

---

## Results

**Nuum agent stats**:
- 7,400+ messages
- 6 days continuous operation
- Maintained coherence throughout
- Could recall file paths from early sessions
- Remembered architectural decisions despite thousands of intervening messages

---

## Implications for Agentive Starter Kit

### Fundamental Difference

| Aspect | Nuum/Miriad | Agentive Starter Kit |
|--------|-------------|---------------------|
| Agent lifecycle | Long-running (days) | Ephemeral (task → exit) |
| Memory location | In-agent + external tiers | File-based handoffs |
| Continuity | Continuous session | Discrete sessions |
| Context management | Distillation | Compaction (Claude's built-in) |

### Critical Questions

1. **Can we adopt their memory model with ephemeral agents?**
   - Tier 3 (long-term) could work - it's external
   - Tier 2 (distilled) could be passed between sessions
   - Tier 1 (temporal) would reset each session

2. **Do we need long-running agents?**
   - Their results suggest significant benefits
   - But: resource usage, failure recovery, complexity
   - Alternative: "warm" agents that persist for a task cluster

3. **What's the minimum viable memory system?**
   - Current: `agent-handoffs.json` + handoff documents
   - Enhanced: Add distilled facts extraction
   - Full: Three-tier with background workers

### Potential Adaptation Path

```
Ephemeral Agent Model + External Memory
────────────────────────────────────────

Session 1 (Agent A)
    │
    ├─► Work on task
    ├─► Extract retained facts → External Store
    └─► Exit

Session 2 (Agent B)
    │
    ├─► Load relevant facts from External Store
    ├─► Work on task
    ├─► Update retained facts → External Store
    └─► Exit

External Store = .agent-context/memory/
```

This preserves our ephemeral model while gaining memory continuity.

---

## Open Questions

- [ ] How does Tymbal relate to Nuum? Same system or separate?
- [ ] What triggers distillation? Time? Message count? Context %?
- [ ] How do they handle conflicting facts across sessions?
- [ ] What's the curator agent's prompt/logic?
- [ ] Can we implement Tier 3 without Tiers 1-2?

---

## Next Steps

1. Research Tymbal protocol - is it the communication layer for Nuum?
2. Examine miriad-app code for distillation implementation
3. Prototype simple fact extraction for our handoff documents
4. Evaluate: adapt their model vs. build simpler version

---

**Research Status**: Initial capture complete
**Recommendation**: This fundamentally changes our understanding - update ADR-0021 scope
