"""Tests for scripts/common.py (rules: docs/business-rules.md, ADR-007)."""

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import common

FIXTURE_PATH = Path(__file__).resolve().parent / "fixtures" / "wikidata_times.json"


class ParseWikidataTimeTest(unittest.TestCase):
    def test_real_wikidata_values_map_onto_the_schema(self):
        cases = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))["times"]
        for case in cases:
            with self.subTest(case["label"]):
                parsed = common.parse_wikidata_time(case["time"], case["precision"])
                self.assertEqual(parsed.year, case["year"])
                self.assertEqual(parsed.month, case["month"])
                self.assertEqual(parsed.day, case["day"])

    def test_bce_years_need_no_offset(self):
        """Wikidata -44 is 44 BCE: not 43, not 45 (the open question from research)."""
        parsed = common.parse_wikidata_time("-0044-03-15T00:00:00Z", 11)
        self.assertEqual(parsed, common.WikidataDate(year=-44, month=3, day=15))

    def test_a_zero_month_or_day_means_unknown(self):
        parsed = common.parse_wikidata_time("+1936-05-00T00:00:00Z", 10)
        self.assertEqual(parsed, common.WikidataDate(year=1936, month=5))

    def test_rejects_precision_below_year(self):
        for precision in (2, 3, 7, 8, 12):
            with self.subTest(precision=precision):
                with self.assertRaises(common.WikidataDateError):
                    common.parse_wikidata_time("-0200-00-00T00:00:00Z", precision)

    def test_a_very_long_year_parses(self):
        """Wikidata pads to at least four digits; deep-time years are wider."""
        parsed = common.parse_wikidata_time("-00010000-00-00T00:00:00Z", 9)
        self.assertEqual(parsed, common.WikidataDate(year=-10000))

    def test_rejects_year_zero(self):
        with self.assertRaisesRegex(common.WikidataDateError, "no year 0"):
            common.parse_wikidata_time("-0000-00-00T00:00:00Z", 9)

    def test_rejects_month_or_day_outside_their_range(self):
        with self.assertRaisesRegex(common.WikidataDateError, "month must be 01-12"):
            common.parse_wikidata_time("+1936-13-01T00:00:00Z", 11)
        with self.assertRaisesRegex(common.WikidataDateError, "day must be 01-31"):
            common.parse_wikidata_time("+1936-01-32T00:00:00Z", 11)
        with self.assertRaisesRegex(common.WikidataDateError, "day without month"):
            common.parse_wikidata_time("+1936-00-05T00:00:00Z", 11)

    def test_ignores_the_month_and_day_at_year_precision(self):
        # Wikidata API stores 00 placeholders, WDQS projects 01 placeholders.
        parsed = common.parse_wikidata_time("-0248-00-00T00:00:00Z", 9)
        self.assertEqual(parsed, common.WikidataDate(year=-248))
        parsed = common.parse_wikidata_time("-0247-01-01T00:00:00Z", 9)
        self.assertEqual(parsed, common.WikidataDate(year=-247))

    def test_month_precision_ignores_the_day(self):
        parsed = common.parse_wikidata_time("+1936-05-17T00:00:00Z", 10)
        self.assertEqual(parsed, common.WikidataDate(year=1936, month=5))

    def test_rejects_missing_month_or_day(self):
        with self.assertRaisesRegex(
            common.WikidataDateError, "month and day precision need a month"
        ):
            common.parse_wikidata_time("+1936-00-00T00:00:00Z", 10)
        with self.assertRaisesRegex(
            common.WikidataDateError, "day precision needs a day"
        ):
            common.parse_wikidata_time("+1936-12-00T00:00:00Z", 11)

    def test_rejects_malformed_values(self):
        for value in (
            "248",
            "+248-01-01T00:00:00Z",
            "+1936-01-01",
            "-0248-01-01 00:00:00Z",
            "",
        ):
            with self.subTest(value=value):
                with self.assertRaises(common.WikidataDateError):
                    common.parse_wikidata_time(value, 11)


class _StubResponse:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload


class _StubSession:
    """Stands in for requests.Session: returns a fixed payload and counts calls."""

    def __init__(self, payload):
        self.payload = payload
        self.calls = []

    def get(self, url, params=None, timeout=None):
        self.calls.append(url)
        return _StubResponse(self.payload)


class FetchJsonTest(unittest.TestCase):
    def test_a_second_call_is_served_from_the_cache(self):
        session = _StubSession({"items": [1, 2]})
        with tempfile.TemporaryDirectory() as tmp:
            args = dict(
                url="https://example.org/api",
                params={"q": "xian"},
                cache_name="test",
                cache_dir=Path(tmp),
                delay_seconds=0,
            )
            first = common.fetch_json(session, **args)
            second = common.fetch_json(session, **args)

        self.assertEqual(first, {"items": [1, 2]})
        self.assertEqual(second, first)
        self.assertEqual(len(session.calls), 1)

    def test_different_requests_use_different_cache_files(self):
        session = _StubSession({"items": []})
        with tempfile.TemporaryDirectory() as tmp:
            cache_dir = Path(tmp)
            common.fetch_json(
                session, "https://example.org/api", {"q": "a"}, "test",
                cache_dir=cache_dir, delay_seconds=0,
            )
            common.fetch_json(
                session, "https://example.org/api", {"q": "b"}, "test",
                cache_dir=cache_dir, delay_seconds=0,
            )
            self.assertEqual(len(list(cache_dir.glob("test-*.json"))), 2)
        self.assertEqual(len(session.calls), 2)


if __name__ == "__main__":
    unittest.main()
