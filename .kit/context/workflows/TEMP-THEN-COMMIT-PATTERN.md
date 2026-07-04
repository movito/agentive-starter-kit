# Temp-Then-Commit Pattern (Two-Pass File Mutation)

**Purpose**: Keep multi-file mutations atomic in `set -e` shell scripts —
either every file is updated, or none is
**Agents**: feature-developer (bootstrap/sync script work), planner (spec review)
**Last Updated**: 2026-07-04 (KIT-0034 F3)

---

## The Rule

When a script step mutates **more than one file** under `set -e`, never
write (or `mv`) into a destination inside the same loop that can still
fail. Instead:

1. **Pass 1 — stage**: produce every output to a temp file
   (`<dest>.tmp` or similar). Any failure aborts here, before a single
   destination has been touched.
2. **Pass 2 — commit**: only after every staged output exists, `mv` the
   temp files into place. This pass contains no fallible work.

Also clear stale temp files from a previously aborted run before pass 1.

## Why

Under `set -e`, a per-item write-then-continue loop dies mid-iteration on
the first failure — leaving some destinations updated and others stale.
The consumer then has a **silently inconsistent** state that no error
message describes, and a re-run may not repair (e.g. `--ignore-existing`
sync semantics, or merges that now read the half-updated file as input).

**Motivating case (KIT-0033 atomicity bug)**: the bootstrap marker-merge
loop originally merged each agent file and moved it into place per
iteration. A malformed KIT-LOCAL marker in the third agent aborted the
loop after two agents were already overwritten — a consumer checkout with
half-refreshed agents and no clean way to tell which half.

## Before / After

**Before — per-item mv inside the loop (broken):**

```bash
set -e
for agent in "${KIT_AGENTS[@]}"; do
    python3 kit_markers.py merge --upstream "$SRC/$agent" \
        --out "$DST/$agent.tmp"
    mv "$DST/$agent.tmp" "$DST/$agent"   # commits item N before item N+1 is known to succeed
done
```

**After — two passes (atomic):**

```bash
set -e
rm -f "$DST/"*.tmp                        # clear stale temps from an aborted run
for agent in "${KIT_AGENTS[@]}"; do       # pass 1: stage everything
    python3 kit_markers.py merge --upstream "$SRC/$agent" \
        --out "$DST/$agent.tmp"
done
for agent in "${KIT_AGENTS[@]}"; do       # pass 2: commit (infallible work only)
    mv "$DST/$agent.tmp" "$DST/$agent"
done
```

Live implementation: the marker-merge step in
`scripts/local/bootstrap-consumer.sh` (Step 2, kit workflow agents).

## When To Apply

- Bootstrap / sync / migration scripts that write N related files
  (agent sets, manifest + files, config pairs)
- Any `set -e` loop whose body mixes fallible work (merge, render,
  download, validate) with destination writes
- Not needed for single-file writes — a plain `write-to-temp && mv` (or a
  direct write, when a torn single file is acceptable) already covers it

## Boundaries

- Pass 2 must stay trivial: `mv` on the same filesystem is effectively
  atomic per file; do not add fallible logic (parsing, network, python)
  to the commit pass. Keep temp files **next to their destinations**
  (same directory, e.g. `<dest>.tmp`) — a temp dir on another mount
  turns `mv` into a fallible copy+delete.
- If pass 2 can still fail for environmental reasons (permissions, disk
  full), the window is at least reduced to that pass — and the staged
  temps make recovery inspectable instead of silent.
