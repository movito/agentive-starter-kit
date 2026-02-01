# ASK-0029: Multi-Evaluator Architecture

**Status**: Done
**Priority**: High
**Assigned To**: feature-developer
**Estimated Effort**: 4-5 hours
**Created**: 2025-02-01
**Source**: Architectural discussion - enabling multiple evaluation providers

## Problem Statement

The starter kit template references specific models and lacks multi-evaluator support:

1. `pyproject.toml` requires `adversarial-workflow>=0.6.2` (older version)
2. `.adversarial/config.yml.template` uses deprecated `evaluator_model` field
3. Agent prompts (planner.md) contain hard-coded "External GPT-4o via Aider"
4. Template lacks `.adversarial/evaluators/` directory for custom evaluators
5. No documentation or onboarding for alternative evaluators

**Version Requirements**:

| Version | Feature | Required for This Task? |
|---------|---------|------------------------|
| v0.6.0 | Custom evaluator support (`.adversarial/evaluators/*.yml`) | Yes - core feature |
| v0.6.3 | Configurable timeout per evaluator (`timeout` field) | Yes - needed for long-running evaluators |
| v0.6.4 | `list-evaluators` CLI command | Yes - user discoverability |
| v0.7.0 | Current stable with all above + bug fixes | **Recommended** |

**Version Constraint Rationale**: We use `>=0.7.0` (not `==0.7.0`) because:
- adversarial-workflow follows semver; minor/patch updates should be backward compatible
- Pinning exact versions would require coordinated starter kit updates for every bugfix
- The `>=` constraint is standard Python packaging practice for libraries
- Users who need exact reproducibility can pin in their own projects

The evaluator library uses version tags for install (more cautious) because it copies files directly into the project, where unexpected changes have higher impact.

**Built-in vs Custom Evaluators**:
- **Built-in** (`evaluate`, `proofread`, `review`): Hard-coded to use OpenAI, require `OPENAI_API_KEY`. These are convenience defaults shipped with adversarial-workflow.
- **Custom** (`.adversarial/evaluators/*.yml`): User-defined, can use any provider supported by aider. This is how users get "provider-agnostic" evaluation.

Users without OpenAI keys can still use the evaluation system by installing custom evaluators for their preferred provider (e.g., Gemini, Mistral, Anthropic).

## Goals

1. **Provider-agnostic documentation** - Remove model-specific references from prompts/docs
2. **Optional evaluator library** - Offer `adversarial-evaluator-library` as an optional enhancement
3. **Reproducible installation** - Pin library version for reproducibility
4. **Clear onboarding** - Add evaluator choice to onboarding flow

## Requirements

### Must Have

- [ ] Bump `adversarial-workflow>=0.7.0` in pyproject.toml
- [ ] Update `.adversarial/config.yml.template` to be model-agnostic
- [ ] Create `.adversarial/evaluators/.gitkeep` directory
- [ ] Update agent prompts to remove "GPT-4o" specificity (planner.md, others)
- [ ] Add `./scripts/project install-evaluators` command
- [ ] Update onboarding agent with evaluator setup phase

### Should Have

- [ ] Update README adversarial section to mention multiple evaluators
- [ ] Update `.adversarial/docs/EVALUATION-WORKFLOW.md` for multi-evaluator
- [ ] Add evaluator selection guidance (when to use which)

### Nice to Have

- [ ] Support selective evaluator installation (e.g., just OpenAI evaluators)
- [ ] Add `./scripts/project list-evaluators` wrapper command
- [ ] Evaluator health check in `./scripts/verify-setup.sh`

## Implementation

### 1. Update pyproject.toml

```python
# Change from:
"adversarial-workflow>=0.6.2",

# To:
"adversarial-workflow>=0.7.0",  # Multi-evaluator support, configurable timeouts
```

### 2. Update .adversarial/config.yml.template

```yaml
# Adversarial Workflow Configuration
# ==================================
#
# Evaluators:
# - Built-in: evaluate, proofread, review (require OPENAI_API_KEY)
# - Custom: Add YAML files to .adversarial/evaluators/
# - Library: Run ./scripts/project install-evaluators
#
# Commands:
#   adversarial list-evaluators     # See available evaluators
#   adversarial evaluate <file>     # Run built-in plan evaluation
#   adversarial <name> <file>       # Run custom evaluator

# Directory containing task specifications
task_directory: delegation/tasks/

# Directory for evaluation logs
log_directory: .adversarial/logs/

# Directory for temporary artifacts
artifacts_directory: .adversarial/artifacts/

# Command to run tests (for test validation phase)
test_command: pytest tests/ -v

# Workflow Settings
auto_run: false
git_integration: true
save_artifacts: true

# Note: evaluator_model field is deprecated.
# To use different models, create custom evaluators in .adversarial/evaluators/
# See: .adversarial/evaluators/README.md
```

### 3. Create Evaluators Directory

```bash
mkdir -p .adversarial/evaluators
touch .adversarial/evaluators/.gitkeep
```

Add `.adversarial/evaluators/README.md`:

```markdown
# Custom Evaluators

Place evaluator YAML files here to add custom evaluation commands.

## Quick Start

1. Create a YAML file (e.g., `my-evaluator.yml`)
2. Define: name, model, api_key_env, prompt
3. Run: `adversarial my-evaluator <file>`

## Example

```yaml
name: my-evaluator
description: Custom document review
model: <provider>/<model-id>  # See aider docs for supported models
api_key_env: <PROVIDER>_API_KEY
timeout: 120
output_suffix: -my-evaluator.md
prompt: |
  Review this document for obvious issues...
```

**Common model formats**:
- OpenAI: `gpt-4o`, `gpt-4o-mini`
- Google: `gemini/gemini-2.0-flash`
- Mistral: `mistral/mistral-large-latest`
- Anthropic: `anthropic/claude-3-5-sonnet`

See [aider's LLM documentation](https://aider.chat/docs/llms.html) for full list.

## Evaluator Library

For pre-built evaluators (Gemini, Mistral, more OpenAI), run:

```bash
./scripts/project install-evaluators
```

See: https://github.com/movito/adversarial-evaluator-library

## API Keys

Each evaluator requires an API key. The environment variable name is specified in the evaluator's YAML file (`api_key_env` field).

Common provider conventions (per aider documentation):

| Provider | Environment Variable | Get Key |
|----------|---------------------|---------|
| OpenAI | `OPENAI_API_KEY` | https://platform.openai.com/api-keys |
| Google | `GOOGLE_API_KEY` | https://aistudio.google.com/apikey |
| Mistral | `MISTRAL_API_KEY` | https://console.mistral.ai/api-keys |
| Anthropic | `ANTHROPIC_API_KEY` | https://console.anthropic.com/settings/keys |

Example `.env`:
```bash
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=AIza...
# Only set keys for providers you use
```

**Note**: Check each evaluator's YAML for the exact `api_key_env` value. The evaluator library may use provider-specific conventions.
```

### 4. Add install-evaluators Command

In `scripts/project`, add:

```python
# Default version tag for reproducibility
EVALUATOR_LIBRARY_VERSION = "v0.2.2"
EVALUATOR_LIBRARY_REPO = "https://github.com/movito/adversarial-evaluator-library.git"

def cmd_install_evaluators(args):
    """Install evaluators from adversarial-evaluator-library."""
    import shutil
    import tempfile

    # Parse arguments
    force = "--force" in args
    version = EVALUATOR_LIBRARY_VERSION

    # Check for --ref flag (e.g., --ref v0.3.0 or --ref main)
    for i, arg in enumerate(args):
        if arg == "--ref" and i + 1 < len(args):
            version = args[i + 1]
            break

    # 1. Check for git (required for cloning)
    git_check = subprocess.run(
        ["git", "--version"],
        capture_output=True, text=True
    )
    if git_check.returncode != 0:
        print("❌ Git is required but not found")
        print()
        print("Install git:")
        print("  macOS:  brew install git")
        print("  Ubuntu: sudo apt install git")
        print("  Windows: https://git-scm.com/download/win")
        sys.exit(1)

    evaluators_dir = Path(".adversarial/evaluators")
    evaluators_dir.mkdir(parents=True, exist_ok=True)

    print("📦 Adversarial Evaluator Library Installer")
    print("=" * 50)
    print(f"   Version: {version}")
    print()

    # 2. Check if already installed
    version_file = evaluators_dir / ".installed-version"
    if version_file.exists() and not force:
        installed = version_file.read_text().strip()
        print(f"⚠️  Evaluators already installed (version: {installed})")
        print("   Use --force to reinstall")
        print("   Use --ref <version> to install a different version")
        return

    # 3. Clone specific version
    with tempfile.TemporaryDirectory() as tmpdir:
        print(f"📥 Cloning evaluator library @ {version}...")
        try:
            result = subprocess.run(
                ["git", "clone", "--depth", "1", "--branch", version,
                 EVALUATOR_LIBRARY_REPO, tmpdir],
                capture_output=True, text=True, timeout=60
            )
        except subprocess.TimeoutExpired:
            print("❌ Clone timed out (network issue?)")
            print("   Check your internet connection and try again")
            sys.exit(1)

        if result.returncode != 0:
            if "Could not resolve host" in result.stderr:
                print("❌ Network error - check your internet connection")
            elif "not found" in result.stderr.lower():
                print(f"❌ Version '{version}' not found")
                print("   Available versions: https://github.com/movito/adversarial-evaluator-library/tags")
            else:
                print(f"❌ Failed to clone: {result.stderr.strip()}")
            sys.exit(1)

        # Get actual commit hash for reproducibility
        hash_result = subprocess.run(
            ["git", "-C", tmpdir, "rev-parse", "HEAD"],
            capture_output=True, text=True
        )
        commit_hash = hash_result.stdout.strip()[:8] if hash_result.returncode == 0 else "unknown"

        # Copy evaluators
        src = Path(tmpdir) / "evaluators"
        if not src.exists():
            print("❌ No evaluators directory in library")
            sys.exit(1)

        installed_count = 0
        for provider_dir in src.iterdir():
            if provider_dir.is_dir() and provider_dir.name not in ("__pycache__", ".git"):
                dest = evaluators_dir / provider_dir.name
                if dest.exists():
                    shutil.rmtree(dest)
                shutil.copytree(provider_dir, dest)
                print(f"  ✅ {provider_dir.name}/")
                installed_count += 1

        # Write version file for tracking
        version_file.write_text(f"{version} ({commit_hash})\n")

    print()
    print("=" * 50)
    print(f"✅ Installed {installed_count} provider(s) from {version} ({commit_hash})")
    print()
    print("List evaluators:  adversarial list-evaluators")
    print()
    print("API keys needed (add to .env):")
    print("  OPENAI_API_KEY   - OpenAI evaluators")
    print("  GOOGLE_API_KEY   - Gemini evaluators")
    print("  MISTRAL_API_KEY  - Mistral evaluators")
```

**Security & Reproducibility Features:**
- Pins to specific version tag by default (`EVALUATOR_LIBRARY_VERSION`)
- Supports `--ref <tag|branch>` to override version
- Records installed version + commit hash in `.installed-version`
- Shows commit hash in output for auditability

### 5. Update Onboarding Agent

Add new phase to `.claude/agents/onboarding.md`:

```markdown
## Phase 7: Evaluator Setup (Optional)

The adversarial workflow reviews task specifications before implementation.

**Ask the user:**

"Would you like to install additional evaluators?"

**Options:**
1. **Built-in only** (default) - Requires OPENAI_API_KEY
2. **Install evaluator library** - Adds evaluators for Google, Mistral, and more
3. **Skip for now** - Can add later with `./scripts/project install-evaluators`

**If user chooses option 2:**

```bash
./scripts/project install-evaluators
```

**Then explain:**
- Run `adversarial list-evaluators` to see available evaluators
- Each evaluator has different cost/speed/depth tradeoffs
- Only set API keys for providers you want to use
- Custom evaluators can be created in `.adversarial/evaluators/`
```

### 6. Update Agent Prompts

In `.claude/agents/planner.md`, change:

```markdown
# From:
**Evaluator**: External GPT-4o via Aider (non-interactive, autonomous)
**Cost**: ~$0.04 per evaluation

# To:
**Evaluator**: External AI via adversarial-workflow (non-interactive, autonomous)
**Cost**: Varies by evaluator (see `adversarial list-evaluators`)
```

Update evaluation command examples:

```markdown
# Built-in evaluator:
adversarial evaluate delegation/tasks/2-todo/TASK-FILE.md

# Custom evaluator (if installed):
adversarial fast-check delegation/tasks/2-todo/TASK-FILE.md

# List available evaluators:
adversarial list-evaluators
```

### 7. Update Documentation

Update `README.md` adversarial section:

```markdown
### Adversarial Evaluation

Task specifications are reviewed by AI before implementation:

```bash
# Run evaluation
adversarial evaluate delegation/tasks/2-todo/my-task.md

# List available evaluators
adversarial list-evaluators

# Install additional evaluators (optional)
./scripts/project install-evaluators
```

Custom evaluators can be added to `.adversarial/evaluators/`. See [adversarial-evaluator-library](https://github.com/movito/adversarial-evaluator-library) for pre-built options.
```

## Acceptance Criteria

1. `adversarial-workflow>=0.7.0` in pyproject.toml
2. Config template deprecates `evaluator_model` field
3. `.adversarial/evaluators/` directory exists with README
4. `./scripts/project install-evaluators`:
   - Pins to specific version by default
   - Supports `--ref <tag>` for version override
   - Records installed version in `.installed-version`
   - Shows commit hash for auditability
5. Onboarding offers evaluator library installation
6. Agent prompts don't reference specific models (provider-agnostic)
7. `adversarial list-evaluators` shows installed evaluators

## Testing

### Automated Tests

Add to `tests/test_project_script.py`:

```python
class TestInstallEvaluatorsCommand:
    """Tests for install-evaluators command."""

    def test_git_not_found(self, tmp_path, monkeypatch):
        """Installer fails gracefully when git is not available."""
        # Mock subprocess.run to simulate git not found
        pass

    def test_already_installed_skips(self, tmp_path):
        """Running twice with same version skips re-install."""
        # Create .installed-version file, verify no clone attempt
        pass

    def test_force_reinstalls(self, tmp_path):
        """--force flag triggers reinstall even if version matches."""
        pass

    def test_ref_flag_overrides_version(self, tmp_path):
        """--ref <tag> uses specified version instead of default."""
        pass

    def test_version_file_written(self, tmp_path):
        """Successful install writes .installed-version with hash."""
        pass
```

**Note**: Full network tests (actual clone) are integration tests and run manually. Unit tests mock subprocess calls.

### Manual Testing

```bash
# Verify version
pip show adversarial-workflow | grep Version

# Verify evaluators directory
ls -la .adversarial/evaluators/

# Test install command
./scripts/project install-evaluators
adversarial list-evaluators

# Verify evaluator works (requires OPENAI_API_KEY)
adversarial fast-check delegation/tasks/2-todo/ASK-0029-multi-evaluator-architecture.md
```

### Edge Cases

| Scenario | Expected Behavior |
|----------|------------------|
| Install without git | Exit with error, show install instructions |
| Install with existing evaluators | Warn and skip (use `--force` to override) |
| Clone timeout (>60s) | Exit with error, suggest network check |
| Invalid --ref tag | Exit with error, show tags URL |
| Config with old `evaluator_model` field | Continue working (field is ignored) |

**Note**: "Run evaluator without API key" error handling is in adversarial-workflow, not this installer. The installer only handles installation.

## References

| Claim | Source |
|-------|--------|
| v0.6.0 custom evaluator support | [adversarial-workflow v0.6.0 release](https://github.com/movito/adversarial-workflow/releases/tag/v0.6.0) |
| v0.6.3 configurable timeout | [adversarial-workflow v0.6.3 release](https://github.com/movito/adversarial-workflow/releases/tag/v0.6.3) |
| v0.6.4 list-evaluators command | [adversarial-workflow v0.6.4 release](https://github.com/movito/adversarial-workflow/releases/tag/v0.6.4) |
| v0.7.0 current stable (as of 2026-02-01) | [adversarial-workflow releases](https://github.com/movito/adversarial-workflow/releases) |
| Supported LLM providers | [aider LLM documentation](https://aider.chat/docs/llms.html) |
| Evaluator library v0.2.2 | [adversarial-evaluator-library v0.2.2](https://github.com/movito/adversarial-evaluator-library/releases/tag/v0.2.2) |

## Related

- **adversarial-workflow**: https://github.com/movito/adversarial-workflow
- **adversarial-evaluator-library**: https://github.com/movito/adversarial-evaluator-library
- **KIT-ADR-0004**: Adversarial Workflow Integration

## Backward Compatibility

**Config Migration**: Not required. The old `evaluator_model` field is still recognized by adversarial-workflow 0.7.0 but is no longer needed. Custom evaluators in `.adversarial/evaluators/` take precedence.

**Existing Projects**: Will continue to work without changes. The new architecture is additive - it enables new capabilities without breaking existing workflows.

**Built-in Evaluators**: The built-in evaluators (`evaluate`, `proofread`, `review`) continue to work as before. They require `OPENAI_API_KEY` (this is a constraint of the built-in evaluators, not of the starter kit).

**Performance**: Evaluators run one at a time (not concurrently). Having multiple evaluator YAML files installed has no performance impact - only the invoked evaluator is loaded and executed.

## Notes

**Backward Compatibility**:
- Built-in evaluators (`evaluate`, `proofread`, `review`) continue to work unchanged
- Library installation is optional and can be done anytime
- Existing config files with `evaluator_model` field still work

**Installer Behavior**:
- Error handling includes: git availability check, network timeout (60s), clone failure
- Idempotent: running twice with same version skips re-install (use `--force` to override)
- Reproducible: version + commit hash recorded in `.installed-version`

**Git Dependency**:
- Git is required for installation (evaluator library is hosted on GitHub)
- Enterprise environments without git access can manually copy evaluator YAMLs
- Alternative: future enhancement could support `--from-zip <path>` for air-gapped installs

**Config File Flow**:
- Onboarding copies `.adversarial/config.yml.template` to `.adversarial/config.yml`
- Users edit the config file, not the template
- Template serves as reference and source for new projects
