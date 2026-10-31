# Milestone 7 research: Summaries & Images

Scope: ADR-008 (local AI summaries), ADR-009 (optional fields). No code changed.

## Current state

- `src/data/events.json`: 16 events. All 16 have `sources`, 14 have `image` (with attribution and license), 0 have `summary`.
- `description` is a Wikipedia extract already trimmed by `enrich_events.py` (max 3 sentences / 500 chars). This is the model input.
- `EventDetails` (replaced the old side panel in Milestone 6) shows title, date and `description` only. It ignores `summary`, `image` and `sources`.
- `HistoricalEvent`, `parseEvents` and tests already support the optional fields (Milestone 5).
- `scripts/` has `common.py`, `fetch_events.py`, `enrich_events.py`, `config/`, `tests/`, and a venv `requirements.txt` (only `requests`). Python follows the `python-standards` skill.
- `enrich_events.py` regenerates `events.json` from scratch, so a summary stored only in `events.json` would be lost on re-export (see Unknowns).

## Hardware check (task 1)

| Item | Machine | `qwen3:4b` (Q4_K_M) needs |
|---|---|---|
| RAM | 15 GiB total, ~8 GiB available | ~2.6 GB weights + context, ~4 GB total |
| GPU | none (NVIDIA driver not running) | optional |
| CPU | 12 cores | CPU inference works |
| Disk | 32 GB free | ~2.6 GB |

Verdict: it fits. CPU-only will be slow (roughly 5-10 tokens/s), but 16 events x ~150 output tokens is a few minutes in total, once. Ollama is not installed (`ollama: command not found`). Installing it is a system-level change (install script + a service), so the user should run it (`! curl -fsSL https://ollama.com/install.sh | sh`, then `ollama pull qwen3:4b`).

Qwen3 defaults to "thinking" mode, which emits a long reasoning block first. On CPU that multiplies the time. The script should disable it (`think: false` in the Ollama `/api/chat` request, or `/no_think`) and strip any `<think>` block defensively.

## Constraints

- Summary is generated at data-prep time only; the site never calls a model (ADR-008).
- Prompt: only the supplied extract, 50-100 words, no invented facts, uncertainty preserved, explicit "insufficient information" answer. Validate length, non-empty, not the marker. Cache so unchanged events are not regenerated. Model name, prompt version and status live in the script cache, not in the site schema.
- A person reviews a sample before commit. The panel always links to the source article.
- Image shown only when it has attribution; a missing or failed image must not break the panel (ADR-009). Remote thumbnails, never embedded.
- No new schema fields without an ADR. No runtime external APIs (the image `<img>` loading a Wikimedia thumbnail is already the accepted ADR-009 design).
- Dependencies: the script talks to Ollama over HTTP; `requests` is already enough, no new package.
- Source extract is a ~500 char excerpt, so a 50-100 word summary is nearly as long as the input. See Option B in Open questions.

## Unknowns / open questions

1. **Where the summary lives so it survives re-export.** `enrich_events.py` overwrites `events.json`.
   - A. `generate_summaries.py` reads `events.json`, writes `summary` back into it. Simple, but re-running `enrich_events.py` drops summaries until the generator runs again (the cache makes that cheap and deterministic, since inputs are unchanged).
   - B. Also make `enrich_events.py` merge `summary` from the cache. More coupling.
   - Recommendation: A. The cache keyed by QID + hash of (extract, prompt version, model) makes re-running the generator free. Document the run order: fetch, enrich, summaries.
2. **Summary vs description in the UI.** Summary is meant to make events "more readable". Recommendation: show `summary` as the body when present, else `description`. Show both would be redundant on a 500-char extract. Marked as AI-generated with a small label, followed by the Wikipedia link.
3. **Summary length vs input.** 50-100 words from a ~500 char (~80 word) extract is a rewrite, not a compression. Options: keep ADR-008 as written, or loosen the range to e.g. 40-80 words. Changing it needs the user's decision (ADR-008 is accepted). Recommendation: keep 50-100 in the prompt but validate against a wider hard range (30-120) so a good short answer is not rejected; flag to the user if the model tends to pad.
4. **Image placement and sizing** inside the sidebar details card (narrow column, scrolling area, mobile full-screen drawer). Needs a fixed aspect ratio box to avoid layout shift, `loading="lazy"`, `alt` from the title, `onError` to hide the figure. 2 events have no image, so the fallback path is exercised by real data.
5. **Attribution text format.** Data has `attribution` (author, may contain HTML-stripped text) and `license`. Show "Photo: {attribution}, {license}" under the image. Licence has no URL in the schema, so it is plain text.

## Options for the UI work (task 3)

- **Option 1 (recommended):** extend `EventDetails` only: image figure (with caption) between date and body, body = summary or description, an "AI-generated summary" note when `summary` is used, and a sources list (Wikipedia, Wikidata links, `rel="noopener noreferrer"`, `target="_blank"`). Small child components are not needed; keep it in one file unless it grows past ~120 lines.
- Option 2: split into `EventImage` and `EventSources` components. More files for little reuse; defer.

Image fallback: a small state flag (`useState` reset on event change, keyed by `event.id`) hides the figure on error. Using `key={event.id}` on the figure resets state without an effect.

## Testing

- Python: unit tests in `scripts/tests/` for prompt building, output validation (length, empty, marker, `<think>` stripping) and cache key logic, with the Ollama call mocked. No network in tests.
- TS: no logic worth a Vitest unit beyond the component; manual check via `npm run dev` for: event with image, without image, broken image URL, with and without `summary`, without `sources`. Component tests are not set up in this repo, so verification stays manual unless the user wants a test harness (out of scope).

## Recommendation and rough plan shape

1. User installs Ollama and pulls `qwen3:4b` (hardware OK, CPU-only).
2. `scripts/generate_summaries.py`: prompt v1, `think: false`, temperature low, validation, QID + hash cache in `scripts/.cache/`, `--limit`/`--only QID` flags for sampling, writes `summary` into `events.json`; unit tests.
3. User reviews a sample of the summaries (ADR-008 requirement) before commit.
4. `EventDetails`: image + attribution + fallback, summary/description body, source links, CSS using only tokens.
5. Verify optional fields missing, broken image URL, light/dark, mobile drawer.
6. No ADR needed unless the summary length range (question 3) is changed.

Timebox stays at ~2.5h; the only schedule risk is CPU generation speed and prompt iteration on a 4B model.

## Decisions needed from the user

- Install Ollama yourself (needs `sudo`), or skip summaries and ship images + links only (ADR-008 fallback)?
- Body text: replace `description` with `summary` when present (recommended), or show both?
- Keep the 50-100 word target as is (recommended, with a wider hard validation range)?
