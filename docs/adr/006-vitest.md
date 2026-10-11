# ADR-006: Vitest for unit tests

- Status: Accepted
- Date: 2026-10-11

## Context
`docs/code-standards.md` requires unit tests for functions in `utils/`. The first real logic (the event validator) arrives in Milestone 2, earlier than the filter tests originally planned for Milestone 4. The project already uses Vite, and no test runner was installed.

## Decision
Use Vitest, pinned to an exact version, run with `npm test` (`vitest run`). Configuration lives in `vite.config.ts` (imported from `vitest/config`) with the `node` environment. Tests sit next to the code as `*.test.ts`. Tests import `describe`, `it` and `expect` from `vitest` explicitly (no globals).

## Consequences
- Tests share Vite's config and TypeScript setup, so there is no separate toolchain
- The `node` environment is enough for pure functions; component tests would need a DOM environment, which is a later decision
- One more dev dependency to keep pinned and updated
