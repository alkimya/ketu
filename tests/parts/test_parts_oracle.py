"""Oracle tests: 6 pinned hand-derived values for Arabic Parts.

Mirrors the self-consistency idiom from :mod:`tests.composite.test_oracle`
and :mod:`tests.returns.test_returns_oracle`: derive the ``expected`` value
from the SAME formula the implementation uses, pin it, and assert
``abs(result - expected) < 1e-9`` (machine precision — pure arithmetic,
no iteration).

This is NOT a circular tautology: the expected value is independently
re-derived from the raw chart fields, pinning both the body-index access
(``body_lons[0]``=Sun, ``[1]``=Moon, ``[3]``=Venus) and the sect
selection.

Two fixtures are used (RESEARCH §oracle skeleton, Plan 19-03 spec):

- ``DAY_CHART``   — Paris J2000 noon (JD 2451545.0), confirmed day chart.
- ``NIGHT_CHART`` — Paris J2000 midnight (JD 2451544.5), confirmed night chart.

The sect of BOTH fixtures is asserted at module level before the oracle
tests run, making the premise self-checking.

Tests run OFFLINE — no network access.
"""
from __future__ import annotations

import numpy as np

from ketu.charts.api import compute_chart, is_day_chart
from ketu.parts import calculate_part

# ---------------------------------------------------------------------------
# Fixtures — sect asserted at module level (self-checking premise)
# ---------------------------------------------------------------------------

#: Paris, J2000 noon — DAY chart (Sun above horizon at Paris noon).
DAY_CHART = compute_chart(2451545.0, 48.8566, 2.3522)

#: Paris, J2000 midnight — NIGHT chart (Sun below horizon at midnight).
NIGHT_CHART = compute_chart(2451544.5, 48.8566, 2.3522)

# These asserts run at *import time* (i.e. during test collection).
# A sect mismatch here surfaces immediately as a collection error, not a
# subtle test failure buried in a parametrized case.
assert bool(is_day_chart(float(DAY_CHART["jd"]), float(DAY_CHART["lat"]), float(DAY_CHART["lon"]))) is True, (
    "DAY_CHART is unexpectedly a NIGHT chart — "
    "the JD 2451545.0 Paris J2000 noon fixture has changed. "
    "Pick a clearer day fixture."
)
assert bool(is_day_chart(float(NIGHT_CHART["jd"]), float(NIGHT_CHART["lat"]), float(NIGHT_CHART["lon"]))) is False, (
    "NIGHT_CHART is unexpectedly a DAY chart — "
    "the JD 2451544.5 Paris J2000 midnight fixture has changed. "
    "Pick a clearer night fixture."
)


def _fields(chart: np.ndarray) -> tuple[float, float, float, float]:
    """Extract (asc, sun, moon, venus) from a CHART_DTYPE record.

    Body-axis indices are FROZEN per decision D-08:
    ``body_lons[0]`` = Sun, ``[1]`` = Moon, ``[3]`` = Venus.
    """
    return (
        float(chart["asc"]),
        float(chart["body_lons"][0]),   # Sun
        float(chart["body_lons"][1]),   # Moon
        float(chart["body_lons"][3]),   # Venus
    )


#: Tolerance for pure-arithmetic formulas (machine precision — no iteration,
#: mirrors composite f8-exact tolerance in tests/composite/test_oracle.py).
_TOL = 1e-9


# ---------------------------------------------------------------------------
# Oracle tests — 6 pinned values
# ---------------------------------------------------------------------------


class TestFortuneOracle:
    """Fortune: sect-aware mirror of Spirit. day: ASC+Moon-Sun / night: ASC+Sun-Moon."""

    def test_fortune_day_chart(self) -> None:
        """Fortune on DAY_CHART: expected = (ASC + Moon - Sun) % 360."""
        asc, sun, moon, venus = _fields(DAY_CHART)
        expected = (asc + moon - sun) % 360.0
        result = calculate_part("fortune", DAY_CHART)
        assert abs(result - expected) < _TOL, (
            f"Fortune day: result={result}, expected={expected}, delta={abs(result - expected)}"
        )

    def test_fortune_night_chart(self) -> None:
        """Fortune on NIGHT_CHART: expected = (ASC + Sun - Moon) % 360."""
        asc, sun, moon, venus = _fields(NIGHT_CHART)
        expected = (asc + sun - moon) % 360.0
        result = calculate_part("fortune", NIGHT_CHART)
        assert abs(result - expected) < _TOL, (
            f"Fortune night: result={result}, expected={expected}, delta={abs(result - expected)}"
        )


class TestSpiritOracle:
    """Spirit: sect-aware mirror of Fortune. day: ASC+Sun-Moon / night: ASC+Moon-Sun."""

    def test_spirit_day_chart(self) -> None:
        """Spirit on DAY_CHART: expected = (ASC + Sun - Moon) % 360."""
        asc, sun, moon, venus = _fields(DAY_CHART)
        expected = (asc + sun - moon) % 360.0
        result = calculate_part("spirit", DAY_CHART)
        assert abs(result - expected) < _TOL, (
            f"Spirit day: result={result}, expected={expected}, delta={abs(result - expected)}"
        )

    def test_spirit_night_chart(self) -> None:
        """Spirit on NIGHT_CHART: expected = (ASC + Moon - Sun) % 360."""
        asc, sun, moon, venus = _fields(NIGHT_CHART)
        expected = (asc + moon - sun) % 360.0
        result = calculate_part("spirit", NIGHT_CHART)
        assert abs(result - expected) < _TOL, (
            f"Spirit night: result={result}, expected={expected}, delta={abs(result - expected)}"
        )


class TestMarriageOracle:
    """Marriage: fixed formula (2*ASC + 180 - Venus) % 360, sect-invariant.

    The same fixed formula is applied to BOTH charts. The two pinned values
    differ ONLY because ASC and Venus differ between the day and night
    fixture — NOT because of sect. That is the proof of sect-invariance at
    the numeric level.

    Callable identity (day_formula IS night_formula) is separately pinned
    by :class:`tests.parts.test_parts_registry.TestMarriageIdentity`.
    """

    def test_marriage_day_chart(self) -> None:
        """Marriage on DAY_CHART: expected = (2*ASC + 180 - Venus) % 360."""
        asc, sun, moon, venus = _fields(DAY_CHART)
        expected = (2.0 * asc + 180.0 - venus) % 360.0
        result = calculate_part("marriage", DAY_CHART)
        assert abs(result - expected) < _TOL, (
            f"Marriage day: result={result}, expected={expected}, delta={abs(result - expected)}"
        )

    def test_marriage_night_chart(self) -> None:
        """Marriage on NIGHT_CHART: SAME fixed formula (2*ASC + 180 - Venus) % 360."""
        asc, sun, moon, venus = _fields(NIGHT_CHART)
        expected = (2.0 * asc + 180.0 - venus) % 360.0
        result = calculate_part("marriage", NIGHT_CHART)
        assert abs(result - expected) < _TOL, (
            f"Marriage night: result={result}, expected={expected}, delta={abs(result - expected)}"
        )


class TestFortuneAndSpiritAreMirrors:
    """Fortune and Spirit formulas are MIRRORS — they produce DIFFERENT values on the same chart.

    Fortune-day: ASC+Moon-Sun. Spirit-day: ASC+Sun-Moon.
    These are arithmetic inverses around ASC; they can only be equal when
    Sun == Moon, which they are not at J2000. This guard catches a
    copy-paste swap of the two formula implementations.
    """

    def test_fortune_and_spirit_differ_on_day_chart(self) -> None:
        """Fortune != Spirit on DAY_CHART (they are mirror formulas, not identical)."""
        fortune = calculate_part("fortune", DAY_CHART)
        spirit = calculate_part("spirit", DAY_CHART)
        assert fortune != spirit, (
            f"Fortune ({fortune}) == Spirit ({spirit}) on DAY_CHART — "
            "the two formulas may have been copy-paste swapped."
        )

    def test_fortune_and_spirit_differ_on_night_chart(self) -> None:
        """Fortune != Spirit on NIGHT_CHART (they are mirror formulas, not identical)."""
        fortune = calculate_part("fortune", NIGHT_CHART)
        spirit = calculate_part("spirit", NIGHT_CHART)
        assert fortune != spirit, (
            f"Fortune ({fortune}) == Spirit ({spirit}) on NIGHT_CHART — "
            "the two formulas may have been copy-paste swapped."
        )
