"""Discovers candidate events and landmarks for Xi'an in Wikidata (ADR-007).

Run from the repository root:

    scripts/.venv/bin/python scripts/fetch_events.py

Two small queries (no `P279*` property paths: they time out on WDQS) produce a
ranked candidate list, written to `scripts/.cache/candidates.json` and printed
for review. The 16 hand-written events are resolved to QIDs the same way, so
the user can confirm the mapping before the curated list is written.

Dates are read from the entity API (wbgetentities), not from SPARQL, because
WDQS shifts BCE years when it projects Gregorian-model dates to xsd:dateTime
(e.g. the Terracotta Army is stored as `-0248-00-00` but comes back from SPARQL
as `-0247-01-01`). The entity API returns values as stored, and the "Dates"
rules in docs/business-rules.md say which copy to prefer.
"""

import json
import sys
from pathlib import Path
from typing import Any, Iterable, Sequence

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import (  # noqa: E402
    WikidataDateError,
    build_session,
    fetch_json,
    parse_wikidata_time,
)

SCRIPTS_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPTS_DIR.parent
SCOPE_PATH = SCRIPTS_DIR / "config" / "scope.json"
EVENTS_JSON_PATH = REPO_ROOT / "src" / "data" / "events.json"
CANDIDATES_PATH = SCRIPTS_DIR / ".cache" / "candidates.json"
EXISTING_QIDS_PATH = SCRIPTS_DIR / ".cache" / "existing-event-qids.json"

USER_AGENT = (
    "HistoricalEventsMap/0.1 (local data-prep script; "
    "contact: vanessapcbarros@gmail.com)"
)
SPARQL_URL = "https://query.wikidata.org/sparql"
API_URL = "https://www.wikidata.org/w/api.php"
XI_AN_QID = "Q5826"
ENGLISH_WIKIPEDIA = "http://en.wikipedia.org/"
SITELINK_BATCH_SIZE = 50
ENTITY_BATCH_SIZE = 50

CALENDAR_GREGORIAN = "Q1985786"
EVENT_DATE_PROPERTY = "P585"
LANDMARK_DATE_PROPERTY = "P571"
DATE_PROPERTIES = {"event": EVENT_DATE_PROPERTY, "landmark": LANDMARK_DATE_PROPERTY}

SPARQL_PREFIXES = """
PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX p: <http://www.wikidata.org/prop/>
PREFIX psv: <http://www.wikidata.org/prop/statement/value/>
PREFIX wikibase: <http://wikiba.se/ontology#>
PREFIX schema: <http://schema.org/>
"""


def build_event_query(class_qids: Sequence[str]) -> str:
    """Q1: events of the whitelisted classes that are located in Xi'an."""
    values = " ".join(f"wd:{qid}" for qid in class_qids)
    return f"""
{SPARQL_PREFIXES}
SELECT DISTINCT ?item ?itemLabel ?class ?classLabel ?coord WHERE {{
  VALUES ?class {{ {values} }}
  ?item wdt:P31 ?class.
  {{ ?item wdt:P131* wd:{XI_AN_QID}. }} UNION {{ ?item wdt:P276 wd:{XI_AN_QID}. }}
  ?item wdt:P585 ?date.
  OPTIONAL {{ ?item wdt:P625 ?coord. }}
  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
}}
"""


def build_landmark_query(class_qids: Sequence[str]) -> str:
    """Q2: whitelisted landmarks with an inception, coordinates, English
    Wikipedia article, located in Xi'an."""
    values = " ".join(f"wd:{qid}" for qid in class_qids)
    return f"""
{SPARQL_PREFIXES}
SELECT DISTINCT ?item ?itemLabel ?class ?classLabel ?coord WHERE {{
  VALUES ?class {{ {values} }}
  ?item wdt:P31 ?class.
  {{ ?item wdt:P131* wd:{XI_AN_QID}. }} UNION {{ ?item wdt:P276 wd:{XI_AN_QID}. }}
  ?item wdt:P571 ?inception.
  ?item wdt:P625 ?coord.
  ?article schema:about ?item;
           schema:inLanguage "en".
  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
}}
"""


def parse_point(value: str) -> tuple[float, float] | None:
    """Parses a WKT point, `Point(lng lat)`, as Wikidata returns coordinates."""
    text = value.strip()
    if not text.startswith("Point(") or not text.endswith(")"):
        return None
    parts = text[len("Point(") : -1].split()
    if len(parts) != 2:
        return None
    try:
        lng, lat = float(parts[0]), float(parts[1])
    except ValueError:
        return None
    return lat, lng


def parse_date(time_value: str, precision: int) -> dict[str, Any]:
    """Keeps the raw value and the parsed date, or the reason it was rejected."""
    date: dict[str, Any] = {"time": time_value, "precision": precision}
    try:
        parsed = parse_wikidata_time(time_value, precision)
    except WikidataDateError as error:
        date["error"] = str(error)
        return date
    date["year"] = parsed.year
    if parsed.month is not None:
        date["month"] = parsed.month
    if parsed.day is not None:
        date["day"] = parsed.day
    return date


def parse_candidates(bindings: Iterable[dict], kind: str) -> list[dict]:
    """Groups the SPARQL rows into one candidate per item, keeping every class
    and the coordinates if present."""
    candidates: dict[str, dict] = {}
    for row in bindings:
        qid = row["item"]["value"].rsplit("/", 1)[-1]
        candidate = candidates.setdefault(
            qid,
            {
                "qid": qid,
                "kind": kind,
                "title": row["itemLabel"]["value"],
                "classes": [],
                "coordinates": None,
                "sitelinks": None,
                "date": None,
            },
        )
        class_qid = row["class"]["value"].rsplit("/", 1)[-1]
        if class_qid not in {entry["qid"] for entry in candidate["classes"]}:
            candidate["classes"].append(
                {"qid": class_qid, "label": row["classLabel"]["value"]}
            )

        if "coord" in row:
            point = parse_point(row["coord"]["value"])
            if point is not None:
                lat, lng = point
                candidate["coordinates"] = {"lat": lat, "lng": lng}
    return list(candidates.values())


def in_bounds(lat: float, lng: float, bounds: dict) -> bool:
    return (
        bounds["south"] <= lat <= bounds["north"]
        and bounds["west"] <= lng <= bounds["east"]
    )


def select_date(claims: Sequence[dict]) -> dict | None:
    """Picks the statement to date an item by: the proleptic Gregorian copy
    first (docs/business-rules.md, "Dates"), then the most precise one."""
    best: dict | None = None
    for claim in claims:
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
            # Prefer Gregorian, then higher precision
            if cand["calendar"] == CALENDAR_GREGORIAN and best["calendar"] != CALENDAR_GREGORIAN:
                best = cand
            elif cand["calendar"] == best["calendar"] and cand["precision"] > best["precision"]:
                best = cand
    return best


def fetch_entities(session, qids: Sequence[str], cache_dir: Path) -> dict[str, dict]:
    """Fetches claims, sitelinks, and labels for the given QIDs in batches."""
    entities: dict[str, dict] = {}
    for start in range(0, len(qids), ENTITY_BATCH_SIZE):
        batch = qids[start : start + ENTITY_BATCH_SIZE]
        data = fetch_json(
            session,
            API_URL,
            {
                "action": "wbgetentities",
                "ids": "|".join(batch),
                "props": "claims|sitelinks|labels",
                "languages": "en",
                "format": "json",
            },
            "entities",
            cache_dir=cache_dir,
        )
        entities.update(data.get("entities", {}))
    return entities


def with_entity_data(candidates: Sequence[dict], entities: dict[str, dict]) -> list[dict]:
    """Adds the stored date (preferring Gregorian) and the sitelink count."""
    enriched = []
    for candidate in candidates:
        entity = entities.get(candidate["qid"], {})
        candidate = dict(candidate)  # shallow copy
        candidate["sitelinks"] = len(entity.get("sitelinks", {}))
        prop = DATE_PROPERTIES[candidate["kind"]]
        date_claim = select_date(entity.get("claims", {}).get(prop, []))
        if date_claim:
            candidate["date"] = parse_date(date_claim["time"], date_claim["precision"])
        enriched.append(candidate)
    return enriched


def rank(candidates: Sequence[dict]) -> list[dict]:
    """Significance proxy: the most linked items first."""
    return sorted(
        candidates,
        key=lambda candidate: (
            -(candidate["sitelinks"] or 0),
            candidate["title"],
            candidate["qid"],
        ),
    )


def format_date(date: dict | None) -> str:
    if date is None:
        return "-"
    if "year" not in date:
        return "unreadable"
    text = str(date["year"])
    if "month" in date:
        text += f"-{date['month']:02d}"
    if "day" in date:
        text += f"-{date['day']:02d}"
    return text


def format_table(candidates: Sequence[dict]) -> str:
    header = ("#", "qid", "sitelinks", "date", "coords", "classes", "title")
    rows = [header]
    for index, candidate in enumerate(candidates, start=1):
        rows.append(
            (
                str(index),
                candidate["qid"],
                "-" if candidate["sitelinks"] is None else str(candidate["sitelinks"]),
                format_date(candidate.get("date")),
                "yes" if candidate["coordinates"] else "no",
                "; ".join(entry["label"] for entry in candidate["classes"]),
                candidate["title"],
            )
        )
    widths = [
        max(len(row[column]) for row in rows) for column in range(len(header))
    ]
    return "\n".join(
        "  ".join(cell.ljust(widths[index]) for index, cell in enumerate(row))
        for row in rows
    )


def search_variants(title: str) -> list[tuple[str, bool]]:
    """The full title, then shorter variants (our titles are sentences,
    Wikidata's are names). Returns (variant, is_approximate)."""
    words = title.split()
    variants = [(" ".join(words), False)]
    for length in range(len(words) - 1, max(len(words) - 4, 0), -1):
        variants.append((" ".join(words[:length]), True))
    return variants


def resolve_existing_titles(
    session, titles: Sequence[str], cache_dir: Path
) -> list[dict]:
    """Asks Wikidata for the closest match to each hand-written event title."""
    resolved = []
    for title in titles:
        matches = []
        for variant, approx in search_variants(title):
            data = fetch_json(
                session,
                API_URL,
                {
                    "action": "wbsearchentities",
                    "search": variant,
                    "language": "en",
                    "type": "item",
                    "limit": 3,
                    "format": "json",
                },
                "title-search",
                cache_dir=cache_dir,
            )
            hits = data.get("search", [])
            if hits:
                matches = [
                    {
                        "qid": hit["id"],
                        "label": hit.get("label", ""),
                        "description": hit.get("description", ""),
                        "matched_via": variant,
                        "approximate": approx,
                    }
                    for hit in hits
                ]
                break
        resolved.append({"title": title, "matches": matches})
    return resolved


def load_scope(path: Path = SCOPE_PATH) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    scope = load_scope()
    bounds = scope["city"]["bounds"]
    session = build_session(USER_AGENT)

    print(f"Querying WDQS for events located in {scope['city']['name']} ...")
    event_rows = fetch_json(
        session,
        SPARQL_URL,
        {
            "query": build_event_query([c["qid"] for c in scope["eventClasses"]]),
            "format": "json",
        },
        "q1-events",
    )["results"]["bindings"]
    events = parse_candidates(event_rows, kind="event")

    print(f"Querying WDQS for landmarks located in {scope['city']['name']} ...")
    landmark_rows = fetch_json(
        session,
        SPARQL_URL,
        {
            "query": build_landmark_query([c["qid"] for c in scope["landmarkClasses"]]),
            "format": "json",
        },
        "q2-landmarks",
    )["results"]["bindings"]
    landmarks = parse_candidates(landmark_rows, kind="landmark")

    outside = [
        candidate
        for candidate in events
        if candidate["coordinates"]
        and not in_bounds(
            candidate["coordinates"]["lat"], candidate["coordinates"]["lng"], bounds
        )
    ]
    events = [candidate for candidate in events if candidate not in outside]
    if outside:
        print(f"\nDropped {len(outside)} event(s) outside the bounds:")
        print(format_table(outside))

    candidates = events + landmarks
    qids = [candidate["qid"] for candidate in candidates]
    entities = fetch_entities(session, qids, SCRIPTS_DIR / ".cache")
    candidates = with_entity_data(candidates, entities)

    ranked = rank(candidates)
    CANDIDATES_PATH.parent.mkdir(parents=True, exist_ok=True)
    CANDIDATES_PATH.write_text(
        json.dumps(ranked, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print(f"\n{len(ranked)} candidates ({len(events)} events, {len(landmarks)} landmarks)")
    print(format_table(ranked))

    titles = [
        event["title"]
        for event in json.loads(EVENTS_JSON_PATH.read_text(encoding="utf-8"))
    ]
    resolved = resolve_existing_titles(session, titles, SCRIPTS_DIR / ".cache")
    EXISTING_QIDS_PATH.write_text(
        json.dumps(resolved, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print("\nExisting events, matched against Wikidata labels (confirm in step 4):")
    for entry in resolved:
        best = entry["matches"][0] if entry["matches"] else None
        if best is None:
            print(f'  "{entry["title"]}" -> no match')
            continue
        approx = " [approx]" if best.get("approximate") else ""
        detail = f" ({best['description']})" if best["description"] else ""
        print(
            f'  "{entry["title"]}" -> {best["qid"]} {best["label"]}{detail}{approx}'
        )

    print(f"\nCandidates written to {CANDIDATES_PATH}")
    print(f"Title mapping written to {EXISTING_QIDS_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())