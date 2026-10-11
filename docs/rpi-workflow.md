# Research -> Plan -> Implement (RPI)

Every non-trivial task moves through three phases. Each phase writes a short artifact to `docs/work/<task-slug>/` and **stops for user approval** before the next.

## 1. Research (`/research <task>`)
- Read relevant code and docs (PRD, TRD, ADRs, standards)
- Identify constraints, unknowns, and options
- Output: `research.md` (findings, options, recommendation). No code changes.

## 2. Plan (`/plan <task>`)
- Based on approved research
- Output: `plan.md` with files to change, ordered steps, tests, and a timebox
- Flag anything that needs an ADR. The user makes architecture decisions.

## 3. Implement (`/implement <task>`)
- Execute the approved plan only; note deviations
- Work one plan step at a time: after each step, stop and report, wait for the user's approval, then commit that step's changes before starting the next
- Run lint/tests/build
- Run the `code-reviewer` agent on the diff and address findings
- Tick the matching items in `TASKS.md`

## Rules
- Small tasks (typo, single-line fix) may skip RPI
- If scope grows during implementation, stop and return to Plan
