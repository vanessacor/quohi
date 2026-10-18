"""Tests for scripts/config/scope.json (rules: docs/business-rules.md, ADR-007)."""

import json
import re
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = SCRIPTS_DIR.parent
SCOPE_PATH = SCRIPTS_DIR / "config" / "scope.json"
CITY_TS_PATH = REPO_ROOT / "src" / "config" / "city.ts"


def read_city_name() -> str:
    """Reads the city name out of src/config/city.ts, so a silent drift fails here."""
    match = re.search(r'name:\s*"([^"]+)"', CITY_TS_PATH.read_text(encoding="utf-8"))
    if not match:
        raise AssertionError(f"no name literal found in {CITY_TS_PATH}")
    return match.group(1)


def read_city_bounds() -> dict[str, float]:
    """Same as read_city_name, for the bounds object."""
    match = re.search(
        r"bounds:\s*\{([^}]*)\}", CITY_TS_PATH.read_text(encoding="utf-8")
    )
    if not match:
        raise AssertionError(f"no bounds literal found in {CITY_TS_PATH}")
    bounds: dict[str, float] = {}
    for pair in match.group(1).split(","):
        key, _, value = pair.partition(":")
        bounds[key.strip()] = float(value.strip())
    return bounds


class ScopeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scope = json.loads(SCOPE_PATH.read_text(encoding="utf-8"))

    def test_the_city_matches_the_app_config(self):
        self.assertEqual(self.scope["city"]["name"], read_city_name())
        self.assertEqual(self.scope["city"]["bounds"], read_city_bounds())

    def test_the_bounds_are_sane(self):
        bounds = self.scope["city"]["bounds"]
        self.assertLess(bounds["south"], bounds["north"])
        self.assertLess(bounds["west"], bounds["east"])

    def test_classes_are_qids_with_labels_and_no_duplicates(self):
        qids = []
        for group in ("eventClasses", "landmarkClasses"):
            for entry in self.scope[group]:
                with self.subTest(group=group, qid=entry["qid"]):
                    self.assertRegex(entry["qid"], r"^Q[0-9]+$")
                    self.assertTrue(entry["label"].strip())
                qids.append(entry["qid"])
        self.assertEqual(len(qids), len(set(qids)), "duplicate class QID")

    def test_event_and_landmark_classes_do_not_overlap(self):
        events = {entry["qid"] for entry in self.scope["eventClasses"]}
        landmarks = {entry["qid"] for entry in self.scope["landmarkClasses"]}
        self.assertEqual(events & landmarks, set())


if __name__ == "__main__":
    unittest.main()
