"""Phase-16 synastry test fixtures.

Builds chart pairs inline via :func:`ketu.charts.compute_chart` so tests
can exercise :func:`ketu.synastry.calculate_synastry` against deterministic,
hand-picked chart inputs. Phase-14's ``tests/charts/conftest.py`` exposes
oracle-validation fixtures (``reference_charts``, ``swe_oracle``); those are
not what synastry needs, so we build our own here.

Fixture scope is ``session`` because :func:`ketu.charts.compute_chart` is
non-trivial (swisseph + house solve); reuse across the synastry test suite
amortises the cost.

The polar fixture (``chart_b_reykjavik``) MUST pass
``polar_fallback='porphyry'`` — at latitude 64.15 placidus may raise
:class:`ketu.houses.HighLatitudeError`, and a polar failure inside the
fixture would mask synastry bugs. This is the Pitfall 3 ratchet from
``.planning/phases/16-synastry/16-RESEARCH.md``.
"""
from __future__ import annotations

import numpy as np
import pytest

from ketu.charts import compute_chart


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
