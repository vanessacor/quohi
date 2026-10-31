# Milestone 7 plan: Summaries & Images

Based on the approved `research.md`. Decisions from the user: they install Ollama; `summary` replaces `description` in the UI when present; the prompt keeps the 50-100 word target and validation accepts 30-120 words. No ADR needed (ADR-008 and ADR-009 already cover this; the validation range is an implementation detail inside the script).

Timebox: ~2.5h (extra budget). If a step overruns by 50%, stop and reassess.

## Files

Create:
- `scripts/generate_summaries.py`
- `scripts/tests/test_generate_summaries.py`

Change:
- `src/components/EventDetails/EventDetails.tsx` and `.module.css`
- `src/data/events.json` (generated `summary` values, after user review)
- `docs/business-rules.md` (UI rule: summary over description, image only with attribution) if not already stated
- `TASKS.md` (tick items)

No change to `types/event.ts`, `parseEvents` or the map adapter.

## Steps

Each step is stopped, reported and committed after approval (RPI rules).

### Step 1: Install Ollama + Qwen3 4B [20m] (user runs the commands)
- User runs `! curl -fsSL https://ollama.com/install.sh | sh` and `! ollama pull qwen3:4b`.
- I verify `ollama list` and a one-shot `/api/chat` smoke call with `think: false`, and note the tokens/second on this CPU.
- Commit: tick the TASKS.md item (hardware check + install). No code.

### Step 2: `scripts/generate_summaries.py` + tests [75m]
- Reads `src/data/events.json`; for each event builds a prompt from `title` + `description` (the Wikipedia extract) only.
- Prompt v1 (`PROMPT_VERSION = 1`): use only the supplied text; 50-100 words; no invented facts; keep uncertainty ("possibly", "traditionally"); if the text is not enough reply exactly `INSUFFICIENT_INFORMATION`.
- Ollama call via `requests` to `http://localhost:11434/api/chat`, `stream: false`, low temperature, fixed seed. Strip any `<think>...</think>` defensively (the instruct model should not emit one).
- Validation (pure function): non-empty, not the marker, 30-120 words, no leftover markdown or lists. Invalid output is not written; it is logged and reported at the end.
- Cache in `scripts/.cache/summaries.json` keyed by QID, storing a hash of (extract, prompt version, model), the summary, model, prompt version and status. Unchanged events are skipped.
- Flags: `--only QID` (repeatable), `--limit N` for sampling, `--model` (default `qwen3:4b-instruct`), `--force`.
- Writes `summary` back into `events.json` (formatting identical to the exporter) only for valid results. Events with an `INSUFFICIENT_INFORMATION` or invalid result keep no `summary`.
- Fails with a clear message if Ollama is not reachable or the model is missing.
- Follows the `python-standards` skill (typing, small functions, constants, no network in tests).
- Tests (Ollama call mocked): prompt contains title and extract; validation (empty, marker, too short, too long, think-block stripping); cache hit skips the call, changed extract or prompt version regenerates; `--only` selection; JSON write keeps other fields untouched.
- Commit: script + tests + TASKS tick.

### Step 3: Run on all events and user review [~15m + user time]
- Run the script on a sample first (`--limit 3`), show the output to the user, adjust the prompt if needed (bump `PROMPT_VERSION`), then run on all 16.
- User reviews a sample of the summaries (ADR-008 requirement) and says which to keep, regenerate or drop.
- Commit: updated `events.json` after approval.

### Step 4: EventDetails: summary, image, sources [45m]
- Body: `event.summary ?? event.description`. When the summary is shown, add a small "AI-generated summary" note.
- Image: shown only when `event.image?.attribution` exists. A `<figure>` with fixed aspect-ratio box (no layout shift), `loading="lazy"`, `alt` = event title, caption "Photo: {attribution}, {license}" (license omitted if missing). `onError` hides the figure via state; the figure is keyed by `event.id` so state resets on selection change (no effect needed).
- Sources: list of links "Wikipedia" and "Wikidata" when present, `target="_blank"` + `rel="noopener noreferrer"`.
- CSS Modules using only tokens from `src/variables.css`. Must work in the desktop sidebar, the mobile full-screen drawer, and light/dark.
- Keep the component under ~120 lines; if it grows, extract a small `EventImage` component in the same folder.
- Commit: component + CSS + TASKS tick.

### Step 5: Verify missing optional fields [15m]
- Manual check with `npm run dev` (via the `run` skill if useful) using temporary edits to the data (reverted, not committed): event without image, image without attribution, broken image URL, without summary, without sources, without every optional field.
- Check real data: the 2 events without an image, the rest with.
- Run `npm run lint`, `npm run typecheck`, `npm test`, `npm run build`, `npm run format`; Python tests.
- Run the `code-reviewer` agent on the full milestone diff and address findings.
- Commit: fixes (if any) + TASKS tick of the last item and the milestone.

## Risks
- CPU-only generation is slow; sample first (`--limit 3`) before the full run.
- A 4B model may pad or invent; the review in step 3 and the Wikipedia link are the safeguards. If quality is poor, fallback per ADR-008: try a larger model or skip summaries (UI already falls back to `description`).
- Images are remote Wikimedia thumbnails; offline or blocked loads are covered by the `onError` fallback.
