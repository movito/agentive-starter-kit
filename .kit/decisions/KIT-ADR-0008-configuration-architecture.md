# KIT-ADR-0008: Configuration Architecture

**Status**: Accepted

**Date**: 2025-11-28

**Deciders**: planner, User

## Context

### Problem Statement

Applications need configuration that varies by environment (development, CI, production). We need a consistent, secure, and discoverable way to manage settings that:
- Keeps secrets out of version control
- Supports environment-specific overrides
- Is easy to understand and extend
- Follows industry best practices (12-factor app)

### Forces at Play

**Technical Requirements:**
- API keys and secrets must be protected
- Configuration should work in local dev, CI, and production
- Tool configurations (pytest, black, etc.) should be centralized
- New team members need clear onboarding path

**Constraints:**
- Must work with GitHub Actions (CI environment)
- Must not require additional infrastructure (no config servers)
- Should use Python ecosystem tools

**Assumptions:**
- All environments support environment variables
- Developers can create `.env` from template
- Secrets are managed per-environment

## Decision

We will adopt a **hierarchical configuration system** with four priority levels and clear separation between secrets and tool configuration.

### Core Principles

1. **Secrets in environment, not code**: API keys via `.env` (gitignored)
2. **Template-driven onboarding**: `.env.template` documents all variables
3. **Tool config in pyproject.toml**: Centralized, version-controlled
4. **Environment variables win**: Runtime can override any setting

### Implementation Details

**Configuration Hierarchy (lowest to highest priority):**

```
1. Defaults (in code)
    ↓ overridden by
2. pyproject.toml / config files
    ↓ overridden by
3. .env file (via python-dotenv)
    ↓ overridden by
4. Environment variables (runtime)
```

**File Locations:**

| File | Purpose | Version Controlled |
|------|---------|-------------------|
| `.env.template` | Documents required variables | ✅ Yes |
| `.env` | Actual secrets | ❌ No (gitignored) |
| `pyproject.toml` | Tool configuration | ✅ Yes |
| `.serena/project.yml` | Serena MCP config | ✅ Yes |
| `.pre-commit-config.yaml` | Pre-commit hooks | ✅ Yes |

**Environment Variable Categories:**

```bash
# .env.template structure

# API Keys (secrets)
OPENAI_API_KEY=          # For adversarial evaluation
LINEAR_API_KEY=          # For task sync (optional)

# Service Configuration
LINEAR_TEAM_ID=          # Team selection (optional)
GITHUB_REPO_URL=         # Auto-detected if unset

# Project Settings
PROJECT_NAME=            # Set during onboarding
TASK_PREFIX=TASK         # Task ID prefix
```

**Loading Configuration (Python):**

```python
from dotenv import load_dotenv
import os
from pathlib import Path

# Load .env from project root
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)

# Access with defaults
api_key = os.getenv("LINEAR_API_KEY")  # None if unset
task_prefix = os.getenv("TASK_PREFIX", "TASK")  # Default: TASK
```

**Tool Configuration (pyproject.toml):**

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["."]

[tool.black]
line-length = 88
target-version = ['py311']

[tool.coverage.run]
source = ["."]
omit = ["tests/*", "venv/*"]
```

**Adding New Configuration:**

1. **For secrets/API keys**:
   - Add to `.env.template` with documentation
   - Document in README if user-facing
   - Access via `os.getenv()` in code

2. **For tool settings**:
   - Add to appropriate `[tool.X]` section in `pyproject.toml`
   - No code changes needed (tools read directly)

3. **For application settings**:
   - Add to `.env.template` with default
   - Load in code with fallback: `os.getenv("KEY", "default")`

## Consequences

### Positive

- ✅ **Security**: Secrets never in version control
- ✅ **Discoverability**: `.env.template` documents all options
- ✅ **12-factor compliance**: Environment-based configuration
- ✅ **Simple onboarding**: Copy template, fill in values
- ✅ **CI-friendly**: Environment variables work everywhere

### Negative

- ⚠️ **Manual sync**: `.env.template` must be updated manually
- ⚠️ **No validation**: Typos in variable names fail silently
- ⚠️ **No type safety**: All values are strings by default

### Neutral

- 📊 **python-dotenv dependency**: Lightweight, well-maintained
- 📊 **Template maintenance**: Must keep `.env.template` current

## Alternatives Considered

### Alternative 1: Pydantic Settings

**Description**: Use Pydantic BaseSettings for typed configuration

**Not adopted yet because**:
- ❌ Additional complexity for current needs
- ❌ Project is simple enough for env vars
- ✅ Good future option if validation needed

### Alternative 2: YAML Configuration Files

**Description**: Use YAML files for all configuration

**Rejected because**:
- ❌ Secrets would need separate handling anyway
- ❌ Environment variables are more universal
- ❌ pyproject.toml already handles tool config

### Alternative 3: No .env.template

**Description**: Document environment variables only in README

**Rejected because**:
- ❌ Less discoverable than template file
- ❌ No clear structure for required vs optional
- ❌ Harder to onboard new developers

## Real-World Results

**Current Configuration Files:**

```
.
├── .env.template          # 82 lines, well-documented
├── .env                   # (gitignored, user-created)
├── pyproject.toml         # Tool configuration
├── .pre-commit-config.yaml
└── .serena/project.yml    # MCP configuration
```

**Onboarding Flow:**

```
1. Clone repository
2. cp .env.template .env
3. Fill in required API keys
4. Ready to develop
```

## Related Decisions

- KIT-ADR-0002: Serena MCP Integration (uses .serena/project.yml)
- KIT-ADR-0007: Dependabot Automation (uses pyproject.toml for Python deps)

## References

- 12-Factor App Config: https://12factor.net/config
- python-dotenv: https://pypi.org/project/python-dotenv/
- Pydantic Settings: https://docs.pydantic.dev/latest/concepts/pydantic_settings/

## Revision History

- 2025-11-28: Initial decision (Accepted)
  - Documented 4-level configuration hierarchy
  - Established .env.template pattern
  - Centralized tool config in pyproject.toml

---

**Template Version**: 1.1.0
**Last Updated**: 2025-11-28
**Project**: agentive-starter-kit
