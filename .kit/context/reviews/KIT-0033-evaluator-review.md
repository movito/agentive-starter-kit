#  Code Reviewer Fast

**Source**: .adversarial/inputs/KIT-0033-code-review-input.md
**Evaluator**: code-reviewer-fast
**Model**: gemini/gemini-2.5-flash
**Generated**: 2026-06-27 00:52 UTC

---

### Findings

**[CORRECTNESS]: Duplicate KIT-LOCAL region names are not handled correctly**
- **Location**: `scripts/local/kit_markers.py:merge`
- **Edge case**: An agent markdown file contains multiple `KIT-LOCAL` regions with the *same* name (e.g., two `project-context` blocks).
- **What happens**: `find_regions` will return the duplicate names. When `merge` iterates through these and calls `replace_region` for each, `replace_region` (due to `count=1`) will consistently modify *only the first* instance of that named region. Subsequent regions with the same name will be ignored during the merge process, silently failing to apply consumer content or placeholders to them. This violates the implicit expectation that if a region is defined, it should be processed.
- **Tested?**: No

**[CORRECTNESS]: `bootstrap-consumer.sh` modifies its own source repository if target is `PROJECT_ROOT`**
- **Location**: `scripts/local/bootstrap-consumer.sh`
- **Edge case**: The target directory (`$TARGET`) for bootstrapping is accidentally set to the `agentive-starter-kit`'s own `PROJECT_ROOT`.
- **What happens**: The `rm -f` commands intended to sweep retired agent variants from the *consumer* project (`"$TARGET/.claude/agents/planner2.md"`, etc.) would execute on the *source* `agentive-starter-kit` repository itself. This would delete the historical `planner2.md`, `planner3.md`, `feature-developer-v3.md`, `feature-developer-v6.md`, and `feature-developer-v7.md` files from the kit's own `.claude/agents` directory. While these are "retired", their deletion from the canonical source repo as a side effect of a consumer bootstrap operation is highly undesirable and likely unintended.
- **Tested?**: No

**[ROBUSTNESS]: `kit_markers.py` does not explicitly validate well-formed marker pairs**
- **Location**: `scripts/local/kit_markers.py:find_regions`
- **Edge case**: An agent markdown file contains a `BEGIN` marker for a region but is missing the corresponding `END` marker (e.g., `<!-- BEGIN KIT-LOCAL: my-region -->\nSome content\n`).
- **What happens**: `find_regions` would still detect and return the region name. However, `extract_region` and `replace_region` would fail to find a match for `_region_pattern` because the pattern requires both `BEGIN\nBODY\nEND`. This would lead `extract_region` to return `None`, and `replace_region` to raise `KeyError` (if called directly for that region) or fallback to placeholder/upstream content in `merge`. While `merge` handles the fallback, it could silently mask a malformed agent file.
- **Tested?**: No

**[ROBUSTNESS]: `default_placeholders` produces empty title for specific `project_name` inputs**
- **Location**: `scripts/local/kit_markers.py:default_placeholders`
- **Edge case**: The `project_name` is an empty string, or consists only of characters that are replaced by spaces (`-`, `_`). For example, `project_name="---"` or `project_name=""`.
- **What happens**: `project_name.replace("-", " ").replace("_", " ").title()` will result in an empty string or a string of spaces. The placeholder content would then include "This is the **''** project." or "This is the **   ** project.". While not a functional failure, it's a cosmetic issue that makes the generated placeholder less user-friendly. `basename` in `bootstrap-consumer.sh` makes truly empty unlikely, but all-whitespace/punctuation is possible.
- **Tested?**: Yes (TestDefaultPlaceholders covers empty and `widget-factory_2`, but doesn't explicitly check for all-whitespace/punctuation names).

### Test Gap Summary
| Edge Case | Function | Tested? | Risk |
|---|---|---|---|
| Duplicate KIT-LOCAL region names | `kit_markers.py:merge` | No | High (logic error, silent failure to apply updates) |
| Target is `PROJECT_ROOT` (self-bootstrap) | `bootstrap-consumer.sh` | No | High (modifies source control of the kit itself) |
| Missing `END` marker for a region | `kit_markers.py:find_regions` | No | Medium (silently masks malformed agent file) |
| Empty content within markers | `kit_markers.py:extract_region`, `kit_markers.py:replace_region` | No | Low (implied by other tests, likely works) |
| Entire `bootstrap-consumer.sh` script | `bootstrap-consumer.sh` (all functions) | No | High (orchestration logic, file system operations) |

### Verdict

**FAIL**: Correctness bugs found. The `rm -f` in `bootstrap-consumer.sh` operating on the source kit is a critical issue that could lead to data loss or corruption of the kit's own history. The silent failure to handle duplicate region names in `kit_markers.py` is also a correctness bug for unexpected but plausible inputs. These must be fixed.
