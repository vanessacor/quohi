---
name: python-standards
description: Python conventions for the local data-prep scripts in scripts/ (Wikidata/Wikipedia fetching, enrichment, Ollama summaries, events.json export). Use whenever writing, editing, refactoring, testing or reviewing any .py file in this repo, or adding a script or test under scripts/, even for small changes.
---

# Python standards (data-prep scripts)

Python here is build-time tooling only (ADR-007): offline scripts in `scripts/`
that produce `src/data/events.json`. They are never deployed. Keep them simple;
the project's MVP rules (simplicity, timebox, no new tooling without an ADR) apply.

**Existing code is the style reference.** Read `scripts/common.py` before writing
new code and match it. If this skill and the surrounding code disagree, follow the code.

## Always apply

- PEP 8: 4 spaces, `snake_case` functions/variables, `PascalCase` classes,
  `UPPER_CASE` constants, `_private` helpers. Imports in three groups
  (stdlib, third-party, local), no wildcard imports.
- Type hints on all function signatures, built-in generics (`list[str]`,
  `dict[str, Any]`) and `X | None`, not `Optional`.
- Every module and public function has a docstring. Match the repo's prose
  style: one summary line in the third person ("Parses ..."), then a short
  paragraph only when the *why* is not obvious. No Args/Returns boilerplate.
- Comments explain why (a Wikidata quirk, an API policy), not what.
- Single responsibility: separate fetching, parsing and writing so the parsing
  can be tested without the network.
- Name magic numbers as constants (`TIMEOUT_SECONDS`, `MAX_EVENTS`).
- Use `pathlib.Path`, not string paths. Derive paths from `__file__`, never the cwd.
- Dependencies go in `scripts/requirements.txt`; use the `scripts/.venv` virtualenv.
  Do not add new tools (formatters, type checkers, `pyproject.toml`) without an ADR.

## Load on demand

Read only the file that matches the task:

| Task | Read |
|---|---|
| Writing or changing tests | `references/testing.md` |
| Network calls, file I/O, error handling, output | `references/errors-and-io.md` |
| Creating a new script or restructuring one | `references/script-structure.md` |

## Before finishing

Run the tests: `scripts/.venv/bin/python -m unittest discover scripts/tests`
