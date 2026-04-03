# Code Review: Agentive Starter Kit — ASK-0048 Unified Artifact Registry Phase 1

## Context

Add `registry:` metadata blocks to all shared agent definitions (14) and skills (5),
create a central registry index (`index.yml`), and provide a content hash computation
script. This is Phase 1 of ADR-0007 — non-breaking, metadata-only, no runtime changes.

**Task**: ASK-0048
**PR**: #45
**Bot review status**: CodeRabbit: 6 findings (4 fixed, 2 resolved as design-doc scope). BugBot: 4 findings (2 fixed, 2 resolved as design tradeoffs).

## Changed Files

### Source: `scripts/core/compute_content_hash.py` (NEW)

Content hash computation per ADR-0007 spec:
- `normalize_content()`: LF line endings, strip trailing whitespace, single trailing newline, UTF-8
- `extract_markdown_body()`: Extract body after closing `---` of YAML frontmatter
- `extract_yaml_functional_content()`: Remove top-level `registry:` and `_meta:` blocks from YAML
- `compute_hash()`: SHA-256 of normalized body content, format `sha256:<64-char-hex>`
- `main()`: CLI interface supporting individual files or `--all` for glob patterns

### Tests: `tests/test_compute_content_hash.py` (NEW)

25 tests covering:
- `TestNormalizeContent` (8 tests): LF passthrough, CRLF/CR conversion, trailing whitespace, trailing newlines, UTF-8, empty string
- `TestExtractMarkdownBody` (5 tests): basic frontmatter, no frontmatter, registry in frontmatter, unclosed frontmatter, triple dashes in body
- `TestExtractYamlFunctionalContent` (5 tests): registry block removal, meta block removal, empty lines after stripped blocks, top-level-only stripping, non-registry preservation
- `TestComputeHash` (7 tests): markdown/yaml files, determinism, frontmatter-only changes, body changes, whitespace normalization, CRLF/LF equivalence

### Registry: `.kit/registry/index.yml` (NEW)

Central registry index listing all 19 artifacts with content hashes, types, tiers, paths, and tags.

### Metadata: 14 agent files + 5 skill files (MODIFIED)

Each received a `registry:` block in YAML frontmatter with type, version, tier, source, content_hash, tags, min_kit_version.

### Manifest: `scripts/.core-manifest.json` (MODIFIED)

Added `core/compute_content_hash.py` to scripts_core array.

### Tests: `tests/test_core_manifest.py` (MODIFIED)

Updated count expectations: scripts_core 14→15, total 39→40.

### Docs: `docs/adr/ADR-0007-unified-artifact-registry.md` (MODIFIED)

Fixed CLI namespace inconsistency, added markdownlint-compliant formatting, added language identifiers to fenced code blocks.

### Config: `.kit/context/agent-handoffs.json` (MODIFIED)

Fixed details_link path from `2-todo/` to `3-in-progress/`.

### Docs: `CLAUDE.md` (MODIFIED)

Added pytest invocation note.

## Review Focus Areas

1. **Content hash correctness**: Does the hash computation correctly ignore metadata while capturing functional content changes?
2. **YAML stripping**: Does `extract_yaml_functional_content()` correctly handle edge cases (nested keys, empty lines, multi-block)?
3. **Frontmatter parsing**: Does `extract_markdown_body()` handle all valid frontmatter patterns?
4. **Registry metadata consistency**: Are all 19 artifacts correctly classified (tier, tags)?
5. **Index schema**: Does `index.yml` match the ADR-0007 specification?
6. **Test coverage**: Are boundary conditions adequately covered?
7. **Backward compatibility**: Do the frontmatter additions break any existing tooling?
