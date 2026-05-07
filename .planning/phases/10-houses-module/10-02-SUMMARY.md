---
phase: 10-houses-module
plan: "02"
subsystem: testing-infrastructure
tags: [houses, swisseph-oracle, pytest-fixtures, reference-charts, hou-09, polar-coverage, placidus, koch, porphyry]

requires:
  - phase: 10-houses-module/10-01-lst-precision-audit
    provides: tests/houses/ subpackage marker (__init__.py) + pytest.importorskip("swisseph") + named-import pattern for mypy --strict
  - phase: 08-lilith-verification
    provides: dual-import pattern (importorskip-without-binding + named import) reused verbatim
provides:
  - tests/houses/conftest.py — SYSTEM_BYTES, swe_oracle, swe_oracle_armc, reference_charts (10 entries), loaded_reference_snapshot fixtures
  - tests/houses/fixtures/reference_charts.json — 10 charts × 3 systems oracle snapshot, polar lats included, swisseph 2.10.03
  - tests/houses/test_oracle_smoke.py — 6 pure-infra tests asserting harness wiring
affects: [10-03 registry-dtype-ascmc, 10-04 placidus-implementation, 10-05 koch-porphyry-polar, 10-06 integration-stub-removal]

tech-stack:
  added: []  # No new deps; pyswisseph already on [project.optional-dependencies].test
  patterns:
    - "Oracle-helper-at-the-conftest-boundary: SYSTEM_BYTES dict centralises bytes-vs-str trap (Pitfall 8); cusps_t[1:13] slice centralises the 13-tuple/0-indexed trap (Pitfall 7); downstream test files never see either"
    - "swe_oracle vs swe_oracle_armc — high-level (jd, lat, lon) vs ARMC-direct (armc, lat, eps); Plans 03/04/05 use ARMC-direct to factor out GST drift when isolating algorithm error"
    - "Snapshot-then-pin pattern: oracle output → JSON committed once + smoke test asserts live≡snapshot @ 1e-9 deg; any environmental drift (swisseph version bump, ephemeris-file change) fails CI loudly"
    - "Polar-marker convention: {error: '<msg>', polar: True} for Placidus/Koch beyond polar circle; closed-form cusps for Porphyry — the JSON encodes the swisseph polar contract Plan 10-05 must replicate"
    - "Snapshot script as one-off scaffolding (NOT committed); only the JSON output is tracked. Regenerate by running the script from venv if a swisseph version bump invalidates the pin."

key-files:
  created:
    - tests/houses/conftest.py
    - tests/houses/fixtures/reference_charts.json
    - tests/houses/test_oracle_smoke.py
    - .planning/phases/10-houses-module/10-02-SUMMARY.md
  modified: []

key-decisions:
  - "SYSTEM_BYTES centralises the bytes-vs-str trap at the oracle boundary — every downstream test file passes lowercase strings ('placidus', 'koch', 'porphyry'); the b'P'/b'K'/b'O' codes appear in exactly one place"
  - "Polar charts (lat=70°, lat=80°) are first-class fixture entries — Plan 10-05's Porphyry-fallback design must produce closed-form cusps matching the JSON snapshot's lat=80° porphyry section"
  - "Snapshot-vs-live tolerance pinned at 1e-9 deg (not loose) — swisseph is deterministic; any drift signals an environmental issue worth flagging"
  - "10 charts (not 11+) — exactly meets HOU-09 floor with no slack: J2000 ×6 (Greenwich, Paris, Sydney, Tokyo, Buenos Aires, Equator) + 1900 (NewYork) + 2050 (Reykjavik) + polar 70°/80°. Plan 10-06 integration tests parametrize 8 non-polar × 3 systems = 24 oracle-agreement cases."
  - "Snapshot script lives at /tmp during execution and is NOT committed — its output (the JSON) is the canonical artifact. Documented in this SUMMARY for later regeneration."

patterns-established:
  - "Oracle harness in conftest.py (importorskip + named import + helper functions + session-scoped fixture); downstream test files import via pytest fixture injection and `from .conftest import swe_oracle, swe_oracle_armc`"
  - "JSON oracle snapshot pinned in tests/houses/fixtures/; smoke test ensures live≡snapshot at 1e-9 deg; any swisseph version bump that changes cusps breaks the smoke test loudly (intentional regression alarm)"

duration: 4m 5s
completed: 2026-05-07
---

# Phase 10 Plan 02: Oracle Harness and Fixtures Summary

**Built the swisseph oracle harness consumed by Plans 10-03/04/05/06: pytest fixtures, SYSTEM_BYTES dict, swe_oracle / swe_oracle_armc helpers, and a 10-charts × 3-systems JSON snapshot with explicit polar 70°/80° coverage per HOU-09.**

## Performance

- **Duration:** 4 min 5 s
- **Started:** 2026-05-07T07:23:44Z
- **Completed:** 2026-05-07T07:27:49Z
- **Tasks:** 2 (conftest helpers + reference fixture; JSON snapshot + smoke tests)
- **Files created:** 3 (+ this SUMMARY)
- **Files modified:** 0

## Accomplishments

- `tests/houses/conftest.py` exposes the swisseph oracle (`swe_oracle`, `swe_oracle_armc`) and a 10-entry session-scoped `reference_charts` fixture spanning normal, mid-, southern, equatorial, 1900/2050 boundary, and **polar 70°/80°** latitudes per HOU-09
- `tests/houses/fixtures/reference_charts.json` snapshots the oracle output for **10 charts × 3 systems = 30 entries**, recording the swisseph polar contract (Placidus/Koch raise `swisseph.Error` at lat=70°/80°; Porphyry produces closed-form cusps at all latitudes)
- `tests/houses/test_oracle_smoke.py` proves harness wiring with 6 pure-infra tests — no production-code dependencies (Plan 10-03 has not yet created `ketu/houses/`)
- The bytes-vs-str trap (Pitfall 8) and 13-tuple/0-indexed cusps trap (Pitfall 7) are now solved at the conftest layer; downstream test files never see them
- Full suite: **510 tests pass** (488 existing + 16 from Plan 10-01 + 6 from this plan); mypy `--strict` clean; `grep -r 'import swisseph' ketu/` returns nothing (production-code constraint preserved)

## Task Commits

1. **Task 1: conftest.py with swe_oracle helpers + reference_charts fixture** — `51c8de5` (feat)
2. **Task 2: JSON snapshot + smoke tests** — `ae41506` (test)

## Files Created/Modified

- `tests/houses/conftest.py` — module-level `pytest.importorskip("swisseph")` + `import swisseph as swe`; `SYSTEM_BYTES` mapping (`{placidus: b'P', koch: b'K', porphyry: b'O'}`); `swe_oracle(jd, lat, lon, system)` via `swe.houses_ex` with `cusps_t[1:13]` slice; `swe_oracle_armc(armc, lat, eps, system)` via `swe.houses_armc`; session-scoped `reference_charts` (10 entries) and `loaded_reference_snapshot` fixtures
- `tests/houses/fixtures/reference_charts.json` — `version: "v1.1-phase10-snapshot"`, `swisseph_version: "2.10.03"`, 10 charts × 3 systems; polar entries marked with `{error, polar: true}` for Placidus/Koch and full cusps for Porphyry; **641 lines, 20 KB, sha256 `b7762c9b7c255f6d8ecb382853d0cdacd7a5a1347964d3a377493790c6769581`**
- `tests/houses/test_oracle_smoke.py` — 6 tests: HOU-09 ≥10-floor, polar coverage, oracle shape, polar error marker, ARMC-direct API, snapshot-vs-live drift @ 1e-9 deg

## Reference Charts Table

| Label                | JD          | Lat (°)  | Lon (°)   | Coverage rationale                                |
| -------------------- | ----------- | -------: | --------: | ------------------------------------------------- |
| `J2000_Greenwich`    | 2451545.0   |  51.4779 |    0.0    | Reference meridian, mid-northern latitude         |
| `J2000_Paris`        | 2451545.0   |  48.8566 |    2.3522 | Mid-northern, non-zero longitude                  |
| `J2000_Sydney`       | 2451545.0   | -33.8688 |  151.2093 | Southern hemisphere, far-east longitude           |
| `J2000_Tokyo`        | 2451545.0   |  35.6762 |  139.6503 | Mid-northern, far-east longitude                  |
| `J2000_BuenosAires`  | 2451545.0   | -34.6037 |  -58.3816 | Southern hemisphere, west longitude               |
| `J2000_Equator`      | 2451545.0   |   0.0    |    0.0    | Degenerate-case stress (lat = 0)                  |
| `1900_NewYork`       | 2415020.5   |  40.7128 |  -74.0060 | 1900 boundary (epoch test)                        |
| `2050_Reykjavik`     | 2470204.0   |  64.1466 |  -21.9426 | 2050 boundary, near-polar (just under polar circle) |
| `J2000_Lat70_North`  | 2451545.0   |  70.0    |    0.0    | Polar (HOU-09 explicit)                           |
| `J2000_Lat80_North`  | 2451545.0   |  80.0    |    0.0    | Polar (HOU-09 explicit; far above polar circle)   |

## swisseph Version

- **`swe.version`**: `2.10.03` (matches Plan 10-01 audit baseline)
- **Snapshot version field**: `"v1.1-phase10-snapshot"` (allows future re-snapshotting without breaking older summaries)

## Polar Behavior Recorded

| Chart                  | Placidus                    | Koch                        | Porphyry                       |
| ---------------------- | --------------------------- | --------------------------- | ------------------------------ |
| `J2000_Lat70_North`    | `{error, polar: True}`      | `{error, polar: True}`      | full cusps + asc/mc/armc/vertex |
| `J2000_Lat80_North`    | `{error, polar: True}`      | `{error, polar: True}`      | full cusps + asc/mc/armc/vertex |

The exception message captured in both polar entries is `"swisseph.houses_ex: error"`. **Porphyry remains finite at all latitudes — that's why Plan 10-05 picks it as the polar fallback path.** Plan 10-05's pure-NumPy Porphyry implementation must reproduce the lat=80° porphyry cusps in the snapshot to within 1e-6 deg (or whatever tolerance Plan 10-05 fixes).

## File Pin (for Plan 10-06)

- **Path:** `tests/houses/fixtures/reference_charts.json`
- **Size:** 20 KB (641 lines)
- **SHA256:** `b7762c9b7c255f6d8ecb382853d0cdacd7a5a1347964d3a377493790c6769581`

Plan 10-06 integration tests can sha256-pin this file if a "no silent JSON drift" guarantee is desired beyond the smoke test's live-vs-snapshot fence.

## Decisions Made

- **SYSTEM_BYTES at the conftest boundary** — solves the bytes-vs-str trap once. `swe_oracle("placidus", ...)` callers never construct bytes literals.
- **Sliced `cusps_t[1:13]` in `swe_oracle`** — converts the swisseph 13-tuple (with placeholder `0.0` at index 0) into a 12-element 0-indexed numpy array. Pitfall 7 solved at the boundary.
- **Polar entries are first-class** — they encode the swisseph contract Plan 10-05 must reproduce. Skipping them ("we'll figure out polar later") would have left HOU-09 partially unsatisfied and Plan 10-05 without an oracle reference.
- **Snapshot file committed; snapshot script not committed** — the script is one-off scaffolding (lived at `snapshot_reference_charts_tmp.py` during execution; deleted after JSON regeneration). The JSON is the canonical artifact tracked in git. Per the plan's explicit anti-pattern guidance.
- **Snapshot-vs-live tolerance 1e-9 deg, not loose** — swisseph is deterministic; tightness is a feature (any drift = environmental change worth flagging).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] `mean_obliquity()` return-type mismatch in `swe_oracle_armc` test**

- **Found during:** Task 2 (mypy `--strict` on `test_oracle_smoke.py`)
- **Issue:** `ketu.ephemeris.coordinates.mean_obliquity()` is annotated as returning `float | np.ndarray` (vectorised), but `swe_oracle_armc(armc: float, lat: float, eps: float, system: str)` expects scalar `float`. Mypy `--strict` flagged: `Argument 3 to "swe_oracle_armc" has incompatible type "float | ndarray[...]"; expected "float"`.
- **Fix:** Cast `eps = float(mean_obliquity(2451545.0))` in `test_swe_oracle_armc_isolates_armc_from_sidereal_time` with an inline comment explaining the vectorised-return-type origin. The test was already passing at runtime — this is purely a static-typing correctness fix.
- **Files modified:** `tests/houses/test_oracle_smoke.py`
- **Verification:** `mypy --strict tests/houses/conftest.py tests/houses/test_oracle_smoke.py` → "Success: no issues found in 2 source files"; smoke tests still 6/6 PASSED.
- **Committed in:** `ae41506` (Task 2; the cast was already in the staged version when committed)

---

**Total deviations:** 1 auto-fixed (1 mypy correctness fix)
**Impact on plan:** No scope creep. The cast is a one-line trivial fix surfaced only by mypy `--strict` — a quality gate the plan explicitly required.

## Issues Encountered

- **None substantive.** Snapshot generated cleanly on first run; smoke tests passed first try; the only friction was the trivial `mean_obliquity` return-type cast (deviation #1 above).

- **`venv/bin/pytest` and `venv/bin/mypy` shebangs point to a stale path** (`/home/loc/workspace/solaris/ketu/venv/bin/python3`) — the project apparently moved cwd at some point. Worked around throughout execution by invoking `venv/bin/python -m pytest` and `venv/bin/python -m mypy`. **Carried-forward issue for someone to fix at their convenience** (`pip install --force-reinstall pytest mypy` from the venv would regenerate correct shebangs); does not block this plan.

## User Setup Required

None — purely internal test infrastructure. No env vars, no external services, no API changes.

## Verification

- `pytest tests/houses/test_oracle_smoke.py -v` → **6 passed** (or all skipped if swisseph absent — module-level `importorskip` gate)
- `pytest tests/` (full suite) → **510 passed** (488 + 16 Plan 10-01 + 6 Plan 10-02), 0 regressions
- `mypy --strict tests/houses/conftest.py tests/houses/test_oracle_smoke.py` → **Success: no issues found in 2 source files**
- `python -c "import json; d = json.load(open('tests/houses/fixtures/reference_charts.json')); assert len(d['charts']) == 10; assert all(s in d['charts']['J2000_Paris']['systems'] for s in ['placidus','koch','porphyry']); assert d['charts']['J2000_Lat80_North']['systems']['placidus'].get('polar') is True; assert 'cusps' in d['charts']['J2000_Lat80_North']['systems']['porphyry']"` → succeeds (10 charts, all systems present, polar marker correct, porphyry finite at lat=80°)
- `wc -l tests/houses/fixtures/reference_charts.json` → 641 (real content, not just `{}`)
- `grep -rn 'import swisseph\|from swisseph' ketu/` → **no hits** — swisseph remains test-only optional dep

## Next Phase Readiness

- **Plan 10-03 (registry/dtype/ascmc):** can `from tests.houses.conftest import swe_oracle` to validate ascmc shape/units; the `reference_charts` fixture provides session-scoped lat/lon/jd inputs.
- **Plan 10-04 (Placidus implementation):** can `from tests.houses.conftest import swe_oracle_armc` to feed ketu's GST/obliquity into swisseph's Placidus and isolate algorithm error from sidereal-time error. Plan 10-01's `sidereal_time()` is now apparent GST, so direct comparison is meaningful.
- **Plan 10-05 (Koch / Porphyry / polar):** the lat=80° porphyry cusps in the snapshot are the canonical oracle for the polar Porphyry-fallback design. Placidus/Koch error markers at lat=70°/80° encode the polar boundary Plan 10-05 must respect (raise / fall back).
- **Plan 10-06 (integration tests):** parametrize over `[("placidus", "koch", "porphyry") × 8 non-polar charts]` = 24 oracle-agreement cases; the JSON pin (sha256 above) lets 10-06 fail loudly on any silent drift.
- **Wave 3 unblock:** Plans 10-04 and 10-05 can run in parallel, both reading the same fixture JSON without modifying it.

## Self-Check: PASSED

All claimed artifacts verified on disk and in git log:

- `tests/houses/conftest.py` — present (244 lines: SYSTEM_BYTES, swe_oracle, swe_oracle_armc, reference_charts fixture, loaded_reference_snapshot fixture)
- `tests/houses/fixtures/reference_charts.json` — present (641 lines, 20 KB, sha256 b7762c9b…6769581, 10 charts × 3 systems)
- `tests/houses/test_oracle_smoke.py` — present (6 tests, all passing)
- `.planning/phases/10-houses-module/10-02-SUMMARY.md` — present (this file)
- Commit `51c8de5` (Task 1 — conftest.py) — present in `git log --all`
- Commit `ae41506` (Task 2 — JSON snapshot + smoke tests) — present in `git log --all`

---
*Phase: 10-houses-module*
*Plan: 02*
*Completed: 2026-05-07*
