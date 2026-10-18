---
description: RPI phase 3 - implement an approved plan
argument-hint: <task slug>
---

Implement phase for: $ARGUMENTS

Read the approved `docs/work/<task-slug>/plan.md` and execute it exactly. If scope grows or the plan is wrong, stop and tell the user instead of improvising.

If a step touches `.py` files, read `.agents/skills/python-standards/SKILL.md` first and follow it.

Work one plan step at a time. After each step: report what changed and how it was verified, then STOP and wait for the user's explicit approval. Only after approval, commit that step's changes (stage specific files, imperative message, attribution line), including ticking the matching items in `TASKS.md` in that same commit, then move to the next step.

Then: run `npm run lint` and `npm run build` (and tests if present; if `scripts/` changed, also `scripts/.venv/bin/python -m unittest discover scripts/tests`), invoke the `code-reviewer` agent on the diff and address its findings, and tick the matching items in `TASKS.md`. Report any deviations from the plan.
