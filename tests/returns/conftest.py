"""Session-scoped natal fixtures for ``tests/returns/``.

Duplicated from ``tests/composite/conftest.py`` and
``tests/synastry/conftest.py`` to keep the returns subpackage tests
self-contained (Phase 17 precedent: each pair-chart test directory
owns its conftest; duplication preferred over cross-package
``pytest_plugins`` import for simplicity).

Six personas, same JDs/lat/lon as the composite + synastry oracle
fixtures (`tests/synastry/fixtures/oracle_*.json` and
`tests/composite/fixtures/oracle_*.json`) — single source of truth
for natal-data identity across pair-chart subpackages:

- Diana — Princess Diana, 1961-07-01 18:45 UT, Sandringham
- Charles — Prince Charles, 1948-11-14 21:14 UT, London
- Marie Curie — 1867-11-07 10:36 UT, Warsaw
- Pierre Curie — 1859-05-15 12:00 UT, Paris
- Lennon — John Lennon, 1940-10-09 18:30 UT, Liverpool
- Ono — Yoko Ono, 1933-02-18 20:30 UT, Tokyo

Each fixture is a ``dict[str, float]`` with keys ``jd``, ``lat``,
``lon`` — the minimal natal triple consumed by ``solar_return`` /
``lunar_return``. Composite/synastry conftest's CHART_DTYPE-shaped
fixtures are NOT replicated here: returns tests work on raw natal
JD + lat + lon, NOT on the natal CHART_DTYPE.
"""
from __future__ import annotations

import pytest


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
