# Testing the scripts

The repo uses stdlib `unittest` in `scripts/tests/` (not pytest). Do not add a
test dependency.

- File per module: `test_<module>.py`; classes `<Thing>Test(unittest.TestCase)`.
- Test names read as sentences: `test_the_bounds_are_sane`.
- Test pure logic (date parsing, scope filtering, schema mapping). Never hit the
  network in tests; use recorded data in `scripts/tests/fixtures/`.
- Verify facts against real data once, then pin them in a fixture
  (see `fixtures/wikidata_times.json`) instead of re-deriving them in the test.
- Use `self.subTest(...)` for table-driven cases.
- Test edge cases the data really has: BCE years, missing month/day, coarse
  precision, empty results.
- Bug fix: write the failing test first, then fix.
- Design for testability: pass data and paths in as arguments instead of
  reading globals, so a test can supply its own.

Run: `scripts/.venv/bin/python -m unittest discover scripts/tests`
