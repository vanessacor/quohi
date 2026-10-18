"""Enriches curated QIDs with Wikipedia content and exports events.json (ADR-007, ADR-009).

Run from the repository root:

    scripts/.venv/bin/python scripts/enrich_events.py

Reads `scripts/config/curated.json`, fetches Wikipedia extracts/images for each QID,
merges with Wikidata data (dates, coordinates) and writes `src/data/events.json`
(capped at 20 events).
"""

import json
import sys
from pathlib import Path
from typing import Any

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
CACHE_DIR = SCRIPTS_DIR / ".cache"
ENTITY_BATCH_SIZE = 50
WIKIPEDIA_BATCH_SIZE = 50

MAX_EVENTS = 20
MAX_SUMMARY_SENTENCES = 3
MAX_SUMMARY_CHARS = 500

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


def fetch_wikipedia_pages(
    session: requests.Session, entities: dict[str, dict]
) -> dict[str, dict]:
    """Fetches Wikipedia extract, URL, and lead image for the entities' English articles."""
    page_titles = {}
    for qid, entity in entities.items():
        sitelinks = entity.get("sitelinks", {})
        enwiki = sitelinks.get("enwiki")
        if enwiki:
            page_titles[qid] = enwiki["title"]

    if not page_titles:
        return {}

    enriched: dict[str, dict] = {}
    titles_list = list(page_titles.values())
    qid_by_title = {v: k for k, v in page_titles.items()}

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
                "piprop": "original",
                "format": "json",
            },
            "wikipedia",
            cache_dir=CACHE_DIR,
        )

        pages = data.get("query", {}).get("pages", {})
        for page in pages.values():
            if "missing" in page:
                continue
            title = page.get("title", "")
            qid = qid_by_title.get(title)
            if not qid:
                continue

            extract = page.get("extract", "").strip()
            if len(extract) > MAX_SUMMARY_CHARS:
                extract = extract[:MAX_SUMMARY_CHARS].rsplit(" ", 1)[0] + "…"

            original = page.get("original", {})
            image_url = original.get("source") if original else None

            enriched[qid] = {
                "summary": extract,
                "wikipedia_url": page.get("fullurl", ""),
                "image_url": image_url,
                "image_attribution": "Wikimedia Commons" if image_url else None,
            }

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

    description = wiki.get("summary", "")
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
    if wiki.get("image_url"):
        event["image"] = {
            "url": wiki["image_url"],
            "attribution": wiki["image_attribution"],
        }
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