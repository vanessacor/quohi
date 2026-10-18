"""Enriches curated QIDs with Wikipedia content and exports events.json (ADR-007, ADR-009).

Run from the repository root:

    scripts/.venv/bin/python scripts/enrich_events.py

Reads `scripts/config/curated.json`, fetches Wikipedia extracts/images for each QID,
merges with Wikidata data (dates, coordinates) and writes `src/data/events.json`
(capped at 20 events).
"""

import html
import json
import re
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit, urlunsplit

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import (  # noqa: E402
    BIRTH_DATE_PROPERTY,
    EVENT_DATE_PROPERTY,
    LANDMARK_DATE_PROPERTY,
    WikidataDateError,
    build_session,
    fetch_json,
    format_date,
    in_bounds,
    load_scope,
    parse_wikidata_time,
    select_date,
)

SCRIPTS_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPTS_DIR.parent
CURATED_PATH = SCRIPTS_DIR / "config" / "curated.json"
CANDIDATES_PATH = SCRIPTS_DIR / ".cache" / "candidates.json"
OUTPUT_PATH = REPO_ROOT / "src" / "data" / "events.json"

USER_AGENT = (
    "HistoricalEventsMap/0.1 (local data-prep script; "
    "contact: vanessapcbarros@gmail.com)"
)
WIKIPEDIA_API = "https://en.wikipedia.org/w/api.php"
WIKIDATA_API = "https://www.wikidata.org/w/api.php"
COMMONS_API = "https://commons.wikimedia.org/w/api.php"
CACHE_DIR = SCRIPTS_DIR / ".cache"
ENTITY_BATCH_SIZE = 50
WIKIPEDIA_BATCH_SIZE = 50
COMMONS_BATCH_SIZE = 50
THUMBNAIL_WIDTH = 640

MAX_EVENTS = 20
MAX_SUMMARY_SENTENCES = 3
MAX_SUMMARY_CHARS = 500

CJK_PARENTHETICAL = re.compile(r"\s*\([^()]*[\u3400-\u9fff][^()]*\)")
EMPTY_PARENTHETICAL = re.compile(r"\s*\(\s*[;,]?\s*\)")
SENTENCE_BREAK = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9\"'])")
HTML_TAG = re.compile(r"<[^>]+>")
UNKNOWN_AUTHOR_PREFIX = "Unknown author"

POINT_IN_TIME_CLASSES = frozenset(
    {
        "Q178561",  # battle
        "Q180684",  # military conflict
        "Q12890393",  # incident
        "Q511866",  # mutiny
        "Q188165",  # war
        "Q3983889",  # conflict
    }
)
HUMAN_CLASS = "Q5"


def load_curated(path: Path = CURATED_PATH) -> dict:
    """Loads the hand-picked QIDs, title overrides and manual dates."""
    return json.loads(path.read_text(encoding="utf-8"))


def manual_event_date(manual_date: dict) -> dict[str, int]:
    """The curated date as an event date; only the fields given are kept."""
    return {
        field: manual_date[field] for field in ("year", "month", "day") if field in manual_date
    }


def load_candidates(path: Path = CANDIDATES_PATH) -> dict[str, dict]:
    """Loads candidates.json into a dict by QID for fast lookup."""
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    return {item["qid"]: item for item in data}


def collect_all_qids(curated: dict) -> list[str]:
    """Collects the unique QIDs from `selected`, `extra_qids` and `title_overrides`."""
    qids = set(curated.get("selected", []))
    qids.update(curated.get("extra_qids", []))
    qids.update(qid for qid in curated.get("title_overrides", {}).values() if qid)
    return sorted(qids)


def fetch_wikidata_entities(session: requests.Session, qids: list[str]) -> dict[str, dict]:
    """Fetches claims, sitelinks, labels, coordinates for QIDs in batches."""
    entities: dict[str, dict] = {}
    for start in range(0, len(qids), ENTITY_BATCH_SIZE):
        batch = qids[start : start + ENTITY_BATCH_SIZE]
        data = fetch_json(
            session,
            WIKIDATA_API,
            {
                "action": "wbgetentities",
                "ids": "|".join(batch),
                "props": "claims|sitelinks|labels|coordinates",
                "languages": "en",
                "format": "json",
            },
            "entities",
            cache_dir=CACHE_DIR,
        )
        entities.update(data.get("entities", {}))
    return entities


def clean_extract(text: str) -> str:
    """Drops parentheticals with Chinese text, then collapses all whitespace to single spaces."""
    text = CJK_PARENTHETICAL.sub("", text)
    text = EMPTY_PARENTHETICAL.sub("", text)
    return " ".join(text.split())


def fit_sentences(text: str, limit: int = MAX_SUMMARY_CHARS) -> str:
    """Keeps whole sentences up to `limit` characters; a single longer sentence is cut at a word."""
    kept = ""
    for sentence in SENTENCE_BREAK.split(text):
        candidate = f"{kept} {sentence}".strip()
        if len(candidate) > limit:
            break
        kept = candidate
    if kept:
        return kept
    return text[:limit].rsplit(" ", 1)[0] + "…"


def thumbnail_url(url: str) -> str:
    """The thumbnail URL without the tracking query string the API appends."""
    parts = urlsplit(url)
    return urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))


def strip_markup(value: str) -> str:
    """Plain text of an HTML fragment from Commons metadata."""
    return " ".join(html.unescape(HTML_TAG.sub("", value)).split())


def image_credit(metadata: dict) -> dict[str, str] | None:
    """The author and license of a Commons file, or None when either is missing or the author is unknown."""
    artist = strip_markup(metadata.get("Artist", {}).get("value", ""))
    license_name = strip_markup(metadata.get("LicenseShortName", {}).get("value", ""))
    if not artist or artist.startswith(UNKNOWN_AUTHOR_PREFIX) or not license_name:
        return None
    return {"attribution": artist, "license": license_name}


def fetch_image_credits(
    session: requests.Session, file_names: list[str]
) -> dict[str, dict[str, str]]:
    """Fetches the credit of each Commons file, keyed by file name (underscores as spaces)."""
    credits: dict[str, dict[str, str]] = {}
    for start in range(0, len(file_names), COMMONS_BATCH_SIZE):
        batch = file_names[start : start + COMMONS_BATCH_SIZE]
        data = fetch_json(
            session,
            COMMONS_API,
            {
                "action": "query",
                "titles": "|".join(f"File:{name}" for name in batch),
                "prop": "imageinfo",
                "iiprop": "extmetadata",
                "iiextmetadatafilter": "Artist|LicenseShortName",
                "format": "json",
            },
            "commons",
            cache_dir=CACHE_DIR,
        )
        for page in data.get("query", {}).get("pages", {}).values():
            infos = page.get("imageinfo", [])
            credit = image_credit(infos[0].get("extmetadata", {})) if infos else None
            if credit:
                credits[page["title"].removeprefix("File:")] = credit
    return credits


def fetch_wikipedia_pages(
    session: requests.Session, entities: dict[str, dict]
) -> dict[str, dict]:
    """Fetches the extract, URL and credited thumbnail of the entities' English articles.

    An image without a known author and license is left out.
    """
    page_titles = {}
    for qid, entity in entities.items():
        enwiki = entity.get("sitelinks", {}).get("enwiki")
        if enwiki:
            page_titles[qid] = enwiki["title"]

    titles_list = list(page_titles.values())
    qid_by_title = {title: qid for qid, title in page_titles.items()}
    enriched: dict[str, dict] = {}
    image_files: dict[str, str] = {}

    for start in range(0, len(titles_list), WIKIPEDIA_BATCH_SIZE):
        batch_titles = titles_list[start : start + WIKIPEDIA_BATCH_SIZE]
        data = fetch_json(
            session,
            WIKIPEDIA_API,
            {
                "action": "query",
                "titles": "|".join(batch_titles),
                "prop": "extracts|info|pageimages",
                "exintro": True,
                "explaintext": True,
                "exsentences": MAX_SUMMARY_SENTENCES,
                "inprop": "url",
                "piprop": "thumbnail|name",
                "pithumbsize": THUMBNAIL_WIDTH,
                "format": "json",
            },
            "wikipedia",
            cache_dir=CACHE_DIR,
        )

        for page in data.get("query", {}).get("pages", {}).values():
            qid = qid_by_title.get(page.get("title", ""))
            if "missing" in page or not qid:
                continue
            enriched[qid] = {
                "extract": fit_sentences(clean_extract(page.get("extract", ""))),
                "wikipedia_url": page.get("fullurl", ""),
            }
            if "thumbnail" in page and "pageimage" in page:
                enriched[qid]["image_url"] = thumbnail_url(page["thumbnail"]["source"])
                image_files[qid] = page["pageimage"].replace("_", " ")

    credits = fetch_image_credits(session, sorted(set(image_files.values())))
    for qid, file_name in image_files.items():
        if file_name in credits:
            enriched[qid]["image"] = {"url": enriched[qid].pop("image_url"), **credits[file_name]}
        else:
            enriched[qid].pop("image_url")
    return enriched


def event_date(time_value: str, precision: int) -> dict[str, int] | None:
    """Converts a Wikidata time to an event date (year, month?, day?), or None if unusable."""
    try:
        parsed = parse_wikidata_time(time_value, precision)
    except WikidataDateError:
        return None
    date = {"year": parsed.year}
    if parsed.month is not None:
        date["month"] = parsed.month
    if parsed.day is not None:
        date["day"] = parsed.day
    return date


def parse_wikidata_coordinates(claims: dict) -> dict[str, float] | None:
    """Extracts the first usable P625 coordinate as `{"lat", "lng"}`."""
    for claim in claims.get("P625", []):
        try:
            value = claim["mainsnak"]["datavalue"]["value"]
            if "latitude" in value and "longitude" in value:
                return {"lat": value["latitude"], "lng": value["longitude"]}
        except KeyError:
            continue
    return None


def infer_date_property(entity: dict, kind_hint: str | None) -> str:
    """Picks the Wikidata property that dates an item: point in time for events,
    inception for landmarks."""
    if kind_hint == "event":
        return EVENT_DATE_PROPERTY
    if kind_hint == "landmark":
        return LANDMARK_DATE_PROPERTY

    for claim in entity.get("claims", {}).get("P31", []):
        try:
            instance = claim["mainsnak"]["datavalue"]["value"]["id"]
        except KeyError:
            continue
        if instance in POINT_IN_TIME_CLASSES:
            return EVENT_DATE_PROPERTY
        if instance == HUMAN_CLASS:
            return BIRTH_DATE_PROPERTY  # not ideal: births are out of scope

    return LANDMARK_DATE_PROPERTY


def resolve_date(
    entity: dict, date_property: str, manual_dates: dict, qid: str
) -> dict[str, int] | None:
    """The curated date if there is one, else the best Wikidata statement."""
    if qid in manual_dates:
        return manual_event_date(manual_dates[qid])
    claim = select_date(entity.get("claims", {}).get(date_property, []))
    if claim is None:
        return None
    return event_date(claim["time"], claim["precision"])


def build_event(
    qid: str,
    entity: dict,
    wiki: dict,
    kind_hint: str | None = None,
    manual_dates: dict | None = None,
    manual_coordinates: dict | None = None,
    bounds: dict | None = None,
) -> tuple[dict | None, str | None]:
    """Builds an event in the ADR-009 shape from a Wikidata entity + Wikipedia enrichment.

    Returns `(event, None)`, or `(None, reason)` when a required field is missing:
    the pipeline never guesses dates, coordinates or descriptions.
    """
    title = entity.get("labels", {}).get("en", {}).get("value", qid)

    date_property = infer_date_property(entity, kind_hint)
    date = resolve_date(entity, date_property, manual_dates or {}, qid)
    if not date:
        return None, "no usable date"

    coordinates = (manual_coordinates or {}).get(qid) or parse_wikidata_coordinates(
        entity.get("claims", {})
    )
    if not coordinates:
        return None, "no coordinates"
    if bounds and not in_bounds(coordinates["lat"], coordinates["lng"], bounds):
        return None, "coordinates outside the city bounds"

    description = wiki.get("extract", "")
    if not description:
        return None, "no Wikipedia extract"

    event: dict[str, Any] = {
        "id": qid,
        "title": title,
        **date,
        "lat": coordinates["lat"],
        "lng": coordinates["lng"],
        "description": description,
    }
    if "image" in wiki:
        event["image"] = wiki["image"]
    sources = {"wikidata": f"https://www.wikidata.org/wiki/{qid}"}
    if wiki.get("wikipedia_url"):
        sources["wikipedia"] = wiki["wikipedia_url"]
    event["sources"] = sources

    # Significance signal for ranking; select_events strips it.
    event["_sitelinks"] = len(entity.get("sitelinks", {}))
    return event, None


def select_events(events: list[dict]) -> list[dict]:
    """Keeps the MAX_EVENTS most linked events (ties by title), without the internal `_sitelinks`."""
    ranked = sorted(events, key=lambda event: (-event.get("_sitelinks", 0), event["title"]))
    return [
        {key: value for key, value in event.items() if key != "_sitelinks"}
        for event in ranked[:MAX_EVENTS]
    ]


def main() -> int:
    curated = load_curated()
    manual_dates = curated.get("manual_dates", {})
    manual_coordinates = curated.get("manual_coordinates", {})
    bounds = load_scope()["city"]["bounds"]
    candidates = load_candidates()
    qids = collect_all_qids(curated)

    print(f"Enriching {len(qids)} QIDs...")

    session = build_session(USER_AGENT)

    entities = fetch_wikidata_entities(session, qids)

    wiki_data = fetch_wikipedia_pages(session, entities)

    events = []
    for qid in qids:
        entity = entities.get(qid)
        if not entity:
            print(f"  WARNING: No Wikidata entity for {qid}")
            continue

        kind = candidates.get(qid, {}).get("kind")
        wiki = wiki_data.get(qid, {})
        event, reason = build_event(
            qid, entity, wiki, kind, manual_dates, manual_coordinates, bounds
        )
        if event:
            events.append(event)
            print(f"  ✓ {qid}: {event['title']} ({event['year']})")
        else:
            print(f"  ✗ {qid}: skipped ({reason})")

    events = select_events(events)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(events, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\nExported {len(events)} events to {OUTPUT_PATH}")
    for event in events:
        print(
            f"  {event['id']}: {event['title']} — {format_date(event)} "
            f"({event['lat']:.4f}, {event['lng']:.4f})"
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())