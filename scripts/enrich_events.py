"""Enriches curated QIDs with Wikipedia content and exports events.json (ADR-007, ADR-009).

Run from the repository root:

    scripts/.venv/bin/python scripts/enrich_events.py

Reads `scripts/config/curated.json`, fetches Wikipedia extracts/images for each QID,
merges with Wikidata data (dates, coordinates), validates against the schema,
and writes `src/data/events.json` (capped at 20 events).
"""

import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import (  # noqa: E402
    build_session,
    fetch_json,
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

# Schema limits (ADR-009, docs/business-rules.md)
MAX_EVENTS = 20
MAX_SUMMARY_SENTENCES = 3
MAX_SUMMARY_CHARS = 500


def load_curated(path: Path = CURATED_PATH) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def apply_manual_date(date_claim: dict | None, manual_dates: dict, qid: str) -> dict | None:
    """Overrides Wikidata date with manual date if provided."""
    if qid in manual_dates:
        md = manual_dates[qid]
        return {
            "time": f"{md['year']:04d}-{md.get('month', 1):02d}-{md.get('day', 1):02d}T00:00:00Z"
            if md["year"] >= 0
            else f"-{-md['year']:04d}-{md.get('month', 1):02d}-{md.get('day', 1):02d}T00:00:00Z",
            "precision": 11 if "day" in md else (10 if "month" in md else 9),
            "calendar": "Q1985786",
        }
    return date_claim


def load_candidates(path: Path = CANDIDATES_PATH) -> dict[str, dict]:
    """Loads candidates.json into a dict by QID for fast lookup."""
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    return {item["qid"]: item for item in data}


def collect_all_qids(curated: dict, candidates: dict[str, dict]) -> list[str]:
    """Collects all unique QIDs from curated config and title_overrides."""
    qids = set()

    # Selected candidates
    qids.update(curated.get("selected", []))

    # Extra QIDs (landmarks missing P571)
    qids.update(curated.get("extra_qids", []))

    # Title overrides (non-empty)
    for qid in curated.get("title_overrides", {}).values():
        if qid:
            qids.add(qid)

    return sorted(qids)


def fetch_wikidata_entities(session, qids: list[str]) -> dict[str, dict]:
    """Fetches claims, sitelinks, labels, coordinates for QIDs in batches."""
    entities = {}
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


def fetch_wikipedia_pages(session, qids: list[str]) -> dict[str, dict]:
    """Fetches Wikipedia extract, URL, and lead image for QIDs via sitelinks."""
    # First, get sitelinks from Wikidata to find English Wikipedia page titles
    entities = fetch_wikidata_entities(session, qids)

    # Map QID -> Wikipedia page title
    page_titles = {}
    for qid, entity in entities.items():
        sitelinks = entity.get("sitelinks", {})
        enwiki = sitelinks.get("enwiki")
        if enwiki:
            page_titles[qid] = enwiki["title"]

    if not page_titles:
        return {}

    # Fetch extracts, URLs, images for all titles in batches
    enriched = {}
    titles_list = list(page_titles.values())
    qid_by_title = {v: k for k, v in page_titles.items()}

    # Batch size for Wikipedia API (50 titles per request)
    for start in range(0, len(titles_list), 50):
        batch_titles = titles_list[start : start + 50]
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


def parse_wikidata_date(claims: dict, prop: str) -> dict | None:
    """Extracts the best date claim (Gregorian preferred, then highest precision)."""
    CALENDAR_GREGORIAN = "Q1985786"
    best = None
    for claim in claims.get(prop, []):
        try:
            value = claim["mainsnak"]["datavalue"]["value"]
        except KeyError:
            continue
        if "time" not in value:
            continue
        calendar = value.get("calendarmodel", "").rsplit("/", 1)[-1]
        precision = value["precision"]
        cand = {"time": value["time"], "precision": precision, "calendar": calendar}
        if best is None:
            best = cand
        else:
            if cand["calendar"] == CALENDAR_GREGORIAN and best["calendar"] != CALENDAR_GREGORIAN:
                best = cand
            elif cand["calendar"] == best["calendar"] and cand["precision"] > best["precision"]:
                best = cand
    return best


def wikidata_time_to_event_date(time_value: str, precision: int) -> dict[str, Any] | None:
    """Converts Wikidata time to our event date format (year, month?, day?)."""
    # Reuse the parser logic from common.py
    import re

    from common import WikidataDateError, parse_wikidata_time

    try:
        parsed = parse_wikidata_time(time_value, precision)
    except WikidataDateError:
        return None

    result = {"year": parsed.year}
    if parsed.month is not None:
        result["month"] = parsed.month
    if parsed.day is not None:
        result["day"] = parsed.day
    return result


def parse_wikidata_coordinates(claims: dict) -> dict[str, float] | None:
    """Extracts coordinates from P625 claims."""
    coords = claims.get("P625", [])
    for claim in coords:
        try:
            value = claim["mainsnak"]["datavalue"]["value"]
            if "latitude" in value and "longitude" in value:
                return {"lat": value["latitude"], "lng": value["longitude"]}
        except KeyError:
            continue
    return None


def infer_date_property(qid: str, entity: dict, kind_hint: str | None) -> str:
    """Infers the correct date property for an item."""
    # Explicit kind from candidates
    if kind_hint == "event":
        return "P585"
    if kind_hint == "landmark":
        return "P571"

    # Heuristics based on P31 (instance of)
    claims = entity.get("claims", {})
    for claim in claims.get("P31", []):
        try:
            instance = claim["mainsnak"]["datavalue"]["value"]["id"]
        except KeyError:
            continue
        # Event classes
        if instance in {
            "Q178561",  # battle
            "Q180684",  # military conflict
            "Q12890393",  # incident
            "Q511866",  # mutiny
            "Q188165",  # war
            "Q3983889",  # conflict
        }:
            return "P585"
        # Dynasty/empire/period -> inception
        if instance in {
            "Q9683",  # Tang dynasty
            "Q1147037",  # Eastern Han
            "Q174687",  # Eastern Han (alt)
        }:
            return "P571"
        # Person -> birth (P569) or death (P570) not ideal; skip for now
        if instance == "Q5":  # human
            return "P569"  # birth date as proxy

    # Default: inception for landmarks/buildings
    return "P571"


def build_event(qid: str, entity: dict, wiki: dict, kind_hint: str | None = None, manual_dates: dict | None = None) -> dict | None:
    """Builds a HistoricalEvent dict from Wikidata entity + Wikipedia enrichment."""
    labels = entity.get("labels", {})
    title = labels.get("en", {}).get("value", qid)

    # Determine date property
    date_prop = infer_date_property(qid, entity, kind_hint)
    date_claim = parse_wikidata_date(entity.get("claims", {}), date_prop)
    date_claim = apply_manual_date(date_claim, manual_dates or {}, qid)
    if not date_claim:
        return None

    date = wikidata_time_to_event_date(date_claim["time"], date_claim["precision"])
    if not date:
        return None

    # Coordinates from P625 claims
    coordinates = parse_wikidata_coordinates(entity.get("claims", {}))

    # Location name from Wikipedia title or Wikidata label
    location_name = None
    if wiki.get("wikipedia_url"):
        location_name = wiki["wikipedia_url"].split("/")[-1].replace("_", " ")
    elif labels.get("en"):
        location_name = labels["en"]["value"]

    event = {
        "id": qid,
        "title": title,
        "date": date,
        "locationName": location_name,
        "coordinates": coordinates,
        "summary": wiki.get("summary", ""),
        "image": wiki.get("image_url"),
        "imageAttribution": wiki.get("image_attribution"),
        "sources": [
            {"label": "Wikipedia", "url": wiki.get("wikipedia_url", "")},
            {"label": "Wikidata", "url": f"https://www.wikidata.org/wiki/{qid}"},
        ],
    }

    # Add Wikidata sitelinks count as a significance signal (optional, for debugging)
    event["_sitelinks"] = len(entity.get("sitelinks", {}))

    return event


def main() -> int:
    curated = load_curated()
    manual_dates = curated.get("manual_dates", {})
    candidates = load_candidates()
    qids = collect_all_qids(curated, candidates)

    print(f"Enriching {len(qids)} QIDs...")

    session = build_session(USER_AGENT)

    # Fetch Wikidata entities (claims, coordinates, sitelinks, labels)
    entities = fetch_wikidata_entities(session, qids)

    # Fetch Wikipedia content
    wiki_data = fetch_wikipedia_pages(session, qids)

    # Build events
    events = []
    for qid in qids:
        entity = entities.get(qid)
        if not entity:
            print(f"  WARNING: No Wikidata entity for {qid}")
            continue

        # Determine kind from candidates if available
        kind = candidates.get(qid, {}).get("kind")
        wiki = wiki_data.get(qid, {})
        event = build_event(qid, entity, wiki, kind, manual_dates)
        if event:
            events.append(event)
            print(f"  ✓ {qid}: {event['title']} ({event['date']['year']})")
        else:
            print(f"  ✗ {qid}: skipped (no usable date)")

    # Sort by sitelinks desc (significance), then title
    events.sort(key=lambda e: (-e.get("_sitelinks", 0), e["title"]))

    # Cap at MAX_EVENTS
    events = events[:MAX_EVENTS]

    # Strip internal fields
    for event in events:
        event.pop("_sitelinks", None)

    # Write output
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(events, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\nExported {len(events)} events to {OUTPUT_PATH}")
    for event in events:
        date_str = str(event["date"]["year"])
        if "month" in event["date"]:
            date_str += f"-{event['date']['month']:02d}"
        if "day" in event["date"]:
            date_str += f"-{event['date']['day']:02d}"
        coords = event.get("coordinates")
        coord_str = f" ({coords['lat']:.4f}, {coords['lng']:.4f})" if coords else " (no coords)"
        print(f"  {event['id']}: {event['title']} — {date_str}{coord_str}")

    return 0


if __name__ == "__main__":
    sys.exit(main())