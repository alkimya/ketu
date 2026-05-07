---
phase: 10-houses-module
plan: 06
type: execute
wave: 4
depends_on:
  - "10-04"
  - "10-05"
files_modified:
  - ketu/houses/__init__.py
  - ketu/houses/api.py
  - ketu/ephemeris/planets.py
  - ketu/ephemeris/__init__.py
  - pyproject.toml
  - tests/test_planets_coverage.py
  - tests/houses/test_house_of.py
  - tests/houses/test_integration.py
autonomous: true
plan_id: "10-06"
requirements:
  - HOU-07
  - HOU-10

must_haves:
  truths:
    - "calculate_houses(jd, lat, lon, system='placidus', polar_fallback='raise') returns ndarray of HOUSES_DTYPE; vectorized inputs preserve leading shape"
    - "calculate_houses dispatches via SYSTEMS[system.lower()] — no if-elif ladder anywhere"
    - "polar_fallback='raise' (default): HighLatitudeError raised when |lat| > polar_circle(jd)"
    - "polar_fallback='porphyry': polar elements get porphyry_cusps; non-polar elements get the requested system; returns the dtype's mixed-source array correctly"
    - "house_of(planet_lon, cusps) returns 1-12 int (or ndarray of int) for any longitude; vectorized over both planet_lon and cusps"
    - "calculate_house_cusps stub is REMOVED from ketu/ephemeris/planets.py; ketu/ephemeris/__init__.py no longer exports it; tests/test_planets_coverage.py loses the stub-related tests"
    - "ketu.houses module coverage is ≥95% via pytest-cov on tests/houses/"
    - "Coverage gate is wired into committed config: pyproject.toml [tool.pytest.ini_options] addopts includes --cov=ketu and --cov-report=term-missing project-wide; the houses-specific 95% threshold lives in a documented script/Makefile target (`pytest tests/houses/ --cov=ketu.houses --cov-fail-under=95`) so a bare `pytest tests/` cannot silently miss the gate"
    - "Public API: ketu.calculate_houses, ketu.house_of, ketu.HOUSES_DTYPE, ketu.HighLatitudeError, ketu.HOUSE_SYSTEMS all importable at the top level"
    - "Migration note in CHANGELOG.md (or scratch note for Plan 12 release prep) documents the calculate_house_cusps removal as a breaking change"
  artifacts:
    - path: "ketu/houses/api.py"
      provides: "Real implementations of calculate_houses (with SYSTEMS dispatch + polar_fallback) and house_of (vectorized), replacing the stubs in __init__.py"
      contains: "def calculate_houses"
      min_lines: 80
    - path: "ketu/houses/__init__.py"
      provides: "Updated to import calculate_houses and house_of FROM api.py instead of stubs"
      contains: "from .api import"
    - path: "ketu/ephemeris/planets.py"
      provides: "calculate_house_cusps function REMOVED; file shorter by ~40 lines"
      min_lines: 0
    - path: "ketu/ephemeris/__init__.py"
      provides: "calculate_house_cusps removed from imports and __all__"
      contains: "__all__"
    - path: "tests/test_planets_coverage.py"
      provides: "calculate_house_cusps tests REMOVED (lines ~186-269 per state.md research)"
      contains: "from ketu.ephemeris"
    - path: "tests/houses/test_house_of.py"
      provides: "house_of correctness tests: scalar, vectorized over planet_lon, vectorized over cusps, edge cases (cusp boundary, planet at cusp exact)"
      contains: "house_of"
      min_lines: 60
    - path: "tests/houses/test_integration.py"
      provides: "End-to-end calculate_houses tests: HOUSES_DTYPE structure, dispatch through SYSTEMS, polar_fallback='raise' raises, polar_fallback='porphyry' returns mixed result, mid-lats no error, vectorized over (jd, lat, lon) preserves shape, ≥95% coverage gate"
      contains: "calculate_houses"
      min_lines: 100
  key_links:
    - from: "ketu/houses/api.py"
      to: "ketu.houses.registry SYSTEMS"
      via: "SYSTEMS[system.lower()] dispatch — no inline if/elif"
      pattern: "SYSTEMS\\["
    - from: "ketu/houses/api.py"
      to: "ketu.houses.porphyry is_polar, porphyry_cusps"
      via: "polar detection + fallback"
      pattern: "is_polar|porphyry_cusps"
    - from: "ketu/houses/api.py"
      to: "ketu.houses.ascmc compute_ascmc"
      via: "ARMC + ASC + MC + Vertex computation"
      pattern: "compute_ascmc"
    - from: "ketu/__init__.py"
      to: "ketu.houses calculate_houses, house_of, HOUSES_DTYPE, HighLatitudeError, HOUSE_SYSTEMS"
      via: "top-level public API re-export"
      pattern: "from ketu\\.houses import"
    - from: "pyproject.toml [tool.pytest.ini_options]"
      to: "ketu.houses coverage gate"
      via: "addopts wires --cov=ketu --cov-report=term-missing project-wide; HOU-09 95% gate runs as `pytest tests/houses/ --cov=ketu.houses --cov-fail-under=95` (documented Makefile target / SUMMARY note)"
      pattern: "tool\\.pytest\\.ini_options"
---

<objective>
Wire all the Phase 10 pieces together into a cohesive public API: a real `calculate_houses` that dispatches through `SYSTEMS` and handles `polar_fallback`; a real `house_of(planet_lon, cusps)` helper (HOU-07); and the **removal of the broken `calculate_house_cusps` stub** from `ephemeris/planets.py` (HOU-10). Close the phase with end-to-end integration tests and verify the ≥95% coverage gate on `ketu.houses`.

Purpose: Plans 10-03 stubs `calculate_houses`/`house_of` raising `NotImplementedError`. Plans 10-04 and 10-05 register Placidus/Koch/Porphyry into SYSTEMS. This plan replaces the stubs with the real bodies, removes the equal-house placeholder that's been wrongly named `calculate_house_cusps` in `ephemeris/planets.py` since v0.x, and proves the surface works end-to-end. The HOU-10 stub-removal is scheduled LAST (this plan, Wave 4) per the quality_gate constraint: "HOU-10 stub removal scheduled AFTER HOU-02..HOU-08 land (so we don't break the public surface mid-phase)."

Output:
- `ketu/houses/api.py` — real `calculate_houses` and `house_of` implementations.
- `ketu/houses/__init__.py` — imports from api.py, removes the NotImplementedError stubs.
- `ketu/ephemeris/planets.py` — `calculate_house_cusps` function deleted (~40 lines removed).
- `ketu/ephemeris/__init__.py` — import + __all__ entry for `calculate_house_cusps` removed.
- `tests/test_planets_coverage.py` — stub-related tests deleted (lines ~186-269).
- `tests/houses/test_house_of.py` — house_of correctness tests.
- `tests/houses/test_integration.py` — end-to-end calculate_houses tests + coverage gate.
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
@.planning/phases/10-houses-module/10-03-registry-dtype-ascmc-PLAN.md
@.planning/phases/10-houses-module/10-04-placidus-implementation-PLAN.md
@.planning/phases/10-houses-module/10-05-koch-porphyry-polar-PLAN.md

# Files this plan modifies
@ketu/houses/__init__.py
@ketu/houses/registry.py
@ketu/houses/ascmc.py
@ketu/houses/porphyry.py
@ketu/ephemeris/planets.py
@ketu/ephemeris/__init__.py
@tests/test_planets_coverage.py
</context>

<tasks>

<task type="auto">
  <name>Task 1: Implement calculate_houses (with polar_fallback) and house_of in ketu/houses/api.py; rewire __init__.py</name>
  <files>ketu/houses/api.py
ketu/houses/__init__.py</files>
  <action>
    Step A — Create `ketu/houses/api.py`. The two key public functions:

    ```python
    """Public API for the houses subpackage.

    calculate_houses() — dispatches through SYSTEMS, handles polar_fallback.
    house_of() — assigns a planet longitude to its 1-indexed house.
    """
    from __future__ import annotations
    from typing import Literal, Union, cast
    import numpy as np

    from .core import HOUSES_DTYPE, HighLatitudeError
    from .registry import SYSTEMS, get_system
    from .ascmc import compute_ascmc
    from .porphyry import is_polar, polar_circle, porphyry_cusps


    ArrayLike = Union[float, np.ndarray]


    def calculate_houses(
        jd: ArrayLike,
        lat: ArrayLike,
        lon: ArrayLike,
        system: str = "placidus",
        polar_fallback: Literal["raise", "porphyry"] = "raise",
    ) -> np.ndarray:
        """Compute house cusps for one or many (jd, lat, lon) inputs.

        Parameters
        ----------
        jd : float or np.ndarray (Julian Date, UT)
        lat : float or np.ndarray (geographic latitude, deg)
        lon : float or np.ndarray (geographic longitude, east-positive, deg)
        system : str, optional
            House system name: "placidus" (default), "koch", "porphyry", or
            any name registered via `ketu.houses.registry.register`.
            Case-insensitive.
        polar_fallback : {"raise", "porphyry"}, optional
            Behavior when |lat| > polar_circle(jd) (≈ 66.56°):
            - "raise" (default): raise HighLatitudeError for those elements.
            - "porphyry": substitute Porphyry cusps for the polar elements;
              non-polar elements get the requested `system`.

        Returns
        -------
        np.ndarray of HOUSES_DTYPE — leading shape == broadcast of (jd, lat, lon).
            Fields: jd, lat, lon, system, cusps[12], asc, mc, armc, vertex.

        Raises
        ------
        HighLatitudeError
            When polar_fallback='raise' and |lat| > polar_circle(jd) for any
            input element.
        ValueError
            When `system` is not registered or polar_fallback is invalid.

        Examples
        --------
        >>> import numpy as np
        >>> r = calculate_houses(2451545.0, 48.8566, 2.3522, system="placidus")
        >>> r["asc"], r["mc"]   # close to 26.77° and 281.78° respectively
        (26..., 281...)
        >>> r["cusps"].shape
        (12,)
        >>> r_batch = calculate_houses(
        ...     np.array([2451545.0, 2470204.0]),
        ...     np.array([48.8566, 64.1466]),
        ...     np.array([2.3522, -21.9426]),
        ...     system="koch", polar_fallback="porphyry",
        ... )
        >>> r_batch.shape, r_batch["cusps"].shape
        ((2,), (2, 12))
        """
        if polar_fallback not in ("raise", "porphyry"):
            raise ValueError(
                f"polar_fallback must be 'raise' or 'porphyry'; got {polar_fallback!r}"
            )

        sys_fn = get_system(system)  # raises ValueError if unknown system

        # Broadcast inputs to common shape S
        jd_a = np.asarray(jd, dtype=np.float64)
        lat_a = np.asarray(lat, dtype=np.float64)
        lon_a = np.asarray(lon, dtype=np.float64)
        jd_b, lat_b, lon_b = np.broadcast_arrays(jd_a, lat_a, lon_a)
        S = jd_b.shape

        # Compute ASC/MC/ARMC/Vertex/eps once for all elements
        ascmc = compute_ascmc(jd_b, lat_b, lon_b)
        armc = np.asarray(ascmc["armc"], dtype=np.float64)
        eps = np.asarray(ascmc["eps"], dtype=np.float64)

        # Detect polar elements
        polar_mask = np.asarray(is_polar(lat_b, jd_b))
        any_polar = bool(polar_mask.any())

        if any_polar and polar_fallback == "raise":
            # Pull the first offending lat for an informative error
            polar_indices = np.argwhere(polar_mask.reshape(-1))
            first_idx = polar_indices[0][0] if polar_indices.size > 0 else 0
            polar_lats = polar_circle(jd_b)
            polar_lats_arr = np.asarray(polar_lats)
            offending_lat = float(lat_b.reshape(-1)[first_idx])
            offending_polar_lat = float(polar_lats_arr.reshape(-1)[first_idx])
            raise HighLatitudeError(
                offending_lat, system, offending_polar_lat
            )

        # Dispatch via SYSTEMS — no if/elif ladder anywhere
        # (research §Anti-Pattern 1: registry-based dispatch only)
        cusps = sys_fn(armc, lat_b, eps)  # shape (*S, 12)

        # If any polar elements AND polar_fallback='porphyry':
        # substitute porphyry cusps for those elements.
        if any_polar and polar_fallback == "porphyry":
            cusps_porphyry = porphyry_cusps(armc, lat_b, eps)
            # Broadcast polar_mask to (*S, 1) so np.where with cusps shape (*S, 12) works
            mask_broadcast = polar_mask[..., np.newaxis]
            cusps = np.where(mask_broadcast, cusps_porphyry, cusps)

        # Build the structured array output
        out = np.empty(S, dtype=HOUSES_DTYPE)
        out["jd"] = jd_b
        out["lat"] = lat_b
        out["lon"] = lon_b
        # System field: if polar_fallback occurred, we report the dispatched
        # system per element. Simple convention: scalar S=() → just `system`;
        # array S → all elements `system`, even where porphyry was substituted.
        # The cusps reflect the actual computation; the `system` field reflects
        # the user's request. Document this in the docstring "Notes" section.
        out["system"] = system.lower()
        out["cusps"] = cusps
        out["asc"] = np.asarray(ascmc["asc"])
        out["mc"] = np.asarray(ascmc["mc"])
        out["armc"] = armc
        out["vertex"] = np.asarray(ascmc["vertex"])

        return out


    def house_of(
        planet_lon: ArrayLike,
        cusps: np.ndarray,
    ) -> np.ndarray:
        """Return the 1-indexed house number containing each planet longitude.

        Parameters
        ----------
        planet_lon : float or np.ndarray (degrees, [0, 360))
        cusps : np.ndarray of shape (12,) or (..., 12)
            cusps[..., i] is the cusp of house (i+1).

        Returns
        -------
        np.ndarray of int32, broadcast shape — values in {1..12}.

        Examples
        --------
        >>> import numpy as np
        >>> result = calculate_houses(2451545.0, 48.8566, 2.3522)
        >>> # 45° lies somewhere
        >>> int(house_of(45.0, result["cusps"]))   # 1..12
        2
        >>> # vectorized: 5 planets at once
        >>> planet_lons = np.array([0.0, 45.0, 90.0, 180.0, 270.0])
        >>> houses = house_of(planet_lons, result["cusps"])
        >>> houses.shape
        (5,)
        """
        planet_lon_a = np.asarray(planet_lon, dtype=np.float64) % 360.0
        cusps_a = np.asarray(cusps, dtype=np.float64)

        # Distance from each cusp going eastward (modular 360)
        # planet_lon shape (...,) → expand to (..., 1) for broadcasting against
        # cusps shape (..., 12) → result shape (..., 12)
        diffs = (planet_lon_a[..., np.newaxis] - cusps_a + 360.0) % 360.0
        next_cusp = np.roll(cusps_a, -1, axis=-1)
        spans = (next_cusp - cusps_a + 360.0) % 360.0
        in_house = diffs < spans  # shape (..., 12); exactly one True per row

        # argmax returns the first True; if multiple True (degenerate), the
        # earliest house wins, which is the conventional choice.
        house_idx = np.argmax(in_house, axis=-1)  # 0..11
        return cast(np.ndarray, (house_idx + 1).astype(np.int32))
    ```

    Step B — Update `ketu/houses/__init__.py` to import the real implementations from api.py and DROP the NotImplementedError stubs:

    Read the current `ketu/houses/__init__.py` (Plan 10-03's stub version), then replace the body with:

    ```python
    """House system calculations.

    >>> from ketu.houses import calculate_houses, house_of, HOUSES_DTYPE
    >>> from ketu.houses import SYSTEMS, HighLatitudeError

    Public API:
    - calculate_houses(jd, lat, lon, system="placidus", polar_fallback="raise")
        → ndarray of HOUSES_DTYPE
    - house_of(planet_lon, cusps) → ndarray of int (1..12)
    - HOUSES_DTYPE — structured array layout
    - HighLatitudeError — raised at polar latitudes (default behavior)
    - SYSTEMS — dict of registered house-system implementations
    """
    from __future__ import annotations

    from .core import HOUSES_DTYPE, HighLatitudeError
    from .registry import SYSTEMS, register, get_system
    from .api import calculate_houses, house_of

    # Trigger registration of built-in systems by importing the modules.
    # Each module's @register decorator runs on import.
    from . import placidus  # noqa: F401  registers 'placidus' in SYSTEMS
    from . import koch       # noqa: F401  registers 'koch' in SYSTEMS
    from . import porphyry   # noqa: F401  registers 'porphyry' in SYSTEMS

    __all__ = [
        "HOUSES_DTYPE",
        "HighLatitudeError",
        "SYSTEMS",
        "calculate_houses",
        "house_of",
    ]
    ```

    Note the `from . import placidus, koch, porphyry` block — this is the registration trigger. Without these imports, calculate_houses(system="placidus") would raise ValueError("unknown house system 'placidus'") because no module would have loaded the @register decorators. This is a common-pitfall trap for registry patterns; document with a comment.

    Anti-patterns to avoid:
    - DO NOT use a try/except around `is_polar` to catch errors — polar detection is pure math; if it fails, surface the error.
    - DO NOT inline an if-elif ladder for system dispatch (`if system == 'placidus'...`) — HOU-02 explicitly forbids this. Use SYSTEMS[system.lower()] via get_system().
    - DO NOT silently fall back to porphyry when an UNKNOWN system is requested — that's a user error, not a polar event. Surface via ValueError from get_system.
    - DO NOT skip the placidus/koch/porphyry imports in __init__.py — without them, SYSTEMS will be empty at import time and every call will fail.
    - DO NOT add a runtime swisseph import — the public API is pure-NumPy.
    - For the `out["system"]` field: use `system.lower()` consistently. If user passes "Placidus" or "PLACIDUS", store "placidus".
  </action>
  <verify>
    `python -c "
    import numpy as np
    from ketu.houses import calculate_houses, house_of, HOUSES_DTYPE, HighLatitudeError, SYSTEMS

    # Built-in registrations
    assert {'placidus', 'koch', 'porphyry'} <= set(SYSTEMS.keys()), SYSTEMS

    # Scalar Placidus
    r = calculate_houses(2451545.0, 48.8566, 2.3522, system='placidus')
    assert r.dtype == HOUSES_DTYPE
    assert r['cusps'].shape == (12,)
    print('scalar placidus OK', r['asc'])

    # Vectorized Koch with polar_fallback='porphyry'
    rb = calculate_houses(
        np.array([2451545.0, 2451545.0]),
        np.array([48.8566, 80.0]),
        np.array([2.3522, 0.0]),
        system='koch', polar_fallback='porphyry',
    )
    assert rb.shape == (2,)
    assert rb['cusps'].shape == (2, 12)
    assert not np.isnan(rb['cusps']).any(), 'porphyry fallback must yield no NaN'
    print('vectorized koch+porphyry-fallback OK')

    # Polar with default raise
    try:
        calculate_houses(2451545.0, 80.0, 0.0, system='placidus')
        raise AssertionError('expected HighLatitudeError')
    except HighLatitudeError as e:
        assert e.lat == 80.0
        print('raise OK', e)

    # house_of — scalar and vectorized
    h = house_of(45.0, r['cusps'])
    assert 1 <= int(h) <= 12, h
    print('house_of scalar OK', int(h))
    h_arr = house_of(np.array([0.0, 45.0, 90.0, 180.0, 270.0]), r['cusps'])
    assert h_arr.shape == (5,)
    assert all(1 <= int(x) <= 12 for x in h_arr)
    print('house_of vectorized OK', h_arr)
    "`

    `mypy --strict ketu/houses/api.py ketu/houses/__init__.py` is clean.
  </verify>
  <done>
    `ketu/houses/api.py` exists with full implementations of calculate_houses (with polar_fallback) and house_of (vectorized). __init__.py imports them and triggers placidus/koch/porphyry registration. SYSTEMS at runtime contains 'placidus', 'koch', 'porphyry'. Scalar and vectorized paths work; polar_fallback='raise' raises, polar_fallback='porphyry' substitutes Porphyry for polar elements without NaN. mypy --strict clean.
  </done>
</task>

<task type="auto">
  <name>Task 2: Remove calculate_house_cusps stub from ephemeris/planets.py and its tests</name>
  <files>ketu/ephemeris/planets.py
ketu/ephemeris/__init__.py
tests/test_planets_coverage.py</files>
  <action>
    Step A — `ketu/ephemeris/planets.py`: delete the entire `calculate_house_cusps` function (currently lines 273-311 per state.md research). The function returns wrong equal-house values and has been a v0.x leftover. Remove the function definition and any blank lines that become redundant. Do NOT leave a stub or a deprecation warning — Plan 10's CHANGELOG entry (Plan 12 will write it) covers the removal as a breaking change.

    Step B — `ketu/ephemeris/__init__.py`: remove `calculate_house_cusps` from:
    - The `from .planets import (...)` import block (current line 49)
    - The `__all__` list (current line 92)

    Step C — `tests/test_planets_coverage.py`: delete the test class/methods that exercise `calculate_house_cusps`. Per state.md research, this is approximately lines 186-269 (one class, ~5 test methods). Specifically:
    - The import `calculate_house_cusps` in the file's import block (current line 22)
    - The TestCalculateHouseCusps class (or whatever it's named) — every method that calls `calculate_house_cusps`
    - Any helper functions that ONLY support those tests

    DO NOT touch tests in this file that exercise other functions (`calc_planet_position`, `body_properties`, etc.) — they're unrelated.

    Step D — Verify nothing else in the codebase references `calculate_house_cusps`:

        grep -rn "calculate_house_cusps" /home/loc/workspace/ketu/

    Should return ZERO matches after this task. If it returns matches in `docs/`, `examples/`, or `fr/`, those need updating too — investigate each.

    Step E — Update CHANGELOG.md (or write a scratch note for Plan 12 release prep). Add an entry under "Unreleased" or "v1.1.0":

        ### Removed
        - `ketu.ephemeris.calculate_house_cusps` — broken equal-house placeholder.
          Use `ketu.calculate_houses(jd, lat, lon, system='placidus' | 'koch')`
          from the new `ketu.houses` module instead. (HOU-10)

    If CHANGELOG.md doesn't exist or doesn't have an Unreleased section, prepend a minimal entry:

        ## [Unreleased]

        ### Removed
        - `ketu.ephemeris.calculate_house_cusps` — broken equal-house placeholder. (HOU-10)

        ### Added
        - `ketu.houses` module with Placidus and Koch house systems,
          extensible via `register('myhouse')`. (HOU-02 .. HOU-10)

    Anti-patterns to avoid:
    - DO NOT keep `calculate_house_cusps` as a deprecated alias that wraps `calculate_houses` — the old function returned wrong equal-house values, so wrapping it would mislead users who were getting wrong answers and now get DIFFERENT (correct) answers; better to remove and let `ImportError` flag the breaking change.
    - DO NOT leave the function and emit DeprecationWarning — mid-phase Plan 11 (CLI) and Plan 12 (release) need a clean break before v1.1.0.
    - DO NOT delete tests that exercise OTHER functions in `tests/test_planets_coverage.py` — only the calculate_house_cusps-specific tests.
    - DO NOT remove the `from .time import sidereal_time` import from `planets.py` if it was inside `calculate_house_cusps` — `sidereal_time` may still be referenced by other functions in the file. Check before deleting; if it's only used by the deleted function, remove that import too.
  </action>
  <verify>
    `grep -rn "calculate_house_cusps" /home/loc/workspace/ketu/ketu/ /home/loc/workspace/ketu/tests/ 2>/dev/null` returns ZERO matches. Should print nothing.

    `python -c "from ketu.ephemeris import calculate_house_cusps" 2>&1 | grep -i "ImportError\|cannot import"` succeeds (the import errors out, which is what we want).

    `python -c "from ketu.ephemeris import calc_planet_position; print(calc_planet_position(2451545.0, 0))"` still works (other ephemeris functions unaffected).

    `pytest tests/test_planets_coverage.py -v` runs and shows fewer tests than before (the calculate_house_cusps ones gone) but all remaining tests still pass.

    `pytest tests/ -v` — full suite green; no regressions.

    `mypy --strict ketu/ephemeris/planets.py ketu/ephemeris/__init__.py` clean.

    `grep -A2 "Removed\|Unreleased" CHANGELOG.md | head -20` shows the new entry.
  </verify>
  <done>
    `calculate_house_cusps` is gone from `ketu/ephemeris/planets.py` (function deleted), `ketu/ephemeris/__init__.py` (import + __all__), and `tests/test_planets_coverage.py` (test class deleted). `grep -r "calculate_house_cusps" ketu/ tests/` returns zero matches. CHANGELOG.md (or scratch note) records the breaking change with a migration hint pointing to `ketu.calculate_houses`. Full pytest suite passes. mypy --strict clean.
  </done>
</task>

<task type="auto">
  <name>Task 3: Write tests/houses/test_house_of.py and tests/houses/test_integration.py; verify ≥95% coverage</name>
  <files>tests/houses/test_house_of.py
tests/houses/test_integration.py</files>
  <action>
    Step A — `tests/houses/test_house_of.py`:

    ```python
    """house_of() tests — assigns planet longitude to 1-indexed house (HOU-07)."""
    from __future__ import annotations
    import numpy as np
    import pytest

    from ketu.houses import calculate_houses, house_of


    @pytest.fixture
    def paris_j2000_cusps():
        r = calculate_houses(2451545.0, 48.8566, 2.3522, system="placidus")
        return r["cusps"]


    def test_house_of_returns_int_in_range_1_to_12(paris_j2000_cusps):
        for lon in [0.0, 30.0, 60.0, 90.0, 120.0, 150.0, 180.0,
                    210.0, 240.0, 270.0, 300.0, 330.0]:
            h = int(house_of(lon, paris_j2000_cusps))
            assert 1 <= h <= 12, f"longitude {lon}° → house {h}; out of range"


    def test_house_of_planet_at_cusp_is_in_that_house(paris_j2000_cusps):
        """A planet at exactly the i-th cusp lives in house i (not i-1).

        Convention: cusp[i] BEGINS house (i+1) (eastward direction).
        So a planet at cusp[0] is in house 1; at cusp[5] is in house 6.
        """
        for i in range(12):
            cusp_value = float(paris_j2000_cusps[i])
            h = int(house_of(cusp_value, paris_j2000_cusps))
            assert h == i + 1, (
                f"planet at cusp[{i}]={cusp_value}° expected house {i+1}, got {h}"
            )


    def test_house_of_vectorized_over_planet_lons(paris_j2000_cusps):
        lons = np.array([0.0, 45.0, 90.0, 135.0, 180.0, 225.0, 270.0, 315.0])
        houses = house_of(lons, paris_j2000_cusps)
        assert houses.shape == (8,)
        assert houses.dtype == np.int32
        assert all(1 <= int(h) <= 12 for h in houses)


    def test_house_of_vectorized_over_cusps_arrays():
        """When cusps has shape (N, 12), house_of broadcasts."""
        # Two charts: Paris J2000 and 2050 Reykjavik
        r = calculate_houses(
            np.array([2451545.0, 2470204.0]),
            np.array([48.8566, 64.1466]),
            np.array([2.3522, -21.9426]),
            system="placidus",
        )
        cusps_2 = r["cusps"]  # shape (2, 12)
        # Same planet longitude (45°) against both charts simultaneously
        # Use planet_lon shape (2,) → match cusps leading shape
        planet_lons = np.array([45.0, 45.0])
        houses = house_of(planet_lons, cusps_2)
        assert houses.shape == (2,)
        for h in houses:
            assert 1 <= int(h) <= 12


    def test_house_of_handles_360_wrap():
        """Planet at 359.99° vs 0.01° must return same house (cusps wrap mod 360)."""
        r = calculate_houses(2451545.0, 48.8566, 2.3522, system="placidus")
        h_low = int(house_of(0.01, r["cusps"]))
        h_high = int(house_of(359.99, r["cusps"]))
        # Either same house or adjacent houses (depending on which side of cusp 0° is on)
        assert abs(h_low - h_high) in (0, 11), (  # 11 = 12-1 (mod-12 adjacency)
            f"0.01° → {h_low}, 359.99° → {h_high}; expected same or adjacent houses"
        )


    def test_house_of_modular_input_normalization():
        """Input planet_lon is normalized mod 360."""
        r = calculate_houses(2451545.0, 48.8566, 2.3522, system="placidus")
        h_45 = int(house_of(45.0, r["cusps"]))
        h_405 = int(house_of(405.0, r["cusps"]))     # 405 % 360 = 45
        h_neg = int(house_of(-315.0, r["cusps"]))    # -315 % 360 = 45
        assert h_45 == h_405 == h_neg
    ```

    Step B — `tests/houses/test_integration.py`:

    ```python
    """End-to-end calculate_houses tests — dispatch, polar_fallback, dtype shape (HOU-02, HOU-05, HOU-06, HOU-09)."""
    from __future__ import annotations
    import numpy as np
    import pytest

    from ketu.houses import (
        calculate_houses, HOUSES_DTYPE, HighLatitudeError, SYSTEMS,
    )


    NON_POLAR_LABELS = [
        "J2000_Greenwich", "J2000_Paris", "J2000_Sydney",
        "J2000_Tokyo", "J2000_BuenosAires", "J2000_Equator",
        "1900_NewYork", "2050_Reykjavik",
    ]


    def test_systems_has_placidus_koch_porphyry_at_import_time():
        """All 3 built-in systems are registered when ketu.houses is imported."""
        for name in ("placidus", "koch", "porphyry"):
            assert name in SYSTEMS, f"{name} not in SYSTEMS={list(SYSTEMS.keys())}"


    def test_calculate_houses_returns_houses_dtype_array():
        r = calculate_houses(2451545.0, 48.8566, 2.3522, system="placidus")
        assert r.dtype == HOUSES_DTYPE
        assert r["cusps"].shape == (12,)
        assert 0.0 <= float(r["asc"]) < 360.0
        assert 0.0 <= float(r["mc"]) < 360.0
        assert 0.0 <= float(r["armc"]) < 360.0


    def test_calculate_houses_meta_fields_populated():
        r = calculate_houses(2451545.0, 48.8566, 2.3522, system="Placidus")  # mixed case
        assert float(r["jd"]) == 2451545.0
        assert float(r["lat"]) == 48.8566
        assert float(r["lon"]) == 2.3522
        assert str(r["system"]) == "placidus"  # normalized lowercase


    @pytest.mark.parametrize("system", ["placidus", "koch", "porphyry"])
    @pytest.mark.parametrize("label", NON_POLAR_LABELS)
    def test_calculate_houses_all_3_systems_match_oracle(
        system, label, reference_charts, loaded_reference_snapshot,
    ):
        """All 3 systems agree with swisseph on every non-polar reference chart."""
        chart = next(c for c in reference_charts if c["label"] == label)
        snap = loaded_reference_snapshot["charts"][label]["systems"]
        if system not in snap:
            pytest.skip(f"snapshot lacks {system} entry for {label}")
        snap_cusps = np.asarray(snap[system]["cusps"])

        r = calculate_houses(chart["jd"], chart["lat"], chart["lon"], system=system)
        deltas = np.abs(((r["cusps"] - snap_cusps + 180.0) % 360.0) - 180.0)
        ARCMIN = 1.0 / 60.0
        for i in range(12):
            assert deltas[i] < ARCMIN, (
                f"{system} {label} cusp {i+1} drift {deltas[i] * 60:.3f} arcmin"
            )


    def test_calculate_houses_unknown_system_raises_value_error():
        with pytest.raises(ValueError, match="unknown house system"):
            calculate_houses(2451545.0, 48.8566, 2.3522, system="nonexistent_xyz")


    def test_calculate_houses_invalid_polar_fallback_raises_value_error():
        with pytest.raises(ValueError, match="polar_fallback"):
            calculate_houses(
                2451545.0, 48.8566, 2.3522,
                system="placidus", polar_fallback="invalid_choice",
            )


    def test_calculate_houses_polar_default_raises_high_latitude_error():
        with pytest.raises(HighLatitudeError) as exc_info:
            calculate_houses(2451545.0, 80.0, 0.0, system="placidus")
        assert exc_info.value.lat == 80.0
        assert exc_info.value.system == "placidus"


    def test_calculate_houses_polar_porphyry_substitutes_for_polar_only():
        """Vectorized: 1 mid-lat + 1 polar; mid gets placidus, polar gets porphyry; both no NaN."""
        jds = np.array([2451545.0, 2451545.0])
        lats = np.array([48.8566, 80.0])
        lons = np.array([2.3522, 0.0])
        r = calculate_houses(
            jds, lats, lons,
            system="placidus", polar_fallback="porphyry",
        )
        assert r.shape == (2,)
        assert r["cusps"].shape == (2, 12)
        assert not np.isnan(r["cusps"]).any(), (
            "polar_fallback='porphyry' must produce no NaN"
        )


    def test_calculate_houses_vectorized_preserves_leading_shape():
        """N inputs → N outputs."""
        N = 5
        jds = np.full(N, 2451545.0)
        lats = np.linspace(0.0, 50.0, N)
        lons = np.zeros(N)
        r = calculate_houses(jds, lats, lons, system="placidus")
        assert r.shape == (N,)
        assert r["cusps"].shape == (N, 12)


    def test_calculate_houses_2d_input_shape_preserved():
        """(2, 3) → output shape (2, 3) with cusps shape (2, 3, 12)."""
        jds = np.full((2, 3), 2451545.0)
        lats = np.full((2, 3), 48.8566)
        lons = np.full((2, 3), 2.3522)
        r = calculate_houses(jds, lats, lons, system="placidus")
        assert r.shape == (2, 3)
        assert r["cusps"].shape == (2, 3, 12)


    def test_calculate_houses_no_runtime_swisseph_import():
        """Sanity: ketu.houses must not import swisseph (test-only AGPL constraint)."""
        import sys
        # Re-import ketu.houses fresh-ish (already imported, but verify swisseph isn't in its imports)
        import ketu.houses
        import ketu.houses.api
        for mod_name, mod in list(sys.modules.items()):
            if mod_name.startswith("ketu.houses") and mod is not None:
                # Inspect module __dict__ for any swisseph import name
                names = [n for n in dir(mod) if n.startswith("swe") or n == "swisseph"]
                # Allow names like "swe_oracle" only in test files (this test is in tests/);
                # in ketu.houses.* nothing should match.
                assert not names, (
                    f"{mod_name} unexpectedly exposes swisseph-related names: {names}"
                )
    ```

    Step C — Coverage gate. Add a test that asserts ≥95% coverage on `ketu.houses`:

    ```python
    # Append to test_integration.py:

    def test_ketu_houses_module_coverage_at_least_95_percent():
        """Coverage gate: ≥95% line coverage on the ketu.houses subpackage.

        This test runs pytest-cov programmatically on `ketu.houses` and
        asserts the line-coverage percentage. It is a slow test (re-runs
        the test suite) — mark with @pytest.mark.slow if runtime becomes
        an issue.
        """
        import subprocess, json, sys
        # Run the test suite with --cov scoped to ketu/houses
        cmd = [
            sys.executable, "-m", "pytest",
            "tests/houses/",
            "--cov=ketu.houses",
            "--cov-report=json:/tmp/houses-coverage.json",
            "-q", "--no-header",
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        with open("/tmp/houses-coverage.json") as f:
            data = json.load(f)
        pct = data["totals"]["percent_covered"]
        assert pct >= 95.0, (
            f"ketu.houses coverage {pct:.1f}% < 95% (HOU-09 spec). "
            f"See /tmp/houses-coverage.json for missing lines."
        )
    ```

    Mark this with `@pytest.mark.slow` and provide an opt-out in CI if needed (the basic suite shouldn't recurse). Better: replace the subprocess with a direct invocation that avoids the recursion (parsing the existing .coverage file). For the simpler-and-cleaner version, omit the inline coverage test and add a CI gate via `pytest --cov=ketu.houses --cov-fail-under=95 tests/houses/` documented in SUMMARY.md instead.

    Decision: prefer the CI gate approach. Drop the inline `test_ketu_houses_module_coverage_at_least_95_percent` from this test file; instead, wire the coverage gate into committed config so a bare `pytest tests/` does NOT silently miss it.

    Step D — Wire coverage gate into `pyproject.toml`. Read the current `pyproject.toml`; locate (or create) the `[tool.pytest.ini_options]` table. Update / add the `addopts` key so EVERY pytest run reports module-level coverage in the terminal:

    ```toml
    [tool.pytest.ini_options]
    minversion = "7.0"
    addopts = "--cov=ketu --cov-report=term-missing"
    testpaths = ["tests"]
    markers = [
        "slow: marks tests as slow (deselect with '-m \"not slow\"')",
        "houses_coverage_gate: HOU-09 95% coverage gate for ketu.houses (run via Makefile target)",
    ]
    ```

    DO NOT set `--cov-fail-under` project-wide (would block test runs that touch only one module). Instead, the houses-specific 95% gate is a SEPARATE invocation, documented in two places:

    - `tests/houses/test_integration.py` module docstring footer: "HOU-09 coverage gate command: `pytest tests/houses/ --cov=ketu.houses --cov-fail-under=95`"
    - `Makefile` (create or update): add a `houses-coverage` target:

    ```makefile
    .PHONY: houses-coverage
    houses-coverage:
    	pytest tests/houses/ --cov=ketu.houses --cov-fail-under=95 --cov-report=term-missing
    ```

    (If a `Makefile` already exists, append the target; do NOT overwrite. Tab indentation is required for Makefile recipes.)

    The verify step for this task runs `make houses-coverage` (or the explicit pytest command if make isn't standard in the project). The committed pyproject.toml change ensures `pytest tests/` will surface the coverage report in every CI run, even when the strict 95% gate is reserved to the houses-specific Makefile target.

    Anti-patterns to avoid (Step D specifically):
    - DO NOT add `--cov-fail-under=95` to the project-wide `addopts` — that would block any partial test run (e.g. `pytest tests/test_ephemeris.py`) that doesn't exercise enough of `ketu.houses` to clear 95%. The gate must scope to `tests/houses/` only.
    - DO NOT delete pre-existing `addopts` content — append `--cov=ketu --cov-report=term-missing` to whatever is there. Read first; merge; write.
    - DO NOT skip the markers entry for `slow` if Phase 9 introduced slow tests — verify by `grep -n "slow" tests/` before editing; if `slow` is already used, the marker MUST be declared in pyproject.toml (pytest 7+ warns on undeclared markers in --strict-markers mode).

    Anti-patterns to avoid:
    - DO NOT use `calculate_houses` from `ketu.ephemeris` anywhere — that import is dead after Task 2.
    - DO NOT skip the `test_calculate_houses_meta_fields_populated` test — it pins the contract that `system` field is normalized to lowercase, which Plan 11 (CLI) will rely on.
    - DO NOT use `assert r['cusps'].shape == (1, 12)` for scalar inputs — `calculate_houses(2451545.0, 48.8566, 2.3522)` returns a 0-d structured array; the cusps subarray on it is shape `(12,)`. Verify this empirically before fixing test assertions.
    - DO NOT skip the test_calculate_houses_no_runtime_swisseph_import sanity check — it's the ratchet preventing accidental swisseph leak from a future "let me just import for a fixture" change.
  </action>
  <verify>
    `pytest tests/houses/test_house_of.py -v` shows 7 tests passing.

    `pytest tests/houses/test_integration.py -v` shows ~30 tests passing (3 systems × 8 charts = 24 oracle-agreement parametrize, plus ~6 invariants).

    `pytest tests/houses/ --cov=ketu.houses --cov-fail-under=95 --cov-report=term-missing` reports ≥95% coverage on the ketu.houses subpackage. Equivalently: `make houses-coverage` (which runs the same command) exits 0. If below 95%, the missing lines are flagged in the term-missing report; address them by either removing dead code or adding a targeted test.

    `grep -A5 "tool.pytest.ini_options" pyproject.toml` shows `addopts = "--cov=ketu --cov-report=term-missing"`. A bare `pytest tests/` now prints a coverage table in stdout (sanity: re-run a known passing test file and confirm coverage section appears).

    `grep "houses-coverage" Makefile` returns the target line — confirms the Makefile target landed (only relevant if a Makefile is present in the project; if not, the Makefile creation is a Step D output too).

    `pytest tests/ -v` — full suite passes (488 + ~80 new house tests = ~570 total).

    `mypy --strict ketu/ tests/houses/` clean.

    `grep -r "swisseph" ketu/` returns nothing.
  </verify>
  <done>
    `tests/houses/test_house_of.py` exists with 7 tests covering scalar, vectorized, mixed cusps, 360° wrap, modular normalization. `tests/houses/test_integration.py` exists with ~30 tests covering systems registration, dtype shape, all 3 systems × 8 charts oracle agreement, polar_fallback raise/porphyry semantics, vectorized scalar/1d/2d shape preservation, no-runtime-swisseph sanity. `pyproject.toml [tool.pytest.ini_options]` contains `addopts = "--cov=ketu --cov-report=term-missing"` and the `slow` + `houses_coverage_gate` markers; `Makefile` has a `houses-coverage` target running the 95% gate. `pytest tests/houses/ --cov=ketu.houses --cov-fail-under=95` passes. mypy --strict clean. Full pytest suite green.
  </done>
</task>

</tasks>

<verification>
- `pytest tests/houses/ -v` shows ~80+ tests across all 7 test files (test_lst_obliquity_precision, test_oracle_smoke, test_dtype, test_registry, test_ascmc, test_placidus, test_koch, test_porphyry, test_polar_safety, test_house_of, test_integration).
- `pytest tests/houses/ --cov=ketu.houses --cov-fail-under=95` passes — the HOU-09 coverage gate. Wired in committed config: `pyproject.toml [tool.pytest.ini_options]` includes `--cov=ketu --cov-report=term-missing` in addopts (every pytest run reports coverage); a `make houses-coverage` Makefile target runs the houses-scoped 95% gate.
- All 3 systems (placidus, koch, porphyry) registered into SYSTEMS at module import time; calculate_houses dispatches via SYSTEMS[name.lower()] with no inline if/elif.
- polar_fallback='raise' (default) raises HighLatitudeError; polar_fallback='porphyry' substitutes Porphyry for polar elements without NaN.
- house_of returns int32 ndarray of values in {1..12}; vectorized over both planet_lon and cusps arrays.
- `calculate_house_cusps` is removed: `grep -r "calculate_house_cusps" ketu/ tests/` returns zero matches.
- ketu/ephemeris/__init__.py no longer exports `calculate_house_cusps`; tests/test_planets_coverage.py no longer tests it.
- CHANGELOG.md (or scratch note) documents the breaking change pointing users to `ketu.calculate_houses`.
- ketu/__init__.py re-exports calculate_houses, house_of, HOUSES_DTYPE, HighLatitudeError, HOUSE_SYSTEMS at the top level.
- `mypy --strict ketu/ tests/houses/` clean.
- `grep -r "import swisseph" ketu/` returns zero matches — runtime constraint preserved.
- Full `pytest tests/` suite green (~570 tests).
</verification>

<success_criteria>
- HOU-07 satisfied: `house_of(planet_lon, cusps) -> int` returns 1-12; vectorized over both inputs.
- HOU-10 satisfied: `calculate_house_cusps` stub removed from `ephemeris/planets.py`; tests removed; CHANGELOG entry added.
- HOU-02 fully wired: SYSTEMS dispatch in `calculate_houses` with no if/elif ladder; new systems plug in via `register('myhouse')` decorator.
- HOU-05 fully wired: HOUSES_DTYPE structured array with all 9 fields populated correctly; vectorized inputs preserve leading shape.
- HOU-06 fully wired: `polar_fallback={"raise", "porphyry"}` parameter; HighLatitudeError raised by default beyond ±polar_circle(jd); Porphyry substituted on opt-in.
- HOU-09 closed: ≥95% coverage on `ketu.houses` (gate verified via `pytest --cov-fail-under=95`); ≥10 reference fixtures × 3 systems × 12 cusps = ~360 oracle-agreement assertions across the test suite.
- All 5 ROADMAP success criteria for Phase 10 satisfied (1: HOUSES_DTYPE+vectorized; 2: <1 arcmin ASC at non-polar lats; 3: HighLatitudeError or porphyry, never NaN; 4: registry pattern + stub removed; 5: ≥95% coverage + ≥10 fixtures + house_of returns 1-12).
</success_criteria>

<output>
After completion, create `.planning/phases/10-houses-module/10-06-SUMMARY.md` documenting:
- calculate_houses end-to-end test results (3 systems × 8 charts × 12 cusps oracle agreement)
- house_of correctness invariants and edge case coverage
- HOU-10 stub removal: lines deleted in ephemeris/planets.py, ephemeris/__init__.py, tests/test_planets_coverage.py
- CHANGELOG entry text
- Final ketu.houses coverage percentage (target ≥95%)
- Coverage gate wiring: pyproject.toml addopts diff + Makefile houses-coverage target excerpt
- Full pytest suite count: ~570+ (488 existing + ~80 Plan 10)
- Confirmation: mypy --strict clean across ketu/ and tests/houses/; grep "swisseph" ketu/ returns zero
- Phase 10 acceptance criteria 1-5 ALL GREEN — list each with evidence
- State.md update guidance: clear the "LST/obliquity precision audit" blocker; mark Phase 10 complete (6/6 plans, 4 waves)
</output>
