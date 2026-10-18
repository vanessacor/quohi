"""Shared helpers for the local data-prep scripts (ADR-007).

These scripts run on a developer machine before a release, never on the
deployed site. Network responses are cached under `scripts/.cache` so that a
re-run does no network calls.
"""

import hashlib
import json
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

import requests

SCRIPTS_DIR = Path(__file__).resolve().parent
CACHE_DIR = SCRIPTS_DIR / ".cache"
# Wikimedia policy: keep requests few, sequential and identifiable.
REQUEST_DELAY_SECONDS = 1.0
TIMEOUT_SECONDS = 60

# Wikidata date precisions: 7 century, 8 decade, 9 year, 10 month, 11 day.
ACCEPTED_PRECISIONS = frozenset({9, 10, 11})

# Wikidata pads years to at least four digits and always signs them:
# `+1936-12-12T00:00:00Z`, `-0044-03-15T00:00:00Z`. SPARQL hands back the
# xsd:dateTime form, which drops the plus sign on CE years.
_TIME_PATTERN = re.compile(
    r"^(?P<sign>[+-]?)(?P<year>\d{4,})-(?P<month>\d{2})-(?P<day>\d{2})"
    r"T\d{2}:\d{2}:\d{2}Z$"
)


class WikidataDateError(ValueError):
    """A Wikidata time value that cannot be mapped onto the event schema."""


@dataclass(frozen=True)
class WikidataDate:
    """A parsed Wikidata time value; `year` is negative for BCE."""

    year: int
    month: int | None = None
    day: int | None = None


def parse_wikidata_time(value: str, precision: int) -> WikidataDate:
    """Parses a Wikidata time value such as `-0044-03-15T00:00:00Z`.

    The sign maps straight onto the schema: `-44` is 44 BCE, `1936` is 1936 CE.
    This was verified against dates nobody disputes
    (scripts/tests/fixtures/wikidata_times.json): Wikidata stores Julius
    Caesar's death, 15 March 44 BCE, as `-0044-03-15`, so BCE years carry no
    offset. A zero month or day means "unknown" and becomes None, unless a day
    depends on it. Only year, month and day precision are accepted; a decade,
    century or anything coarser cannot be dated honestly.

    One early date can be stored twice, once per calendar model (proleptic
    Gregorian Q1985786, proleptic Julian Q1985727), and the two copies can
    differ by a year: Caesar's death is stored both as `-0044-03-15` and as
    `-0043-03-13`. Which copy reaches the data is decided at export time, per
    the "Dates" rules in docs/business-rules.md.
    """
    if precision not in ACCEPTED_PRECISIONS:
        raise WikidataDateError(
            f"unsupported precision {precision}, need 9 (year), 10 (month) or 11 (day): {value}"
        )

    match = _TIME_PATTERN.match(value)
    if not match:
        raise WikidataDateError(f"unrecognized time value {value!r}")

    sign = -1 if match["sign"] == "-" else 1
    year = sign * int(match["year"])
    if year == 0:
        raise WikidataDateError(f"the schema has no year 0: {value}")

    raw_month = int(match["month"])
    raw_day = int(match["day"])
    month = raw_month or None
    day = raw_day or None

    if month is not None and not 1 <= month <= 12:
        raise WikidataDateError(f"month must be 01-12: {value}")
    if day is not None and not 1 <= day <= 31:
        raise WikidataDateError(f"day must be 01-31: {value}")
    if day is not None and month is None:
        raise WikidataDateError(f"day without month: {value}")
    if precision == 9 and (month is not None or day is not None):
        raise WikidataDateError(f"year precision cannot carry a month or day: {value}")
    if precision == 10 and (month is None or day is not None):
        raise WikidataDateError(f"month precision needs a month and no day: {value}")
    if precision == 11 and (month is None or day is None):
        raise WikidataDateError(f"day precision needs a month and a day: {value}")

    return WikidataDate(year=year, month=month, day=day)


def build_session(user_agent: str) -> requests.Session:
    """A session that names us to the Wikimedia APIs, as their policy requires."""
    session = requests.Session()
    session.headers.update({"User-Agent": user_agent})
    return session


def fetch_json(
    session: requests.Session,
    url: str,
    params: Mapping[str, str],
    cache_name: str,
    cache_dir: Path = CACHE_DIR,
    delay_seconds: float = REQUEST_DELAY_SECONDS,
) -> Any:
    """GETs `url` as JSON, caching the response so a re-run does no network calls."""
    key = hashlib.sha256(
        json.dumps({"url": url, "params": dict(params)}, sort_keys=True).encode(
            "utf-8"
        )
    ).hexdigest()[:12]
    cache_path = Path(cache_dir) / f"{cache_name}-{key}.json"
    if cache_path.exists():
        return json.loads(cache_path.read_text(encoding="utf-8"))

    time.sleep(delay_seconds)
    response = session.get(url, params=dict(params), timeout=TIMEOUT_SECONDS)
    response.raise_for_status()
    data = response.json()

    Path(cache_dir).mkdir(parents=True, exist_ok=True)
    cache_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return data
