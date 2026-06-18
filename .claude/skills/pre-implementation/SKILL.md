---
description: Pre-implementation checks to run before writing any new code — prevents pattern reuse failures, API misuse, and spec drift
user-invocable: false
version: 1.2.0
origin: dispatch-kit
origin-version: 0.3.2
last-updated: 2026-04-27
created-by: "@movito with planner2"
---

# Pre-Implementation Checklist

Run these checks BEFORE writing any code. Based on analysis of 247+ bot findings across 20+ PRs — these catch 36% of recurring issues at the source.

## 1. Search before you write

Before creating any new function, search the codebase for existing implementations of the same concept.

```text
Pattern:  "I need to parse a timestamp"
Action:   grep -r "fromisoformat\|parse.*iso\|parse.*timestamp" src/
Result:   Find existing utility — reuse or import it
```

Look for:
- DateTime parsing/formatting utilities
- Duration/interval parsing helpers
- Event/model construction patterns
- Config/settings loading patterns
- CLI argument parsing patterns

**If you find an existing implementation**: import it, or match its exact approach. Do NOT rewrite from scratch with "slight improvements."

## 2. Verify the spec against reality

Before copying language from the task spec or handoff into docstrings or comments:

- Does the docstring describe what the code ACTUALLY does (not what was planned)?
- Are "optional" features actually implemented, or deferred?
- Do field names and data structures match what the codebase actually uses?

## 3. Declare matching semantics

For any function that compares strings, decide and document:

- **Exact**: `==` (task IDs, event types, agent names) — this is the default
- **Substring**: `in` (only when explicitly justified in a comment)
- **Pattern**: `re.match` (only when explicitly needed)

Default to exact. Substring requires justification in a comment.

## 4. Plan error handling before writing

Before writing a module's functions, read sibling functions and decide the error strategy for the whole module:

- **Raises**: Caller handles errors (pure domain logic, validators, parsers)
- **Returns empty/default**: Function handles errors internally (CLI-facing, user-facing)
- **Logs and continues**: Fire-and-forget (event emission, telemetry, notifications)

All functions in one module should follow the same strategy. If a sibling function catches OSError, yours must too.

## 5. List boundary inputs

For each new function, enumerate before writing tests:

- Empty input (`[]`, `""`, `{}`)
- None
- Negative numbers / negative time deltas
- Multiple values where you expect one
- Future timestamps / clock skew

These become your TDD test cases — write them BEFORE the implementation.

## 6. External integration audit

**When your feature shells out to a CLI tool or parses external output**, do this BEFORE writing code:

1. **Read the tool's docs for the exact subcommand**. Run `tool --help` or check the online reference. Note:
   - All available flags (especially filter/query flags that avoid client-side work)
   - The documented output format (JSON schema, possible values for each field)
   - All possible values for status/state/enum fields — enumerate them exhaustively

2. **Write down the output contract**. For example:

   ```text
   gh run list --json status,conclusion,name
   - Returns: JSON array of objects (could be empty)
   - status: "completed" | "in_progress" | "queued" | "waiting" | "requested" | "pending"
   - conclusion: "success" | "failure" | "cancelled" | "skipped" | null (when not completed)
   ```

3. **Copy full status sets from sibling implementations**. If another module in the codebase uses the same API, find its status tuples and copy them completely — don't subset. If a sibling handles 6 possible statuses, your new code must handle all 6, not just the 2 you think are common.

4. **List defensive checks needed** before indexing into parsed output:
   - Is the parsed result the expected type? (`isinstance(data, list)`)
   - Is each item the expected type? (`isinstance(item, dict)`)
   - Are the values the expected type? (status is always a string? conclusion can be null?)

These become test cases AND implementation guards. Writing them first prevents the most common bot finding: "you handled 2 of 7 possible values."

## 7. Verify spec algorithm-example cross-references

When the task spec lists format variants (e.g., output format examples) AND describes a parsing algorithm:

1. **Map each format variant to a step in the algorithm.** If any variant isn't covered by an explicit step, it will be silently mishandled.
2. **Check heading/inline priority.** If a heading line can contain an inline value (e.g., `Verdict: APPROVED`), the algorithm must check the heading line BEFORE scanning subsequent lines.
3. **Add a test for each format variant.** The spec's format table becomes the test matrix.

This prevents a common class of bug where the spec describes multiple output formats but the implementation only handles one.

## 8. Exception surface for subprocess integrations

When the spec calls for `subprocess.run()`, verify the full exception surface is documented. Standard set:

| Exception | Cause | Caught by `except OSError`? |
|-----------|-------|---------------------------|
| `FileNotFoundError` | CLI not on PATH | Yes (subclass) |
| `subprocess.TimeoutExpired` | Timed out | No |
| `OSError` | Permission denied, etc. | Yes |
| `UnicodeDecodeError` | Non-UTF-8 output with `text=True` | **No** (subclass of ValueError) |

If the spec doesn't list `UnicodeDecodeError`, add it to your implementation. This is a frequently missed exception — `text=True` in subprocess.run causes it when output contains non-UTF-8 bytes.

## 9. Numeric config param bounds

For every numeric parameter from YAML config, verify the spec defines:

- **Type**: `isinstance(x, int) and not isinstance(x, bool)` (bool is int subclass)
- **Lower bound**: Usually `>= 0`
- **Upper bound**: Max value + clamping with `min(value, MAX_VALUE)`
- **Default**: When absent (None) or invalid type

If the spec omits the upper bound, add a reasonable clamp (e.g., `MAX_TIMEOUT = 3600`).

## 10. pytest exit code 5 (zero-test repos)

**When lowering a coverage gate (e.g., `fail_under=0`) in a repo with no tests
yet**, remember that pytest returns **exit code 5** when it collects zero items
— independently of any coverage threshold. CI will fail even with
`fail_under=0` if pytest collects nothing.

Before lowering the gate, verify:

- At least one `test_*.py` file exists that pytest can collect
- Or add `--exitfirst` handling / a placeholder test
- Or use `pytest ... || [ $? -eq 5 ]` in the CI step (only if you explicitly
  want to tolerate "no tests yet")

Source: ID2-0016 retro — lowering `fail_under` without a collectable test
caused a second fix commit.

## 11. Custom `loadQuery` shape check (Sanity + SvelteKit)

**For any `+page.server.js` change in a Sanity-backed SvelteKit project**,
read the project's `loadQuery` wrapper BEFORE writing merge logic in the
load function.

Sanity's built-in `loadQuery` returns `{ data, sourceMap, perspective }`,
but projects commonly wrap it to return just `data` or a custom envelope
(e.g., `{ initial, query, params }` for live preview). Writing merge logic
against the wrong shape produces a silent null-access bug that only surfaces
at render time.

Check:

- The return shape of the project's `loadQuery` (grep for its definition)
- Whether consuming components expect the wrapped or unwrapped shape
- Whether preview mode uses a different shape than published mode

Source: ID2-0002 retro — shape mismatch caused a load-function refactor
to ship broken before catch.

## 12. Audit file for old pattern (whole-file fixes)

**When changing a pattern in a file** (e.g., `python` → `python3`, an
import path rename, a deprecated API call), grep for **all remaining
instances of the old pattern in the same file** before committing.

```text
Pattern:  Replacing `python script.py` with `python3 script.py` in setup.sh
Action:   grep -n "python " setup.sh   # find every other instance
Result:   Fix them all in one pass — same commit
```

Fixing the whole file in one pass prevents a CodeRabbit/BugBot finding
that triggers a second round when the bot spots a sibling instance you
missed. One scan + one batch is cheaper than two review rounds.

Source: ID2-0018 retro — partial pattern fix triggered an extra bot round.

## 13. Mock patch audit (module-to-package splits only)

**When refactoring a single module into a package** (`module.py` -> `module/`),
audit all `mock.patch` targets in tests BEFORE extracting:

1. Grep for `mock.patch("your_package.<module>.` in all test files
2. Classify each patch target:
   - **Module attribute** (e.g., `subprocess.run`): Safe — patching a module
     object is global
   - **Function reference** (e.g., `_parse_verdict`): **Needs fix** — the
     function resolves in the submodule's namespace, not `__init__.py`
3. For function references, plan a late-import pattern:

   ```python
   # In the submodule method that calls the patched function:
   import your_package.module as _pkg
   result = _pkg._helper_function(...)
   ```

   This ensures `mock.patch("your_package.module.X")` intercepts the call.

**Why**: When `module.py` becomes `module/__init__.py`, `mock.patch("module.X")`
modifies `__init__.__dict__`, but the function runs in `submodule.__dict__` where
the original binding is still cached. Late imports resolve through the package
namespace at call time.

## 14. Test shell recipes against real output before documenting

**When documenting a shell recipe** (in a SKILL, workflow doc, or
runbook), run it against real output once before writing the doc.
One execution catches typos and quoting bugs that no amount of
re-reading will surface — `.md.md` vs `.md`, missing/stray quotes,
flag spelling, copy-paste glitches in the prompt.

```text
Pattern:  About to write `find foo -name "*.md" -exec mv {} {}.md \;`
Action:   Run it in a scratch dir with one file first
Result:   Catches the `.md.md` double-extension before the doc lands
```

This is cheaper than every reader hitting the same typo.

Source: ID2-0015 retro — `.md.md` vs `.md` slip in a documented recipe;
one trial run would have caught it.

## 15. Self-contained snippets (bash blocks in skill docs)

**When writing a bash block in a skill file**, never assume shell variables
from earlier markdown sections are live. Either re-derive state from
authoritative sources (CLAUDE.md, `gh` CLI), or explicitly instruct the
agent to `export NAME=value` before the block. A literal-follower must
be able to copy-paste any single block and have it run.

Markdown bullet lists like:

```markdown
- **target_path**: the value after `- **Path**:`
- **target_github**: the value after `- **GitHub**:`
```

read like variable assignments but **do not** export anything to the
shell. A subsequent block that uses `$target_github` will see an empty
string. The fix is one of:

1. Add an explicit `export` block immediately before the consumer:

   ```bash
   export target_github=$(grep -E '^\- \*\*GitHub\*\*:' CLAUDE.md \
       | sed 's/.*: `\([^`]*\)`.*/\1/')
   ```

2. Or re-derive inside the consumer block itself:

   ```bash
   gh --repo "$(grep -E '^\- \*\*GitHub\*\*:' CLAUDE.md \
       | sed 's/.*: `\([^`]*\)`.*/\1/')" pr view ...
   ```

**Source**: ID2-0026 fix-of-fix shipped a silent failure because
`$target_github` was a markdown value, not an exported shell variable.
The bash block ran with an empty repo flag, succeeded against the
default repo, and looked correct.

## 16. Inline-test extraction logic against real input

**When writing regex / sed / jq / awk that parses a real config file**
(CLAUDE.md, YAML, JSON, handoff files), run the extractor against the
actual file in the repo before committing. Document the test in the
commit message.

```text
Pattern:  About to ship `grep -E '[A-Za-z0-9_.-]+/...' CLAUDE.md` to extract the GitHub slug
Action:   Run it against CLAUDE.md once and inspect the first match
Result:   Catches that `.` is in the character class and `../ixda-services` (Path) matches before `IxDA-Oslo/ixda-services` (GitHub)
```

Common gotchas this catches:
- Character classes that include `.` or `/` matching path-like values
  before slug-like values
- Greedy quantifiers grabbing more than the line you intended
- `sed -i` portability differences (BSD vs GNU)
- jq paths assuming a key exists on every element of an array

**Source**: ID2-0026 — the `gh-review-helper.sh` repo-detection regex
matched `../ixda-services` before `IxDA-Oslo/ixda-services` because the
character class `[A-Za-z0-9_.-]+` accepted `..`. One inline test
against `CLAUDE.md` would have surfaced it before commit.

This rule and the previous ("Self-contained snippets") apply
equivalently to skill files in `.kit/skills/` and workflow docs in
`.kit/context/workflows/`.

## For refactoring tasks: skip steps 1-11

Steps 1-11 are optimized for **feature development** (new code, new logic). For
**pure refactoring** (module splits, renames, reorganization), steps 12 (audit
file for old pattern — directly relevant to renames and pattern replacements)
and 13 (mock patch audit) apply. Also skip:

- Self-review boundary audit (no new input boundaries)
- Keep: code-review evaluator (catches latent bugs in pre-existing code),
  spec compliance check, bot triage, CI verification

**Why keep the evaluator for refactoring?** Empirical evidence shows the evaluator
finds different issues than bots or human analysis — with zero overlap. For
refactoring, it provides "fresh eyes on pre-existing code" and catches latent
correctness/robustness issues (~$0.01, ~2 min).
