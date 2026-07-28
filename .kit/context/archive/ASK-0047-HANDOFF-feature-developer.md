## ASK-0047: Flatten ADR Directory Structure

**You are the feature-developer. Implement this task directly.**

### Goal

Remove unnecessary nesting in ADR directories:

| Old Path | New Path |
|----------|----------|
| `docs/adr/` | `docs/adr/` |
| `docs/adr/README.md` | `docs/adr/about-adr.md` |
| `docs/adr/TEMPLATE-FOR-ADR-FILES.md` | `docs/adr/TEMPLATE-FOR-ADR-FILES.md` |
| `.kit/adr/` | `.kit/adr/` |
| `.kit/adr/README.md` | `.kit/adr/about-kit-adr.md` |
| `docs/adr/` | *(delete after moves)* |

### Steps

1. **Create branch**: `git checkout -b feature/ASK-0047-flatten-adr-dirs`
2. **Move project ADRs**:
   - `git mv docs/adr/ docs/adr/`
   - Rename `docs/adr/README.md` → `docs/adr/about-adr.md`
   - Delete `docs/adr/` (will be empty)
3. **Move kit ADRs**:
   - `git mv .kit/adr/ .kit/adr/`
   - Rename `.kit/adr/README.md` → `.kit/adr/about-kit-adr.md`
4. **Update all path references** — there are ~137 references across 58 files:
   - `docs/adr/` → `docs/adr/`
   - `.kit/adr/` → `.kit/adr/`
   - `docs/adr/` → `docs/adr/` (bare references)
   - Update internal links in both about-adr.md files
5. **Update `.core-manifest.json`** if it references `.kit/adr/`
6. **Update CLAUDE.md** directory structure table
7. **Grep verification** — zero matches for:
   - `grep -r 'docs/adr/' .claude/ CLAUDE.md README.md scripts/ .kit/ --include='*.md' --include='*.py' --include='*.sh' --include='*.yml' --include='*.json'`
   - `grep -r '\.kit/adr/' .claude/ CLAUDE.md README.md scripts/ .kit/ --include='*.md' --include='*.py' --include='*.sh' --include='*.yml' --include='*.json'`
8. **Run CI**: `./scripts/core/ci-check.sh`

### Scope

This is a structural rename — single atomic PR per PR-SIZE-WORKFLOW §3.

### What NOT to change

- Do not modify the content of any ADR files (only paths/links)
- Do not reorganize KIT-ADR files or renumber them
- Historical/archive task files (`.kit/tasks/8-archive/`, `.kit/tasks/5-done/`) — update references in these too, they're still read by agents

### Risk

Low. Pure renames + find-and-replace. Grep verification is the gate.
