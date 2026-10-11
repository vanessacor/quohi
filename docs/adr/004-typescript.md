# ADR-004: Use TypeScript

- Status: Accepted
- Date: 2026-10-11
- Amends: ADR-003 (stack was React + Vite without a language choice)

## Context
The project relies on a single unified event schema and, per ADR-005, a library-agnostic map interface. Both are contracts that benefit from static checking, and later phases (AI-generated data) will need schema-compliant events.

## Decision
Use TypeScript with the Vite `react-ts` template (TypeScript 6, strict mode on by default). Source files are `.ts`/`.tsx`. `npm run typecheck` (`tsc -b`) must pass alongside lint and build.

## Consequences
- Event schema and map types are enforced at compile time
- `any` is not used; implicit `any` is a compile error
- Slightly more setup and typing effort than plain JavaScript
- The event JSON file is not type-checked at runtime; Milestone 2 adds a validation util for that
