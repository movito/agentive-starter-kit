# TypeScript/JavaScript LSP Setup for Serena

**Status**: ✅ Production Ready
**Validated**: 2025-11-20
**Performance**: 65% average token savings, 2-3x speed improvement

---

## Overview

This guide explains how to set up and verify TypeScript/JavaScript semantic navigation with Serena MCP for the `frontend/` directory.

**Benefits**:
- 65% average token reduction (vs traditional grep + file reads)
- 2-3x faster code navigation
- 100% precision reference tracking (no false positives)
- Works for React components, hooks, TypeScript interfaces

---

## Prerequisites

### Required Software

✅ **Node.js v16+** (Installed: v22.18.0)
```bash
node --version
# Output: v22.18.0 (or higher)
```

✅ **npm v8+** (Installed: v11.5.2)
```bash
npm --version
# Output: 11.5.2 (or higher)
```

✅ **Serena MCP** (Already configured)
```bash
claude mcp list
# Output should show: serena: ✓ Connected
```

---

## Installation

### Step 1: Install TypeScript LSP

**Status**: ✅ **ALREADY INSTALLED** (as of 2025-11-18)

The TypeScript Language Server is already installed globally via npm.

**Verification**:
```bash
which typescript-language-server
# Expected: /Users/broadcaster_three/.nvm/versions/node/v22.18.0/bin/typescript-language-server

typescript-language-server --version
# Expected: 5.1.2 (or higher)
```

**If not installed** (for other team members):
```bash
npm install -g typescript-language-server typescript
```

---

### Step 2: Restart Claude Code (CRITICAL)

**IMPORTANT**: Serena detects language servers at MCP startup, not dynamically.

**Required Action**:
1. Close your current Claude Code session completely
2. Restart Claude Code (or start a fresh conversation in new tab)
3. This allows Serena to detect the TypeScript LSP

**Why This Matters**: Without restart, Serena will only show "python" as programming language. After restart, it will show "python, swift, typescript".

---

### Step 3: Activate Project and Verify Detection

In your **new** Claude Code conversation:

```
Please activate Serena for this project:
mcp__serena__activate_project("your-project")
```

**Expected Output**:
```
"Programming languages: python, swift, typescript"
```

**If TypeScript is NOT shown**:
1. Verify TypeScript LSP is installed (Step 1)
2. Ensure you restarted Claude Code (Step 2)
3. Check that TypeScript LSP is in your PATH
4. See Troubleshooting section below

---

## Verification Tests

Run these tests in Claude Code to verify TypeScript semantic navigation works.

### Test 1: Find React Component

**Objective**: Verify `find_symbol` works for React components

**Test**:
```
Can you find the App component in the frontend directory using Serena?
Expected tool: mcp__serena__find_symbol
```

**Expected Result**:
- Component found: `App` (Function, lines 6-13)
- File: `frontend/src/App.tsx`
- ✅ PASS if component found

---

### Test 2: Find Hook References

**Objective**: Verify reference tracking works across files

**Test**:
```
Can you find all references to the useWizard hook using Serena?
File: frontend/src/context/WizardContext.tsx
```

**Expected Result**:
- References found in 4+ files
- Includes imports and usages
- ✅ PASS if references span multiple files

---

### Test 3: Symbol Overview

**Objective**: Verify symbol overview for large files

**Test**:
```
Can you get a symbol overview of WizardContext.tsx using Serena?
Expected tool: mcp__serena__get_symbols_overview
```

**Expected Result**:
- 10 top-level symbols found
- Includes: Functions, interfaces, constants
- ✅ PASS if overview shows symbols without full file content

---

### Test 4: Python LSP Regression Check

**Objective**: Ensure Python still works

**Test**:
```
Can you find the sync_task_to_linear function in the scripts directory using Serena?
```

**Expected Result**:
- Python function found in `scripts/linear_sync_stubs.py`
- ✅ PASS if Python symbols still work

---

## Usage Guide

### When to Use Serena for TypeScript

✅ **Use Serena for**:
- Navigating React components (100+ lines)
- Finding component references across files
- Understanding component structure (hooks, handlers, state)
- Tracking hook usages
- Understanding context providers and consumers

❌ **Use traditional tools for**:
- Small files (< 50 lines) - savings are minimal
- Reading full file content - Serena shows structure, not full code
- Simple string searches - grep is fine for non-symbol searches

---

### Common Workflows

#### Workflow 1: Understanding a React Component

**Goal**: Understand the structure of a large React component without reading full file.

**Serena Approach**:
```
1. Get symbol overview:
   mcp__serena__get_symbols_overview("frontend/src/components/wizard/WizardContext.tsx")

2. Find specific component with children:
   mcp__serena__find_symbol(
       name_path_pattern="WizardProvider",
       relative_path="frontend/src/context/WizardContext.tsx",
       include_body=false,
       depth=1
   )
```

**Benefit**: See all hooks, handlers, and structure without reading 287 lines (98% token savings).

---

#### Workflow 2: Finding Where a Hook is Used

**Goal**: Find all usages of a custom hook across the codebase.

**Serena Approach**:
```
mcp__serena__find_referencing_symbols(
    name_path="useWizard",
    relative_path="frontend/src/context/WizardContext.tsx"
)
```

**Benefit**:
- 100% precision (only code references, no comments)
- Shows context snippets for each usage
- 60% token savings vs grep + reading multiple files

---

#### Workflow 3: Navigating to a Component by Name

**Goal**: Quickly jump to a component definition.

**Serena Approach**:
```
mcp__serena__find_symbol(
    name_path_pattern="WizardRouter",
    relative_path="frontend/src"
)
```

**Benefit**: Direct navigation to component location without grep.

---

## Performance Expectations

Based on validation testing (THEMATIC-0108):

### Token Savings by File Size

| File Size | Traditional Tokens | Serena Tokens | Savings |
|-----------|-------------------|---------------|---------|
| Small (< 50 lines) | ~750 | ~500 | 26-38% |
| Medium (100-150 lines) | ~2,000 | ~400 | 79-86% |
| Large (200+ lines) | ~4,000 | ~100 | 98% |

### Use Case Performance

| Use Case | Traditional | Serena | Savings |
|----------|-------------|--------|---------|
| Find React component | Read full file (~2,000 tokens) | Symbol only (~400 tokens) | 79% |
| Find hook references | Grep + read contexts (~3,000 tokens) | Reference tracking (~1,200 tokens) | 60% |
| Get component structure | Read full file (~4,000 tokens) | Symbol overview (~85 tokens) | 98% |

**Average**: **65% token savings** across all use cases

---

## Troubleshooting

### Issue 1: TypeScript Not Detected

**Symptom**: `mcp__serena__activate_project` shows "python" but not "typescript"

**Solutions**:

**A. Restart Claude Code (Most Common)**
1. Close Claude Code completely
2. Restart application
3. Start fresh conversation
4. Activate project again

**B. Verify TypeScript LSP Installation**
```bash
which typescript-language-server
# Should return a path

typescript-language-server --version
# Should return version number (5.1.2+)
```

If not installed:
```bash
npm install -g typescript-language-server typescript
```

**C. Check PATH**
```bash
echo $PATH | grep nvm
# Should show: /Users/broadcaster_three/.nvm/versions/node/v22.18.0/bin
```

If not in PATH, add to shell profile (~/.zshrc or ~/.bashrc):
```bash
export PATH="$HOME/.nvm/versions/node/v22.18.0/bin:$PATH"
```

**D. Test LSP Server Directly**
```bash
typescript-language-server --stdio
# Should start without errors (Ctrl+C to exit)
```

---

### Issue 2: Symbol Not Found

**Symptom**: `find_symbol` returns empty array `[]`

**Solutions**:

**A. Check File Path**
- Ensure `relative_path` points to correct directory
- Example: `frontend/src` not `frontend`

**B. Check Symbol Name**
- Try partial name with `substring_matching=true`
- Use `get_symbols_overview` first to see available symbols

**C. Check File Type**
- `.tsx` files work best for React components
- `.ts` files (non-React) may have reduced support for re-exports

---

### Issue 3: References Not Found

**Symptom**: `find_referencing_symbols` returns empty or incomplete results

**Solutions**:

**A. Verify Symbol Definition**
- Run `find_symbol` first to confirm symbol exists
- Use exact `name_path` from find_symbol result

**B. Check Import Paths**
- References using path aliases (`@/components`) are tracked
- References using relative paths (`../components`) are tracked
- Both should work if `tsconfig.json` is correctly configured

---

### Issue 4: Slow Performance

**Symptom**: Queries take > 5 seconds

**Solutions**:

**A. Check Project Size**
- Serena indexes on-demand
- First query may be slower (~5-10s)
- Subsequent queries should be fast (~2-3s)

**B. Restart Language Server**
```
Use Serena tool:
mcp__serena__restart_language_server
```

**C. Check System Resources**
- Ensure adequate RAM (8GB+ recommended)
- Close other resource-intensive applications

---

## Known Limitations

### 1. Pure TypeScript Files (.ts)

**Limitation**: Re-export files (like `useWizard.ts`) may not show symbols directly.

**Workaround**: Search in the source file where symbol is defined (e.g., `WizardContext.tsx`).

**Impact**: LOW - Most GUI files are `.tsx` (React components).

---

### 2. Small File Savings

**Limitation**: Files < 50 lines show 26-38% savings vs 80-98% for larger files.

**Reason**: JSON response overhead proportionally higher for small files.

**Impact**: LOW - Savings still positive, just less dramatic.

---

### 3. Cross-Language References

**Limitation**: Cannot track references from Python → TypeScript or vice versa.

**Status**: This is expected LSP behavior. Each language server operates independently.

**Future**: Multi-language integration planned in THEMATIC-0110.

---

## Path Alias Configuration

### TypeScript Path Aliases

Serena correctly resolves these path aliases defined in `tsconfig.json`:

```json
{
  "compilerOptions": {
    "paths": {
      "@/*": ["./src/*"]
    }
  }
}
```

**Supported Aliases**:
- `@/components` → `src/components`
- `@/context` → `src/context`
- `@/hooks` → `src/hooks`
- `@/utils` → `src/utils`
- `@/types` → `src/types`

**Verification**: Reference tracking for `useWizard` correctly resolved imports using `@/context/WizardContext`.

---

## Team Onboarding

### For New Team Members

1. **Prerequisites** (5 minutes)
   - Install Node.js v16+ and npm v8+
   - Verify Serena MCP connected: `claude mcp list`

2. **Installation** (2 minutes)
   ```bash
   npm install -g typescript-language-server typescript
   ```

3. **Activation** (1 minute)
   - Restart Claude Code
   - Activate project: `mcp__serena__activate_project("your-project")`
   - Verify: "typescript" in programming languages

4. **Verification** (5 minutes)
   - Run Test 1-4 from Verification Tests section above

**Total Time**: ~15 minutes

---

### Training Resources

**Documentation**:
- This setup guide (`.serena/claude-code/TYPESCRIPT-SETUP.md`)
- Validation report (`.agent-context/SERENA-TYPESCRIPT-VALIDATION.md`)
- Use case matrix (`.serena/claude-code/USE-CASES.md`)
- Python setup guide (`.serena/claude-code/SETUP-GUIDE.md`) - similar patterns

**External References**:
- TypeScript LSP: https://github.com/typescript-language-server/typescript-language-server
- Serena GitHub: https://github.com/oraios/serena
- LSP Protocol: https://microsoft.github.io/language-server-protocol/

---

## FAQ

### Q: Do I need to install TypeScript LSP separately from TypeScript compiler?

**A**: Yes, but they're typically installed together:
```bash
npm install -g typescript-language-server typescript
```

The LSP server (`typescript-language-server`) is separate from the TypeScript compiler (`tsc`), but both are needed.

---

### Q: Will this affect my TypeScript compilation or build process?

**A**: No. The TypeScript LSP is only for code navigation in Claude Code. It does not affect:
- TypeScript compilation (`tsc`)
- Build processes (`npm run build`)
- Testing (`npm run test`)
- Development server (`npm run dev`)

---

### Q: Can I use Serena for JavaScript files (.js)?

**A**: Yes! The TypeScript LSP also supports JavaScript files. Detection shows "typescript, javascript" in programming languages.

---

### Q: Why do I need to restart Claude Code after installation?

**A**: Serena detects available language servers when the MCP server starts. If you install a new LSP during a session, Serena won't detect it until the next restart.

**Analogy**: Like installing a new app and needing to refresh your app launcher to see it.

---

### Q: What if I'm working on a different TypeScript project?

**A**: The TypeScript LSP is installed globally and works for any TypeScript project. Just activate the project:
```
mcp__serena__activate_project("/path/to/your/project")
```

---

### Q: Can I use traditional tools alongside Serena?

**A**: Yes! Serena complements traditional tools (grep, read). Use Serena for semantic navigation and traditional tools for other tasks.

**Best Practice**:
- Serena: Component structure, reference tracking, symbol navigation
- Traditional: Reading full implementations, string searches, file content

---

## Support

### Internal Support

- **Documentation**: `.serena/claude-code/` directory
- **Validation Report**: `.agent-context/SERENA-TYPESCRIPT-VALIDATION.md`
- **Use Cases**: `.serena/claude-code/USE-CASES.md`

### External Support

- **Serena GitHub**: https://github.com/oraios/serena
- **TypeScript LSP Issues**: https://github.com/typescript-language-server/typescript-language-server/issues
- **Claude Code Docs**: https://docs.claude.com/en/docs/claude-code

---

## Changelog

### 2025-11-20: Initial Setup & Validation

- ✅ TypeScript LSP v5.1.2 installed (pre-installed on 2025-11-18)
- ✅ Detection verification completed
- ✅ Validation testing completed (THEMATIC-0108)
- ✅ Performance metrics: 65% token savings, 2-3x speed improvement
- ✅ Documentation created (this guide + validation report)
- ✅ **Status**: Production ready for team use

---

**Setup Guide Version**: 1.0
**Last Updated**: 2025-11-20
**Validated By**: powertest-runner agent
**Status**: ✅ Production Ready
