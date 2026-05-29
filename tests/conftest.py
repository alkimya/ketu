"""Shared session-scoped fixtures auto-discovered by all test subpackages.

Consolidates the six ``chart_*`` (:data:`ketu.charts.CHART_DTYPE` arrays)
and six ``natal_*`` (``dict[str, float]`` natal triples) fixtures that were
previously duplicated across ``tests/synastry/conftest.py``,
``tests/composite/conftest.py``, and ``tests/returns/conftest.py``.

Pytest's standard conftest auto-discovery makes every fixture defined here
available to every test beneath ``tests/`` — no ``pytest_plugins`` import,
no cross-package import needed (REF-03, Phase 22 ephemeris refactor).

Subpackage-specific fixtures (``oracle_fixture``, ``ORACLE_SLUGS``,
``load_oracle_fixture``) remain in their respective conftests because
synastry and composite each point to a DIFFERENT ``fixtures/`` directory
and declare DIFFERENT mandatory JSON keys; those are NOT shared.
"""
from __future__ import annotations

import numpy as np
import pytest

from ketu.charts import compute_chart


# ---------------------------------------------------------------------------
# chart_* fixtures — CHART_DTYPE structured arrays
# ---------------------------------------------------------------------------
# Six session-scoped chart fixtures covering a range of latitudes, JDs, and
# edge cases. Originally defined in tests/synastry/conftest.py and
# tests/composite/conftest.py (byte-for-byte identical copies). Moved here
# by REF-03 so Phase 24+ only needs one place to add new natal personas.
#
# The polar fixture (chart_b_reykjavik) MUST keep polar_fallback="porphyry"
# — at latitude 64.15 Placidus may raise HighLatitudeError; losing the
# fallback would let a house-system failure mask synastry/composite bugs.
# This is the Pitfall 3 ratchet from .planning/phases/16-synastry/16-RESEARCH.md.
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def chart_a_paris() -> np.ndarray:
    """J2000 noon UTC chart for Paris (lat 48.86, lon 2.35) — chart A baseline."""
    return compute_chart(2451545.0, 48.86, 2.35)


@pytest.fixture(scope="session")
def chart_b_reykjavik() -> np.ndarray:
    """JD 2470204 noon UTC chart for Reykjavik (lat 64.15, lon -21.94).

    MUST pass ``polar_fallback='porphyry'`` — at lat 64.15 placidus may
    raise :class:`ketu.houses.HighLatitudeError` and the test would fail
    because ``compute_chart`` itself raises, not because synastry is
    wrong.
    """
    return compute_chart(2470204.0, 64.15, -21.94, polar_fallback="porphyry")


@pytest.fixture(scope="session")
def chart_b_nyc() -> np.ndarray:
    """JD 2451900 noon UTC chart for New York (lat 40.71, lon -74.01)."""
    return compute_chart(2451900.0, 40.71, -74.01)


@pytest.fixture(scope="session")
def chart_b_tokyo() -> np.ndarray:
    """JD 2451545 noon UTC chart for Tokyo (lat 35.69, lon 139.69)."""
    return compute_chart(2451545.0, 35.69, 139.69)


@pytest.fixture(scope="session")
def chart_b_sydney() -> np.ndarray:
    """JD 2451545 noon UTC chart for Sydney (lat -33.87, lon 151.21)."""
    return compute_chart(2451545.0, -33.87, 151.21)


@pytest.fixture(scope="session")
def chart_a_retrograde_mercury() -> np.ndarray:
    """JD 2460530 noon UTC chart for Paris with Mercury retrograde.

    Mid-August 2024 sits inside the Mercury retrograde window
    (approximately 2024-08-05..2024-08-28); Mercury's longitudinal speed
    is negative (~-0.19 deg/day). Used by Pitfall 4 ratchet tests to
    verify that the velocity-based ``applying`` field preserves the
    signed convention even when one body is retrograde.
    """
    return compute_chart(2460530.0, 48.86, 2.35)


# ---------------------------------------------------------------------------
# natal_* fixtures — dict[str, float] natal triples (jd / lat / lon)
# ---------------------------------------------------------------------------
# Six session-scoped natal triples consumed by tests/returns/ tests.
# NOT CHART_DTYPE — returns tests work on raw JD + lat + lon, not on the
# full CHART_DTYPE struct. Originally defined in tests/returns/conftest.py;
# moved here by REF-03.
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def natal_diana() -> dict[str, float]:
    """Princess Diana — 1961-07-01 18:45 UT, Sandringham (52.83 N, 0.50 E).

    Returns
    -------
    dict[str, float]
        Natal triple ``{"jd": 2437482.28125, "lat": 52.83, "lon": 0.50}``.
        Sourced from ``tests/synastry/fixtures/oracle_diana_charles.json``
        (AA rating per AstroDatabank; UTC = 18:45 = 19:45 BST - 1 h).
    """
    return {"jd": 2437482.28125, "lat": 52.83, "lon": 0.50}


@pytest.fixture(scope="session")
def natal_charles() -> dict[str, float]:
    """Prince Charles — 1948-11-14 21:14 UT, London (51.50 N, -0.17 E).

    Returns
    -------
    dict[str, float]
        Natal triple ``{"jd": 2432870.384722, "lat": 51.50, "lon": -0.17}``.
        Sourced from ``tests/synastry/fixtures/oracle_diana_charles.json``
        (AA rating per AstroDatabank; GMT = UTC in November).
    """
    return {"jd": 2432870.384722, "lat": 51.50, "lon": -0.17}


@pytest.fixture(scope="session")
def natal_marie_curie() -> dict[str, float]:
    """Marie Curie — 1867-11-07 10:36 UT, Warsaw (52.23 N, 21.01 E).

    Returns
    -------
    dict[str, float]
        Natal triple ``{"jd": 2403277.941667, "lat": 52.23, "lon": 21.01}``.
        Sourced from ``tests/synastry/fixtures/oracle_curie.json``
        (AA rating per AstroDatabank).
    """
    return {"jd": 2403277.941667, "lat": 52.23, "lon": 21.01}


@pytest.fixture(scope="session")
def natal_pierre_curie() -> dict[str, float]:
    """Pierre Curie — 1859-05-15 11:51 UT, Paris (48.85 N, 2.35 E).

    Returns
    -------
    dict[str, float]
        Natal triple ``{"jd": 2400179.993750, "lat": 48.85, "lon": 2.35}``.
        Sourced from ``tests/synastry/fixtures/oracle_curie.json``
        (C rating per AstroDatabank — noon LMT approximate).
    """
    # 1859-05-15T11:51:00Z → JD 2400179.99375
    return {"jd": 2400179.99375, "lat": 48.85, "lon": 2.35}


@pytest.fixture(scope="session")
def natal_lennon() -> dict[str, float]:
    """John Lennon — 1940-10-09 18:30 UT, Liverpool (53.41 N, -2.99 E).

    Returns
    -------
    dict[str, float]
        Natal triple ``{"jd": 2429912.270833, "lat": 53.41, "lon": -2.99}``.
        Sourced from ``tests/synastry/fixtures/oracle_lennon_ono.json``
        (A rating per AstroDatabank; ±15 min uncertainty).
    """
    return {"jd": 2429912.270833, "lat": 53.41, "lon": -2.99}


@pytest.fixture(scope="session")
def natal_ono() -> dict[str, float]:
    """Yoko Ono — 1933-02-18 11:30 UT, Tokyo (35.69 N, 139.69 E).

    Returns
    -------
    dict[str, float]
        Natal triple ``{"jd": 2427121.979167, "lat": 35.69, "lon": 139.69}``.
        Sourced from ``tests/synastry/fixtures/oracle_lennon_ono.json``
        (AA rating per AstroDatabank; 11:30 UT = 20:30 JST in pre-1948 Tokyo).
    """
    # 1933-02-18T11:30:00Z → JD 2427121.979167
    return {"jd": 2427121.979167, "lat": 35.69, "lon": 139.69}
