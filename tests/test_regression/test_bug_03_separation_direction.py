"""Regression: angular_separation must follow the body1 -> body2 direction.

Before the fix, ``generate_cycle_series`` derived ``angular_separation`` from
``cycle_ratio_vectorized(b1, b2) = exp(i*(lon1 - lon2))``, yielding
``(lon1 - lon2) % 360`` -- the *reverse* of the documented "direction of the
cycle, body1 -> body2". For a Sun->Moon pair this inverted the phase reading:
the first quarter reported ~270deg and the last quarter ~90deg (and
``cycle_phase`` waxing/waning was flipped accordingly).

The standard astronomical convention is the phase angle ``(Moon - Sun) % 360``:
0deg new moon, 90deg first quarter, 180deg full moon, 270deg last quarter.
``ketu.complex.CycleRatio`` already used this convention, so the cycle module
was internally inconsistent. These tests pin the corrected direction against
four known 2025-2026 lunar phases.
"""

from datetime import datetime

import numpy as np

from ketu.cycles import generate_cycle_series


# (label, datetime UTC, expected separation deg, expected cycle_phase)
KNOWN_PHASES = [
    ("new moon 2026-01-18 19:52", datetime(2026, 1, 18, 19, 52), 0.0, 1),
    ("first quarter 2026-01-26 04:48", datetime(2026, 1, 26, 4, 48), 90.0, 1),
    ("full moon 2026-01-03 10:03", datetime(2026, 1, 3, 10, 3), 180.0, 1),
    ("last quarter 2026-01-10 16:00", datetime(2026, 1, 10, 16, 0), 270.0, -1),
]


def test_lunar_phase_angles_follow_moon_minus_sun():
    """Sun->Moon angular_separation matches the (Moon - Sun) phase angle."""
    for label, dt, expected_sep, _ in KNOWN_PHASES:
        result = generate_cycle_series("Sun", "Moon", [dt])
        sep = float(result["angular_separation"][0])
        # Compare on the circle so 0 and 360 are equivalent.
        delta = abs((sep - expected_sep + 180.0) % 360.0 - 180.0)
        assert delta < 2.0, (
            f"{label}: angular_separation={sep:.2f} deg, "
            f"expected ~{expected_sep:.0f} deg (delta {delta:.2f})"
        )


def test_cycle_phase_matches_waxing_waning():
    """cycle_phase is +1 while waxing (0-180deg) and -1 while waning."""
    for label, dt, _, expected_phase in KNOWN_PHASES:
        result = generate_cycle_series("Sun", "Moon", [dt])
        # New/full moon sit on the 0/180 boundary; only assert the quarters,
        # where waxing vs waning is unambiguous.
        if label.startswith(("first quarter", "last quarter")):
            assert int(result["cycle_phase"][0]) == expected_phase, (
                f"{label}: cycle_phase={int(result['cycle_phase'][0])}, "
                f"expected {expected_phase}"
            )


def test_separation_matches_moon_minus_sun_longitudes():
    """angular_separation equals (body2_lon - body1_lon) % 360 over a lunation."""
    ts = np.arange(
        "2026-03-01", "2026-04-01", dtype="datetime64[D]"
    ).astype("datetime64[s]")
    result = generate_cycle_series("Sun", "Moon", ts)
    expected = (result["body2_lon"] - result["body1_lon"]) % 360.0
    # Compare on the circle (atol in degrees).
    delta = np.abs((result["angular_separation"] - expected + 180.0) % 360.0 - 180.0)
    assert np.all(delta < 1e-3), f"max direction delta = {delta.max():.5f} deg"
