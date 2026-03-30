# Research Quality Standards

**Version**: 1.0.0
**Last Updated**: 2025-01-28
**Applies To**: All agents producing research, analysis, or knowledge documents

---

## Purpose

This document establishes mandatory quality standards for research documents produced by knowledge-focused agents. These standards ensure research outputs are factually accurate, well-sourced, and defensible under scrutiny.

---

## The Four Quality Gates

Every research document must pass these gates before being considered complete:

### Gate 1: Citation Integrity

**Requirement**: All factual claims must be traceable to verifiable sources.

**Standards**:
| Marker | Meaning | Action Required |
|--------|---------|-----------------|
| ✅ | Verified accessible | None |
| ⚠️ | Paywalled/restricted | Note access requirements |
| ❌ | 404/unavailable | Find alternative or remove claim |
| 🔄 | Requires periodic check | Add to verification backlog |

**Process**:
1. **At time of citation**: Attempt to access the URL
2. **If inaccessible**: Note the status inline (e.g., "[Paywalled - accessed via institutional login]")
3. **For official sources**: Prefer .gov/.org domains over third-party summaries
4. **For statistics**: Cite primary source, not news articles citing the source

### Gate 2: Factual Accuracy

**Requirement**: Claims must be verified against authoritative sources, with explicit confidence levels.

**Confidence Levels**:
| Level | Definition | Documentation Required |
|-------|------------|----------------------|
| **High** | Verified against primary legal/official source | Citation to statute, regulation, or official guidance |
| **Medium** | Verified against reputable secondary source | Citation + note that primary source should be checked |
| **Low** | Based on inference, older sources, or single source | Explicit caveat in text |

**Verification Hierarchy**:
1. **Primary sources** (statutes, regulations, official guidance)
2. **Official publications** (government reports, authority manuals)
3. **Professional analysis** (major consultancies, law firms)
4. **Academic literature** (peer-reviewed)
5. **Industry publications** (trade associations, news)

**Red Flags to Check**:
- Round numbers (often estimates, not official figures)
- Rates and percentages (change frequently, verify currency)
- Deadlines and timeframes (often misquoted)
- "According to..." without specific citation

### Gate 3: Reproducibility

**Requirement**: Another researcher must be able to verify findings using documented methodology.

**Required Documentation**:

```markdown
## Appendix: Search Methodology

### Sources Consulted
- [List databases, websites, search engines used]

### Search Terms
- [List actual search queries]

### Date Range
- Research conducted: [dates]
- Sources current as of: [date]

### Limitations
- [What couldn't be accessed]
- [What languages were/weren't searched]
- [What time constraints applied]
```

### Gate 4: External Validation

**Requirement**: High-stakes documents must undergo external adversarial review.

**When Required**:
- Documents intended for external audiences
- Analysis making novel or controversial claims
- Comparative analyses across domains
- Any document > 500 lines

**How to Request**:
```bash
# Run external evaluator
adversarial evaluate <document-path>

# Read results
cat .adversarial/logs/<document>-EVALUATION.md
```

**Evaluator Selection**:
| Evaluator | Best For |
|-----------|----------|
| `gpt52-reasoning` | Policy documents, logical analysis |
| `mistral-content` | European context, content review |
| `o3-chain` | Complex multi-step claims |

**Iteration Protocol**:
- Address CRITICAL findings (must fix)
- Consider HIGH findings (should fix)
- Use judgment on MEDIUM/LOW
- Max 2-3 evaluation rounds per document
- Escalate if feedback is contradictory

---

## Document Lifecycle

### Draft Stage
- [ ] All claims have citations
- [ ] URLs tested for accessibility
- [ ] Confidence levels assigned
- [ ] Search methodology documented

### Review Stage
- [ ] External evaluation requested (if required)
- [ ] Critical/High findings addressed
- [ ] Citation status markers added (✅/⚠️/❌)

### Final Stage
- [ ] Version number assigned
- [ ] "Working Process" section at top with:
  - Version history
  - External review status
  - Outstanding verification items
- [ ] Moved to appropriate research folder

---

## Working Process Section Template

Add this to the top of all research documents:

```markdown
## Working Process

| Version | Date | Changes | Reviewer |
|---------|------|---------|----------|
| 1.0 | YYYY-MM-DD | Initial draft | [Agent] |
| 2.0 | YYYY-MM-DD | Addressed evaluator findings | [Agent] |

### External Review Status
- **External Review**: [Date] - [APPROVED/NEEDS_REVISION]
- **Key findings addressed**: [List]

### Outstanding Verification Items
- [ ] [Item requiring future verification]

### Citation Integrity Summary
- Total citations: N
- Verified (✅): N
- Paywalled (⚠️): N
- Broken (❌): N
```

---

## Quick Reference Checklist

Before marking a research document complete:

```markdown
## Pre-Completion Checklist

### Citation Integrity
- [ ] All factual claims have citations
- [ ] URLs tested and marked (✅/⚠️/❌)
- [ ] Primary sources preferred over secondary

### Factual Accuracy
- [ ] Confidence levels assigned to key claims
- [ ] Key facts verified against official sources
- [ ] No unattributed statistics

### Reproducibility
- [ ] Search methodology appendix included
- [ ] Sources and search terms documented
- [ ] Limitations acknowledged

### External Validation (if required)
- [ ] Evaluator run on document
- [ ] Critical/High findings addressed
- [ ] Working Process section updated
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-01-28 | Initial version |
