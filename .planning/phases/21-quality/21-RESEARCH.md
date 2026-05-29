# Phase 21: Quality — Research

**Researched:** 2026-05-29
**Domain:** Python test coverage, numerical guard, docstring doctests
**Confidence:** HIGH — all findings are direct codebase observations, zero web lookups needed.

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Div/0 guard (QAL-11)**
- Strategy: FLOOR `r`, not clamp. Apply `np.maximum(r, 1e-10)` before the `arcsin(z / r)` division at `orbital.py:755`.
- Epsilon = `1e-10`.
- Scope: ALL equivalent sites. Audit `orbital.py` and rest of `ketu/ephemeris/` for any division by `r` or same-shape `arcsin` and guard consistently.
- Regression test asserts the full contract: force `r→0`, assert (1) no `RuntimeWarning` (via `warnings.catch_warnings` + `filterwarnings("error")`), (2) no `NaN` in latitude, (3) latitude in `[-90, 90]`.

**Docstring depth (QAL-12)**
- Scope: exported public API = everything in `ketu/__init__.py` `__all__` plus subpackage `api.py` surfaces.
- Language: English.
- Examples: real, CI-collected doctests (`>>>` with actual outputs, collected by `pytest --doctest-modules`).
- Determinism: fixed dates/JD + rounded output (`round(x, 2)`) or `ELLIPSIS`.
- Notes cover accuracy vs Swiss + edge cases (precision, supported date range, limit behavior).

**Coverage strategy (QAL-10)**
- Targeted tests, ZERO pragmas. Every missing line covered by a real test.
- `_ecliptic.py` outlier: assert known astronomical values + round-trip identity.

**Quality gate scope (QAL-10)**
- `fail_under` 70 → 100 in `pyproject.toml`.
- Existing `omit` list unchanged (`ketu/__main__.py`, `ketu/lunar_calendar.py`).
- Per-subpackage 95% Makefile gates kept as-is.

### Claude's Discretion
- Exact set of additional regression tests to close remaining (non-`_ecliptic`) coverage gaps.
- Precise wording/structure of each docstring's Examples and Notes.
- How `--doctest-modules` is wired into pytest config/CI without breaking partial runs.

### Deferred Ideas
None.
</user_constraints>

---

## Summary

Current project coverage is **97.90%** (66 lines missed across 3149 statements), baseline from a clean `pytest` run. The gap inventory below is the exact planner input for 21-01. The `ketu/houses/_ecliptic.py` file is the most severe outlier at 64% (10 lines), as called out in requirements; the remaining 56 missed lines are scattered across 18 files and are individually small (1–7 lines each).

The div/0 site at `orbital.py:755` is confirmed. However, the audit reveals **9 additional `arcsin(z / r)` call sites** across `orbital.py` (lines 353, 405, 436, 462, 503, 558, 813) and `coordinates.py` (line 86). Of those, `coordinates.py:86` already has an inline guard; the scalar path at `orbital.py:353` uses a scalar `r`; the perturbation paths (405, 436, 462) use scalar r computed inside `apply_perturbations`; and `orbital.py:503, 558, 813` are analogous. The vectorised path at line 755 (inside `get_body_position_vectorized`) is the highest-risk site. The CONTEXT decision to guard "all equivalent sites" means each must be evaluated case by case.

Existing doctests in `ketu/calculations.py` are broken (stale expected values) and must be fixed before `--doctest-modules` can be enabled. Several docstrings use `# doctest: +SKIP` patterns that should be replaced with real runnable examples.

**Primary recommendation:** Execute in three focused plans — (1) close all coverage gaps with targeted tests + lift `fail_under` to 100; (2) guard all `arcsin(z / r)` division sites in `ketu/ephemeris/`; (3) fix broken doctests, add missing Examples/Notes, wire `--doctest-modules` into CI as a separate gate.

---

## 1. Actual Coverage Gaps (QAL-10)

**Current total: 97.90% (66 missed lines / 3149 statements)**

Run command that produced this: `python3 -m pytest --cov=ketu --cov-report=term-missing -q`
(The venv shebang points to a moved path; use `python3 -m pytest` or `python -m pytest` per Makefile convention.)

### Gap inventory — exact file:line table

| File | Lines missed | % cover | Pattern / what it is |
|------|-------------|---------|---------------------|
| `ketu/houses/_ecliptic.py` | 43-47, 69-73 | 64% | `ra_to_lambda` body (lines 43-47) and `lambda_to_ra` body (lines 69-73) — RA↔λ converters for Placidus/Koch, never called by the existing test suite |
| `ketu/houses/api.py` | 120, 241-254 | 84% | Line 120: `raise ValueError` for bad `polar_fallback` arg. Lines 241-254: entire `house_of()` function body (the function exists but zero direct coverage — existing tests use `calculate_houses` and don't call `house_of` directly) |
| `ketu/aspects/core.py` | 68-69, 185, 336, 380, 409, 428 | 94% | 68-69: `raise ValueError` for unknown aspect angle; 185: `return best_jd` in `refine_exact_moment`; 336: `offset = 0.0` branch in `interpolate_minimum`; 380: clamp `relative_speed` floor; 409: retrograde return; 428: `estimate_duration_hours` return |
| `ketu/aspects/timelines.py` | 431, 443, 452, 472, 497-499 | 96% | 431: `tz = timezone` (ZoneInfo branch); 443, 452: datetime with no tzinfo replacement; 472, 497-499: int/float aspect type handling + error branch |
| `ketu/aspects/windows.py` | 343, 350, 449, 458, 466 | 96% | 343: `continue` on `jd_exact is None`; 350: `continue` on None boundaries; 449: aspect\_list is None default; 458: datetime JD conversion; 466: float start\_date path |
| `ketu/calculations.py` | 170, 172, 174 | 94% | Lines 170-174: `body_name` branches for `"true Node"` and `"mean Apogee"` ("North Node" / "Lilith" aliases) — covered if test calls `body_name(11)` or `body_name(12)` |
| `ketu/cycles/calculator.py` | 26-29, 222 | 96% | 26-29: `CACHE_AVAILABLE = False` branch (ImportError); 222: `use_ephemeris_cache` branch with float timestamps |
| `ketu/ephemeris/time.py` | 88, 369 | 98% | 88: `A = Z` Julian calendar branch (JD < 2299161, i.e. pre-1582-10-15); 369: `gst += 360.0` branch (gst < 0) |
| `ketu/ephemeris/orbital.py` | 227 | 99% | `angle += 360.0` branch in `normalize_angle` — needs a negative-valued angle input |
| `ketu/ephemeris/planets.py` | 354, 362, 448 | 99% | 354: `return jd_mid` early exit; 362: `return (left+right)/2` fallback return in `find_exact_aspect`; 448: `avg_speed == 0` guard in `calculate_speed_ratio` |
| `ketu/houses/koch.py` | 132-133 | 95% | polar mask branch: `if polar_mask.any():` → NaN-out path |
| `ketu/houses/regiomontanus.py` | 152-153 | 95% | Same polar mask branch as koch.py |
| `ketu/houses/porphyry.py` | 100 | 98% | `return result` array path in `is_polar` — returned as ndarray, not bool |
| `ketu/cache/ephemeris_cache.py` | 391 | 99% | `next_year, next_month` boundary calculation branch (month==12 rollover) |
| `ketu/cli/harmonics_spec.py` | 80-81, 93 | 92% | 80-81: defensive `except ValueError` in preset branch; 93: empty harmonics list error |
| `ketu/cli/aspects_cmd.py` | 65 | 98% | `return "custom"` branch when aspect mask matches no named preset |
| `ketu/cli/houses_cmd.py` | 74 | 97% | `raise SystemExit` for bad cusp count (Ketu bug diagnostic) |
| `ketu/cli/synastry_cmd.py` | 70 | 98% | `raise ValueError` for invalid body index in synastry CLI |
| `ketu/complex.py` | 421 | 99% | `return self.radians + 2 * math.pi` — `CycleRatio.normalized_radians` negative radians branch |
| `ketu/display.py` | 28 | 96% | `from .aspects.presets import AspectSetSpec` inside `if TYPE_CHECKING:` — this is dead runtime code, covered only if `TYPE_CHECKING is True` which never happens. **This line cannot be covered at runtime without a pragma.** Needs investigation — possibly already excluded by `exclude_lines` patterns, or needs `pragma: no cover` per project policy (but project has zero pragmas — see note). |

**Note on `display.py:28`:** Line 28 is `from .aspects.presets import AspectSetSpec` inside an `if TYPE_CHECKING:` block. Coverage.py counts this as executable but it never runs (TYPE_CHECKING is always False at runtime). The existing `exclude_lines` in `pyproject.toml` does NOT exclude TYPE_CHECKING guards. However, adding `pragma: no cover` violates QAL-10's "ZERO pragmas" constraint. Resolution: add `"if TYPE_CHECKING:"` to `exclude_lines` in `[tool.coverage.report]` — this is a standard pattern that does not violate the spirit of no-pragma. Alternatively, the test could `mock TYPE_CHECKING` but that's fragile. Planner must decide: add `"if TYPE_CHECKING:"` to `exclude_lines`, or find another approach. This is the one genuine open question.

---

## 2. Div/0 Guard Sites (QAL-11)

### Confirmed primary site

**`ketu/ephemeris/orbital.py:755`** — inside `get_body_position_vectorized()`:
```python
lat = np.rad2deg(np.arcsin(z / r))
```
`r` is computed as `np.sqrt(x_prime**2 + y_prime**2)` where `x_prime = a * (cos(E) - e)`, `y_prime = a * sqrt(1-e^2) * sin(E)`. Physically `r` is the heliocentric distance in AU — it cannot be zero for real orbits, but can be zero if `a=0` or `e=1` (degenerate orbit). The RuntimeWarning is already fired and observed in CI output during the test run (confirmed: `orbital.py:755: RuntimeWarning: invalid value encountered in divide` appears in pytest warnings).

**How to force r→0 in test:** Call `get_body_position_vectorized(body_id, jd_array)` with a patched orbital element where `a=0` (or use `unittest.mock.patch.dict` to override `ORBITAL_ELEMENTS[body_id]`). Alternatively, patch `numpy.sqrt` to return zero for a specific input — but the cleanest approach is monkeypatching `ORBITAL_ELEMENTS[0]` with `a=0.0` for the test duration.

### All additional `arcsin(z / r)` sites — full audit

| File | Line | Function | `r` computed as | Current guard? |
|------|------|----------|----------------|---------------|
| `ketu/ephemeris/orbital.py` | 353 | `compute_position` (scalar) | `sqrt(x'^2+y'^2)` from Kepler | None |
| `ketu/ephemeris/orbital.py` | 405 | `apply_perturbations` — Jupiter branch | `sqrt(x^2+y^2+z^2)` from perturbed xyz | None |
| `ketu/ephemeris/orbital.py` | 436 | `apply_perturbations` — Saturn branch | same | None |
| `ketu/ephemeris/orbital.py` | 462 | `apply_perturbations` — Uranus branch | same | None |
| `ketu/ephemeris/orbital.py` | 503 | `get_body_position` after perturbation | `sqrt(x^2+y^2+z^2)` | None |
| `ketu/ephemeris/orbital.py` | 558 | `get_moon_position` (scalar) | `sqrt(x'^2+y'^2)` | None |
| `ketu/ephemeris/orbital.py` | 813 | `get_moon_position_vectorized` | `sqrt(x'^2+y'^2)` | None |
| `ketu/ephemeris/coordinates.py` | 86 | `rectangular_to_spherical` | `sqrt(x^2+y^2+z^2)` | **YES** — scalar path returns `(0,0,0)` early; array path replaces zeros with 1.0 |

**Verdict:** `coordinates.py:86` is already guarded (different strategy: scalar early-return, array replace). The 7 remaining orbital.py sites are unguarded.

**Guard scope decision for planner:** CONTEXT says "guard consistently." Since physical orbits never produce r=0 in normal operation, the FLOOR strategy (`np.maximum(r, 1e-10)`) is the right fix. For scalar sites (353, 558), use `max(r, 1e-10)` or `r if r > 1e-10 else 1e-10`. For vectorized sites (755, 813), use `np.maximum(r, 1e-10)`. For the perturbation sites (405, 436, 462, 503), the `r` is recomputed inside the function — same pattern applies.

---

## 3. `--doctest-modules` Wiring (QAL-12 + discretion)

### Current pytest configuration

From `pyproject.toml [tool.pytest.ini_options]`:
```toml
addopts = "-v --cov=ketu --cov-report=term-missing"
```
The comment explicitly says: **do NOT add `--cov-fail-under` here** to allow partial runs. There is no `--doctest-modules` in `addopts`.

### Existing doctests state

- **215 non-skipped `>>>` lines** exist across `ketu/`. Many are in `ketu/calculations.py` and have **stale expected values** (confirmed: 14/15 doctests in `calculations.py` fail when run with `--doctest-modules` because the expected outputs are wrong — e.g. `dd_to_dms(123.456)` expects `[123, 27, 22]` but returns `[123, 27, 21]`).
- `ketu/__init__.py` doctest expects `'Sun'` (with quotes from `print()`) but `print(str)` never outputs quotes — fails.
- `ketu/houses/api.py`: `house_of(45.0, ...)` expects `2` but returns `1` — stale.
- Several `ketu/charts/api.py` examples use `# doctest: +SKIP` — these are not collected and do not fail, but they also do not count as "runnable."
- `ketu/composite/api.py`: `calculate_composite` Examples section says "See `circular_midpoint`" with no `>>>` lines at all — has no examples.

### Recommendation for wiring (discretion area)

**Do NOT add `--doctest-modules` to `addopts`** — this would break every partial run that doesn't exercise all modules (same rationale as `--cov-fail-under`).

**Recommended approach:** Add a dedicated Makefile target and CI step:

```makefile
## doctest: Collect and run all module doctests.
doctest:
    $(PYTHON) -m pytest --doctest-modules ketu/ --no-cov -q \
        --ignore=ketu/lunar_calendar.py \
        --ignore=ketu/__main__.py
```

CI change: add a new step in `.github/workflows/tests.yml` (python-version == '3.13' block):
```yaml
- name: Module doctests
  if: matrix.python-version == '3.13'
  run: |
    python -m pytest --doctest-modules ketu/ --no-cov -q \
      --ignore=ketu/lunar_calendar.py \
      --ignore=ketu/__main__.py
```

**Important:** Before enabling, ALL existing broken doctests in scope must be fixed (see §4 below). The `--no-cov` avoids the NumPy `_NoValueType` reload issue documented in Makefile comments.

**Alternative:** Use `doctest_optionflags = ["ELLIPSIS", "NORMALIZE_WHITESPACE"]` in `[tool.pytest.ini_options]` as a project-wide default so docstrings can use `...` for variable parts without per-doctest directives.

---

## 4. Public API Docstring Inventory (QAL-12)

### `ketu/__init__.py` `__all__` surface

These 9 symbols are the top-level public API:

| Symbol | Type | Has Examples? | Has Notes? | Status |
|--------|------|--------------|-----------|--------|
| `bodies` | structured array | YES (broken — `'Sun'` vs `Sun`) | YES (module docstring) | Fix example |
| `aspects` | structured array | YES (broken — same block) | YES | Fix example |
| `signs` | structured array | YES (same block) | YES | Fix example |
| `HOUSES_DTYPE` | dtype | No | No | Add |
| `HighLatitudeError` | exception | No | No | Add |
| `HOUSE_SYSTEMS` | dict | No | No | Add |
| `calculate_houses` | function | YES (real, works) | YES | OK — verify still accurate |
| `house_of` | function | YES (broken — returns 1 not 2) | YES | Fix example |
| `__version__`, `__author__`, `__license__` | str | N/A | N/A | Skip (not functions) |

### Subpackage `api.py` surfaces

**`ketu/houses/api.py`** (`calculate_houses`, `house_of`): `calculate_houses` has real working doctests. `house_of` has a broken doctest (expected `2`, actual `1`).

**`ketu/charts/api.py`** (`compute_chart`, `is_day_chart`):
- `compute_chart`: has Examples section with `# doctest: +SKIP` on all lines — no runnable example. Needs real `>>>` with fixed JD.
- `is_day_chart`: has real runnable doctests (verified present) — check if they pass.

**`ketu/composite/api.py`** (`calculate_composite`, `circular_midpoint` — check `__all__`):
- `calculate_composite`: Examples section says "See `circular_midpoint`" — zero `>>>` lines. Needs runnable example.
- Requires `compute_chart` first, so example needs either `# doctest: +SKIP` (unacceptable per QAL-12) or a self-contained fixture.

**`ketu/synastry/api.py`** (`calculate_synastry`):
- Has Examples with all lines `# doctest: +SKIP`. Needs real examples.

**`ketu/parts/api.py`** (`calculate_part`, `calculate_all_parts`):
- Both have Examples with all lines `# doctest: +SKIP`. Need real examples.
- Challenge: `calculate_part` requires a CHART_DTYPE input from `compute_chart` — same determinism issue.

**`ketu/returns/` api surface** (`solar_return`, `lunar_return` in `ketu/returns/solar.py`, `ketu/returns/lunar.py`):
- `ketu/returns/solar.py:159-160` has a `>>>` without expected output (narrative-only) — incomplete doctest.

### Notes coverage (accuracy vs Swiss, edge cases)

Most `api.py` functions have detailed Notes sections. The primary gap is **runnable Examples** (not Notes). Functions that already have strong Notes: `calculate_composite`, `house_of`, `calculate_houses`. Functions needing Notes additions: `calculate_part`, `calculate_all_parts` (no accuracy caveats about the non-Swiss implementation).

### Broken doctests to fix before enabling `--doctest-modules`

| File | Symbol | Issue |
|------|--------|-------|
| `ketu/__init__.py` | module docstring | `print(x)` expected `'Sun'` but prints `Sun` (no quotes) |
| `ketu/calculations.py` | `dd_to_dms` | expects `[123, 27, 22]` gets `[123, 27, 21]` (rounding) |
| `ketu/calculations.py` | `body_properties`, `long`, `lat`, etc. | stale planetary positions for 2025-01-15 (values changed?) |
| `ketu/houses/api.py` | `house_of` | expected `2` gets `1` |

**Key insight on `calculations.py` failures:** The Sun longitude for `utc_to_julian(datetime(2025, 1, 15, 12, 0, tzinfo=timezone.utc))` is returning `295.59°` not `294.82°`. This could be a JD computation difference or ephemeris change. Either the docstring expected values are wrong, or there was a subtle calculation change. All date-based expected values need to be re-verified by running the actual computation and noting the result.

---

## 5. Test Structure & Patterns

### Directory layout

```
tests/
├── houses/           # sub-dir with conftest.py + swisseph oracle
├── charts/           # similar sub-dir pattern
├── synastry/         # similar
├── composite/        # similar
├── returns/          # similar
├── parts/            # similar
├── test_coverage_improvements.py  # catch-all for gap tests
├── test_ketu.py      # main integration tests
└── test_*.py         # per-module tests
```

### Conventions observed

1. **Class-based grouping:** `class TestFunctionName:` with `setup_method` for shared fixtures.
2. **Direct import with JD:** Tests use `utc_to_julian(datetime(..., tzinfo=ZoneInfo("UTC")))` or raw JD values like `2451545.0`.
3. **No conftest at root level** (except `tests/houses/conftest.py` etc.) — no project-wide fixtures.
4. **Swisseph tests skipped when absent:** `pytest.importorskip("swisseph")` at module level in conftest.
5. **RuntimeWarning tests:** Use `warnings.catch_warnings()` + `warnings.filterwarnings("error")` to assert no warnings are emitted — confirmed in project, pattern to follow for QAL-11 regression test.
6. **No `# pragma: no cover` anywhere in the codebase** — confirmed by grep.

### numpydoc/interrogate invocation

- **Makefile target:** `make doc-gates` runs both: `python -m interrogate ketu/` then `python -m numpydoc lint $(find ketu -name "*.py" ! -path "*/__pycache__/*" ! -name "lunar_calendar.py" ! -name "_*.py")`.
- **numpydoc excludes:** `_*.py` files (all internal helpers) are excluded. `lunar_calendar.py` excluded.
- **CI:** Both gates run on Python 3.13 only, as separate `if: matrix.python-version == '3.13'` steps.
- **interrogate config:** `fail-under = 95`, `ignore-init-method = true`, `ignore-magic = true`, `ignore-nested-functions = true`.
- **numpydoc config:** checks `"all"` but ignores EX01 (no examples required), SA01 (no See Also required), ES01 (no extended summary required). The `EX01` ignore means missing Examples does NOT currently fail numpydoc — adding Examples is qualitative improvement only, not a breaking change to existing gates.
- **EX01 implications for QAL-12:** Adding `--doctest-modules` to CI (new gate) is the only way to enforce that Examples are *runnable*. The existing numpydoc gate does not enforce Examples presence or correctness.

### Coverage gate details

`pyproject.toml [tool.coverage.report]`:
```toml
fail_under = 70   # → change to 100 for QAL-10
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
]
```

The `display.py:28` (`if TYPE_CHECKING:`) case requires either adding `"if TYPE_CHECKING:"` to `exclude_lines`, or a `pragma: no cover` on that specific line. Since QAL-10 mandates ZERO pragmas, recommend adding `"if TYPE_CHECKING:"` to `exclude_lines` (standard practice, preserves the zero-pragma policy spirit).

---

## Open Questions

1. **`display.py:28` (`if TYPE_CHECKING:` block):** Cannot be covered at runtime without mocking. Recommend adding `"if TYPE_CHECKING:"` to `[tool.coverage.report] exclude_lines` in `pyproject.toml`. This is the only line that cannot be covered by a real test without contorting the code.

2. **`calculations.py` doctest values:** Before fixing, planner should run the computation live to get current correct values. The 2025-01-15 ephemeris output appears to have changed (`294.82` → `295.59` for Sun longitude). Either use dates where the output is stable and verifiable, or add `round(x, 1)` + `# doctest: +ELLIPSIS` patterns.

3. **`composite/api.py` and `synastry/api.py` runnable doctests:** These require a `compute_chart` call first. Options: (a) use a pre-known JD where outputs are stable and embed expected structured-array field values; (b) only assert `.shape` or dtype fields (deterministic regardless of date). The CONTEXT says "real, CI-collected doctests" — option (b) is cleanest.

---

## Sources

All findings are direct codebase reads and `pytest` execution. Confidence: HIGH.

- `/home/loc/workspace/ketu/pyproject.toml` — pytest config, coverage config, interrogate/numpydoc config
- `/home/loc/workspace/ketu/Makefile` — make targets, two-step coverage pattern
- `/home/loc/workspace/ketu/.github/workflows/tests.yml` — CI gate configuration
- `/home/loc/workspace/ketu/ketu/ephemeris/orbital.py` — div/0 sites (lines 353, 405, 436, 462, 503, 558, 755, 813)
- `/home/loc/workspace/ketu/ketu/ephemeris/coordinates.py` — existing guard at line 83-86
- `pytest --cov=ketu --cov-report=term-missing -q` — live coverage run, 97.90%, 66 missed lines

---

## RESEARCH COMPLETE

**Phase:** 21 — Quality
**Confidence:** HIGH

### Key Findings

1. **Coverage gap is 66 lines / 97.90%** — not 100%. The `_ecliptic.py` outlier (10 lines, 64%) plus 56 scattered lines across 18 files. No file has more than 10 missed lines; most have 1-6. Full table above.

2. **Div/0 at `orbital.py:755` confirmed** — the RuntimeWarning already fires during `pytest` (visible in warnings output). There are **8 unguarded `arcsin(z / r)` sites in `orbital.py`** (lines 353, 405, 436, 462, 503, 558, 755, 813) plus one already-guarded site in `coordinates.py:86`.

3. **Existing doctests are broken** — 14 of 15 in `calculations.py` fail; `__init__.py` module doctest fails; `houses/api.py:house_of` fails. Must fix before `--doctest-modules` gate can be enabled. The failures are stale expected values, not structural issues.

4. **`--doctest-modules` must NOT go in `addopts`** — use a separate Makefile target + CI step to avoid breaking partial runs (same constraint as `--cov-fail-under`).

5. **`display.py:28` is an `if TYPE_CHECKING:` import** — cannot be covered at runtime. Add `"if TYPE_CHECKING:"` to `exclude_lines` in `pyproject.toml` to reach 100% without violating the zero-pragma policy.

### File Created
`.planning/phases/21-quality/21-RESEARCH.md`

### Confidence Assessment
| Area | Level | Reason |
|------|-------|--------|
| Coverage gap inventory | HIGH | Direct `pytest --cov` run, exact line numbers |
| Div/0 sites | HIGH | grep + read of all source files |
| Doctest wiring | HIGH | Confirmed by running `--doctest-modules` locally |
| Public API docstring surface | HIGH | Direct file reads of all api.py files |
| Test patterns | HIGH | Read of conftest, test files, Makefile |

### Open Questions
- `display.py:28` (`if TYPE_CHECKING:`): add to `exclude_lines` or accept as a 1-line pragma exception
- `calculations.py` stale doctest values: re-run and capture current outputs before writing fixed docstrings
