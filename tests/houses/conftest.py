"""Test infrastructure for ``tests/houses/``.

Provides swisseph oracle helpers and reference chart fixtures.

``swisseph`` is a test-only AGPL-licensed dep — :func:`pytest.importorskip`
ensures the module is wholesale-skipped (never partially imported) when
swisseph is absent. Same dual-import pattern as
``tests/test_lilith_cross_check.py`` and
``tests/houses/test_lst_obliquity_precision.py``: module-level
``pytest.importorskip("swisseph")`` followed by ``import swisseph as swe``,
because mypy ``[tool.mypy.overrides] module = ["swisseph.*"]`` matches
direct ``import`` statements only, not the ``swe = importorskip(...)``
binding.

Public surface (consumed by Plans 10-03, 10-04, 10-05, 10-06):

- :data:`SYSTEM_BYTES` — maps lowercase system name (str) to the single-byte
  ``hsys`` code expected by pyswisseph (Pitfall 8 from research §"Don't
  Hand-Roll" — the bytes-vs-str trap is solved at this oracle boundary).
- :func:`swe_oracle` — high-level oracle: ``(jd, lat, lon, system) -> dict``
  via :func:`swe.houses_ex`.
- :func:`swe_oracle_armc` — ARMC-direct oracle: ``(armc, lat, eps, system)
  -> dict`` via :func:`swe.houses_armc`. Used by Plans 03/04/05 to isolate
  algorithm error from sidereal-time error.
- ``reference_charts`` — session-scoped fixture: list of ≥10 chart dicts
  spanning normal, mid-, southern, 1900/2050 boundary, AND polar (70°/80°)
  latitudes per HOU-09.
- ``loaded_reference_snapshot`` — session-scoped fixture: loads the JSON
  snapshot at :data:`REFERENCE_CHARTS_JSON`; pytest-skips if missing.
"""

from __future__ import annotations

# IMPORTANT: numpy MUST be imported BEFORE swisseph. The pyswisseph C
# extension links against numpy at load time; if coverage.py's import
# hooks rewrite the numpy module mid-flight (e.g. when more test
# modules load numpy paths via ``ketu.houses`` BEFORE this conftest is
# reached), the swisseph extension and numpy can end up holding
# different module instances of numpy's sentinels (``_NoValueType``),
# manifesting as ``TypeError: float() argument must be ... not
# '_NoValueType'`` from inside numpy's reductions. Pinning numpy first
# (and BEFORE the importorskip below) keeps the import order stable
# across coverage and non-coverage runs.
import numpy as np
import pytest

import json  # noqa: E402  (after numpy import per ordering rationale above)
from pathlib import Path  # noqa: E402
from typing import Any  # noqa: E402

# Module-level gate: when pysweph is absent, the line below raises
# pytest.skip.Exception at collection time so the entire tests/houses/
# directory is reported as SKIPPED rather than ERRORED. We deliberately
# do NOT bind the return value (``swe = pytest.importorskip(...)``) because
# that yields a ``ModuleType`` local that mypy --strict rejects on every
# attribute access. The pyproject ``[[tool.mypy.overrides]] module =
# ["swisseph.*"]`` rule matches direct ``import swisseph`` statements only,
# not bindings; hence the separate ``import swisseph as swe`` line below.
pytest.importorskip("swisseph")
import swisseph as swe  # noqa: E402  (after importorskip is project convention)


# ----------------------------------------------------------------------------
# Module-level constants
# ----------------------------------------------------------------------------

# Map public system name (lowercase) -> swisseph single-byte ``hsys`` code.
# Pitfall 8 from research §"Don't Hand-Roll": pyswisseph requires bytes, not
# str. Centralising the mapping here means downstream test files never see
# the bytes-vs-str trap.
#
# Codes per the Astrodienst hsys table:
#   b"P" = Placidus
#   b"K" = Koch
#   b"O" = Porphyry  (closed-form; finite at all latitudes — used as the
#                    polar fallback in Plan 10-05)
SYSTEM_BYTES: dict[str, bytes] = {
    "placidus": b"P",
    "koch": b"K",
    "porphyry": b"O",
}

# Path to the snapshotted oracle JSON. Computed once at import time using
# Path(__file__) so the conftest works from any cwd (pytest invocation,
# ad-hoc REPL exploration, snapshot-regeneration script).
FIXTURES_DIR: Path = Path(__file__).parent / "fixtures"
REFERENCE_CHARTS_JSON: Path = FIXTURES_DIR / "reference_charts.json"


# ----------------------------------------------------------------------------
# Oracle helpers
# ----------------------------------------------------------------------------


def swe_oracle(jd: float, lat: float, lon: float, system: str) -> dict[str, Any]:
    """Call :func:`swe.houses_ex` and return a normalised result dict.

    Parameters
    ----------
    jd : float
        Julian Day (UT) for which to compute house cusps.
    lat : float
        Geographic latitude in degrees (positive north).
    lon : float
        Geographic longitude in degrees (positive east).
    system : str
        Lowercase system name; key into :data:`SYSTEM_BYTES`
        (``"placidus"``, ``"koch"``, ``"porphyry"``).

    Returns
    -------
    dict
        On success::

            {
                "cusps":  np.ndarray shape (12,)   # 0-indexed cusps 1..12
                "asc":    float
                "mc":     float
                "armc":   float
                "vertex": float
            }

        On polar failure (swisseph raises :class:`swisseph.Error` for
        Placidus/Koch beyond the polar circle)::

            {"error": "<exception message>", "polar": True}

    Notes
    -----
    :func:`swe.houses_ex` returns ``(cusps_13_tuple, ascmc_8_tuple)``.
    ``cusps_t[0]`` is a C-style 1-indexed placeholder (= 0.0); we slice
    ``cusps_t[1:13]`` to obtain the 12-element 0-indexed array
    (research Pitfall 7).
    """
    try:
        cusps_t, ascmc_t = swe.houses_ex(jd, lat, lon, SYSTEM_BYTES[system])
    except swe.Error as exc:
        return {"error": str(exc), "polar": True}

    cusps_arr = np.asarray(cusps_t[1:13], dtype=np.float64)
    return {
        "cusps": cusps_arr,
        "asc": float(ascmc_t[0]),
        "mc": float(ascmc_t[1]),
        "armc": float(ascmc_t[2]),
        "vertex": float(ascmc_t[3]),
    }


def swe_oracle_armc(
    armc: float, lat: float, eps: float, system: str
) -> dict[str, Any]:
    """Call :func:`swe.houses_armc` and return a normalised result dict.

    Same return shape as :func:`swe_oracle`. Used by Plans 03/04/05 to
    isolate algorithm error from sidereal-time error: caller supplies its
    own ARMC, oracle returns cusps for that ARMC without invoking
    :func:`swe.sidtime`.

    Parameters
    ----------
    armc : float
        Apparent right ascension of the meridian, in degrees.
    lat : float
        Geographic latitude in degrees.
    eps : float
        True obliquity of the ecliptic in degrees.
    system : str
        Lowercase system name; key into :data:`SYSTEM_BYTES`.

    Returns
    -------
    dict
        See :func:`swe_oracle`.
    """
    try:
        cusps_t, ascmc_t = swe.houses_armc(armc, lat, eps, SYSTEM_BYTES[system])
    except swe.Error as exc:
        return {"error": str(exc), "polar": True}

    cusps_arr = np.asarray(cusps_t[1:13], dtype=np.float64)
    return {
        "cusps": cusps_arr,
        "asc": float(ascmc_t[0]),
        "mc": float(ascmc_t[1]),
        "armc": float(ascmc_t[2]),
        "vertex": float(ascmc_t[3]),
    }


# ----------------------------------------------------------------------------
# Pytest fixtures
# ----------------------------------------------------------------------------


@pytest.fixture(scope="session")
def reference_charts() -> list[dict[str, Any]]:
    """≥10 reference (label, jd, lat, lon) entries for HOU-09.

    Coverage:

    - **Normal latitudes**: Greenwich (51.5°N), Paris (48.9°N),
      Buenos Aires (-34.6°N), New York (40.7°N).
    - **Mid-latitudes**: Sydney (-33.9°N), Tokyo (35.7°N).
    - **Southern hemisphere**: Sydney, Buenos Aires.
    - **Equator** (degenerate case): lat = 0°.
    - **Time boundary**: 1900-01-01 (JD 2415020.5), 2050-01-01.5 (JD
      2470204.0), J2000.0 (JD 2451545.0).
    - **Polar** (HOU-09 explicit requirement): lat=70°N and lat=80°N at
      J2000.0 (Placidus/Koch raise :class:`swisseph.Error` here; Porphyry
      remains finite).

    Returns
    -------
    list[dict]
        Each entry has keys ``label`` (str), ``jd`` (float), ``lat`` (float),
        ``lon`` (float).
    """
    return [
        {"label": "J2000_Greenwich",   "jd": 2451545.0, "lat": 51.4779, "lon": 0.0},
        {"label": "J2000_Paris",       "jd": 2451545.0, "lat": 48.8566, "lon": 2.3522},
        {"label": "J2000_Sydney",      "jd": 2451545.0, "lat": -33.8688, "lon": 151.2093},
        {"label": "J2000_Tokyo",       "jd": 2451545.0, "lat": 35.6762, "lon": 139.6503},
        {"label": "J2000_BuenosAires", "jd": 2451545.0, "lat": -34.6037, "lon": -58.3816},
        {"label": "J2000_Equator",     "jd": 2451545.0, "lat": 0.0, "lon": 0.0},
        {"label": "1900_NewYork",      "jd": 2415020.5, "lat": 40.7128, "lon": -74.0060},
        {"label": "2050_Reykjavik",    "jd": 2470204.0, "lat": 64.1466, "lon": -21.9426},
        # Polar (HOU-09 explicit requirement)
        {"label": "J2000_Lat70_North", "jd": 2451545.0, "lat": 70.0, "lon": 0.0},
        {"label": "J2000_Lat80_North", "jd": 2451545.0, "lat": 80.0, "lon": 0.0},
    ]


@pytest.fixture(scope="session")
def loaded_reference_snapshot() -> dict[str, Any]:
    """Load the committed JSON oracle snapshot from disk.

    Skips the test (rather than crashing collection) if the file is
    missing — supports a fresh-checkout flow where the snapshot has not
    yet been regenerated.

    Returns
    -------
    dict
        Top-level structure: ``{"version": str, "charts": {...}}``.
    """
    if not REFERENCE_CHARTS_JSON.exists():
        pytest.skip(
            f"Reference snapshot not found at {REFERENCE_CHARTS_JSON}. "
            "Run scripts/snapshot_reference_charts.py to regenerate."
        )
    with REFERENCE_CHARTS_JSON.open() as f:
        loaded: dict[str, Any] = json.load(f)
    return loaded
