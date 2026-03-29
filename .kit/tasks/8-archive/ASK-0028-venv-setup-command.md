# ASK-0028: Add Project Setup Command for Virtual Environment

**Status**: Done
**Priority**: High
**Assigned To**: feature-developer
**Estimated Effort**: 2-3 hours
**Created**: 2025-02-01
**Source**: User report - agents failing with "externally-managed-environment" error

## Problem Statement

New projects cloned from the starter kit lack a virtual environment. When agents try to install dependencies, they encounter:

```
error: externally-managed-environment

× This environment is externally managed
╰─> To install Python packages system-wide, try brew install xyz...
```

This happens because:
1. macOS Homebrew Python is "externally managed" and blocks system-wide pip installs
2. No venv is created during project setup
3. Agents don't know to create venv before pip operations
4. `gql` and other dependencies aren't available even though they're in `pyproject.toml`

## Requirements

### Must Have

- [ ] Add `./scripts/project setup` command that:
  - Verifies Python 3.9+ is available
  - Creates `.venv/` if not exists
  - Installs `pip install -e ".[dev]"` in the venv
  - Runs `pre-commit install` (if available)
  - Prints activation instructions
- [ ] Update `scripts/project --help` to include setup command
- [ ] Handle case where venv already exists (skip or recreate with `--force`)
- [ ] Error handling with clear messages and remediation steps for:
  - Python version too old
  - Venv creation failure
  - Dependency installation failure
  - Corrupted venv detection

### Should Have

- [ ] Update onboarding agent to call `./scripts/project setup` during initial setup
- [ ] Add venv check to OPERATIONAL-RULES.md for all agents
- [ ] Update README Quick Start to mention setup command

### Nice to Have

- [ ] Add `--force` flag to recreate venv
- [ ] Add `--no-dev` flag to skip dev dependencies
- [ ] Detect and use `uv` if available for faster installs

## Implementation

### 1. Add setup command to `scripts/project`

Add new command handler with proper error handling:

```python
def cmd_setup(args):
    """Set up virtual environment and install dependencies."""
    project_dir = Path(__file__).resolve().parent.parent
    venv_dir = project_dir / ".venv"
    force = "--force" in args

    # 1. Verify Python version (3.9+ required)
    version = sys.version_info
    if version < (3, 9):
        print(f"❌ Python 3.9+ required, found {version.major}.{version.minor}")
        print("   Install Python 3.9+ and try again")
        sys.exit(1)
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")

    # 2. Handle existing venv
    if venv_dir.exists():
        if force:
            print(f"🗑️  Removing existing venv: {venv_dir}")
            import shutil
            try:
                shutil.rmtree(venv_dir)
            except Exception as e:
                print(f"❌ Failed to remove venv: {e}")
                print("   Try: rm -rf .venv")
                sys.exit(1)
        else:
            # Verify venv is valid (has python executable)
            venv_python = venv_dir / "bin" / "python"
            if not venv_python.exists():
                print(f"⚠️  Corrupted venv detected (missing python)")
                print("   Run with --force to recreate: ./scripts/project setup --force")
                sys.exit(1)
            print(f"✅ Virtual environment exists: {venv_dir}")

    # 3. Create venv if needed
    if not venv_dir.exists():
        print("📦 Creating virtual environment...")
        try:
            result = subprocess.run(
                [sys.executable, "-m", "venv", str(venv_dir)],
                capture_output=True, text=True
            )
            if result.returncode != 0:
                print(f"❌ Failed to create venv: {result.stderr}")
                sys.exit(1)
            print(f"✅ Created: {venv_dir}")
        except Exception as e:
            print(f"❌ Failed to create venv: {e}")
            sys.exit(1)

    # 4. Install dependencies
    pip = venv_dir / "bin" / "pip"
    print("\n📦 Installing dependencies...")
    try:
        result = subprocess.run(
            [str(pip), "install", "-e", ".[dev]"],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            print(f"❌ Failed to install dependencies:")
            print(result.stderr[-500:] if len(result.stderr) > 500 else result.stderr)
            print("\nTry manually: source .venv/bin/activate && pip install -e '.[dev]'")
            sys.exit(1)
        print("✅ Dependencies installed")
    except Exception as e:
        print(f"❌ Failed to install dependencies: {e}")
        sys.exit(1)

    # 5. Install pre-commit hooks (optional - skip if pre-commit not installed)
    pre_commit = venv_dir / "bin" / "pre-commit"
    if pre_commit.exists():
        print("\n🔧 Installing pre-commit hooks...")
        try:
            result = subprocess.run(
                [str(pre_commit), "install"],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                print("✅ Pre-commit hooks installed")
            else:
                print(f"⚠️  Pre-commit install failed (non-critical): {result.stderr}")
        except Exception as e:
            print(f"⚠️  Pre-commit install failed (non-critical): {e}")
    else:
        print("\n⚠️  pre-commit not found in venv (install manually if needed)")

    # 6. Print success and activation instructions
    print("\n" + "=" * 60)
    print("✅ Setup complete!")
    print("\nTo activate the virtual environment:")
    print(f"  source {venv_dir}/bin/activate")
    print("\nTo verify setup:")
    print("  ./scripts/verify-setup.sh")
```

**Error Handling Strategy**:
- Python version check upfront (fail fast)
- Corrupted venv detection (missing python binary)
- `--force` flag to recreate venv cleanly
- Subprocess errors captured and reported
- Pre-commit failure is non-critical (warning only)
- Clear remediation instructions on each failure

### 2. Update onboarding agent

In `.claude/agents/onboarding.md`, add setup step after project configuration:

```markdown
## Step 5: Set Up Development Environment

Run the setup command to create venv and install dependencies:

\`\`\`bash
./scripts/project setup
\`\`\`

This creates a virtual environment with all dependencies.
```

### 3. Update OPERATIONAL-RULES.md

Add venv awareness section:

```markdown
## Virtual Environment Handling

Before running pip commands:
1. Check if venv exists: `ls .venv/bin/activate 2>/dev/null`
2. If not, suggest: `./scripts/project setup`
3. Always use venv pip: `.venv/bin/pip install ...`

Never run `pip install` with system Python on macOS.
```

### 4. Update README Quick Start

Add step after cloning:

```markdown
### 2. Set Up Development Environment

\`\`\`bash
cd your-project-name
./scripts/project setup
source .venv/bin/activate
\`\`\`
```

## Acceptance Criteria

1. `./scripts/project setup` creates venv and installs deps successfully
2. Running setup twice doesn't break anything (idempotent)
3. Onboarding agent runs setup as part of initial flow
4. Agents know to check for venv before pip operations
5. README documents the setup step clearly

## Testing

### Manual Testing

```bash
# Clean slate
rm -rf .venv venv

# Run setup
./scripts/project setup

# Verify
source .venv/bin/activate
python -c "import gql; print('gql available')"
pytest --version
pre-commit --version
```

### Edge Cases

- [ ] Setup with existing valid venv (should update deps, not recreate)
- [ ] Setup with `--force` flag (should remove and recreate venv)
- [ ] Setup with corrupted venv (detect missing python, suggest --force)
- [ ] Setup without write permissions (clear error from subprocess)
- [ ] Setup with Python < 3.9 (should fail with version requirement message)
- [ ] Dependency conflict during pip install (show truncated error, suggest manual fix)

## Related

- **KIT-ADR-0005**: Test Infrastructure Strategy (documents venv expectations)
- **ASK-0004**: Scripts Directory (established scripts/project pattern)
- Previous issue: gql import breaking test collection (fixed in separate commit)

## Notes

This addresses the root cause of the "gql not installed" issue. While ASK-0028-predecessor fixed the symptom (graceful test skipping), this task fixes the cause (missing venv setup).
