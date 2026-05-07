---
phase: 10-houses-module
plan: 02
type: execute
wave: 2
depends_on:
  - "10-01"
files_modified:
  - tests/houses/conftest.py
  - tests/houses/fixtures/reference_charts.json
  - tests/houses/test_oracle_smoke.py
autonomous: true
plan_id: "10-02"
requirements:
  - HOU-09

must_haves:
  truths:
    - "tests/houses/conftest.py exposes a session-scoped reference_charts fixture with ≥10 (label, jd, lat, lon) entries spanning normal latitudes, mid-latitudes, southern hemisphere, 1900/2050 boundary, AND polar lats 70° and 80°"
    - "tests/houses/conftest.py exposes a swe_oracle(jd, lat, lon, system) helper that calls swe.houses_ex(jd, lat, lon, BYTES) and returns a dict with cusps[12], asc, mc, armc, vertex (slicing the [1:13] of the 13-tuple to get to 0-indexed 12-element cusps)"
    - "tests/houses/conftest.py exposes a swe_oracle_armc(armc, lat, eps, system) helper for isolating algorithm error from sidereal-time error during fixture authoring (uses swe.houses_armc)"
    - "tests/houses/fixtures/reference_charts.json contains the snapshotted oracle output for all ≥10 charts × {placidus, koch} = ≥20 entries — committed as a planning artifact"
    - "Polar charts at lat=70° and lat=80° are present in the fixture corpus and the snapshot records the swisseph polar behavior (raises swisseph.Error for Placidus/Koch beyond the polar circle)"
    - "tests/houses/test_oracle_smoke.py asserts the fixture loads correctly and the oracle helpers are wired (no production-code dependencies — this is pure infra)"
    - "All swisseph access is gated by pytest.importorskip in conftest.py — module imports cleanly even if swisseph is not installed (entire test directory is skipped, never partial)"
    - "SYSTEM_BYTES dict maps system name (str, lowercase) to single-byte code (b'P', b'K', b'O') — the bytes-vs-str pyswisseph trap is solved at the oracle boundary"
  artifacts:
    - path: "tests/houses/conftest.py"
      provides: "Pytest fixtures for swisseph oracle, reference_charts list, and helpers (swe_oracle, swe_oracle_armc) — module-level pytest.importorskip + named import for mypy"
      contains: "swe_oracle"
      min_lines: 100
    - path: "tests/houses/fixtures/reference_charts.json"
      provides: "≥10 chart oracle snapshots × 2 systems (placidus + koch); polar lats included; structured as JSON with sections for normal-lat (cusps populated) and polar-lat (records oracle's swisseph.Error or Porphyry fallback)"
      contains: "placidus"
      min_lines: 50
    - path: "tests/houses/test_oracle_smoke.py"
      provides: "Pure-infra smoke tests: fixture loads, ≥10 entries present, swe_oracle returns expected dict shape, polar entries marked"
      contains: "def test_"
      min_lines: 40
  key_links:
    - from: "tests/houses/conftest.py"
      to: "swisseph oracle"
      via: "pytest.importorskip('swisseph') module gate"
      pattern: "importorskip\\(.swisseph.\\)"
    - from: "tests/houses/conftest.py"
      to: "tests/houses/fixtures/reference_charts.json"
      via: "fixture file path resolved via Path(__file__).parent / 'fixtures'"
      pattern: "fixtures.*reference_charts\\.json"
    - from: "tests/houses/test_oracle_smoke.py"
      to: "tests/houses/conftest.py reference_charts fixture"
      via: "pytest fixture injection"
      pattern: "reference_charts"
---

<objective>
Build the test infrastructure that Plans 10-03, 10-04, 10-05, 10-06 will all consume: a pytest conftest exposing the swisseph oracle, a session-scoped reference-charts list, and a JSON fixture file containing ≥10 reference snapshots × 2 systems (Placidus + Koch). This plan owns the oracle-side helpers; production-code modules are still empty at this point.

Purpose: HOU-09 mandates "≥10 reference fixtures vs Astro.com / Swiss Ephemeris including polar lats (70°, 80°)." Authoring fixtures programmatically through swisseph is the right pattern (research §"Don't Hand-Roll" row 1) — eliminates copy-paste errors, lets us re-snapshot on demand, and creates a stable JSON artifact tracked in git. The other 4 plans (03, 04, 05, 06) all import this conftest; building it as a separate plan unblocks parallel Wave 3 (Plans 04 and 05 can both consume it without touching it).

Output:
- `tests/houses/conftest.py` — swe_oracle / swe_oracle_armc helpers, reference_charts session-scoped fixture, SYSTEM_BYTES dict
- `tests/houses/fixtures/reference_charts.json` — committed snapshot of ≥10 charts × {placidus, koch} oracle output
- `tests/houses/test_oracle_smoke.py` — proves the fixture and helpers are wired correctly (no production-code dependencies yet)
</objective>

<execution_context>
@./.claude/get-shit-done/workflows/execute-plan.md
@./.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/STATE.md
@.planning/phases/10-houses-module/10-RESEARCH.md

# Phase 10 Plan 01 — establishes tests/houses/ subpackage and the importorskip pattern
@.planning/phases/10-houses-module/10-01-lst-precision-audit-PLAN.md

# Reference: swisseph importorskip pattern from Phase 8
@tests/test_lilith_cross_check.py
</context>

<tasks>

<task type="auto">
  <name>Task 1: Write conftest.py with swe_oracle helpers, SYSTEM_BYTES, and reference_charts fixture</name>
  <files>tests/houses/conftest.py</files>
  <action>
    Create `tests/houses/conftest.py`. Follow the dual-import pattern from `tests/test_lilith_cross_check.py` (Phase 8 precedent): module-level `pytest.importorskip("swisseph")` followed by `import swisseph as swe` (mypy honours `[tool.mypy.overrides] swisseph.* ignore_missing_imports`).

    Required contents:

    1. Module docstring: "Test infrastructure for tests/houses/. Provides swisseph oracle helpers and reference chart fixtures. swisseph is a test-only AGPL-licensed dep — `pytest.importorskip` ensures the module is wholesale-skipped (never partially imported) when swisseph is absent."

    2. Imports:
        ```python
        from __future__ import annotations
        import json
        from pathlib import Path
        from typing import Any
        import numpy as np
        import pytest

        pytest.importorskip("swisseph")
        import swisseph as swe  # noqa: E402  (after importorskip is project convention)
        ```

    3. Module-level constants:
        ```python
        # Map public system name (lowercase) -> swisseph single-byte code.
        # Pitfall 8 from research: pyswisseph requires bytes, not str.
        SYSTEM_BYTES: dict[str, bytes] = {
            "placidus": b"P",
            "koch": b"K",
            "porphyry": b"O",
        }

        # Path to the snapshotted oracle JSON. Computed once at import time.
        FIXTURES_DIR: Path = Path(__file__).parent / "fixtures"
        REFERENCE_CHARTS_JSON: Path = FIXTURES_DIR / "reference_charts.json"
        ```

    4. `swe_oracle(jd: float, lat: float, lon: float, system: str) -> dict[str, Any]`:
        - Call `cusps_t, ascmc_t = swe.houses_ex(jd, lat, lon, SYSTEM_BYTES[system])`. Note: `houses_ex` returns `(cusps_13_tuple, ascmc_8_tuple)`. cusps[0] = 0.0 is the C-style 1-indexed placeholder.
        - Slice: `cusps_arr = np.asarray(cusps_t[1:13], dtype=np.float64)`  # shape (12,)
        - Return dict:
          ```python
          return {
              "cusps": cusps_arr,
              "asc": float(ascmc_t[0]),
              "mc": float(ascmc_t[1]),
              "armc": float(ascmc_t[2]),
              "vertex": float(ascmc_t[3]),
          }
          ```
        - Wrap in try/except `swisseph.Error`: catch the polar exception and return `{"error": str(e), "polar": True}` instead of cusps. Caller (snapshot script in Task 2) records this as the polar oracle behavior.

    5. `swe_oracle_armc(armc: float, lat: float, eps: float, system: str) -> dict[str, Any]`:
        - Same pattern but using `swe.houses_armc(armc, lat, eps, SYSTEM_BYTES[system])`. Used by Plans 03/04/05 to isolate algorithm error from sidereal-time error: feed your own ARMC, oracle returns cusps for that ARMC. Same return shape.

    6. `reference_charts` — session-scoped fixture returning a list[dict] of ≥10 entries:
        ```python
        @pytest.fixture(scope="session")
        def reference_charts() -> list[dict[str, Any]]:
            return [
                {"label": "J2000_Greenwich",     "jd": 2451545.0, "lat": 51.4779, "lon": 0.0},
                {"label": "J2000_Paris",         "jd": 2451545.0, "lat": 48.8566, "lon": 2.3522},
                {"label": "J2000_Sydney",        "jd": 2451545.0, "lat": -33.8688, "lon": 151.2093},
                {"label": "J2000_Tokyo",         "jd": 2451545.0, "lat": 35.6762, "lon": 139.6503},
                {"label": "J2000_BuenosAires",   "jd": 2451545.0, "lat": -34.6037, "lon": -58.3816},
                {"label": "J2000_Equator",       "jd": 2451545.0, "lat": 0.0,     "lon": 0.0},
                {"label": "1900_NewYork",        "jd": 2415020.5, "lat": 40.7128, "lon": -74.0060},
                {"label": "2050_Reykjavik",      "jd": 2470204.0, "lat": 64.1466, "lon": -21.9426},
                # Polar (HOU-09 explicit requirement)
                {"label": "J2000_Lat70_North",   "jd": 2451545.0, "lat": 70.0,   "lon": 0.0},
                {"label": "J2000_Lat80_North",   "jd": 2451545.0, "lat": 80.0,   "lon": 0.0},
            ]
        ```

    7. `loaded_reference_snapshot` — session-scoped fixture loading the JSON written by Task 2:
        ```python
        @pytest.fixture(scope="session")
        def loaded_reference_snapshot() -> dict[str, Any]:
            if not REFERENCE_CHARTS_JSON.exists():
                pytest.skip(
                    f"Reference snapshot not found at {REFERENCE_CHARTS_JSON}. "
                    "Run scripts/snapshot_reference_charts.py to regenerate."
                )
            with REFERENCE_CHARTS_JSON.open() as f:
                return json.load(f)
        ```

    Anti-patterns to avoid:
    - DO NOT import from `ketu.houses` here — that subpackage doesn't exist yet (Plan 03 creates it). conftest is pure-test infrastructure.
    - DO NOT use `b"P"` literally inline — go through `SYSTEM_BYTES["placidus"]` so a single rename refactors all callers.
    - DO NOT slice `cusps_t[0:12]` (off-by-one — that includes the placeholder 0.0). Use `cusps_t[1:13]` (research Pitfall 7).
    - DO NOT hard-code the fixtures dir path (`"tests/houses/fixtures/..."`); use `Path(__file__).parent / "fixtures"` so the conftest works from any cwd.
    - DO NOT load the JSON eagerly at module import time — gate it behind the `loaded_reference_snapshot` fixture so a fresh checkout (no JSON yet) doesn't crash collection.
  </action>
  <verify>
    `pytest tests/houses/ --collect-only` — collects without ImportError. If swisseph is installed, all conftest fixtures are visible (`pytest tests/houses/ --fixtures` lists `reference_charts`, `loaded_reference_snapshot`).

    `python -c "from tests.houses.conftest import SYSTEM_BYTES, swe_oracle, swe_oracle_armc; r = swe_oracle(2451545.0, 48.8566, 2.3522, 'placidus'); assert r['cusps'].shape == (12,); print('OK', r['asc'])"` runs and prints the Paris J2000 ascendant.

    `mypy --strict tests/houses/conftest.py` is clean (the swisseph imports are covered by `[tool.mypy.overrides] swisseph.*`).
  </verify>
  <done>
    `tests/houses/conftest.py` exists with: module-level importorskip+named-import, SYSTEM_BYTES, swe_oracle, swe_oracle_armc, reference_charts session-scoped fixture (≥10 entries incl. lat=70 and lat=80), loaded_reference_snapshot fixture. mypy --strict clean. `pytest --collect-only` succeeds.
  </done>
</task>

<task type="auto">
  <name>Task 2: Snapshot ≥10 charts × {placidus, koch} oracle output to fixtures/reference_charts.json</name>
  <files>tests/houses/fixtures/reference_charts.json
tests/houses/test_oracle_smoke.py</files>
  <action>
    Step A — Create `tests/houses/fixtures/reference_charts.json` by running a one-off snapshot script. The script itself is NOT committed (or lives at scripts/snapshot_reference_charts.py and is documented in the SUMMARY); the JSON output IS committed.

    Snapshot script logic:
    ```python
    import json, sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent / "tests"))
    from houses.conftest import (
        SYSTEM_BYTES, swe_oracle,
    )

    CHARTS = [...same list as conftest reference_charts...]
    SYSTEMS = ["placidus", "koch"]

    snapshot: dict = {"version": "v1.1-phase10-snapshot", "charts": {}}
    for chart in CHARTS:
        snapshot["charts"][chart["label"]] = {"meta": chart, "systems": {}}
        for sys_name in SYSTEMS:
            try:
                result = swe_oracle(chart["jd"], chart["lat"], chart["lon"], sys_name)
                # Convert ndarray to list for JSON serializability
                if "cusps" in result:
                    result["cusps"] = result["cusps"].tolist()
                snapshot["charts"][chart["label"]]["systems"][sys_name] = result
            except Exception as e:
                # Should be caught inside swe_oracle, but defensive
                snapshot["charts"][chart["label"]]["systems"][sys_name] = {
                    "error": f"{type(e).__name__}: {e}", "polar": True,
                }

    out = Path("tests/houses/fixtures/reference_charts.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(snapshot, indent=2, sort_keys=True))
    print(f"Wrote {out}: {len(snapshot['charts'])} charts × {len(SYSTEMS)} systems")
    ```

    Run from `venv/bin/activate`. Verify the resulting JSON:
    - Top-level keys: `version`, `charts`
    - Exactly 10 entries under `charts`
    - For non-polar charts (8 of them): both `placidus` and `koch` entries have a `cusps` array of length 12, plus `asc`, `mc`, `armc`, `vertex` floats.
    - For polar charts (lat=70, lat=80, 2 of them): both `placidus` and `koch` entries have an `error` key (swisseph raises `swisseph.Error` beyond the polar circle — research §"Empirical baseline" verified this) and `polar: true`.

    Expected file size: ~10 KB (compact). Commit with `git add tests/houses/fixtures/reference_charts.json`.

    Step B — Create `tests/houses/test_oracle_smoke.py`:

    ```python
    """Smoke tests for the oracle harness — verifies fixtures and helpers are wired
    correctly. Pure-infra tests: NO dependencies on ketu.houses production code
    (which doesn't exist until Plan 10-03 lands).
    """
    from __future__ import annotations
    import numpy as np
    import pytest


    def test_reference_charts_has_at_least_ten_entries(reference_charts):
        assert len(reference_charts) >= 10, (
            f"HOU-09 requires ≥10 reference fixtures, got {len(reference_charts)}"
        )


    def test_reference_charts_includes_polar_latitudes(reference_charts):
        lats = {abs(c["lat"]) for c in reference_charts}
        assert any(lat >= 70.0 for lat in lats), "HOU-09 requires lat=70°"
        assert any(lat >= 80.0 for lat in lats), "HOU-09 requires lat=80°"


    def test_swe_oracle_returns_12_cusps_at_paris_j2000():
        from .conftest import swe_oracle
        result = swe_oracle(2451545.0, 48.8566, 2.3522, "placidus")
        assert result["cusps"].shape == (12,)
        assert 0.0 <= result["asc"] < 360.0
        assert 0.0 <= result["mc"] < 360.0


    def test_swe_oracle_polar_returns_error_marker():
        from .conftest import swe_oracle
        # lat=80° is well beyond polar circle for Placidus
        result = swe_oracle(2451545.0, 80.0, 0.0, "placidus")
        assert "error" in result
        assert result.get("polar") is True


    def test_swe_oracle_armc_isolates_armc_from_sidereal_time():
        """ARMC-direct API skips swe.sidtime — useful for Plans 03/04/05 algorithm tests."""
        from .conftest import swe_oracle_armc
        from ketu.ephemeris.coordinates import mean_obliquity
        eps = mean_obliquity(2451545.0)
        result = swe_oracle_armc(0.0, 48.8566, eps, "placidus")  # armc=0 is meridian alignment
        assert result["cusps"].shape == (12,)


    def test_loaded_reference_snapshot_matches_oracle(reference_charts, loaded_reference_snapshot):
        """The committed JSON snapshot must match the live oracle output (within 1e-9 deg)."""
        from .conftest import swe_oracle
        for chart in reference_charts:
            label = chart["label"]
            assert label in loaded_reference_snapshot["charts"], (
                f"Snapshot missing chart {label}"
            )
            for sys_name in ["placidus", "koch"]:
                snap = loaded_reference_snapshot["charts"][label]["systems"][sys_name]
                live = swe_oracle(chart["jd"], chart["lat"], chart["lon"], sys_name)
                if "error" in snap:
                    assert "error" in live, (
                        f"{label}/{sys_name}: snapshot has error but live does not"
                    )
                else:
                    np.testing.assert_allclose(
                        snap["cusps"], live["cusps"], atol=1e-9, rtol=0,
                        err_msg=f"{label}/{sys_name} cusps drifted",
                    )
                    assert abs(snap["asc"] - live["asc"]) < 1e-9
                    assert abs(snap["mc"] - live["mc"]) < 1e-9
    ```

    Anti-patterns to avoid:
    - DO NOT import from `ketu.houses` (production package) in this test file. Plan 10-03 creates it; Plan 10-02 must remain pure-infra so it can land before Plan 10-03 in case parallel Wave-2 execution gets reordered.
    - DO NOT make the snapshot-vs-live tolerance loose (the 1e-9 deg pin is tight on purpose — swisseph is deterministic; any drift signals an environmental issue worth flagging).
    - DO NOT commit the snapshot script (one-off scaffolding); commit only the JSON output.
    - DO NOT skip individual cases when swisseph is missing — the module-level importorskip in conftest.py makes the entire `tests/houses/` directory skip wholesale.
  </action>
  <verify>
    `pytest tests/houses/test_oracle_smoke.py -v` runs and shows 6 tests passing (or all skipped if swisseph not installed).

    `python -c "import json; d = json.load(open('tests/houses/fixtures/reference_charts.json')); assert len(d['charts']) == 10; assert all(s in d['charts']['J2000_Paris']['systems'] for s in ['placidus', 'koch']); assert d['charts']['J2000_Lat80_North']['systems']['placidus'].get('polar') is True; print('OK', len(d['charts']), 'charts')"` succeeds.

    `mypy --strict tests/houses/test_oracle_smoke.py` is clean.

    `pytest tests/ --collect-only -q | grep test_oracle_smoke | wc -l` returns 6 (collection happy across the project, no name collisions).

    `wc -l tests/houses/fixtures/reference_charts.json` shows >50 lines (sanity: real content, not just `{}`).
  </verify>
  <done>
    `tests/houses/fixtures/reference_charts.json` committed with version field, 10 charts × 2 systems, polar charts marked with `error` + `polar: true`, non-polar charts with full cusps + asc + mc + armc + vertex. `tests/houses/test_oracle_smoke.py` exists with 6 smoke tests, all passing. The full `pytest tests/` suite still passes (488 + 15 from Plan 01 + 6 from this plan = 509+ total tests). mypy --strict clean.
  </done>
</task>

</tasks>

<verification>
- `pytest tests/houses/ -v` passes (≥6 + 15 = 21 tests; or wholesale-skipped if swisseph missing).
- `tests/houses/fixtures/reference_charts.json` is valid JSON, ≥10 charts, includes lat=70° and lat=80° polar entries marked with error.
- `mypy --strict tests/houses/conftest.py tests/houses/test_oracle_smoke.py` clean.
- No production-code imports of `ketu.houses` in this plan's deliverables (it doesn't exist yet).
- `grep -r "import swisseph" ketu/` returns nothing — runtime constraint preserved.
</verification>

<success_criteria>
- HOU-09 fixture infrastructure landed: ≥10 charts including polar 70°/80° snapshotted to a committed JSON.
- Oracle helpers (swe_oracle, swe_oracle_armc) are reusable across plans 03/04/05/06 via pytest fixture mechanism.
- bytes-vs-str trap (Pitfall 8) and 13-tuple slicing trap (Pitfall 7) are solved at the conftest layer; downstream test files never see them.
- Plans 04 and 05 can run in Wave 3 simultaneously, both reading the same fixture JSON without modifying it.
</success_criteria>

<output>
After completion, create `.planning/phases/10-houses-module/10-02-SUMMARY.md` documenting:
- The 10 reference charts chosen (table: label, jd, lat, lon)
- swisseph version used for the snapshot (from `swe.version`)
- Polar charts and the error-marker shape recorded for them
- File size and SHA256 of `reference_charts.json` (so Plan 06 integration test can pin against it if desired)
- Confirmation: 488 + 15 (Plan 01) + 6 (Plan 02) = 509+ tests pass; mypy strict clean; no `ketu/` imports of swisseph
</output>
