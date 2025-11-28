# ADR-0007: Dependabot Automated Dependency Management

**Status**: Accepted

**Date**: 2025-11-28

**Deciders**: planner, User

## Context

### Problem Statement

Dependencies become outdated and vulnerable over time. Manual tracking of security advisories and version updates is time-consuming and error-prone. We need automated dependency management that:
- Alerts us to security vulnerabilities
- Creates PRs for updates automatically
- Integrates with our CI pipeline for validation

### Forces at Play

**Technical Requirements:**
- Python package updates (pip ecosystem)
- GitHub Actions version updates
- Weekly update cadence (balance freshness vs. noise)
- CI validation before merge

**Constraints:**
- Must work with GitHub's native features
- PRs should be testable via existing CI workflow
- Should not overwhelm maintainers with PR volume

**Assumptions:**
- Repository is hosted on GitHub
- CI runs on all PRs (including Dependabot PRs)
- Maintainers review and merge dependency PRs

## Decision

We will use **GitHub Dependabot** for automated dependency management with weekly updates and grouped minor/patch PRs.

### Core Principles

1. **Security first**: Dependabot alerts for known vulnerabilities
2. **Controlled updates**: Weekly schedule, limited PR volume
3. **CI validation**: All updates tested before merge
4. **Reduced noise**: Group minor/patch updates together

### Implementation Details

**Configuration Location**: `.github/dependabot.yml`

**Package Ecosystems Monitored:**

| Ecosystem | Directory | Schedule | PR Limit |
|-----------|-----------|----------|----------|
| pip (Python) | `/` | Weekly (Monday 9am PT) | 5 |
| github-actions | `/` | Weekly (Monday 9am PT) | 3 |

**Update Grouping:**

Minor and patch updates are grouped together to reduce PR noise:

```yaml
groups:
  python-minor-patch:
    patterns:
      - "*"
    update-types:
      - "minor"
      - "patch"
```

Major updates are kept separate for careful review.

**Commit Message Convention:**

```
deps(scope): Update package from x.y.z to a.b.c
ci(scope): Update action from v1 to v2
```

**Workflow Integration:**

```
Dependabot detects update
    ↓
Creates PR with changes
    ↓
CI workflow runs (test.yml)
    ↓
Tests pass? → Ready for review
Tests fail? → Investigate compatibility
```

**Labels Applied:**
- `dependencies` - All Dependabot PRs
- `python` - Python package updates
- `github-actions` - Actions updates

## Consequences

### Positive

- ✅ **Automated security**: Vulnerabilities detected and patched promptly
- ✅ **Reduced manual work**: No need to track versions manually
- ✅ **CI integration**: Updates validated before merge
- ✅ **Controlled volume**: Grouped updates reduce PR noise
- ✅ **Audit trail**: All dependency changes tracked in git history

### Negative

- ⚠️ **Review overhead**: Still requires human review/merge
- ⚠️ **Potential breakage**: Updates may introduce incompatibilities
- ⚠️ **GitHub dependency**: Relies on GitHub's Dependabot service

### Neutral

- 📊 **Weekly cadence**: Balance between freshness and stability
- 📊 **PR limits**: May queue updates if limit reached

## Alternatives Considered

### Alternative 1: Manual Dependency Updates

**Description**: Manually track and update dependencies periodically

**Rejected because**:
- ❌ Time-consuming and easy to forget
- ❌ Security vulnerabilities may go unnoticed
- ❌ No automation benefits

### Alternative 2: Renovate Bot

**Description**: Use Renovate instead of Dependabot

**Rejected because**:
- ❌ Requires additional setup/hosting
- ❌ Dependabot is built into GitHub (simpler)
- ❌ Similar functionality for our needs
- Note: Renovate offers more configuration options if needed later

### Alternative 3: Daily Updates

**Description**: Run Dependabot daily instead of weekly

**Rejected because**:
- ❌ Too many PRs to review
- ❌ Excessive noise for maintainers
- ❌ Weekly is sufficient for non-critical updates

## Real-World Results

**Before this decision:**
- Manual dependency tracking
- Security vulnerabilities discovered reactively
- Inconsistent update cadence

**After this decision:**
- Automated weekly PRs for updates
- Security alerts within 24 hours
- Consistent, predictable update schedule
- All updates validated by CI before merge

## Related Decisions

- ADR-0005: Test Infrastructure Strategy (CI runs on Dependabot PRs)

## References

- GitHub Dependabot: https://docs.github.com/en/code-security/dependabot
- Dependabot configuration: https://docs.github.com/en/code-security/dependabot/dependabot-version-updates/configuration-options-for-the-dependabot.yml-file
- Security advisories: https://github.com/advisories

## Revision History

- 2025-11-28: Initial decision (Accepted)
  - Weekly updates for pip and github-actions
  - Grouped minor/patch updates
  - Integrated with CI workflow

---

**Template Version**: 1.1.0
**Last Updated**: 2025-11-28
**Project**: agentive-starter-kit
