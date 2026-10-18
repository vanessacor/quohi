# Structuring a script

Follow `scripts/enrich_events.py`:

1. Module docstring: what it does, the exact run command from the repo root
   (`scripts/.venv/bin/python scripts/<name>.py`), inputs, outputs, ADR refs.
2. Imports, then path and config constants at the top
   (`SCRIPTS_DIR`, `REPO_ROOT`, `*_PATH`, API URLs, limits).
3. Small functions: fetch, parse/transform, write. Shared helpers go in `common.py`
   only when a second script needs them.
4. `main() -> int` (exit code) that wires the steps together, guarded by
   `if __name__ == "__main__":`. Keep import-time side effects out of modules
   so tests can import them.
5. Arguments: none by default (paths and limits are constants). If a script needs
   flags, use `argparse` with a short `parse_args()`; do not add a CLI framework.

Scripts import siblings via the `sys.path.insert(0, ...)` pattern already used,
marked `# noqa: E402`. Do not turn `scripts/` into a package.

Config data (curated QIDs, scope) lives in `scripts/config/*.json`, not in code.
