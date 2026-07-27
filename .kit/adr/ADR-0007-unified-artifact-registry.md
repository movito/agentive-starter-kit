# ADR-0007: Unified Artifact Registry for Agents, Evaluators, and Skills

**Status**: Proposed

**Date**: 2026-04-01

**Deciders**: project maintainers, adversarial-workflow team, agentive-starter-kit team

**Implementation home**: agentive-starter-kit. This ADR lives in adversarial-evaluator-library where the design analysis and adversarial review were conducted. The registry tooling (`kit registry` commands) will be implemented in agentive-starter-kit, which owns the `.kit/` directory convention and the `kit` CLI namespace.

## Glossary
- **Artifact**: A reusable component or asset within the agentive ecosystem, such as agent definitions, evaluator configs, and skills.
- **Registry**: The metadata index and tooling that tracks artifact identity, version, provenance, and distribution state across projects. Not a hosted service — implemented as YAML files in git repos.
- **Sync Protocol**: The process by which artifacts are compared against upstream sources and updated locally, governed by the project's manifest policy.
- **Metadata Envelope**: The `registry:` block embedded in each artifact's native header format (YAML frontmatter for Markdown, top-level keys for YAML). Contains all tracking fields.
- **Upstream**: The canonical source repository for an artifact (e.g., agentive-starter-kit for agents).
- **Downstream**: A project that consumes artifacts from an upstream source.
- **Propose-back**: The act of submitting a locally improved artifact back to its upstream source via a pull request.

## Context

### Problem Statement

The agentive ecosystem distributes three types of artifacts across projects: agent definitions, evaluator configs, and skills. Each has evolved its own ad-hoc distribution mechanism, none of which scales:

| Artifact | Format | Distribution | Tracking | Update path |
|----------|--------|-------------|----------|-------------|
| Agents (`.claude/agents/`) | Markdown + YAML frontmatter | Manual copy-paste | Partial (newer agents have `version`, `origin`) | None — copy-paste again |
| Evaluators (`.adversarial/evaluators/`) | YAML | `adversarial library install` + manual | `_meta` provenance block | Manual re-install |
| Skills (`.claude/skills/`) | Markdown | Manual copy-paste | None | None |

At 4 projects this is tolerable. At 40 or 400, it breaks:

- **11 "universal" agent definitions** are copy-pasted identically across 4 projects with no version tracking. When `planner.md` improves in one project, the others never know.
- **Evaluator installation** copies YAML files with a `_meta` block, but no mechanism alerts projects to available updates. Projects fossilize on whatever they installed day one.
- **Skills** have no distribution mechanism at all.
- **Upstream contribution** is entirely informal. When a downstream project improves an agent or evaluator, there's no path to propose it back.

### Forces at Play

**Technical Requirements:**
- Artifacts must be self-describing — all tracking metadata lives inside the artifact, not in a separate database
- Distribution must be git-based with no hosted service beyond git hosting itself
- Projects must be able to override, extend, or exclude any artifact without breaking sync
- The system must handle artifacts that evolve across projects independently (forking)

**Offline/online split:**

| Operation | Network required? | Why |
|-----------|------------------|-----|
| `kit registry status` | No | Compares local files against cached index |
| `kit registry diff` | No | Diffs local against cached upstream copy |
| `kit registry sync` | Yes | Fetches from git remote |
| `kit registry install` | Yes | Fetches from git remote |
| `kit registry propose` | Yes | Opens PR via `gh` CLI |
| Content hash verification | No | Computed locally |

After initial sync, all read operations work offline. Only fetch and contribute operations require network access.

**Constraints** (as of Claude Code v1.x, adversarial-evaluator-library v0.5.x):
- Claude Code resolves agents from `.claude/agents/` — this path is not configurable (verified: no env var or config flag exists as of March 2026)
- The `adversarial` CLI resolves evaluators from `.adversarial/evaluators/` — hardcoded in `adversarial_workflow/evaluators/discovery.py`
- Skills live in `.claude/skills/` — also hardcoded in Claude Code
- These path constraints mean the registry is a source/sync layer, not a runtime resolution layer
- Must remain backwards-compatible with existing artifacts that lack metadata
- If runtime paths become configurable in future tooling versions, the registry can adapt — artifact identity is name-based, not path-based

**Assumptions:**
- Git is the transport layer (all projects are git repos)
- The agentive-starter-kit remains the canonical upstream for shared artifacts (multi-source is supported; this is the default, not a hard constraint)
- Projects will always need local-only artifacts that are never shared
- Model identifiers in all artifact types require periodic updates as providers release new models (this is a maintenance cost the registry can track but not eliminate)

## Non-Goals / Scope Boundary

This registry is a **provenance tracker and sync tool for independent text files**. It is not a package manager. The following are explicitly out of scope, permanently:

| Non-goal | Why | If you need this, use |
|----------|-----|----------------------|
| Dependency resolution | Artifacts are independent. An agent does not "depend on" another agent. | A real package manager (npm, pip) |
| Transitive version constraints | No artifact pulls in other artifacts as prerequisites. | Dependency graphs (e.g., Cargo, Go modules) |
| Build steps or compilation | Artifacts are source files consumed as-is. No transform pipeline. | A build system (Make, Turbopack, Bazel) |
| Hosted registry infrastructure | Git repos are the registries. No hosted index service (PyPI, npm registry). | A package registry |
| Cryptographic signing / key management | Disproportionate for text-file artifacts in a trusted-source model. See Trust Model. | sigstore, cosign, GPG |
| Constraint solving (`>=1.2 <2.0`) | Versions are informational. Projects pin exact versions or float to latest. No range resolution. | A SAT solver (pip, Cargo) |
| Plugin/extension system | Artifacts don't load other artifacts at runtime. | A plugin framework |

**The litmus test**: If this system ever needs dependency resolution, transitive version constraints, or a build step, it has outgrown its design — stop and adopt a real package manager instead. The registry's value is its simplicity: metadata in the file, git as transport, PRs as contribution. Adding package-manager complexity would make it strictly worse than existing package managers at their own job.

The closest analogies are **dotfiles managers** (chezmoi, stow) and **Homebrew taps** — small registries for small collections of config files with known sources.

## Decision

We adopt a **Unified Artifact Registry** — a single metadata envelope, distribution protocol, and contribution mechanism for agents, evaluators, and skills.

### Core Principles

1. **The artifact is the record**: All tracking metadata lives inside the artifact file itself, in its existing frontmatter/header format. No external database, no sidecar files.
2. **Declare intent, resolve at sync time**: Projects declare what they want (by tier, by name, by version). Sync resolves declarations to concrete files. Runtime reads files as-is.
3. **Three-layer cascade**: `local > pinned > upstream`. Local always wins. Pinned holds a specific version. Upstream floats to latest.
4. **Contribution is a first-class operation**: Proposing an artifact back upstream is as simple as `kit propose <artifact>`.
5. **Scan-then-execute atomicity**: Sync validates all artifacts before writing any. If validation fails (conflict, hash mismatch, missing source), no files are modified. Inspired by GNU Stow 2.0's two-phase algorithm.
6. **Idempotent apply**: Running `kit registry sync` twice produces identical results. No side effects on repeated runs. Inspired by Dotbot and chezmoi.
7. **No templating**: Artifacts are distributed as-is, not rendered per-project. Local customization is a full file replacement (tier: `local`), not conditional template expansion. This is an explicit non-goal — unlike chezmoi, we never transform artifact content during sync.

---

### Component 1: The Metadata Envelope

Every distributable artifact carries a metadata block in its native header format. The envelope is the same structure regardless of artifact type.

**For agents** (YAML frontmatter in Markdown):

```yaml
---
# === Claude Code fields (required by runtime) ===
name: feature-developer-v5
description: Feature implementation specialist — gated workflow
model: claude-opus-4-6
tools: [Bash, Read, Edit, Write, Glob, Grep]

# === Registry fields (required for distribution) ===
registry:
  type: agent                    # agent | evaluator | skill
  version: 1.2.0                # semver — the artifact's own version
  tier: core                    # core | optional | local
  source: agentive-starter-kit  # canonical upstream repo (omit for local)
  upstream_version: 1.1.0       # version in source repo (tracks drift)
  last_synced: 2026-03-29       # ISO date of last sync from upstream

  # Lineage (how this artifact evolved)
  origin: feature-developer-v3  # what it was derived from
  created_by: "@movito"         # who created or last substantially changed it

  # Content hash (enables drift detection without diffing)
  content_hash: sha256:a1b2c3   # hash of everything below the frontmatter

  # Tags (for filtering and discovery)
  tags: [implementation, tdd, gated-workflow]

  # Compatibility
  min_kit_version: 0.5.0        # minimum .kit/ version required
  replaces: feature-developer-v3 # if this supersedes another artifact
---
```

**For evaluators** (YAML, replacing the current `_meta` block):

```yaml
# evaluator.yml
name: claude-quick
registry:
  type: evaluator
  version: 1.5.0
  tier: core
  source: adversarial-evaluator-library
  upstream_version: 1.5.0
  last_synced: 2026-03-08
  content_hash: sha256:d4e5f6
  tags: [quick-check, anthropic, fast]

model_requirement:
  family: claude
  tier: haiku
  min_version: "4.5"
prompt: |
  ...
```

**For skills** (YAML frontmatter in Markdown):

```yaml
---
name: self-review
registry:
  type: skill
  version: 1.0.0
  tier: core
  source: agentive-starter-kit
  upstream_version: 1.0.0
  last_synced: 2026-03-29
  content_hash: sha256:g7h8i9
  tags: [code-quality, review, gate]
---
```

**Design rationale for embedding metadata in the artifact:**

- No sidecar files that can drift out of sync with the artifact they describe
- `git blame` on the artifact shows when metadata and content changed together
- Copy-pasting an artifact to a new project carries its provenance automatically
- Tools that don't understand registry fields ignore them — verified for Claude Code's YAML frontmatter parser (unknown keys are silently skipped) and the `adversarial` evaluator loader (reads only known keys from YAML). See **Backwards Compatibility** section below for the verification matrix.
- `content_hash` enables constant-time drift comparison: hash the body (linear in artifact size, typically < 10 KB), compare to stored hash. If they differ, the artifact has been locally modified since last sync. No need to fetch or diff against upstream.

**Tier semantics:**

| Tier | Meaning | Sync behavior |
|------|---------|--------------|
| `core` | Every project should have this | Synced by default. Project can exclude explicitly. |
| `optional` | Available on request | Only synced if project opts in. |
| `local` | Project-specific | Never synced. No `source` field. No `upstream_version`. |

**Versioning policy for non-code artifacts:**

Semver applies to artifact behavior, not code:

| Change type | Version bump | Examples |
|------------|-------------|----------|
| Patch | Typo fix, metadata update, whitespace, comment clarification | Fix spelling in prompt, update `last_synced` |
| Minor | Behavior change that is compatible with existing usage | Add a new optional section to an agent, expand an evaluator's rubric |
| Major | Breaking change to invocation, required tools, or expected inputs/outputs | Rename required tool, change output format, remove a gate phase |

**Content hash specification:**

The `content_hash` field uses SHA-256 over a normalized representation of the artifact body:

1. **For Markdown artifacts** (agents, skills): hash everything after the closing `---` of YAML frontmatter, excluding the `---` delimiter itself
2. **For YAML artifacts** (evaluators): hash the entire file after removing the `registry:` block and any `_meta:` block (i.e., hash the functional content only)
3. **Normalization**: before hashing, convert line endings to LF (`\n`), strip trailing whitespace from each line, ensure file ends with a single `\n`, encode as UTF-8
4. **Format**: `sha256:<hex-digest>` (lowercase, full 64-character digest)

This normalization ensures consistent hashes across platforms (Windows CRLF, macOS/Linux LF) and editors that handle trailing whitespace differently.

**Identity and conflict resolution:**

Artifact identity is the tuple `(type, name)`. Rules:

1. **Uniqueness**: Within a single project, no two artifacts may share the same `(type, name)`. If two sources define `(agent, planner)`, sync fails with an explicit error naming both sources.
2. **Source precedence**: When a manifest lists multiple sources, artifacts are resolved in source declaration order. The first source providing an artifact wins. Projects can override by pinning or excluding.
3. **Name stability**: An artifact's `name` is its permanent identity. Renaming creates a new artifact; use `replaces` to declare succession.
4. **Deletion/deprecation**: To remove an artifact from distribution, set its tier to `deprecated` in the upstream index. Downstream projects receive a notice on `kit registry status` but are not forced to delete.

**Trust and integrity model:**

This registry operates within a trusted-source model:

- **Source authentication**: Sources are git repositories accessed via the user's existing git credentials (SSH keys or HTTPS tokens). No additional authentication layer.
- **Integrity via content hash**: After fetching an artifact from a pinned SHA, the sync tool verifies that the computed content hash matches the hash in the upstream index. Mismatch aborts the install with an error.
- **No cryptographic signing** (intentional): Signing adds significant operational overhead (key management, rotation, revocation) that is disproportionate for text-file artifacts in a small-to-medium ecosystem. The trust boundary is "can you push to the source repo?" — the same trust model as the code itself.
- **Supply-chain mitigation**: Sources must be explicitly declared in `manifest.yml`. There is no auto-discovery of registries. The lockfile pins exact commit SHAs, preventing tag mutation attacks.
- **Future option**: If the ecosystem grows to untrusted third-party sources, signed tags (`git verify-tag`) can be added as an optional verification layer without changing the envelope format.

**Backwards compatibility verification:**

| Tool | Version | Extra YAML frontmatter keys | Extra YAML top-level keys | Status |
|------|---------|---------------------------|--------------------------|--------|
| Claude Code agent loader | v1.x | Ignored (verified) | N/A | Safe |
| `adversarial` evaluator loader | v0.5.x | N/A | Ignored — reads only known keys | Safe |
| Claude Code skill loader | v1.x | Ignored (verified) | N/A | Safe |
| `aider` (used by evaluator pipeline) | v0.86.x | Ignored | N/A | Safe |

**Rollback strategy**: If an unknown-key-intolerant parser is discovered, the `registry:` block can be moved to a sidecar `<name>.registry.yml` file without changing the sync protocol. The envelope format is designed to be relocatable.

**Automation requirements for metadata fields:**

The following fields are **tool-managed** — humans should not edit them directly:

| Field | Updated by | When |
|-------|-----------|------|
| `content_hash` | `kit registry sync`, `kit registry install` | On every sync or install |
| `last_synced` | `kit registry sync` | On every sync from upstream |
| `upstream_version` | `kit registry sync` | When upstream version changes |
| `proposed.status` | `kit registry propose`, upstream merge hooks | On propose, accept, reject |

Human-editable fields: `version` (bumped by the author), `tier`, `tags`, `origin`, `created_by`, `min_kit_version`, `replaces`.

---

### Component 2: Distribution and Update Protocol

**The registry index** lives in the source repository (agentive-starter-kit for agents/skills, adversarial-evaluator-library for evaluators):

```yaml
# .kit/registry/index.yml
schema_version: "1.0"
updated: 2026-04-01

artifacts:
  - name: feature-developer-v5
    type: agent
    version: 1.2.0
    tier: core
    path: .claude/agents/feature-developer-v5.md
    content_hash: sha256:a1b2c3
    tags: [implementation, tdd, gated-workflow]
    replaces: feature-developer-v3

  - name: claude-quick
    type: evaluator
    version: 1.5.0
    tier: core
    path: evaluators/anthropic/claude-quick/evaluator.yml
    content_hash: sha256:d4e5f6
    tags: [quick-check, anthropic, fast]

  - name: self-review
    type: skill
    version: 1.0.0
    tier: core
    path: .kit/skills/self-review/SKILL.md
    content_hash: sha256:g7h8i9
    tags: [code-quality, review, gate]
```

**Project manifest** declares what the project wants:

```yaml
# .kit/registry/manifest.yml
schema_version: "1.0"
sources:
  - repo: movito/agentive-starter-kit
    ref: main                       # branch or tag
    types: [agent, skill]           # what to pull from this source

  - repo: movito/adversarial-evaluator-library
    ref: v1.5.0                     # pin to a release tag
    types: [evaluator]

policy:
  agents:
    use: [core]                     # install all core-tier agents
    pin:
      feature-developer-v5: 1.2.0  # hold this version even if upstream advances
    exclude: [bootstrap]            # don't install this one

  evaluators:
    use: [core]
    pin:
      o3-chain: 1.5.0
    exclude: [cognitive-diversity]

  skills:
    use: [core]
```

**Sync operations:**

```bash
# Check what's available vs what's installed
kit registry status

# Output:
# AGENTS (source: movito/agentive-starter-kit@main)
#   feature-developer-v5  1.2.0  ✓ current
#   planner               1.0.0  ⬆ 1.1.0 available
#   test-runner            1.0.0  ~ locally modified (content_hash mismatch)
#   bot-watcher            0.3.0  · local-only (no upstream)
#
# EVALUATORS (source: movito/adversarial-evaluator-library@v1.5.0)
#   claude-quick           1.5.0  ✓ current
#   o3-chain               1.5.0  📌 pinned
#   gemini-flash           1.4.0  ⬆ 1.5.0 available

# Pull updates for everything that isn't pinned or locally modified
kit registry sync

# Pull updates and overwrite local modifications (with confirmation)
kit registry sync --force

# Pull a specific artifact
kit registry install feature-developer-v5

# Show what changed between local and upstream
kit registry diff planner
```

**Update notification** (passive, non-intrusive):

When any `kit` command runs (or on session start via a hook), it can compare local `content_hash` + `version` against upstream `index.yml`. If updates exist, emit a one-line notice:

```
kit: 3 artifact updates available (2 agents, 1 evaluator). Run `kit registry status` to see details.
```

This is advisory only. No automatic updates. No blocking prompts. Projects pull when ready.

**Lockfile** (optional, for reproducibility):

```yaml
# .kit/registry/lock.yml (generated by kit registry sync)
synced_at: 2026-04-01T14:30:00Z
artifacts:
  - name: feature-developer-v5
    type: agent
    version: 1.2.0
    source: movito/agentive-starter-kit@d72598c
    content_hash: sha256:a1b2c3
    installed_to: .claude/agents/feature-developer-v5.md
  - name: claude-quick
    type: evaluator
    version: 1.5.0
    source: movito/adversarial-evaluator-library@3f0bda1
    content_hash: sha256:d4e5f6
    installed_to: .adversarial/evaluators/claude-quick.yml
```

The lockfile pins exact commit SHAs, enabling reproducible installs across machines and CI. Content hash verification after fetch ensures the installed artifact matches expectations regardless of platform-specific git settings (e.g., `core.autocrlf`), because the hash is computed after LF normalization (see Content Hash Specification above).

---

### Component 3: Upstream Contribution (Propose-Back)

When a downstream project improves an artifact — better prompts, new tool patterns, bug fixes — there should be a low-friction path to propose it back upstream.

**The propose operation:**

```bash
# Propose a locally modified artifact back to its upstream source
kit registry propose planner

# What happens:
# 1. Reads planner.md's registry.source → movito/agentive-starter-kit
# 2. Detects content_hash mismatch (local differs from upstream_version)
# 3. Generates a diff between upstream_version and local
# 4. Opens a PR on the source repo with:
#    - Title: "propose: planner 1.0.0 → 1.1.0 (from <downstream-repo>)"
#    - Body: diff + changelog + downstream context
#    - Branch: propose/<downstream-repo>/planner
```

**Propose metadata** (added to the artifact when proposed):

```yaml
registry:
  # ... existing fields ...
  proposed:
    to: movito/agentive-starter-kit
    pr: "#47"
    date: 2026-04-01
    status: pending              # pending | accepted | rejected | withdrawn
```

**Contribution lifecycle:**

```
downstream modifies artifact
       ↓
kit registry propose <name>
       ↓
PR opened on upstream repo
       ↓
upstream reviews, may request changes
       ↓
accepted → upstream bumps version → next sync propagates to all projects
rejected → downstream keeps local version, propose.status = rejected
```

**Design rationale:**

- Uses git + PRs as the review mechanism — no new infrastructure
- The PR carries full context: what changed, why, where it was battle-tested
- Upstream maintainer has final say — the downstream project is proposing, not pushing
- If rejected, the downstream project keeps working fine with its local version
- If accepted, all other downstream projects benefit on their next sync

**Handling divergence:**

When an artifact has been modified locally AND upstream has a newer version, `kit registry status` reports it as a conflict:

```
planner  1.0.0  ⚡ conflict: locally modified + upstream 1.1.0 available
```

Resolution options:
- `kit registry diff planner` — see both changes
- `kit registry sync planner --theirs` — take upstream, discard local
- `kit registry sync planner --ours` — keep local, update `upstream_version` to acknowledge the upstream change
- `kit registry propose planner` — propose local changes to upstream first, then sync

**Governance and contribution controls:**

- **Who can propose**: Any downstream project with push access to its own repo. Propose opens a PR — it does not push to upstream.
- **Who can accept**: Upstream repo maintainers (standard GitHub permissions apply).
- **Rate limiting**: No technical rate limit. Social norm: one propose PR per artifact per downstream project at a time. Duplicate proposals from the same project for the same artifact are rejected by the tool.
- **Proposal template**: `kit registry propose` generates a structured PR body with: artifact name, version diff, changelog, test results, and downstream project context. Upstream maintainers can require additional checklist items via `.github/PULL_REQUEST_TEMPLATE/propose.md`.

---

### Migration Path

**Phase 1: Metadata adoption** (non-breaking)
- Add `registry:` block to all shared agents, evaluators, and skills in agentive-starter-kit and adversarial-evaluator-library
- Existing tooling ignores unknown YAML frontmatter fields — zero breakage
- Build `index.yml` from existing artifacts

**Phase 2: CLI tooling** (`kit registry` commands)
- Implement `status`, `sync`, `install`, `diff` in a new `kit` CLI (or extend `adversarial` CLI)
- Projects that don't adopt the CLI continue working as before — files are files

**Phase 3: Propose-back**
- Implement `propose` command
- Requires `gh` CLI for PR creation (already a dependency in all 4 current projects; checked March 2026)
- Fallback for environments without `gh`: `kit registry propose --patch` generates a `.patch` file that can be submitted manually

**Phase 4: Deprecate old mechanisms**
- `adversarial library install` → `kit registry install` (with compatibility shim)
- Manual copy-paste → `kit registry sync` (agents finally managed)
- `.core-manifest.json` sync tiers → `manifest.yml` policy (superset)

## Consequences

### Positive

- **Agents get distribution**: The 11 universal agents that are currently copy-pasted gain version tracking, drift detection, and update notification
- **Single mental model**: One envelope, one sync command, one contribution path for all artifact types
- **Drift detection**: `content_hash` tells you instantly whether a local artifact has been modified, without diffing against upstream
- **Organic improvement**: Downstream innovations have a path back upstream, benefiting the entire ecosystem
- **No new infrastructure**: Git repos as registries, PRs as proposals, YAML frontmatter as metadata

### Negative

- **Migration effort**: ~30 agents + ~22 evaluators + ~5 skills need `registry:` metadata added across 4+ projects
- **Frontmatter growth**: Agent definitions gain ~10 lines of metadata. Acceptable for files that are already 50-200 lines.
- **Two sync systems temporarily**: During migration, both `.core-manifest.json` and `manifest.yml` coexist

### Neutral

- **No runtime impact**: The registry is a sync-time concept. Runtime reads files from their hardcoded paths as always.
- **Backwards compatible**: Artifacts without `registry:` blocks continue to work. They're just invisible to the registry.

## Alternatives Considered

### Alternative 1: Extend `.core-manifest.json` to cover agents

**Description**: Add `agents_core` and `skills_core` tiers to the existing manifest system.

**Rejected because**:
- The manifest tracks file paths, not artifact identity. If an agent is renamed or restructured, the manifest breaks.
- No version tracking, no drift detection, no contribution path.
- Solves distribution but not the other two atomic components (metadata, contribution).

### Alternative 2: Git submodules for shared artifacts

**Description**: Mount agentive-starter-kit as a submodule and symlink agents/evaluators/skills.

**Rejected because**:
- Submodules are fragile — developers forget to init/update them
- Symlinks break on Windows and in some CI environments
- No mechanism for local overrides or project-specific artifacts
- No contribution path — submodules are read-only

### Alternative 3: NPM/PyPI package for artifact distribution

**Description**: Publish artifacts as a package, install via package manager.

**Rejected because**:
- Agents and skills are Markdown files, not code libraries. Package managers add ceremony (build, publish, semver lockstep) without benefit.
- Package updates are all-or-nothing — can't pin one artifact while floating another
- No natural contribution path back to upstream
- Adds a hosted registry dependency (PyPI/npm) to what is currently a pure-git workflow

## Related Decisions

- ADR-0004: Evaluator Definition and Model Routing Separation (established WHAT/HOW layering for evaluators — this ADR extends the principle to all artifacts)
- ADR-0005: Library-Workflow Interface Contract (formalized the evaluator registry schema — `providers/registry.yml` continues as the model resolution layer, orthogonal to the artifact registry)
- KIT-ADR-0023: Builder-Project Separation (established `.kit/` as the builder layer — the artifact registry lives here)

## References

- agentive-starter-kit issue #35: "Separate kit internals from downstream-exportable content"
- agentive-starter-kit issue #43: "ASK-0034 left stale SETUP.md in downstream repos" (example of the stale-artifact problem this ADR solves)
- `.core-manifest.json` v2.0.0 format (the sync mechanism this ADR supersedes)
- `adversarial-workflow` evaluator discovery code (`adversarial_workflow/evaluators/discovery.py`)

### Prior Art

This design draws from dotfile managers and lightweight registries. The table below maps which patterns were adopted and which were explicitly rejected:

| Tool | What we adopted | What we rejected | Why |
|------|----------------|-----------------|-----|
| **chezmoi** | SHA-256 content hashing for drift detection; three-state model (source/target/actual) | Templating engine; filename-encoded metadata; single-source-of-truth constraint | We need multi-source; no per-project templating; metadata belongs in frontmatter, not filenames |
| **GNU Stow 2.0** | Two-phase scan-then-execute atomicity | Symlink-based installation; stateless model | Runtime tools require real files; we need drift detection |
| **Dotbot** | Idempotent apply; declarative YAML configuration | Stateless design; no drift detection | We need to know when artifacts have been locally modified |
| **YADM** | Git-as-transport philosophy | Git-as-the-entire-tool; suffix-based per-machine alternates | We wrap git, not replace it; no per-machine variants needed |
| **RCM** | Host/tag organizational concept (maps to our tier system) | Symlinks; no state tracking | Same as Stow |
| **Homebrew taps** | Distributed registry = just a git repo; no central index server | Ruby DSL formulae; build-from-source model | Our artifacts are pre-built text files |

Key architectural lesson: **chezmoi and Stow represent opposite ends of a spectrum** — chezmoi tracks everything (hashes, state DB, templates) while Stow tracks nothing (pure filesystem inference). We sit deliberately in between: content hashes for drift detection (chezmoi-style), but no state database and no templating (Stow-style simplicity).

## Notes

- All model identifiers in examples (e.g., `claude-opus-4-6`, `min_version: "4.5"`) are illustrative and will change as providers release new models. The registry tracks these as data, not as fixed constants.
- Artifact counts (11 agents, ~22 evaluators, ~5 skills) are approximate as of March 2026. Run `kit registry status` for current counts after adoption.
- Path conventions (`.claude/agents/`, `.adversarial/evaluators/`, `.claude/skills/`) are documented as of Claude Code v1.x and adversarial-evaluator-library v0.5.x. If these tools make paths configurable in the future, the registry adapts — artifact identity is name-based, not path-based.

## Revision History

- 2026-04-01: Revision 3 — Add Prior Art section (chezmoi, Stow, Dotbot, YADM, RCM, Homebrew taps). Add three core principles: scan-then-execute atomicity, idempotent apply, no templating. (Proposed)
- 2026-04-01: Revision 2 — Add Non-Goals / Scope Boundary section with litmus test against package-manager creep. (Proposed)
- 2026-04-01: Revision 1 — Address evaluator feedback: add content hash spec, identity/conflict rules, trust model, backwards compat matrix, versioning policy, offline/online split, governance, automation requirements, glossary expansion. Correct O(1) claim, qualify version-sensitive statements. (Proposed)
- 2026-04-01: Initial proposal (Proposed)
