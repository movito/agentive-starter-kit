# Context Archive

Frozen session artifacts for tasks that have reached a terminal folder
(`.kit/tasks/5-done/`, `6-canceled/`, `7-blocked/`, `8-archive/`), plus
dated one-off session records that predate the task-ID convention.

Established by KIT-0077 to make `.kit/context/`'s flat listing legible:
live coordination files stay one level up, finished work moves here.

## What lives here

| Pattern | What it is |
|---|---|
| `<TASK-ID>-HANDOFF-*.md` | Planner → implementer briefs |
| `<TASK-ID>-REVIEW-STARTER.md` | Implementer → reviewer summaries |
| `<TASK-ID>-TASK-STARTER.md` | Task dispatch records |
| `<TASK-ID>-SESSION-*.md`, `*-INVENTORY.md`, `*-SPIKE-*.md` | Session one-offs |
| `YYYY-MM-DD-*.md` | Dated session handovers and early records |

## Rules

- **Read-only.** These are historical evidence. Read them for precedent;
  never edit them to match a later reality. A path cited here that has
  since moved is a fact about when the file was written, not a bug.
- **Not a deletion queue.** Files move here to be kept, not to age out.
- **Excluded from new-project exports** — `scripts/local/engine-export.sh`
  drops this directory so consumers start clean.

## Adding to it

When a task reaches a terminal folder, move its flat `.kit/context/`
artifacts here:

```bash
git mv .kit/context/<TASK-ID>-*.md .kit/context/archive/
```

Leave the current task's own handoff in the flat listing until the task
itself is done.
