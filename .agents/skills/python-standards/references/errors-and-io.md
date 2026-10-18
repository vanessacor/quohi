# Errors, network and I/O

## Errors
- Raise specific exceptions. Subclass a built-in when the failure is domain-specific
  (`class WikidataDateError(ValueError)`), and give the message the offending value.
- Never use a bare `except:`. Catch the narrowest exception you can handle;
  let everything else fail loudly. These are developer tools, so a clear
  traceback beats silent recovery.
- Invalid or unusable data (coarse dates, missing coordinates) is skipped
  explicitly with a reason, not silently dropped. Report what was skipped.
- Use context managers (`with`) for files and sessions.

## Network (Wikimedia APIs, ADR-007)
- Go through the helpers in `common.py` (`build_session`, `fetch_json`): they set
  the identifiable User-Agent, the request delay, the timeout and the cache.
- Keep requests few and sequential. Cache responses under `scripts/.cache` so a
  re-run makes no network calls.
- Always set a timeout. Never call external APIs from anything the frontend loads.

## Output
- `print()` is fine for progress and summaries (current scripts do this); do not
  introduce `logging` configuration for this scale.
- Write JSON with `ensure_ascii=False, indent=2` (as the current scripts do),
  so diffs of `events.json` stay readable.
- Validate against the event schema before writing `src/data/events.json`;
  enforce the 20-event cap.
