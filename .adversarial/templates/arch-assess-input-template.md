# Architectural Assessment: [Project Name] — [Component Being Built]

## Context

[1-2 sentences: what the project is, what stage it's at]

## What Exists: Current Architecture

### Package Structure

```text
[Directory tree with brief annotations]
```

### Module APIs (signatures only)

#### Module 1: `path/to/module.py`

```python
[Public API signatures with brief comments — no implementation bodies]
[Include: class definitions, public methods, key functions]
[Exclude: private methods, implementation details]
```

**Dependencies**: [list internal and external deps]

#### Module 2: ...

[Repeat for each relevant module]

### Dependency Graph

```text
[ASCII diagram showing module dependencies]
[Arrow direction: A ←── B means "B depends on A"]
```

[One sentence summarizing the dependency structure]

---

## What's Planned: Upcoming Work

### Task: [TASK-ID] — [Task Title]

**Goal**: [What this task accomplishes in 1-2 sentences]

### Planned Structure

```text
[Directory tree showing new files to be created]
```

### Planned API

```python
[Proposed public API signatures for new code]
[Include: new classes, functions, entry points]
```

### Integration Points

- New code will import: [which existing modules]
- New code will be imported by: [which future modules, if known]
- New external dependencies: [any new pip packages]
- Entry point: [if applicable, e.g., console_script]

### Future Context

[Brief note on what comes after this task — what will build on top of this work]

---

## Key Questions for the Assessor

1. [Specific question about integration approach]
2. [Specific question about boundary placement]
3. [Any other architectural concerns]
