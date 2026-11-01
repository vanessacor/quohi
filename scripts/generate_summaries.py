"""Generates short event summaries with a local Ollama model (ADR-008, ADR-009).

Run from the repository root, after `enrich_events.py`:

    scripts/.venv/bin/python scripts/generate_summaries.py [--only QID] [--limit N] [--force]

Reads `src/data/events.json`, asks the model to rewrite each event's Wikipedia
extract (`description`) as a 50-100 word summary, and writes valid results back
as the optional `summary` field. Results are cached in `scripts/.cache/summaries.json`
so unchanged events are not regenerated. Requires `ollama serve` and the model
pulled (`ollama pull qwen3:4b-instruct`).
"""

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Callable

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import load_scope  # noqa: E402

SCRIPTS_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPTS_DIR.parent
EVENTS_PATH = REPO_ROOT / "src" / "data" / "events.json"
CACHE_PATH = SCRIPTS_DIR / ".cache" / "summaries.json"

OLLAMA_URL = "http://localhost:11434"
DEFAULT_MODEL = "qwen3:4b-instruct"
# Bump when the prompt changes so cached summaries are regenerated.
PROMPT_VERSION = 3
TEMPERATURE = 0.2
SEED = 1
MAX_OUTPUT_TOKENS = 300
# CPU inference is slow; a single call can take a minute.
TIMEOUT_SECONDS = 300

INSUFFICIENT_MARKER = "INSUFFICIENT_INFORMATION"
# The prompt asks for 50-100 words; a good shorter or longer answer is not rejected (ADR-008).
MIN_WORDS = 30
MAX_WORDS = 120

STATUS_OK = "ok"
STATUS_INSUFFICIENT = "insufficient"

# A summary containing a run of this many extract words in a row is a copy, not a rewrite.
COPIED_RUN_WORDS = 8

THINK_END = "</think>"
LIST_OR_HEADING = re.compile(r"^\s*(?:[-*#>]|\d+[.)])\s", re.MULTILINE)

PROMPT_TEMPLATE = """You write short summaries of historical events for a map of {city}.

Use ONLY the text between the markers. Do not add facts, dates, names or numbers that are not in it.
Keep any uncertainty the text expresses (for example "traditionally", "possibly", "around").
Rewrite it in your own words for a general reader, in simpler and more direct sentences. Do not copy sentences from the text.
Prefer concrete facts from the text (who, what, where, when) over general praise. Do not add vague filler sentences such as "it remains one of the most famous" or "a bright time for many people".
Copy every number, date and time span exactly as the text gives it. Never convert, estimate or compute a time span (for example "years ago") yourself.
Write 50 to 100 words of plain prose in one paragraph: no title, list, markdown or quotation marks.
If the text does not contain enough information for a summary, reply with exactly {marker}.

Title: {title}

--- TEXT ---
{extract}
--- END TEXT ---"""


class OllamaError(RuntimeError):
    """Ollama is unreachable, the model is missing, or the reply is malformed."""


Chat = Callable[[str], str]


def build_prompt(event: dict, city: str) -> str:
    """The constrained prompt for one event, built from its title and Wikipedia extract only."""
    return PROMPT_TEMPLATE.format(
        city=city,
        marker=INSUFFICIENT_MARKER,
        title=event["title"],
        extract=event["description"],
    )


def clean_output(raw: str) -> str:
    """The model's answer without any reasoning block before a closing `</think>` tag."""
    return raw.rsplit(THINK_END, 1)[-1].strip()


def copies_extract(summary: str, extract: str) -> bool:
    """Whether `summary` repeats a run of `COPIED_RUN_WORDS` or more words of `extract` verbatim."""
    words = extract.split()
    summary_text = " ".join(summary.split())
    return any(
        " ".join(words[start : start + COPIED_RUN_WORDS]) in summary_text
        for start in range(len(words) - COPIED_RUN_WORDS + 1)
    )


def summary_problem(text: str, extract: str = "") -> str | None:
    """Why `text` is not usable as a summary, or None when it is valid."""
    if not text:
        return "empty output"
    if text == INSUFFICIENT_MARKER:
        return "model reported insufficient information"
    if INSUFFICIENT_MARKER in text:
        return "output mentions the insufficient-information marker"
    if "<think>" in text or THINK_END in text:
        return "output contains reasoning tags"
    if LIST_OR_HEADING.search(text) or "**" in text:
        return "output contains markdown"
    words = len(text.split())
    if not MIN_WORDS <= words <= MAX_WORDS:
        return f"{words} words (allowed {MIN_WORDS}-{MAX_WORDS})"
    if copies_extract(text, extract):
        return "output copies the extract instead of rewriting it"
    return None


def input_hash(event: dict, model: str) -> str:
    """Identifies what a summary was generated from; any change invalidates the cached one."""
    parts = [model, str(PROMPT_VERSION), event["title"], event["description"]]
    return hashlib.sha256("\n".join(parts).encode("utf-8")).hexdigest()


def load_cache(path: Path = CACHE_PATH) -> dict[str, dict]:
    """Loads the summary cache keyed by QID; empty when it does not exist yet."""
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        print(f"Warning: {path} is not valid JSON; starting with an empty cache")
        return {}


def save_cache(cache: dict[str, dict], path: Path = CACHE_PATH) -> None:
    """Writes the summary cache."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")


def ollama_chat(model: str, prompt: str) -> str:
    """One non-streaming chat call to the local Ollama server; returns the reply text."""
    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/chat",
            json={
                "model": model,
                "stream": False,
                "messages": [{"role": "user", "content": prompt}],
                "options": {
                    "temperature": TEMPERATURE,
                    "seed": SEED,
                    "num_predict": MAX_OUTPUT_TOKENS,
                },
            },
            timeout=TIMEOUT_SECONDS,
        )
    except requests.ConnectionError as error:
        raise OllamaError(f"Ollama is not reachable at {OLLAMA_URL}; run `ollama serve`") from error
    except requests.Timeout as error:
        raise OllamaError(f"Ollama did not answer within {TIMEOUT_SECONDS}s") from error
    except requests.RequestException as error:
        raise OllamaError(f"Ollama request failed: {error}") from error
    if response.status_code == 404:
        raise OllamaError(f"Model {model!r} not found; run `ollama pull {model}`")
    if not response.ok:
        raise OllamaError(f"Ollama returned HTTP {response.status_code}: {response.text[:200]}")
    try:
        return response.json()["message"]["content"]
    except (KeyError, ValueError) as error:
        raise OllamaError(f"Unexpected Ollama reply: {response.text[:200]}") from error


def process_event(
    event: dict, cache: dict[str, dict], model: str, chat: Chat, city: str, force: bool
) -> tuple[str | None, str]:
    """Returns the summary (or None) and how it was obtained; updates `cache` in place.

    Outcomes: `cached`, `generated`, `insufficient`, `skipped: ...` or `invalid: <reason>`.
    Invalid results are not cached, so the next run tries again. An event without a
    source link gets no summary: AI text must appear next to a source (business rules).
    """
    if not any((event.get("sources") or {}).values()):
        return None, "skipped: no source link"
    key = input_hash(event, model)
    entry = cache.get(event["id"])
    if entry and entry["input_hash"] == key and not force:
        return entry.get("summary"), "cached"

    text = clean_output(chat(build_prompt(event, city)))
    problem = summary_problem(text, event["description"])
    if text == INSUFFICIENT_MARKER:
        cache[event["id"]] = {"input_hash": key, "model": model, "status": STATUS_INSUFFICIENT}
        return None, "insufficient"
    if problem:
        return None, f"invalid: {problem}"
    cache[event["id"]] = {
        "input_hash": key,
        "model": model,
        "prompt_version": PROMPT_VERSION,
        "status": STATUS_OK,
        "summary": text,
    }
    return text, "generated"


def with_summary(event: dict, summary: str | None) -> dict:
    """A copy of `event` whose `summary` is set (placed after `description`) or removed."""
    updated: dict = {}
    for field, value in event.items():
        if field == "summary":
            continue
        updated[field] = value
        if field == "description" and summary:
            updated["summary"] = summary
    return updated


def select_events(events: list[dict], only: list[str] | None, limit: int | None) -> list[dict]:
    """The events to process: those named by `only` (all when empty), then the first `limit`."""
    selected = [event for event in events if not only or event["id"] in only]
    return selected[:limit] if limit else selected


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--only", action="append", metavar="QID", help="only this event (repeatable)")
    parser.add_argument("--limit", type=int, metavar="N", help="only the first N events")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--force", action="store_true", help="ignore the cache")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    events = json.loads(EVENTS_PATH.read_text(encoding="utf-8"))
    selected_ids = {event["id"] for event in select_events(events, args.only, args.limit)}
    cache = load_cache()
    city = load_scope()["city"]["name"]

    def chat(prompt: str) -> str:
        return ollama_chat(args.model, prompt)

    updated = []
    invalid = []
    for event in events:
        if event["id"] not in selected_ids:
            updated.append(event)
            continue
        summary, outcome = process_event(event, cache, args.model, chat, city, args.force)
        updated.append(with_summary(event, summary))
        print(f"  {event['id']}: {event['title']} - {outcome}")
        if outcome.startswith("invalid"):
            invalid.append(event["id"])
        save_cache(cache)

    EVENTS_PATH.write_text(json.dumps(updated, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    with_text = sum("summary" in event for event in updated)
    print(f"\n{with_text}/{len(updated)} events have a summary in {EVENTS_PATH}")
    if invalid:
        print(f"Invalid output, no summary written: {', '.join(invalid)}")
    return 1 if invalid else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except OllamaError as error:
        sys.exit(f"error: {error}")
