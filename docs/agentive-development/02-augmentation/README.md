# Layer 2: Augmentation (External Review)

**Status:** 🚧 Content Coming Soon
**Estimated Completion:** Late November 2025
**Estimated Reading Time:** 2-3 weeks

---

## Overview

This layer teaches how to use external AI evaluation to catch design flaws before implementation. You'll learn to separate "maker" from "checker" mindset using multiple AI models, interpret adversarial feedback effectively, and know when evaluation is worth the cost.

**Goal:** Develop judgment about when to request evaluation vs. just ship

**Prerequisites:**
- Layer 1 (Foundation) completed
- Access to GPT-4o API (for evaluation)
- Basic understanding of cost/benefit analysis

---

## What You'll Learn

### 2.1 The Evaluation Concept
- **Concept:** Using external AI to critique implementation plans
- **Example:** TASK-2025-0073 evaluation (NEEDS_REVISION verdict)
- **Practice:** Submit a task plan for evaluation
- **Pattern:** Evaluation request format and severity ratings

### 2.2 Multi-Model Collaboration
- **Concept:** Claude for implementation, GPT-4o for evaluation
- **Example:** Wizard bugs evaluation (corrected wrong diagnosis)
- **Practice:** Compare Claude and GPT-4o on same plan
- **Pattern:** Model selection matrix (which model for what)

### 2.3 Interpreting Adversarial Feedback
- **Concept:** Understanding CRITICAL/MEDIUM/LOW severity levels
- **Example:** Triage evaluation recommendations by impact
- **Practice:** Process 10 recommendations, decide which to address
- **Pattern:** Feedback triage template (impact × effort matrix)

### 2.4 Iteration Protocols
- **Concept:** When to iterate vs. when to ship or escalate
- **Example:** 2-3 evaluation maximum with escalation rules
- **Practice:** Run evaluation, address feedback, decide next step
- **Pattern:** Iteration decision tree

### 2.5 Cost Awareness and ROI
- **Concept:** Balancing evaluation cost vs. value
- **Example:** $0.02-0.08 per evaluation, 50-400x ROI
- **Practice:** Estimate evaluation ROI for different task types
- **Pattern:** ROI calculation worksheet

### 2.6 When to Ask Humans Instead
- **Concept:** Recognizing evaluation limits and escalation needs
- **Example:** Contradictory feedback requires human judgment
- **Practice:** Categorize questions as "AI eval" vs. "ask human"
- **Pattern:** Escalation decision matrix

---

## Available Now

While layer content is being developed, you can:

**✅ Study existing examples:**
- [Example A1: Evaluation Workflow](../examples/11-evaluation-TASK-2025-0073-B.md)
- [Example A/D21: Wizard Bugs with Evaluation](../examples/21-wizard-bugs-evaluation-TASK-0040.md)

**✅ Review evaluation setup:**
- See project `.adversarial/docs/EVALUATION-WORKFLOW.md`
- See project `docs/decisions/adr/ADR-0011-adversarial-workflow-integration.md`

---

## Next Steps

After completing this layer, proceed to:
- **[Layer 3: Delegation](../03-delegation/README.md)** - Design specialized agents

---

**Layer Status:** Framework complete, content in development
**Last Updated:** 2025-11-14
**Estimated Content:** 30 documents (6 topics × 5 sections)
