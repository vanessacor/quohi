"""Tests for scripts/enrich_events.py (rules: docs/business-rules.md, ADR-007)."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import enrich_events


def time_claim(time, precision, calendar="Q1985786"):
    return {
        "mainsnak": {
            "datavalue": {
                "value": {
                    "time": time,
                    "precision": precision,
                    "calendarmodel": f"http://www.wikidata.org/entity/{calendar}",
                }
            }
        }
    }


def instance_claim(qid):
    return {"mainsnak": {"datavalue": {"value": {"id": qid}}}}


class CollectAllQidsTest(unittest.TestCase):
    def test_merges_sorts_and_dedupes_the_sources(self):
        curated = {
            "selected": ["Q3", "Q1"],
            "extra_qids": ["Q1", "Q2"],
            "title_overrides": {"a": "Q5", "b": "Q3"},
        }
        self.assertEqual(
            enrich_events.collect_all_qids(curated), ["Q1", "Q2", "Q3", "Q5"]
        )

    def test_skips_empty_title_overrides(self):
        curated = {"title_overrides": {"no match": ""}}
        self.assertEqual(enrich_events.collect_all_qids(curated), [])


class EventDateTest(unittest.TestCase):
    def test_keeps_only_the_precision_present(self):
        self.assertEqual(
            enrich_events.event_date("+0709-00-00T00:00:00Z", 9), {"year": 709}
        )
        self.assertEqual(
            enrich_events.event_date("+1936-12-12T00:00:00Z", 11),
            {"year": 1936, "month": 12, "day": 12},
        )

    def test_bce_year_stays_negative(self):
        self.assertEqual(
            enrich_events.event_date("-0044-03-15T00:00:00Z", 11),
            {"year": -44, "month": 3, "day": 15},
        )

    def test_returns_none_for_a_date_that_cannot_be_used(self):
        self.assertIsNone(enrich_events.event_date("+1900-00-00T00:00:00Z", 8))


class ManualEventDateTest(unittest.TestCase):
    def test_keeps_only_the_fields_given(self):
        self.assertEqual(enrich_events.manual_event_date({"year": -4500}), {"year": -4500})
        self.assertEqual(
            enrich_events.manual_event_date({"year": 742, "month": 5}),
            {"year": 742, "month": 5},
        )


class InferDatePropertyTest(unittest.TestCase):
    def test_kind_hint_wins(self):
        self.assertEqual(enrich_events.infer_date_property({}, "event"), "P585")
        self.assertEqual(enrich_events.infer_date_property({}, "landmark"), "P571")

    def test_event_class_uses_point_in_time(self):
        entity = {"claims": {"P31": [instance_claim("Q178561")]}}
        self.assertEqual(enrich_events.infer_date_property(entity, None), "P585")

    def test_unknown_item_defaults_to_inception(self):
        entity = {"claims": {"P31": [instance_claim("Q41176")]}}
        self.assertEqual(enrich_events.infer_date_property(entity, None), "P571")
        self.assertEqual(enrich_events.infer_date_property({}, None), "P571")


class ResolveDateTest(unittest.TestCase):
    def test_manual_date_overrides_wikidata(self):
        entity = {"claims": {"P571": [time_claim("+0700-00-00T00:00:00Z", 9)]}}
        date = enrich_events.resolve_date(entity, "P571", {"Q1": {"year": 709}}, "Q1")
        self.assertEqual(date, {"year": 709})

    def test_prefers_the_gregorian_copy(self):
        entity = {
            "claims": {
                "P571": [
                    time_claim("-0247-00-00T00:00:00Z", 9, calendar="Q1985727"),
                    time_claim("-0248-00-00T00:00:00Z", 9),
                ]
            }
        }
        self.assertEqual(
            enrich_events.resolve_date(entity, "P571", {}, "Q1"), {"year": -248}
        )

    def test_returns_none_without_a_statement(self):
        self.assertIsNone(enrich_events.resolve_date({"claims": {}}, "P571", {}, "Q1"))


class BuildEventTest(unittest.TestCase):
    BOUNDS = {"south": 34.05, "north": 34.6, "west": 108.6, "east": 109.45}

    def setUp(self):
        self.entity = {
            "labels": {"en": {"value": "Big Wild Goose Pagoda"}},
            "claims": {
                "P571": [time_claim("+0652-00-00T00:00:00Z", 9)],
                "P625": [
                    {
                        "mainsnak": {
                            "datavalue": {
                                "value": {"latitude": 34.22, "longitude": 108.96}
                            }
                        }
                    }
                ],
            },
            "sitelinks": {"enwiki": {}, "frwiki": {}},
        }
        self.wiki = {
            "extract": "A pagoda.",
            "wikipedia_url": "https://en.wikipedia.org/wiki/Giant_Wild_Goose_Pagoda",
            "image": {
                "url": "https://upload.wikimedia.org/a.jpg",
                "attribution": "A. Photographer",
                "license": "CC BY 2.0",
            },
        }

    def build(self, **kwargs):
        return enrich_events.build_event(
            "Q1047061", self.entity, self.wiki, "landmark", bounds=self.BOUNDS, **kwargs
        )

    def test_builds_the_adr_009_shape(self):
        event, reason = self.build()
        self.assertIsNone(reason)
        self.assertEqual(
            event,
            {
                "id": "Q1047061",
                "title": "Big Wild Goose Pagoda",
                "year": 652,
                "lat": 34.22,
                "lng": 108.96,
                "description": "A pagoda.",
                "image": {
                    "url": "https://upload.wikimedia.org/a.jpg",
                    "attribution": "A. Photographer",
                    "license": "CC BY 2.0",
                },
                "sources": {
                    "wikidata": "https://www.wikidata.org/wiki/Q1047061",
                    "wikipedia": "https://en.wikipedia.org/wiki/Giant_Wild_Goose_Pagoda",
                },
                "_sitelinks": 2,
            },
        )

    def test_omits_the_image_when_there_is_none(self):
        self.wiki.pop("image")
        event, _ = self.build()
        self.assertNotIn("image", event)

    def test_skips_an_item_without_a_usable_date(self):
        self.entity["claims"].pop("P571")
        self.assertEqual(self.build(), (None, "no usable date"))

    def test_skips_an_item_without_coordinates(self):
        self.entity["claims"].pop("P625")
        self.assertEqual(self.build(), (None, "no coordinates"))

    def test_manual_coordinates_fill_a_gap(self):
        self.entity["claims"].pop("P625")
        event, _ = self.build(manual_coordinates={"Q1047061": {"lat": 34.3, "lng": 108.9}})
        self.assertEqual((event["lat"], event["lng"]), (34.3, 108.9))

    def test_skips_coordinates_outside_the_city_bounds(self):
        event, reason = self.build(manual_coordinates={"Q1047061": {"lat": 34.2, "lng": 108.5}})
        self.assertIsNone(event)
        self.assertEqual(reason, "coordinates outside the city bounds")

    def test_skips_an_item_without_a_wikipedia_extract(self):
        self.wiki["extract"] = ""
        self.assertEqual(self.build(), (None, "no Wikipedia extract"))


class CleanExtractTest(unittest.TestCase):
    def test_drops_a_parenthetical_with_chinese_text(self):
        text = "Zhang Qian (Chinese: 張騫; died c. 114 BC) was an explorer."
        self.assertEqual(enrich_events.clean_extract(text), "Zhang Qian was an explorer.")

    def test_keeps_a_parenthetical_without_chinese_text(self):
        text = "Jianguomen (Xi'an) is a gate."
        self.assertEqual(enrich_events.clean_extract(text), text)

    def test_drops_a_parenthetical_left_empty(self):
        self.assertEqual(enrich_events.clean_extract("A gate ( ; ) stands."), "A gate stands.")

    def test_collapses_newlines_and_repeated_spaces(self):
        self.assertEqual(enrich_events.clean_extract("One.\nTwo   here."), "One. Two here.")


class FitSentencesTest(unittest.TestCase):
    def test_keeps_whole_sentences_within_the_limit(self):
        text = "First one. Second one. Third one is much longer than the rest."
        self.assertEqual(enrich_events.fit_sentences(text, limit=25), "First one. Second one.")

    def test_returns_short_text_unchanged(self):
        self.assertEqual(enrich_events.fit_sentences("Only one."), "Only one.")

    def test_cuts_a_single_long_sentence_at_a_word(self):
        text = "word " * 20
        fitted = enrich_events.fit_sentences(text.strip(), limit=22)
        self.assertEqual(fitted, "word word word word…")


class ImageCreditTest(unittest.TestCase):
    def test_thumbnail_url_drops_the_query_string(self):
        url = "https://thumb.wikimedia.org/a/960px-a.jpg?utm_source=en.wikipedia.org"
        self.assertEqual(
            enrich_events.thumbnail_url(url), "https://thumb.wikimedia.org/a/960px-a.jpg"
        )

    def test_strip_markup_returns_plain_text(self):
        self.assertEqual(
            enrich_events.strip_markup('<a href="x">xiquinho &amp; co</a>\n'), "xiquinho & co"
        )

    def test_credit_needs_an_author_and_a_license(self):
        metadata = {
            "Artist": {"value": '<a href="x">xiquinhosilva</a>'},
            "LicenseShortName": {"value": "CC BY 2.0"},
        }
        self.assertEqual(
            enrich_events.image_credit(metadata),
            {"attribution": "xiquinhosilva", "license": "CC BY 2.0"},
        )
        self.assertIsNone(enrich_events.image_credit({"LicenseShortName": {"value": "CC0"}}))
        self.assertIsNone(enrich_events.image_credit({"Artist": {"value": "Someone"}}))

    def test_an_unknown_author_is_not_a_credit(self):
        metadata = {
            "Artist": {"value": "Unknown authorUnknown author"},
            "LicenseShortName": {"value": "Public domain"},
        }
        self.assertIsNone(enrich_events.image_credit(metadata))


class SelectEventsTest(unittest.TestCase):
    def test_caps_the_list_and_drops_the_internal_field(self):
        events = [{"title": f"E{n:02d}", "_sitelinks": n} for n in range(25)]
        selected = enrich_events.select_events(events)
        self.assertEqual(len(selected), enrich_events.MAX_EVENTS)
        self.assertNotIn("_sitelinks", selected[0])

    def test_orders_by_sitelinks_then_title(self):
        events = [
            {"title": "B", "_sitelinks": 3},
            {"title": "A", "_sitelinks": 3},
            {"title": "C", "_sitelinks": 9},
        ]
        titles = [event["title"] for event in enrich_events.select_events(events)]
        self.assertEqual(titles, ["C", "A", "B"])


if __name__ == "__main__":
    unittest.main()
