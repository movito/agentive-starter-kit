---
description: Self-review pass after tests pass but before committing — systematic input boundary audit that catches issues TDD misses
user-invocable: false
version: 1.0.0
origin: dispatch-kit
origin-version: 0.3.2
last-updated: 2026-02-27
created-by: "@movito with planner2"
---

# Self-Review: Input Boundary Audit

Run AFTER tests pass, BEFORE committing.

**Every place where data enters a function is a boundary. Audit every boundary, not just the ones you thought about while coding.**

## Step 1: Enumerate input boundaries

For each function you changed, list every source of input data:

| Boundary type | Example | What can go wrong |
|---------------|---------|-------------------|
| **Function parameter** | `gate: GateDefinition` | Caller passes wrong type, None, or unexpected value |
| **Dict `.get()` / `[]`** | `params.get("workflow")` | Key missing, value is wrong type (int instead of str) |
| **External process output** | `json.loads(result.stdout)` | Not JSON, wrong top-level type, items wrong shape |
| **Attribute access** | `event.payload` | Attribute is None, wrong type |
| **Protocol/interface input** | `checker.check(branch)` | Implementation returns unexpected status string |

**Write the list down** (mentally or in a comment). Then audit each one.

## Step 2: Audit each boundary

For each boundary you listed, ask these three questions:

### Q1: What types can this value actually be?

Not "what type should it be" — what types COULD it be at runtime?

```text
params.get("workflow")
  Expected: str or None
  Actually possible: str, None, int, list, dict, bool (YAML is permissive)
  -> Need: isinstance(workflow, str) guard, or coerce non-string to None
```

```text
json.loads(result.stdout)
  Expected: list[dict]
  Actually possible: dict, list, str, int, float, None, list[None], list[str]
  -> Need: isinstance(data, list) AND isinstance(data[0], dict) guards
```

### Q2: Do parallel code paths have matching guards?

If you added `isinstance(x, str)` in one branch, check ALL other branches that use the same value:

```text
_resolve_branch():
  Dotted-path branch: isinstance(current, str) at the end  [OK]
  Default fallback branch: returns payload.get("branch") — NO type check  [MISSING]
  -> Both paths must validate the final value is a string
```

This is the **mirror guards** pattern — the most common source of round-2 bot findings.

### Q3: What happens when this value is missing/None/wrong-type?

Trace the code path for each:
- **None**: Does `.get()` return None? Does None propagate to a `.split()` or `[0]` that crashes?
- **Wrong type**: Does an int where you expected a string reach `str.split(".")` and crash?
- **Empty**: Does `[]` reach `[0]` and raise IndexError? Does `""` pass an `if value:` guard?

## Step 3: Check consistency across the file

Read every function in the file you changed (not just the ones you wrote):

1. **Error handling strategy**: All functions in one module should follow the same error handling pattern. If function A returns a default value on failure, function B in the same module must NOT raise an exception on failure. Match the strategy used by sibling functions.

2. **Mirror exception audit**: After fixing ANY exception handler, grep the same file for other `except` blocks with the same narrow clause. Fix ALL of them — not just the one in the findings.

   ```bash
   # Example: if you broadened "except (ValueError, KeyError)" in read_all(),
   # check for the same pattern in sibling functions:
   grep -n "except.*ValueError.*KeyError" path/to/module.py
   ```

   This catches the mirror guards pattern — the #1 source of preventable CodeRabbit findings. If one function in a module needs a broader exception tuple, its siblings almost certainly do too.

3. **String comparison semantics**: `==` for identifiers. If you used `in` anywhere for substring matching, it needs a comment explaining why. Default to exact match.

4. **Docstring accuracy**: Does each docstring describe what the code does NOW (post-implementation), not what was planned? Did the spec say "queries GitHub" but the function actually does something different?

5. **Early-return ordering**: For each early-return path, verify it doesn't block a cheaper or more important early-return that should come first. Example: validating tools (cheap, may short-circuit) should come before resolving PR (expensive subprocess call).

6. **Module documentation**: If you changed a module's public API, parameters, or invariants, check if the module has a documentation file or contract (e.g., a module-level CLAUDE.md, README, or docstring). Update it if the public interface changed. When adding a breaking-change trigger that references another module, verify the inverse trigger exists in that module's documentation too.

## Step 4: Test assertion audit

Before checking boundary coverage, audit test assertion quality:

1. **Negative inputs through argparse**: If the source validates input (e.g., `<= 0` guard), test it via the full CLI arg path, not just by calling the function directly with bad input. Argparse `type=int` catches some issues the function guard catches others — test both paths.
2. **Assert content identity, not just count**: `assert len(json_lines) == 2` is weak. Also check that the content is correct (e.g., event types, ordering, specific field values).
3. **Assert ordering when claimed**: If a docstring or test name says "returns events in order," assert the actual order (e.g., `timestamps[0] < timestamps[1]`), not just membership.

## Step 5: Verify test coverage of boundaries

For each boundary you identified in Step 1, verify you have a test. The TDD phase produces happy-path tests. This step produces boundary tests:

```text
Boundary: params.get("workflow") could be int
Test needed: test_non_string_workflow_param_treated_as_none
Present? NO -> write it now

Boundary: json.loads could return dict instead of list
Test needed: test_non_list_json_output
Present? NO -> write it now
```

**Minimum bar**: every `isinstance` guard you added in Step 2 must have a test that exercises the guard.

## Step 6: Dead code and spec completeness (after 2+ fix rounds)

Only needed if you've done multiple rounds of fixes:

- **Dead code**: Variables assigned but never read? `if` branches that can never trigger?
- **Spec re-read**: Re-read the task spec requirements. For each numbered item, point to the code that implements it. "Understanding" is not "implementing."

## Quick Reference

Key defensive patterns — consult before every self-review:

| Pattern | What to check | Catches |
|---------|--------------|---------|
| **External API enumeration** | Read --help/docs BEFORE coding; enumerate all possible values | Missing CLI flags, incomplete status handling |
| **Mirror guards** | When you add isinstance() in one path, apply to all parallel paths | Inconsistent type validation across branches |
| **Shape validation** | After json.loads/deserialization, validate type at each level before indexing | Crashes on unexpected JSON structure |
| **Empty string substring** | Guard `x in s` with `if x and x in s` when x comes from config/user input | `"" in any_string` is always True — bypasses checks silently |
| **Empty iterable all()** | Guard `all(...)` with non-empty check — `all([])` is True (vacuous truth) | Empty result sets silently satisfy gate conditions |
| **Fallback status semantics** | Define every status BEFORE implementing; audit else/fallback paths | Found-but-failed != missing; in-progress != missing |
| **Shared helper over copy** | When spec says "mirror function X", create parameterized helper, don't copy-paste | Duplicated logic means bug fixes must be applied twice |
| **Sentinel cache** | Use `object()` sentinel for cache state, not `None` — `None` may be a valid cached result | Re-fetching on every call when lookup legitimately returns None |
| **None vs falsy** | Use `x is None` not `not x` for absence checks — YAML values like `0`, `""`, `[]` are falsy but valid | Rejecting valid user-provided empty/zero values as "missing" |
| **Subprocess text decode** | Catch `UnicodeDecodeError` alongside `FileNotFoundError`, `TimeoutExpired`, `OSError` when using `text=True` | Non-UTF-8 subprocess output crashes the process (UnicodeDecodeError is ValueError, not OSError) |
| **Config value clamping** | After type-validating numeric config params, clamp to a max with `min(value, MAX)` before system calls | Unbounded timeout/retry from YAML passes isinstance() but exhausts resources |
| **Path traversal sanitization** | When constructing paths from config/external names, sanitize with `Path(name).name` to strip dir components | `../../etc/passwd` escapes intended directory via path separators in evaluator/tool names |
| **None in f-strings** | Before interpolating potentially-None values in f-strings, check for None explicitly | `f"{value}"` silently produces the string `"None"` — looks valid but misleading |
