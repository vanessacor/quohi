# ADR-008: Local AI summaries with Ollama + Qwen3

- Status: Accepted
- Date: 2026-10-18
- Depends on: ADR-007

## Context
`notes/wiki-plan.md` proposes short AI summaries to make events more readable, without paying for a hosted API or adding a backend.

## Decision
- Summaries are generated **at data-preparation time**, by a local script (`scripts/generate_summaries.py`) calling Ollama with a Qwen3 model (`qwen3:4b-instruct`). The site never calls a model.
- The prompt restricts the model to the supplied Wikipedia extract: 50-100 words, no invented facts, uncertainty preserved, and an explicit "insufficient information" answer.
- Output is validated (length, non-empty, not the "insufficient" marker) and cached so unchanged events are not regenerated.
- The result is stored in the event's optional `summary` field. Model name, prompt version and generation status live in the script's cache, not in the site schema.
- A person reviews a sample of summaries before they are committed. The panel always links to the source article.
- Hardware requirements for the chosen model are checked before installing; a smaller model or skipping summaries is the fallback.

## Amendment (Milestone 7)
`qwen3:4b` was tried first. On Ollama 0.40.13 it ignores `think: false` and `/no_think` and puts its reasoning into the response (~350 tokens, ~45 s per call on CPU). The user switched to `qwen3:4b-instruct`, which has no thinking mode and answers in seconds with the same hardware needs (~2.5 GB).

## Consequences
- No runtime AI cost, latency or infrastructure
- Summaries can still contain errors, so review and the source link are required
- Needs a developer machine able to run the model
