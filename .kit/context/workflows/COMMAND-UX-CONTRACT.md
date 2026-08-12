# The Command UX Contract

**Origin**: KIT-0101 (operator findings F7/F9/F10, live cold-start use,
2026-08-11). This is the single authority for how user-invocable
commands present themselves. Command bodies carry their own concrete
header (they are self-contained — plugin copies must not depend on
this file existing downstream); this doc defines the pattern they
instantiate.

## 1. The transparency header (R1 / F7)

Every **user-invocable** command (everything in `.claude/commands/`)
instructs its executing agent to open its FIRST response with a
transparency header — before any other output or tool call. Skills
with `user-invocable: false` are internal machinery and are out of
scope.

The format, exactly three lines in one blockquote:

```markdown
> 🧭 `/<name>` — <one line: what this command does>.
> Reads: <what it reads, where> · Writes: <what it writes, where — or "nothing">
> Source: [<name>.md](<kit GitHub URL>) · Docs: [<page>](<kit GitHub URL>)
```

Binding rules:

- **Truthful at print time**: the Reads/Writes line names the real
  surfaces the command touches — a displayed fact is a claim
  (the `displayed_commands_are_contracts` rule).
- **Writes: nothing** is stated explicitly for read-only commands —
  silence about writes is what the header exists to end.
- **The Docs link** points at the most relevant explainer page; where
  no genuinely relevant page exists, the Source link alone is
  acceptable (never link a page just to fill the slot).

### The dual-home link decision (recorded once, here)

Twelve of the fourteen commands ship to consumers via the
`agentive-workflow` plugin; two (`/new-project`, `/setup-preset`) are
kit-side only. (A command whose frontmatter says `distribution:
builder-only` — or, in older wording, "not distributed via the
manifest" — can still ship in the plugin; `/wrap-up` does. The manifest
that wording referred to was retired in KIT-0102.)
**All Source links point at the kit canonical**
(`https://github.com/movito/agentive-starter-kit/blob/main/...`),
never at the marketplace copy. Why:

1. The marketplace file is a *derived artifact* — regenerated and
   namespace-transformed every release, so deep links to it rot or
   point mid-transform.
2. The kit file is the body both homes share; its history and issues
   live in the kit repo.
3. Two commands have no marketplace copy at all — one URL scheme
   covers the whole set, and the kit→marketplace refresh needs no
   per-release link rewriting.

## 2. Session hops: collapse or give the live reason (R2 / F9)

Any instruction that sends the operator to a new session/tab must
either be **collapsed** (the current session does the work inline) or
**kept with a one-sentence reason stated in the text**. The two live
reasons:

- **Agent identity is fixed at session launch** — the current session
  cannot become another agent mid-flight.
- **A different contract needs fresh context** — the new role must not
  inherit this session's working state.

The launcher-era rationale (persona fragility) died with native
`--agent` support — never cite it. A bare "open a new session with
X" with no reason is a defect.

## 3. The completion contract (R3 / F10)

A flow's completion summary is ONE checklist ending in ONE command
(format operator-specified, KIT-0100 §F10):

- every ✓ line is a claim **verified at print time**, never assumed;
- anything outstanding appears **in the same list** as ✗ with the
  exact remedy command — "done" and "still needed" never contradict
  across two messages;
- the single closing launch command carries its opening prompt (a
  session cannot speak first) and is printed **only when the doctor
  has no FAILs** — otherwise the last line is the re-run instruction.

Implemented in: `project-intake` Step 5 and the setup door's tail
(`scripts/local/bootstrap` — contract strings pinned by
`tests/test_scaffold_acceptance.py`).
