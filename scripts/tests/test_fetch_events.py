"""Tests for scripts/fetch_events.py (rules: docs/business-rules.md, ADR-007)."""

import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import fetch_events
import common

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"


class ParsePointTest(unittest.TestCase):
    def test_parses_wkt_point(self):
        lat, lng = fetch_events.parse_point("Point(108.94 34.26)")
        self.assertAlmostEqual(lat, 34.26)
        self.assertAlmostEqual(lng, 108.94)

    def test_returns_none_for_malformed(self):
        self.assertIsNone(fetch_events.parse_point("Point()"))
        self.assertIsNone(fetch_events.parse_point("not a point"))
        self.assertIsNone(fetch_events.parse_point(""))


class InBoundsTest(unittest.TestCase):
    def setUp(self):
        self.bounds = {"south": 34.05, "north": 34.6, "west": 108.6, "east": 109.45}

    def test_inside(self):
        self.assertTrue(fetch_events.in_bounds(34.3, 109.0, self.bounds))

    def test_on_edge(self):
        self.assertTrue(fetch_events.in_bounds(34.05, 108.6, self.bounds))
        self.assertTrue(fetch_events.in_bounds(34.6, 109.45, self.bounds))

    def test_outside(self):
        self.assertFalse(fetch_events.in_bounds(34.0, 109.0, self.bounds))
        self.assertFalse(fetch_events.in_bounds(34.3, 108.0, self.bounds))


class SelectDateTest(unittest.TestCase):
    def test_prefers_gregorian_over_julian(self):
        claims = [
            {
                "mainsnak": {
                    "datavalue": {
                        "value": {
                            "time": "-0247-01-01T00:00:00Z",
                            "precision": 9,
                            "calendarmodel": "http://www.wikidata.org/entity/Q1985727",
                        }
                    }
                }
            },
            {
                "mainsnak": {
                    "datavalue": {
                        "value": {
                            "time": "-0248-00-00T00:00:00Z",
                            "precision": 9,
                            "calendarmodel": "http://www.wikidata.org/entity/Q1985786",
                        }
                    }
                }
            },
        ]
        selected = fetch_events.select_date(claims)
        self.assertEqual(selected["calendar"], "Q1985786")
        self.assertEqual(selected["time"], "-0248-00-00T00:00:00Z")

    def test_prefers_higher_precision_when_same_calendar(self):
        claims = [
            {
                "mainsnak": {
                    "datavalue": {
                        "value": {
                            "time": "+1936-00-00T00:00:00Z",
                            "precision": 9,
                            "calendarmodel": "http://www.wikidata.org/entity/Q1985786",
                        }
                    }
                }
            },
            {
                "mainsnak": {
                    "datavalue": {
                        "value": {
                            "time": "+1936-12-12T00:00:00Z",
                            "precision": 11,
                            "calendarmodel": "http://www.wikidata.org/entity/Q1985786",
                        }
                    }
                }
            },
        ]
        selected = fetch_events.select_date(claims)
        self.assertEqual(selected["precision"], 11)

    def test_returns_none_for_empty(self):
        self.assertIsNone(fetch_events.select_date([]))

    def test_skips_claims_without_time(self):
        claims = [
            {"mainsnak": {"datavalue": {"value": {"precision": 9}}}}
        ]
        self.assertIsNone(fetch_events.select_date(claims))


class RankTest(unittest.TestCase):
    def test_sorts_by_sitelinks_desc_then_title(self):
        candidates = [
            {"qid": "Q2", "sitelinks": 10, "title": "A", "kind": "event"},
            {"qid": "Q1", "sitelinks": 50, "title": "B", "kind": "event"},
            {"qid": "Q3", "sitelinks": 10, "title": "Z", "kind": "event"},
            {"qid": "Q4", "sitelinks": None, "title": "C", "kind": "event"},
        ]
        ranked = fetch_events.rank(candidates)
        self.assertEqual([c["qid"] for c in ranked], ["Q1", "Q2", "Q3", "Q4"])


class FormatDateTest(unittest.TestCase):
    def test_formats_complete(self):
        self.assertEqual(fetch_events.format_date({"year": 1936, "month": 12, "day": 12}), "1936-12-12")

    def test_formats_year_only(self):
        self.assertEqual(fetch_events.format_date({"year": -248}), "-248")

    def test_formats_year_month(self):
        self.assertEqual(fetch_events.format_date({"year": 1936, "month": 5}), "1936-05")

    def test_unreadable(self):
        self.assertEqual(fetch_events.format_date({"precision": 9, "error": "x"}), "unreadable")

    def test_none(self):
        self.assertEqual(fetch_events.format_date(None), "-")


class SearchVariantsTest(unittest.TestCase):
    def test_full_title_then_shorter(self):
        variants = fetch_events.search_variants("Banpo Neolithic village inhabited")
        self.assertEqual(variants[0], ("Banpo Neolithic village inhabited", False))
        self.assertEqual(variants[1], ("Banpo Neolithic village", True))
        self.assertEqual(variants[2], ("Banpo Neolithic", True))
        self.assertEqual(variants[3], ("Banpo", True))

    def test_two_words_gives_full_and_one_short(self):
        variants = fetch_events.search_variants("Xi'an Incident")
        self.assertEqual(len(variants), 2)
        self.assertEqual(variants[0], ("Xi'an Incident", False))
        self.assertEqual(variants[1], ("Xi'an", True))


class ParseCandidatesTest(unittest.TestCase):
    def test_groups_by_qid_and_merges_classes(self):
        bindings = [
            {
                "item": {"value": "http://www.wikidata.org/entity/Q1"},
                "itemLabel": {"value": "Test Event"},
                "class": {"value": "http://www.wikidata.org/entity/Q178561"},
                "classLabel": {"value": "battle"},
                "coord": {"value": "Point(108.94 34.26)"},
            },
            {
                "item": {"value": "http://www.wikidata.org/entity/Q1"},
                "itemLabel": {"value": "Test Event"},
                "class": {"value": "http://www.wikidata.org/entity/Q180684"},
                "classLabel": {"value": "military conflict"},
                "coord": {"value": "Point(108.94 34.26)"},
            },
        ]
        candidates = fetch_events.parse_candidates(bindings, kind="event")
        self.assertEqual(len(candidates), 1)
        self.assertEqual(candidates[0]["qid"], "Q1")
        self.assertEqual(len(candidates[0]["classes"]), 2)
        self.assertEqual(candidates[0]["coordinates"], {"lat": 34.26, "lng": 108.94})

    def test_handles_missing_coordinates(self):
        bindings = [
            {
                "item": {"value": "http://www.wikidata.org/entity/Q1"},
                "itemLabel": {"value": "Test Event"},
                "class": {"value": "http://www.wikidata.org/entity/Q178561"},
                "classLabel": {"value": "battle"},
            },
        ]
        candidates = fetch_events.parse_candidates(bindings, kind="event")
        self.assertIsNone(candidates[0]["coordinates"])


class FixtureTest(unittest.TestCase):
    def test_parses_q1_event_bindings(self):
        data = json.loads((FIXTURES_DIR / "q1_bindings.json").read_text(encoding="utf-8"))
        bindings = data["results"]["bindings"]
        candidates = fetch_events.parse_candidates(bindings, kind="event")
        self.assertEqual(len(candidates), 2)
        qids = {c["qid"] for c in candidates}
        self.assertIn("Q244941", qids)  # Xi'an Incident
        self.assertIn("Q10844449", qids)  # 2003 Northwest University controversy

    def test_parses_q2_landmark_bindings(self):
        data = json.loads((FIXTURES_DIR / "q2_bindings.json").read_text(encoding="utf-8"))
        bindings = data["results"]["bindings"]
        candidates = fetch_events.parse_candidates(bindings, kind="landmark")
        self.assertEqual(len(candidates), 7)
        qids = {c["qid"] for c in candidates}
        expected = {"Q47672", "Q1047061", "Q1158530", "Q275515", "Q5370929", "Q11061833", "Q11065242"}
        self.assertEqual(qids, expected)
        # All landmarks should have coordinates
        for c in candidates:
            self.assertIsNotNone(c["coordinates"], f"{c['qid']} missing coordinates")


if __name__ == "__main__":
    unittest.main()