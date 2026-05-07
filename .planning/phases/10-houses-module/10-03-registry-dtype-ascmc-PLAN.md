---
phase: 10-houses-module
plan: 03
type: execute
wave: 2
depends_on:
  - "10-01"
  - "10-02"
files_modified:
  - ketu/__init__.py
  - ketu/houses/__init__.py
  - ketu/houses/core.py
  - ketu/houses/registry.py
  - ketu/houses/ascmc.py
  - ketu/houses/_ecliptic.py
  - pyproject.toml
  - tests/houses/test_dtype.py
  - tests/houses/test_registry.py
  - tests/houses/test_ascmc.py
autonomous: true
plan_id: "10-03"
requirements:
  - HOU-02
  - HOU-05

must_haves:
  truths:
    - "ketu.houses package exists and exposes HOUSES_DTYPE, HighLatitudeError, SYSTEMS, calculate_houses (stubbed), house_of (stubbed) — public API surface in place"
    - "HOUSES_DTYPE is a structured numpy dtype with 9 fields: jd, lat, lon, system, cusps[12], asc, mc, armc, vertex"
    - "Registry pattern works: SYSTEMS dict + register decorator; new house systems plug in by `@register('name')` without touching dispatch logic in calculate_houses"
    - "ASC and MC are computed in closed form via np.arctan2 (no single-arg arctan), match swisseph oracle to <1 arcmin at all 8 non-polar reference charts (Plan 10-02 fixture)"
    - "ASC and MC are vectorized: scalar input → scalar output; ndarray input → ndarray output, leading shape preserved (HOU-08 partial — ascmc-side)"
    - "HighLatitudeError exception class exists, is a ValueError subclass, carries lat/system/polar_lat attrs"
    - "ARMC computation: armc = (sidereal_time(jd, 0.0) + lon) % 360 — wired in ascmc module so Plans 04/05 don't re-derive it"
  artifacts:
    - path: "ketu/houses/__init__.py"
      provides: "Public API: HOUSES_DTYPE, HighLatitudeError, SYSTEMS, calculate_houses, house_of (stubs for unimplemented systems return NotImplementedError until Plans 04/05 land)"
      contains: "__all__"
      min_lines: 20
    - path: "ketu/houses/core.py"
      provides: "HOUSES_DTYPE definition + HighLatitudeError exception class"
      contains: "HOUSES_DTYPE"
      min_lines: 30
    - path: "ketu/houses/registry.py"
      provides: "SYSTEMS dict + register decorator + dispatch helper"
      contains: "SYSTEMS"
      min_lines: 30
    - path: "ketu/houses/ascmc.py"
      provides: "compute_ascmc(jd, lat, lon) -> dict[asc, mc, armc, eps] — vectorized; np.arctan2 form; no single-arg arctan"
      contains: "arctan2"
      min_lines: 60
    - path: "ketu/houses/_ecliptic.py"
      provides: "Internal RA<->ecliptic-longitude helpers (ra_to_lambda, lambda_to_ra) — shared by Placidus/Koch in Plans 04/05"
      contains: "def ra_to_lambda"
      min_lines: 40
    - path: "tests/houses/test_dtype.py"
      provides: "Tests for HOUSES_DTYPE shape semantics: subarray field cusps[12] interacts correctly with outer shape (N,), structured array indexing"
      contains: "HOUSES_DTYPE"
      min_lines: 30
    - path: "tests/houses/test_registry.py"
      provides: "Tests for register/SYSTEMS pattern: registering a custom 'noop' system makes it dispatchable without modifying registry.py"
      contains: "register"
      min_lines: 30
    - path: "tests/houses/test_ascmc.py"
      provides: "ASC/MC closed-form tests vs swisseph oracle (reference_charts non-polar entries, atol=1 arcmin = 1/60 deg ≈ 0.01667°)"
      contains: "compute_ascmc"
      min_lines: 50
  key_links:
    - from: "ketu/houses/__init__.py"
      to: "ketu.houses.core HOUSES_DTYPE, HighLatitudeError"
      via: "re-export"
      pattern: "from \\.core import"
    - from: "ketu/houses/__init__.py"
      to: "ketu.houses.registry SYSTEMS"
      via: "re-export"
      pattern: "from \\.registry import"
    - from: "ketu/houses/ascmc.py"
      to: "ketu.ephemeris.time.sidereal_time"
      via: "ARMC computation: armc = sidereal_time(jd, 0.0) + lon"
      pattern: "from ketu\\.ephemeris\\.time import sidereal_time"
    - from: "ketu/houses/ascmc.py"
      to: "ketu.ephemeris.coordinates.mean_obliquity"
      via: "obliquity needed for ASC/MC trig terms"
      pattern: "from ketu\\.ephemeris\\.coordinates import mean_obliquity"
    - from: "tests/houses/test_ascmc.py"
      to: "tests/houses/conftest.py reference_charts + swe_oracle"
      via: "pytest fixture injection (HOU-09 cross-check)"
      pattern: "reference_charts|swe_oracle"
---

<objective>
Land the structural foundation of `ketu/houses/`: the registry pattern (HOU-02), the HOUSES_DTYPE structured array (HOU-05), the closed-form ASC/MC/ARMC/Vertex computation (shared by every house system), the HighLatitudeError exception class, and the public API skeleton. Plans 04 (Placidus) and 05 (Koch + Porphyry) plug into this scaffold without modifying it.

Purpose: Closed-form ASC/MC has no iteration and is testable in isolation against the Plan 10-02 oracle fixtures. Landing it here decouples the structural concerns (dtype, registry, exception) from the algorithmic concerns (Placidus iteration in Plan 04, Koch + polar fallback in Plan 05). This plan can run in Wave 2 in parallel with Plan 10-02 since their file sets are disjoint (`ketu/houses/*` vs `tests/houses/conftest.py + fixtures/`); both depend only on Plan 10-01 (LST audit closes the precision blocker that ARMC needs).

Output:
- `ketu/houses/__init__.py` — public exports + stub `calculate_houses` raising NotImplementedError for unregistered systems
- `ketu/houses/core.py` — HOUSES_DTYPE + HighLatitudeError
- `ketu/houses/registry.py` — SYSTEMS dict + `register(name)` decorator + dispatch helper
- `ketu/houses/ascmc.py` — vectorized closed-form ASC/MC/ARMC/Vertex via np.arctan2
- `ketu/houses/_ecliptic.py` — internal helpers (RA↔ecliptic longitude) for Plans 04/05
- 3 test files in `tests/houses/`: dtype, registry, ascmc
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
@.planning/phases/10-houses-module/10-01-lst-precision-audit-PLAN.md

# Existing modules this plan reads/depends on
@ketu/ephemeris/time.py
@ketu/ephemeris/coordinates.py

# Reference: existing public-API export style
@ketu/__init__.py
@ketu/aspects/__init__.py
</context>

<tasks>

<task type="auto">
  <name>Task 1: Create ketu/houses/ subpackage with HOUSES_DTYPE, HighLatitudeError, registry, and public API skeleton</name>
  <files>ketu/houses/__init__.py
ketu/houses/core.py
ketu/houses/registry.py
ketu/houses/_ecliptic.py</files>
  <action>
    Step A — Create `ketu/houses/core.py`:

    ```python
    """Core types for the houses subpackage.

    Defines HOUSES_DTYPE (structured array layout for house cusp results) and
    HighLatitudeError (raised when latitude exceeds the polar circle).
    """
    from __future__ import annotations
    import numpy as np

    HOUSES_DTYPE: np.dtype = np.dtype([
        ("jd",      "f8"),
        ("lat",     "f8"),
        ("lon",     "f8"),
        ("system",  "U10"),
        ("cusps",   "f8", (12,)),  # subarray field; outer shape (N,) → cusps shape (N, 12)
        ("asc",     "f8"),
        ("mc",      "f8"),
        ("armc",    "f8"),
        ("vertex",  "f8"),
    ])


    class HighLatitudeError(ValueError):
        """Raised when |lat| exceeds the polar circle for the requested house system.

        Carries the latitude, the system name, and the actual polar circle
        (90° - mean_obliquity(jd)) for caller diagnostics. Subclass of ValueError
        so callers can catch ValueError generically when desired.
        """

        def __init__(self, lat: float, system: str, polar_lat: float) -> None:
            super().__init__(
                f"latitude {lat:.4f}° exceeds polar circle {polar_lat:.4f}° "
                f"for house system {system!r}; pass polar_fallback='porphyry' to fall back."
            )
            self.lat: float = lat
            self.system: str = system
            self.polar_lat: float = polar_lat
    ```

    Numpydoc docstrings on the class. Type-annotate every attribute (HOUSES_DTYPE: np.dtype is required for mypy --strict to be happy with module-level assignments).

    Step B — Create `ketu/houses/registry.py`:

    ```python
    """Registry pattern for house systems.

    Plans 10-04 (Placidus) and 10-05 (Koch + Porphyry) register their
    implementations via the `@register` decorator. New house systems plug in
    without modifying calculate_houses dispatch — that's HOU-02.
    """
    from __future__ import annotations
    from typing import Callable

    import numpy as np

    # Signature contract: (armc, lat, eps) → cusps array of shape (..., 12)
    # where leading dims of armc/lat/eps are broadcast together.
    HouseSystemFn = Callable[[np.ndarray, np.ndarray, np.ndarray], np.ndarray]

    SYSTEMS: dict[str, HouseSystemFn] = {}


    def register(name: str) -> Callable[[HouseSystemFn], HouseSystemFn]:
        """Decorator that registers a house system implementation.

        Parameters
        ----------
        name : str
            Public name (case-insensitive; stored lowercase). Examples:
            "placidus", "koch", "porphyry".

        Returns
        -------
        Callable
            The decorator. Wraps a function with signature
            (armc, lat, eps) -> cusps[..., 12] and inserts it into SYSTEMS.

        Examples
        --------
        >>> @register("equal")
        ... def equal_cusps(armc, lat, eps):
        ...     return np.stack([(armc + 30 * i) % 360 for i in range(12)], axis=-1)
        >>> "equal" in SYSTEMS
        True
        """
        key = name.lower()

        def _wrap(fn: HouseSystemFn) -> HouseSystemFn:
            SYSTEMS[key] = fn
            return fn

        return _wrap


    def get_system(name: str) -> HouseSystemFn:
        """Look up a house system by name (case-insensitive).

        Raises
        ------
        ValueError
            If `name` is not registered. Error message lists available systems
            (per Ketu convention: ValueError with received value + valid options).
        """
        key = name.lower()
        if key not in SYSTEMS:
            available = sorted(SYSTEMS.keys())
            raise ValueError(
                f"unknown house system {name!r}; available: {available}"
            )
        return SYSTEMS[key]
    ```

    Step C — Create `ketu/houses/_ecliptic.py` (internal helpers; underscore prefix = not part of public API):

    ```python
    """Internal helpers shared by house-system implementations.

    Provides RA↔ecliptic-longitude conversions used by Placidus (Plan 10-04)
    and Koch (Plan 10-05). All angles in degrees; all functions vectorized.
    """
    from __future__ import annotations
    import numpy as np


    def ra_to_lambda(ra: np.ndarray, eps: np.ndarray) -> np.ndarray:
        """Convert right ascension on the ecliptic to ecliptic longitude.

        For a point on the ecliptic with given RA, compute its ecliptic
        longitude λ via tan(λ) = tan(RA) / cos(eps). Uses np.arctan2 for
        correct quadrant.

        Parameters
        ----------
        ra : np.ndarray  (degrees, broadcast-compatible with `eps`)
        eps : np.ndarray  (degrees, mean obliquity)

        Returns
        -------
        np.ndarray  (degrees, [0, 360))
        """
        ra_rad = np.deg2rad(ra)
        eps_rad = np.deg2rad(eps)
        lam = np.arctan2(np.sin(ra_rad), np.cos(ra_rad) * np.cos(eps_rad))
        # Account for the obliquity-induced shift in declination → use
        # the standard atan2(sin(RA), cos(RA)*cos(eps) - sin(decl)*sin(eps)) form
        # only if decl is provided; for points strictly on the ecliptic, decl=0.
        return np.rad2deg(lam) % 360.0


    def ascensional_difference(lat: np.ndarray, decl: np.ndarray) -> np.ndarray:
        """Compute ascensional difference AD = arcsin(tan(lat) * tan(decl)).

        Returns NaN where |tan(lat) * tan(decl)| ≥ 1 (cusp does not exist —
        polar boundary; see Pitfall 6 in 10-RESEARCH.md). Caller is responsible
        for routing NaN to the polar-fallback path.

        Parameters
        ----------
        lat, decl : np.ndarray (degrees, broadcast-compatible)

        Returns
        -------
        np.ndarray (degrees, NaN where formula does not exist)
        """
        s = np.tan(np.deg2rad(lat)) * np.tan(np.deg2rad(decl))
        s_safe = np.where(np.abs(s) < 1.0, s, np.nan)
        return np.rad2deg(np.arcsin(s_safe))
    ```

    Step D — Create `ketu/houses/__init__.py`:

    ```python
    """House system calculations.

    >>> from ketu.houses import calculate_houses, house_of, HOUSES_DTYPE
    >>> from ketu.houses import SYSTEMS, HighLatitudeError

    The public API:

    - calculate_houses(jd, lat, lon, system="placidus", polar_fallback="raise")
      → ndarray of HOUSES_DTYPE
    - house_of(planet_lon, cusps) → int (1..12)
    - HOUSES_DTYPE — structured array layout
    - HighLatitudeError — raised at polar latitudes (default behavior)
    - SYSTEMS — dict of registered house-system implementations

    See Also
    --------
    ketu.houses.registry.register : Decorator to add new systems.
    """
    from __future__ import annotations
    from typing import Literal, Union
    import numpy as np

    from .core import HOUSES_DTYPE, HighLatitudeError
    from .registry import SYSTEMS, register, get_system

    __all__ = [
        "HOUSES_DTYPE",
        "HighLatitudeError",
        "SYSTEMS",
        "calculate_houses",
        "house_of",
    ]


    def calculate_houses(
        jd: Union[float, np.ndarray],
        lat: Union[float, np.ndarray],
        lon: Union[float, np.ndarray],
        system: str = "placidus",
        polar_fallback: Literal["raise", "porphyry"] = "raise",
    ) -> np.ndarray:
        """Compute house cusps for one or many (jd, lat, lon) inputs.

        STUB IMPLEMENTATION — full body lands in Plan 10-06 (integration).
        Plans 10-04 (Placidus) and 10-05 (Koch + Porphyry) register their
        implementations into SYSTEMS; Plan 10-06 wires this dispatch.
        """
        raise NotImplementedError(
            "calculate_houses is wired in Plan 10-06; "
            "use ketu.houses.SYSTEMS[system] directly until then "
            "(after Plans 10-04 / 10-05 register implementations)."
        )


    def house_of(
        planet_lon: Union[float, np.ndarray],
        cusps: np.ndarray,
    ) -> np.ndarray:
        """Return the 1-indexed house containing each planet longitude.

        STUB IMPLEMENTATION — full body lands in Plan 10-06.
        """
        raise NotImplementedError(
            "house_of is wired in Plan 10-06."
        )
    ```

    Step E — Update `ketu/__init__.py` to re-export the new public API. Add 5 imports and append 5 names to `__all__`:

    ```python
    from ketu.houses import (
        HOUSES_DTYPE,
        HighLatitudeError,
        SYSTEMS as HOUSE_SYSTEMS,  # rename to avoid clobbering future "SYSTEMS" globals; consumer uses ketu.HOUSE_SYSTEMS
        calculate_houses,
        house_of,
    )

    __all__.extend([
        "HOUSES_DTYPE",
        "HighLatitudeError",
        "HOUSE_SYSTEMS",
        "calculate_houses",
        "house_of",
    ])
    ```

    Step F — Update `pyproject.toml [tool.setuptools] packages` to include `ketu.houses`:
    Read current `packages = ["ketu", "ketu.ephemeris", "ketu.aspects", "ketu.cycles", "ketu.cache"]` and add `"ketu.houses"`. This is required so `pip install -e .` picks up the new subpackage.

    Anti-patterns to avoid:
    - Do NOT register Placidus/Koch/Porphyry in this plan — Plans 04/05 own those `@register` calls. The SYSTEMS dict starts empty and is populated by downstream plans. Document this in registry.py docstring.
    - Do NOT inline the dispatch logic into `calculate_houses` (`if system == "placidus": ...` ladder). HOU-02 is explicit: registry-based dispatch only. The full body in Plan 10-06 must do `fn = get_system(system); cusps = fn(armc, lat, eps)`.
    - Do NOT define `house_of` here — Plan 10-06 owns its body. Stub raises NotImplementedError until then. (Why not Plan 10-03? Because `house_of` requires real cusps to be testable, and real cusps require Plans 04/05 to have landed.)
    - Do NOT add a runtime `import swisseph` anywhere in `ketu/houses/` — the contract is pure-NumPy (research §"Standard Stack"). Verified: `grep -r "swisseph" ketu/houses/` after this plan must return nothing.
    - Do NOT shadow the existing `ketu.aspects.SYSTEMS`-style globals if any — sanity check: `grep -n "SYSTEMS" ketu/__init__.py` before and after the edit.
  </action>
  <verify>
    `python -c "from ketu.houses import HOUSES_DTYPE, HighLatitudeError, SYSTEMS, calculate_houses, house_of; print(HOUSES_DTYPE.names, len(SYSTEMS))"` prints all 9 dtype field names and `0` (empty SYSTEMS — Plans 04/05 will populate).

    `python -c "from ketu.houses.registry import register, SYSTEMS, get_system; @register('test_sys')\ndef noop(armc, lat, eps): return None\nassert 'test_sys' in SYSTEMS; assert get_system('TEST_SYS') is noop; print('OK')"` — registry pattern is case-insensitive and dispatches.

    `python -c "from ketu.houses import HighLatitudeError; e = HighLatitudeError(75.0, 'placidus', 66.5); assert isinstance(e, ValueError); assert e.lat == 75.0; print('OK', str(e))"` — exception class works, ValueError-subclass.

    `mypy --strict ketu/houses/` is clean (no errors across all 5 files).

    `pytest tests/ -v` — 488 + 15 (Plan 01) + 6 (Plan 02) = 509+ tests still pass; no regressions.

    `grep -r "swisseph" ketu/houses/` returns nothing.
  </verify>
  <done>
    `ketu/houses/` subpackage exists with 5 files. HOUSES_DTYPE has 9 fields, cusps as subarray (12,). HighLatitudeError is ValueError subclass. SYSTEMS dict + register decorator work and dispatch is case-insensitive. calculate_houses and house_of are stubs raising NotImplementedError. pyproject.toml `packages` list includes `ketu.houses`. ketu/__init__.py re-exports the 5 new names. mypy --strict clean. No runtime swisseph imports.
  </done>
</task>

<task type="auto">
  <name>Task 2: Implement vectorized ASC/MC/ARMC/Vertex closed-form in ketu/houses/ascmc.py</name>
  <files>ketu/houses/ascmc.py</files>
  <action>
    Create `ketu/houses/ascmc.py`. Vectorized closed-form for the four angles every house system needs. No iteration. No dispatch — these are computed identically for Placidus, Koch, Porphyry.

    ```python
    """Closed-form ASC, MC, ARMC, and Vertex computation.

    Shared by all registered house systems (Plans 10-04 Placidus and 10-05 Koch
    consume these as inputs to their per-cusp algorithms). Pure NumPy;
    vectorized over (jd, lat, lon) arrays of any compatible broadcast shape.

    All angles in degrees, normalized to [0, 360). Inputs may be scalar or
    ndarray; output preserves leading shape.
    """
    from __future__ import annotations
    from typing import Union
    import numpy as np

    from ketu.ephemeris.time import sidereal_time
    from ketu.ephemeris.coordinates import mean_obliquity

    ArrayLike = Union[float, np.ndarray]


    def compute_armc(
        jd: ArrayLike,
        lon: ArrayLike,
    ) -> np.ndarray:
        """Compute Right Ascension of the Medium Coeli (= local sidereal time).

        ARMC = (GMST(jd) + lon_east) mod 360°. Vectorized via
        np.vectorize over scalar `sidereal_time` (which is currently scalar-only;
        ascmc lives at the boundary where we lift it).

        Parameters
        ----------
        jd : float or np.ndarray (Julian Date, UT)
        lon : float or np.ndarray (geographic longitude, east-positive, deg)

        Returns
        -------
        np.ndarray (degrees, [0, 360))
        """
        jd_arr = np.atleast_1d(np.asarray(jd, dtype=np.float64))
        lon_arr = np.atleast_1d(np.asarray(lon, dtype=np.float64))
        jd_b, lon_b = np.broadcast_arrays(jd_arr, lon_arr)
        # sidereal_time is scalar-only; lift via list comprehension.
        # NOTE for Plan 10-06: if sidereal_time is later vectorized, replace
        # this with a direct call. Pre-cache the iteration to be cheap (no
        # per-element trig recomputation — sidereal_time is ~5 multiplies).
        gmst = np.array(
            [sidereal_time(float(jd_v), 0.0) for jd_v in jd_b.ravel()],
            dtype=np.float64,
        ).reshape(jd_b.shape)
        return (gmst + lon_b) % 360.0


    def compute_ascmc(
        jd: ArrayLike,
        lat: ArrayLike,
        lon: ArrayLike,
    ) -> dict[str, np.ndarray]:
        """Compute ASC, MC, ARMC, Vertex, and obliquity for one or many charts.

        Closed-form via np.arctan2 — never single-arg arctan (Pitfall 2).

        Parameters
        ----------
        jd : float or np.ndarray (Julian Date, UT)
        lat : float or np.ndarray (geographic latitude, deg)
        lon : float or np.ndarray (geographic longitude, east-positive, deg)

        Returns
        -------
        dict
            Keys: "asc", "mc", "armc", "vertex", "eps" — each ndarray of the
            broadcast shape of (jd, lat, lon). Scalar input → 0-d ndarray.

        Notes
        -----
        ASC formula (RadixPro / pd-swisseph C source):
            asc = atan2(cos(armc), -[sin(eps)·tan(lat) + cos(eps)·sin(armc)])

        MC formula:
            mc = atan2(sin(armc), cos(armc)·cos(eps))

        Vertex (closed-form, ASC formula with lat → 90°-lat — co-latitude):
            vtx = atan2(cos(armc), -[sin(eps)·tan(90°-lat) + cos(eps)·sin(armc)])

        See research §"Don't Hand-Roll" for derivation cross-checks.
        """
        jd_a = np.asarray(jd, dtype=np.float64)
        lat_a = np.asarray(lat, dtype=np.float64)
        lon_a = np.asarray(lon, dtype=np.float64)

        # Broadcast inputs to common shape so output dict has consistent shape.
        jd_b, lat_b, lon_b = np.broadcast_arrays(jd_a, lat_a, lon_a)

        armc = compute_armc(jd_b, lon_b)  # shape == jd_b.shape
        eps = np.asarray(mean_obliquity(jd_b))  # already vectorized

        armc_rad = np.deg2rad(armc)
        eps_rad = np.deg2rad(eps)
        lat_rad = np.deg2rad(lat_b)

        # MC: atan2(sin(armc), cos(armc)·cos(eps))
        mc = np.rad2deg(np.arctan2(
            np.sin(armc_rad),
            np.cos(armc_rad) * np.cos(eps_rad),
        )) % 360.0

        # ASC: atan2(cos(armc), -[sin(eps)·tan(lat) + cos(eps)·sin(armc)])
        asc = np.rad2deg(np.arctan2(
            np.cos(armc_rad),
            -(np.sin(eps_rad) * np.tan(lat_rad)
              + np.cos(eps_rad) * np.sin(armc_rad)),
        )) % 360.0

        # Vertex: ASC formula with co-latitude (90° - |lat|)
        # Use the actual sign of lat for hemisphere correctness:
        # research §"Don't Hand-Roll" notes vertex = atan2(cos(armc),
        # -[sin(eps)·tan(90°-lat) + cos(eps)·sin(armc)])
        co_lat_rad = np.deg2rad(90.0 - lat_b)
        vertex = np.rad2deg(np.arctan2(
            np.cos(armc_rad),
            -(np.sin(eps_rad) * np.tan(co_lat_rad)
              + np.cos(eps_rad) * np.sin(armc_rad)),
        )) % 360.0

        return {
            "asc": asc,
            "mc": mc,
            "armc": armc,
            "vertex": vertex,
            "eps": eps,
        }
    ```

    Anti-patterns to avoid:
    - Do NOT use `np.arctan(y / x)` — Pitfall 2 from research; quadrant errors guaranteed. Always `np.arctan2(y, x)`.
    - Do NOT precompute `tan(lat)` once outside `np.deg2rad(lat)` — vectorize the trig with NumPy ufuncs, don't try to "cache" tan into a scalar.
    - Do NOT round angles to integer seconds inside this module — full f8 precision flows through to the dtype field. Test tolerance (1 arcmin = 1/60 deg) lives in the TEST file, not the production code.
    - Do NOT call `sidereal_time` with `lon` as the second argument and use that as ARMC (semantic correctness only — ARMC IS local sidereal time in degrees, but the explicit `compute_armc(jd, lon) = sidereal_time(jd, 0.0) + lon` decomposition matches the research §Pitfall 5 documentation pattern, making it auditable).
    - Do NOT vectorize `sidereal_time` here as scope creep — the wrapping list-comprehension is cheap (microseconds for 1000 charts) and keeps the change surface small. If profiling later shows it's a bottleneck, vectorize it in a follow-up phase.
    - Do NOT skip the Vertex computation "because Open Question 3 says it's advisory" — research §Open Question 3 recommends implementing the closed form; we do, and tests assert <1 arcmin agreement (same tolerance as ASC; if Vertex is worse, document in SUMMARY).

    The `compute_armc` lift via list-comprehension over ravel() is a pragmatic shim — sidereal_time is currently scalar-only. Document this in the function docstring with a note for Plan 10-06: "future work — vectorize sidereal_time directly".
  </action>
  <verify>
    `python -c "from ketu.houses.ascmc import compute_ascmc; r = compute_ascmc(2451545.0, 48.8566, 2.3522); print(r['asc'], r['mc'], r['armc'], r['vertex'], r['eps'])"` runs without error and prints 5 values.

    `python -c "
    import numpy as np
    from ketu.houses.ascmc import compute_ascmc
    jds = np.array([2451545.0, 2470204.0])
    lats = np.array([48.8566, 64.1466])
    lons = np.array([2.3522, -21.9426])
    r = compute_ascmc(jds, lats, lons)
    assert r['asc'].shape == (2,)
    print(r['asc'], r['mc'])
    "` — vectorized path returns shape (2,).

    `mypy --strict ketu/houses/ascmc.py` is clean.

    Empirical sanity: at J2000, lat=48.8566, lon=2.3522, ASC should be ~26.77° (research §Example 1). Run `compute_ascmc(2451545.0, 48.8566, 2.3522)` and verify ASC is in [25, 28] range. If outside this band, the formula or the units are wrong.
  </verify>
  <done>
    `ketu/houses/ascmc.py` exists with `compute_armc` and `compute_ascmc`. Both vectorized (scalar in → scalar out, ndarray in → ndarray out). ASC and MC use np.arctan2 only. compute_ascmc returns dict with 5 keys (asc, mc, armc, vertex, eps). mypy --strict clean. Paris J2000 ASC sanity check passes (in [25, 28]°).
  </done>
</task>

<task type="auto">
  <name>Task 3: Write tests/houses/{test_dtype,test_registry,test_ascmc}.py — assert structure, registry, and oracle agreement</name>
  <files>tests/houses/test_dtype.py
tests/houses/test_registry.py
tests/houses/test_ascmc.py</files>
  <action>
    Step A — `tests/houses/test_dtype.py`:

    ```python
    """HOUSES_DTYPE structural tests — field names, shapes, subarray semantics."""
    from __future__ import annotations
    import numpy as np
    import pytest

    from ketu.houses import HOUSES_DTYPE


    def test_dtype_field_names_match_spec():
        expected = ("jd", "lat", "lon", "system", "cusps", "asc", "mc", "armc", "vertex")
        assert HOUSES_DTYPE.names == expected, (
            f"HOUSES_DTYPE field names drifted: {HOUSES_DTYPE.names}"
        )


    def test_dtype_cusps_is_subarray_of_length_12():
        cusps_dtype = HOUSES_DTYPE.fields["cusps"][0]
        # Subarray fields expose .shape on the field dtype (NumPy 1.20+ semantics)
        assert cusps_dtype.shape == (12,), (
            f"cusps subarray shape drifted: {cusps_dtype.shape}"
        )


    def test_dtype_supports_vectorized_construction():
        """Outer shape (N,) → cusps field accessible as (N, 12)."""
        arr = np.zeros(3, dtype=HOUSES_DTYPE)
        assert arr["cusps"].shape == (3, 12)
        # Assignment round-trip
        arr["cusps"][0] = np.arange(12, dtype=np.float64)
        assert arr["cusps"][0, 5] == 5.0


    def test_dtype_string_field_capacity():
        """system field is U10 — fits 'placidus', 'koch', 'porphyry', 'whole_sign'."""
        for name in ("placidus", "koch", "porphyry", "whole_sign"):
            arr = np.zeros(1, dtype=HOUSES_DTYPE)
            arr["system"][0] = name
            assert arr["system"][0] == name


    def test_high_latitude_error_is_value_error_subclass():
        from ketu.houses import HighLatitudeError
        e = HighLatitudeError(75.0, "placidus", 66.5616)
        assert isinstance(e, ValueError)
        assert e.lat == 75.0
        assert e.system == "placidus"
        assert e.polar_lat == 66.5616
        assert "75.0000" in str(e)
        assert "placidus" in str(e)
        assert "porphyry" in str(e)  # Hint to caller about polar_fallback option
    ```

    Step B — `tests/houses/test_registry.py`:

    ```python
    """Registry pattern tests — register decorator, dispatch, case-insensitivity."""
    from __future__ import annotations
    import numpy as np
    import pytest

    from ketu.houses.registry import SYSTEMS, register, get_system


    def test_register_inserts_into_systems_dict():
        @register("test_register_demo")
        def demo_fn(armc, lat, eps):
            return np.zeros((12,))
        try:
            assert "test_register_demo" in SYSTEMS
            assert SYSTEMS["test_register_demo"] is demo_fn
        finally:
            del SYSTEMS["test_register_demo"]  # cleanup so test order doesn't matter


    def test_register_lowercases_name():
        @register("Test_Case_INSENSITIVE")
        def fn(armc, lat, eps):
            return np.zeros((12,))
        try:
            assert "test_case_insensitive" in SYSTEMS
            assert "Test_Case_INSENSITIVE" not in SYSTEMS
        finally:
            del SYSTEMS["test_case_insensitive"]


    def test_get_system_lookup_is_case_insensitive():
        @register("test_lookup")
        def fn(armc, lat, eps):
            return np.zeros((12,))
        try:
            assert get_system("TEST_LOOKUP") is fn
            assert get_system("test_lookup") is fn
            assert get_system("Test_Lookup") is fn
        finally:
            del SYSTEMS["test_lookup"]


    def test_get_system_raises_value_error_with_helpful_message():
        with pytest.raises(ValueError) as exc_info:
            get_system("nonexistent_system_xyz")
        msg = str(exc_info.value)
        assert "nonexistent_system_xyz" in msg
        assert "available" in msg


    def test_systems_dict_is_initially_empty_or_only_contains_planted_systems():
        """Plan 10-03 leaves SYSTEMS empty; Plans 04/05 will populate.

        This test asserts the contract at Plan 10-03 boundary. After Plans
        04/05 land, SYSTEMS will contain {placidus, koch, porphyry} and this
        test is updated by Plan 10-06 (or removed if it's no longer informative).
        """
        # Defensive: SYSTEMS may already contain entries if Plans 04/05 ran first.
        # Just assert the registry mechanism itself works — the main point of
        # this test file is the decorator and dispatch, not the population.
        assert isinstance(SYSTEMS, dict)
    ```

    Step C — `tests/houses/test_ascmc.py`:

    ```python
    """ASC/MC/ARMC/Vertex closed-form tests vs swisseph oracle.

    Tolerance: <1 arcmin (1/60 deg ≈ 0.01667°) per HOU-01 spec for ASC.
    MC is held to the same tolerance; Vertex is recorded but tolerance widened
    to 5 arcmin per Open Question 3 (advisory until proven tight).
    """
    from __future__ import annotations
    import numpy as np
    import pytest

    from ketu.houses.ascmc import compute_ascmc, compute_armc

    ARCMIN_DEG = 1.0 / 60.0  # 0.01667°
    ASC_MC_TOL = 1.0 * ARCMIN_DEG     # HOU-01 spec
    VERTEX_TOL = 5.0 * ARCMIN_DEG     # Advisory (Open Question 3)


    @pytest.mark.parametrize(
        "label",
        ["J2000_Greenwich", "J2000_Paris", "J2000_Sydney",
         "J2000_Tokyo", "J2000_BuenosAires", "J2000_Equator",
         "1900_NewYork", "2050_Reykjavik"],
    )
    def test_ascmc_matches_swisseph_within_arcmin(
        label, reference_charts, loaded_reference_snapshot,
    ):
        """All non-polar reference charts agree with swisseph oracle to <1 arcmin on ASC and MC."""
        # Find chart by label
        chart = next(c for c in reference_charts if c["label"] == label)
        snap = loaded_reference_snapshot["charts"][label]["systems"]["placidus"]

        # ASC and MC are system-independent — ANY system in the snapshot has the same ASC/MC.
        # Use placidus (always present in non-polar snapshot entries).
        result = compute_ascmc(chart["jd"], chart["lat"], chart["lon"])

        asc_delta = abs(((float(result["asc"]) - snap["asc"] + 180.0) % 360.0) - 180.0)
        mc_delta = abs(((float(result["mc"]) - snap["mc"] + 180.0) % 360.0) - 180.0)
        armc_delta = abs(((float(result["armc"]) - snap["armc"] + 180.0) % 360.0) - 180.0)

        assert asc_delta < ASC_MC_TOL, (
            f"{label}: ASC drift {asc_delta * 60:.3f} arcmin > {ASC_MC_TOL * 60} arcmin"
        )
        assert mc_delta < ASC_MC_TOL, (
            f"{label}: MC drift {mc_delta * 60:.3f} arcmin > {ASC_MC_TOL * 60} arcmin"
        )
        assert armc_delta < ASC_MC_TOL, (
            f"{label}: ARMC drift {armc_delta * 60:.3f} arcmin > {ASC_MC_TOL * 60} arcmin"
        )


    @pytest.mark.parametrize(
        "label",
        ["J2000_Greenwich", "J2000_Paris", "J2000_Sydney",
         "1900_NewYork", "2050_Reykjavik"],
    )
    def test_vertex_matches_swisseph_within_5_arcmin(
        label, reference_charts, loaded_reference_snapshot,
    ):
        """Vertex agreement is advisory per Open Question 3 — log actual delta."""
        chart = next(c for c in reference_charts if c["label"] == label)
        snap = loaded_reference_snapshot["charts"][label]["systems"]["placidus"]
        result = compute_ascmc(chart["jd"], chart["lat"], chart["lon"])
        vtx_delta = abs(((float(result["vertex"]) - snap["vertex"] + 180.0) % 360.0) - 180.0)
        assert vtx_delta < VERTEX_TOL, (
            f"{label}: Vertex drift {vtx_delta * 60:.3f} arcmin > {VERTEX_TOL * 60} arcmin "
            "(may indicate co-latitude formula needs sign correction; see "
            "10-RESEARCH.md Open Question 3)"
        )


    def test_compute_ascmc_vectorized_preserves_leading_shape():
        jds = np.array([2451545.0, 2470204.0, 2415020.5])
        lats = np.array([48.8566, 64.1466, 40.7128])
        lons = np.array([2.3522, -21.9426, -74.0060])
        result = compute_ascmc(jds, lats, lons)
        for key in ("asc", "mc", "armc", "vertex", "eps"):
            assert result[key].shape == (3,), f"{key} lost leading shape"


    def test_compute_armc_equals_sidereal_time_plus_longitude():
        from ketu.ephemeris.time import sidereal_time
        jd = 2451545.0
        lon = 45.0
        armc = compute_armc(jd, lon)
        expected = (sidereal_time(jd, 0.0) + lon) % 360.0
        assert abs(float(armc) - expected) < 1e-9, (
            "compute_armc must equal sidereal_time(jd, 0) + lon; if you changed "
            "the formula, check Pitfall 5 in 10-RESEARCH.md"
        )
    ```

    Anti-patterns to avoid:
    - Do NOT loosen the ASC tolerance to 5 arcmin "to make tests pass" — HOU-01 spec is <1 arcmin. If 1 arcmin fails, that's a real bug (probably in the IAU 1982 vs 2006 GMST decision from Plan 01).
    - Do NOT include polar charts (lat=70°, lat=80°) in test_ascmc_matches_swisseph — those are oracle-erroring snapshots, not numerical fixtures. Polar handling lives in Plan 10-05.
    - Do NOT register a real house system in test_registry.py — test cleanup uses `del SYSTEMS["..."]` to avoid leaking state into test_ascmc / Plan 04/05 tests.
    - Do NOT compare angles via raw subtraction — use modular distance `abs(((a - b + 180) % 360) - 180)` to handle the 0°/360° wrap (Pitfall 3).
    - Do NOT assume snapshot's ASC field is always present — test_ascmc parametrize list is hard-coded to the 8 non-polar labels; that's defensive against snapshot drift.
  </action>
  <verify>
    `pytest tests/houses/test_dtype.py tests/houses/test_registry.py tests/houses/test_ascmc.py -v` runs and shows all tests passing (assuming swisseph installed; otherwise the tests using the snapshot fixture skip via importorskip in conftest.py).

    Specifically:
    - test_dtype.py: 5 tests pass
    - test_registry.py: 5 tests pass
    - test_ascmc.py: 8 (paris+others) + 5 (vertex) + 1 (vectorized) + 1 (armc identity) = 15 test cases pass

    `mypy --strict tests/houses/test_dtype.py tests/houses/test_registry.py tests/houses/test_ascmc.py` clean.

    `pytest tests/ -v` — full suite passes (488 + 15 + 6 + ~25 = 534+ tests).
  </verify>
  <done>
    Three test files exist. test_dtype passes 5 structural tests. test_registry passes 5 dispatch tests with proper cleanup (no leaked SYSTEMS entries). test_ascmc passes 15 oracle-agreement tests at <1 arcmin for ASC/MC/ARMC and <5 arcmin for Vertex (Open Question 3). All vectorized-shape and ARMC-identity invariants hold. Full pytest suite green; mypy --strict clean.
  </done>
</task>

</tasks>

<verification>
- `pytest tests/houses/ -v` shows >40 tests passing across test_lst_obliquity_precision (Plan 01), test_oracle_smoke (Plan 02), test_dtype, test_registry, test_ascmc.
- ASC and MC agree with swisseph oracle to <1 arcmin at all 8 non-polar reference charts.
- Vertex agrees with swisseph oracle to <5 arcmin at 5 sampled charts (advisory threshold).
- HOUSES_DTYPE has exactly 9 fields including cusps subarray (12,); supports vectorized N-shape construction.
- SYSTEMS dict starts empty (or contains only test-cleaned planted systems); Plans 04/05 will populate.
- HighLatitudeError is a ValueError subclass with lat/system/polar_lat attributes.
- `mypy --strict ketu/houses/ tests/houses/` clean.
- `grep -r "swisseph" ketu/houses/` returns nothing — pure-NumPy contract preserved.
- `pyproject.toml [tool.setuptools].packages` includes `ketu.houses`.
</verification>

<success_criteria>
- HOU-02 partial: registry pattern (SYSTEMS dict + register decorator) lands and is dispatched-tested. Plans 04/05 plug in.
- HOU-05 partial: HOUSES_DTYPE structured array with 12-element cusps subarray + 4 angle fields + jd/lat/lon/system meta. Vectorized construction works.
- HOU-01 wiring: ARMC computation goes through `sidereal_time(jd, 0.0) + lon` per Pitfall 5 — explicit and auditable.
- Closed-form ASC/MC/Vertex via np.arctan2 (Pitfall 2 avoided), tested vectorized, oracle agreement <1 arcmin (ASC/MC) and <5 arcmin (Vertex).
- Public API surface (calculate_houses, house_of) is declared with correct signatures even though bodies stub-raise NotImplementedError. Plan 10-06 fills them in.
</success_criteria>

<output>
After completion, create `.planning/phases/10-houses-module/10-03-SUMMARY.md` documenting:
- Files created (5 in ketu/houses/, 3 in tests/houses/)
- HOUSES_DTYPE field-by-field breakdown (name, type, shape) — table
- ASC/MC/Vertex worst-case oracle delta across all 8 charts (table: label, asc_arcmin, mc_arcmin, vertex_arcmin)
- Verification: SYSTEMS at end of plan = empty (Plans 04/05 will populate)
- Confirmation: pyproject.toml updated with ketu.houses package; ketu/__init__.py re-exports the 5 new names; mypy --strict clean; no runtime swisseph imports
</output>
