"""Tests for scripts/generate_summaries.py (rules: ADR-008, ADR-009). Ollama is never called."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import generate_summaries as gs

CITY = "Xi'an"
PROSE = " ".join(["word"] * 60)


def make_event(**overrides):
    event = {
        "id": "Q1",
        "title": "Terracotta Army",
        "year": -210,
        "lat": 34.38,
        "lng": 109.27,
        "description": "A collection of terracotta sculptures depicting the armies of Qin Shi Huang.",
    }
    return {**event, **overrides}


class FakeChat:
    def __init__(self, reply):
        self.reply = reply
        self.prompts = []

    def __call__(self, prompt):
        self.prompts.append(prompt)
        return self.reply


class BuildPromptTest(unittest.TestCase):
    def test_contains_the_title_extract_city_and_marker(self):
        prompt = gs.build_prompt(make_event(), CITY)
        for part in ("Terracotta Army", "armies of Qin Shi Huang", CITY, gs.INSUFFICIENT_MARKER):
            with self.subTest(part=part):
                self.assertIn(part, prompt)


class CleanOutputTest(unittest.TestCase):
    def test_keeps_only_the_text_after_a_reasoning_block(self):
        self.assertEqual(gs.clean_output("thinking...\n</think>\n\nThe answer."), "The answer.")

    def test_trims_plain_output(self):
        self.assertEqual(gs.clean_output("  The answer.\n"), "The answer.")


class SummaryProblemTest(unittest.TestCase):
    def test_accepts_plain_prose_in_range(self):
        self.assertIsNone(gs.summary_problem(PROSE))

    def test_rejects_unusable_output(self):
        cases = {
            "empty": "",
            "marker": gs.INSUFFICIENT_MARKER,
            "too short": "word " * 5,
            "too long": "word " * 200,
            "bullet list": "- " + PROSE,
            "numbered list": "1. " + PROSE,
            "heading": "# Title\n" + PROSE,
            "bold": "**bold** " + PROSE,
            "think tag": "<think> " + PROSE,
        }
        for name, text in cases.items():
            with self.subTest(name=name):
                self.assertIsNotNone(gs.summary_problem(text.strip()))

    def test_the_word_limits_are_inclusive(self):
        for words in (gs.MIN_WORDS, gs.MAX_WORDS):
            with self.subTest(words=words):
                self.assertIsNone(gs.summary_problem(" ".join(["word"] * words)))


class CopiesExtractTest(unittest.TestCase):
    extract = "The wall was built in the third century BCE to keep out nomads from the north."

    def test_detects_a_verbatim_run(self):
        copy = "Historians say the wall was built in the third century BCE to keep out nomads."
        self.assertTrue(gs.copies_extract(copy, self.extract))

    def test_accepts_a_rewrite(self):
        rewrite = "Builders raised the barrier around 300 BCE as defence against northern raiders."
        self.assertFalse(gs.copies_extract(rewrite, self.extract))

    def test_a_short_extract_never_counts_as_copied(self):
        self.assertFalse(gs.copies_extract("Short text here.", "Short text."))

    def test_summary_problem_rejects_a_copy(self):
        self.assertIsNotNone(gs.summary_problem(self.extract, self.extract))


class InputHashTest(unittest.TestCase):
    def test_changes_with_the_extract_model_and_prompt_version(self):
        base = gs.input_hash(make_event(), "m")
        self.assertNotEqual(base, gs.input_hash(make_event(description="Other."), "m"))
        self.assertNotEqual(base, gs.input_hash(make_event(), "other-model"))
        original = gs.PROMPT_VERSION
        try:
            gs.PROMPT_VERSION = original + 1
            self.assertNotEqual(base, gs.input_hash(make_event(), "m"))
        finally:
            gs.PROMPT_VERSION = original

    def test_ignores_fields_that_are_not_prompt_input(self):
        self.assertEqual(
            gs.input_hash(make_event(), "m"), gs.input_hash(make_event(year=1), "m")
        )


class ProcessEventTest(unittest.TestCase):
    def test_generates_and_caches_a_valid_summary(self):
        cache, chat = {}, FakeChat(PROSE)
        summary, outcome = gs.process_event(make_event(), cache, "m", chat, CITY, False)
        self.assertEqual((summary, outcome), (PROSE, "generated"))
        self.assertEqual(cache["Q1"]["status"], gs.STATUS_OK)

    def test_a_cache_hit_skips_the_model(self):
        cache, chat = {}, FakeChat(PROSE)
        gs.process_event(make_event(), cache, "m", chat, CITY, False)
        summary, outcome = gs.process_event(make_event(), cache, "m", chat, CITY, False)
        self.assertEqual((summary, outcome, len(chat.prompts)), (PROSE, "cached", 1))

    def test_a_changed_extract_regenerates(self):
        cache, chat = {}, FakeChat(PROSE)
        gs.process_event(make_event(), cache, "m", chat, CITY, False)
        _, outcome = gs.process_event(make_event(description="New."), cache, "m", chat, CITY, False)
        self.assertEqual((outcome, len(chat.prompts)), ("generated", 2))

    def test_force_ignores_the_cache(self):
        cache, chat = {}, FakeChat(PROSE)
        gs.process_event(make_event(), cache, "m", chat, CITY, False)
        gs.process_event(make_event(), cache, "m", chat, CITY, True)
        self.assertEqual(len(chat.prompts), 2)

    def test_the_insufficient_marker_gives_no_summary_and_is_cached(self):
        cache, chat = {}, FakeChat(gs.INSUFFICIENT_MARKER)
        summary, outcome = gs.process_event(make_event(), cache, "m", chat, CITY, False)
        self.assertEqual((summary, outcome), (None, "insufficient"))
        self.assertEqual(cache["Q1"]["status"], gs.STATUS_INSUFFICIENT)
        _, again = gs.process_event(make_event(), cache, "m", chat, CITY, False)
        self.assertEqual((again, len(chat.prompts)), ("cached", 1))

    def test_invalid_output_is_reported_and_not_cached(self):
        cache, chat = {}, FakeChat("too short")
        summary, outcome = gs.process_event(make_event(), cache, "m", chat, CITY, False)
        self.assertIsNone(summary)
        self.assertTrue(outcome.startswith("invalid"))
        self.assertEqual(cache, {})


class WithSummaryTest(unittest.TestCase):
    def test_places_the_summary_after_the_description_and_keeps_other_fields(self):
        event = make_event(image={"url": "u"})
        updated = gs.with_summary(event, "S")
        self.assertEqual(list(updated)[list(updated).index("description") + 1], "summary")
        self.assertEqual(updated["image"], {"url": "u"})

    def test_replaces_or_removes_an_existing_summary(self):
        event = make_event(summary="old")
        self.assertEqual(gs.with_summary(event, "new")["summary"], "new")
        self.assertNotIn("summary", gs.with_summary(event, None))

    def test_does_not_change_the_input(self):
        event = make_event()
        gs.with_summary(event, "S")
        self.assertNotIn("summary", event)


class SelectEventsTest(unittest.TestCase):
    events = [make_event(id=f"Q{n}") for n in range(1, 5)]

    def ids(self, only, limit):
        return [e["id"] for e in gs.select_events(self.events, only, limit)]

    def test_selects_all_by_default(self):
        self.assertEqual(self.ids(None, None), ["Q1", "Q2", "Q3", "Q4"])

    def test_only_filters_by_id(self):
        self.assertEqual(self.ids(["Q3", "Q1"], None), ["Q1", "Q3"])

    def test_limit_keeps_the_first_n(self):
        self.assertEqual(self.ids(None, 2), ["Q1", "Q2"])


if __name__ == "__main__":
    unittest.main()
