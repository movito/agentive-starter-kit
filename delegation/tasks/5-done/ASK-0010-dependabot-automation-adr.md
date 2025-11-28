# ASK-0010: Dependabot Automation ADR

**Status**: Done
**Priority**: medium
**Assigned To**: planner
**Estimated Effort**: 1-2 hours
**Created**: 2025-11-28

## Related Tasks

**Parent Task**: None (ADR Migration - Tier 1)
**Depends On**: None
**Blocks**: None
**Related**: ASK-0007 (Test Infrastructure)

## Overview

Adapt and document the Dependabot Automation pattern from thematic-cuts (TC ADR-0042) for the agentive-starter-kit. This ADR establishes automated dependency updates with security scanning and testing integration.

**Source**: `thematic-cuts/docs/decisions/adr/ADR-0042-dependabot-automated-dependency-management.md`

**Why Essential**: Automated security updates are a production best practice. Dependabot creates PRs for outdated/vulnerable dependencies, which are then tested by CI before merge.

## Key Concepts to Document

### Dependabot Configuration

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
```

### Integration with CI

```
Dependabot PR Created
       ↓
GitHub Actions Run
       ↓
Tests Pass? → Merge / Review
```

### Security Benefits

1. **Vulnerability alerts** - GitHub security advisories
2. **Automated PRs** - No manual tracking required
3. **Version pinning** - Controlled updates
4. **Testing integration** - CI validates before merge

## Requirements

### Functional Requirements
1. Document the Dependabot pattern as an ADR
2. Explain configuration options
3. Show CI integration
4. Cover security considerations

### Non-Functional Requirements
- ADR follows project template
- Includes `.github/dependabot.yml` example
- References GitHub documentation

## Acceptance Criteria

### Must Have
- [ ] ADR-0008 created following project template
- [ ] Documents Dependabot configuration
- [ ] Explains CI integration for testing PRs
- [ ] Covers security scanning benefits
- [ ] Includes example configuration file

### Should Have
- [ ] Guidance on update frequency
- [ ] Handling breaking changes
- [ ] Grouping related updates

## Implementation Plan

1. **Read source ADR** from thematic-cuts
2. **Check existing Dependabot config** in starter-kit
3. **Adapt for starter-kit** - Match project structure
4. **Create ADR-0008** in `docs/decisions/adr/`

## Success Metrics

### Quantitative
- ADR created and follows template
- All acceptance criteria met

### Qualitative
- Security posture documented
- Clear update workflow

## Time Estimate

| Phase | Time |
|-------|------|
| Read source ADR | 20 min |
| Check existing config | 20 min |
| Adapt and write | 1 hour |
| Review and finalize | 20 min |
| **Total** | **1-2 hours** |

## References

- Source: `thematic-cuts/docs/decisions/adr/ADR-0042-dependabot-automated-dependency-management.md`
- GitHub Dependabot: https://docs.github.com/en/code-security/dependabot
- Example: `.github/dependabot.yml`

## Notes

- Dependabot is a GitHub feature, no code required
- This is primarily a configuration + documentation task
- May need to verify CI runs on Dependabot PRs

---

**Template Version**: 1.0.0
**Created**: 2025-11-28
