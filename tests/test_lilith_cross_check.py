"""Cross-check Ketu's Mean Black Moon Lilith against Swiss Ephemeris.

This module is a parametrized pytest harness that compares Ketu's
:func:`ketu.ephemeris.orbital.get_lilith_position` against the Swiss
Ephemeris reference computation ``swe.calc_ut(jd, swe.MEAN_APOG)`` on
five dates spanning 1900-2050.

The module is **auto-skipped** when the optional ``pysweph`` test
extra is not installed: the top-level :func:`pytest.importorskip`
gate raises ``pytest.skip.Exception`` at collection time so a bare
``pytest tests/`` reports the harness as SKIPPED rather than ERRORED.

The acceptance tolerance is fixed at :data:`TOLERANCE_DEG` (= 0.01 deg).
The arithmetic justification of that constant lives in
``docs/LILITH_DEFINITION.md`` Section 7 ("Tolerance Justification"):
0.01 deg = 36 arcseconds = ~129 minutes of mean-apogee drift at the
0.111404 deg/day rate. The harness's empirical max |delta| determines
whether Phase 8 Plan 04 executes its no-op or formula-correction branch.

Notes
-----
The same pattern can verify ``swe.MEAN_NODE`` and ``swe.TRUE_NODE`` in
a future phase; out of scope for v1.1.

References
----------
- ``docs/LILITH_DEFINITION.md`` -- authoritative reference frame, formula,
  tolerance derivation, and AGPL test-only-dependency commitment.
- Phase 8 Plan 03 (cross-check harness) -- this file.
- Phase 8 Plan 04 (conditional formula fix) -- gated on the empirical
  max |delta| reported by this harness.
"""

from __future__ import annotations

import pytest

# Runtime gate: when pysweph is absent, the line below raises
# pytest.skip.Exception at collection time and the entire module is reported
# as SKIPPED rather than ERRORED. We deliberately do NOT bind the return
# value (e.g. `swe = pytest.importorskip(...)`) because that yields a
# `ModuleType` local that mypy --strict rejects on every `swe.MEAN_APOG`
# access. The pyproject `[[tool.mypy.overrides]] module = ["swisseph.*"]`
# rule matches direct `import swisseph` statements, NOT locals; hence the
# separate `import swisseph as swe` line below.
pytest.importorskip("swisseph", minversion="2.10.3.6")
import swisseph as swe

from datetime import datetime, timezone

from ketu.ephemeris.orbital import get_lilith_position
from ketu.ephemeris.time import utc_to_julian


# Tolerance derived in docs/LILITH_DEFINITION.md Section 7:
#   0.01 deg = 36 arcseconds
#   0.01 / 0.111404 deg/day ~= 0.0898 days ~= 2.15 hours ~= 129 minutes
# of mean-apogee drift at the rate constant from orbital.py:591. This is
# one order of magnitude tighter than printed-ephemeris precision (0.1 deg)
# and well below Ketu's smallest aspect orb (1 deg), so any miss at this
# tolerance is observable by downstream consumers.
TOLERANCE_DEG = 0.01

# Mid-month, mid-day to avoid integer-JD coincidences. J2000.0 included as a
# self-consistency anchor; 1900 and 2050 expose any rate drift across the
# requirement window.
CROSS_CHECK_DATES: list[datetime] = [
    datetime(1900, 6, 15, 12, 0, tzinfo=timezone.utc),
    datetime(1950, 3, 21, 18, 30, tzinfo=timezone.utc),
    datetime(2000, 1, 1, 12, 0, tzinfo=timezone.utc),  # J2000.0 anchor
    datetime(2025, 9, 23, 6, 0, tzinfo=timezone.utc),
    datetime(2050, 12, 21, 0, 0, tzinfo=timezone.utc),
]


def _signed_circular_diff(a: float, b: float) -> float:
    """Smallest signed angular difference ``a - b`` in (-180, 180].

    Handles wrap-around correctly: e.g. ``_signed_circular_diff(0.005, 359.99)``
    returns approximately ``+0.015``, not ``-359.985``.

    Parameters
    ----------
    a, b : float
        Angles in degrees in [0, 360).

    Returns
    -------
    float
        Signed difference in (-180, 180].
    """
    return (a - b + 180.0) % 360.0 - 180.0


@pytest.mark.parametrize("dt", CROSS_CHECK_DATES, ids=lambda d: d.isoformat())
def test_lilith_matches_swiss_ephemeris(dt: datetime) -> None:
    """Ketu's Lilith longitude must match swe.MEAN_APOG within TOLERANCE_DEG.

    Uses ``swe.calc_ut`` (NOT ``swe.calc``) so that input is interpreted as
    JD-UT, matching ``ketu.ephemeris.time.utc_to_julian``'s output contract
    (no Delta-T injection). The 6-tuple returned by ``calc_ut`` is unpacked
    explicitly to the canonical ``xx, _retflag`` form documented in the
    Swiss Ephemeris reference.
    """
    jd = utc_to_julian(dt)
    xx, _retflag = swe.calc_ut(jd, swe.MEAN_APOG)
    expected_lon = xx[0]
    actual_lon = get_lilith_position(jd)
    delta = _signed_circular_diff(actual_lon, expected_lon)
    assert abs(delta) < TOLERANCE_DEG, (
        f"Lilith mismatch on {dt.isoformat()}: "
        f"Ketu={actual_lon:.6f} deg, swe={expected_lon:.6f} deg, "
        f"delta={delta:+.6f} deg (tolerance {TOLERANCE_DEG} deg)"
    )
