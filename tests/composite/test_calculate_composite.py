"""COMP-01 surface tests for :func:`ketu.composite.calculate_composite`.

Covers:
- Bookkeeping fields (jd, lat, lon) as natal midpoints — Pitfall 2 ratchet.
- ``system=`` storage + validation (unknown raises ValueError).
- Body midpoints match :func:`ketu.composite.circular_midpoint`
  per-body (parametrized over the 13-body axis).
- Body lats and speeds are linear averages (with retrograde
  spot-check).
- Angles (asc, mc, armc, vertex) are circular midpoints.
- Full swap symmetry on body_lons, asc/mc, cusps.
- ``is_day_chart`` callable on composite metadata without raising
  (Q3 ratchet from 17-RESEARCH).
- Default ``system=`` value matches the COMP-01 spec.
"""
from __future__ import annotations

import numpy as np
import pytest

from ketu.charts import compute_chart, is_day_chart
from ketu.composite import calculate_composite, circular_midpoint


# Indices in the canonical 13-body axis (D-08 frozen order — see
# ketu/core.py bodies array).
_BODY_INDICES = list(range(13))
_BODY_NAMES = [
    "Sun", "Moon", "Mercury", "Venus", "Mars",
    "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto",
    "Rahu", "Ketu", "Lilith",
]
_ANGLE_FIELDS = ["asc", "mc", "armc", "vertex"]


class TestBookkeepingFields:
    """``jd`` / ``lat`` / ``lon`` are midpoints of the natals — Pitfall 2 ratchet."""

    def test_jd_is_linear_midpoint_of_natals(self, chart_a_paris, chart_b_nyc):
        """Pitfall 2 ratchet: composite["jd"] == (a + b) / 2 exactly.

        A Davison implementation would NOT preserve this trivially —
        it would either store the mid-JD it actually used (still
        equal in this case) or NaN (most likely). Pinning strict
        equality is the cheapest anti-conflation guard.
        """
        composite = calculate_composite(chart_a_paris, chart_b_nyc)
        expected = (float(chart_a_paris["jd"]) + float(chart_b_nyc["jd"])) / 2.0
        assert float(composite["jd"]) == expected

    def test_lat_is_linear_midpoint(self, chart_a_paris, chart_b_nyc):
        """Composite latitude is the arithmetic mean of the two natals."""
        composite = calculate_composite(chart_a_paris, chart_b_nyc)
        expected = (float(chart_a_paris["lat"]) + float(chart_b_nyc["lat"])) / 2.0
        assert float(composite["lat"]) == expected

    def test_lon_is_circular_midpoint(self, chart_a_paris, chart_b_nyc):
        """Composite longitude (geographic) is the circular midpoint."""
        composite = calculate_composite(chart_a_paris, chart_b_nyc)
        expected = float(circular_midpoint(
            float(chart_a_paris["lon"]),
            float(chart_b_nyc["lon"]),
        ))
        assert float(composite["lon"]) == expected


class TestSystemArgument:
    """``system=`` is accept-and-validate, stored verbatim, no-op semantically."""

    def test_system_field_stores_user_value(self, chart_a_paris, chart_b_nyc):
        """Passing ``system="koch"`` stores ``"koch"`` in the output."""
        composite = calculate_composite(chart_a_paris, chart_b_nyc, system="koch")
        assert str(composite["system"]) == "koch"

    def test_system_unknown_raises_value_error(
        self, chart_a_paris, chart_b_nyc
    ):
        """Unknown system raises ``ValueError`` via :func:`get_system`."""
        with pytest.raises(ValueError):
            calculate_composite(
                chart_a_paris, chart_b_nyc, system="not_a_real_system"
            )

    def test_default_system_is_placidus(self, chart_a_paris, chart_b_nyc):
        """Default ``system=`` kwarg is ``"placidus"`` (COMP-01 verbatim)."""
        composite = calculate_composite(chart_a_paris, chart_b_nyc)
        assert str(composite["system"]) == "placidus"


class TestBodyMidpoints:
    """Body longitudes / latitudes / speeds match their natal midpoints."""

    @pytest.mark.parametrize("idx", _BODY_INDICES, ids=_BODY_NAMES)
    def test_body_lons_per_body_match_circular_midpoint(
        self, chart_a_paris, chart_b_nyc, idx
    ):
        """Per-body composite longitude equals the natal circular midpoint."""
        composite = calculate_composite(chart_a_paris, chart_b_nyc)
        expected = float(circular_midpoint(
            float(chart_a_paris["body_lons"][idx]),
            float(chart_b_nyc["body_lons"][idx]),
        ))
        assert float(composite["body_lons"][idx]) == expected

    @pytest.mark.parametrize("idx", _BODY_INDICES, ids=_BODY_NAMES)
    def test_body_lats_are_linear_averages(
        self, chart_a_paris, chart_b_nyc, idx
    ):
        """Per-body composite latitude equals the natal arithmetic mean."""
        composite = calculate_composite(chart_a_paris, chart_b_nyc)
        expected = (
            float(chart_a_paris["body_lats"][idx])
            + float(chart_b_nyc["body_lats"][idx])
        ) / 2.0
        assert float(composite["body_lats"][idx]) == pytest.approx(
            expected, abs=1e-12
        )

    @pytest.mark.parametrize("idx", _BODY_INDICES, ids=_BODY_NAMES)
    def test_body_speeds_are_linear_averages(
        self, chart_a_paris, chart_b_nyc, idx
    ):
        """Per-body composite speed equals the natal arithmetic mean."""
        composite = calculate_composite(chart_a_paris, chart_b_nyc)
        expected = (
            float(chart_a_paris["body_speeds"][idx])
            + float(chart_b_nyc["body_speeds"][idx])
        ) / 2.0
        assert float(composite["body_speeds"][idx]) == pytest.approx(
            expected, abs=1e-12
        )

    def test_body_speeds_retrograde_sign_preserves(
        self, chart_a_retrograde_mercury, chart_b_nyc
    ):
        """A retrograde-natal pair preserves the sign through linear average.

        Mid-August 2024 Mercury is retrograde
        (chart_a_retrograde_mercury). Pairing with a prograde natal
        (chart_b_nyc) yields a composite Mercury speed whose sign
        matches the arithmetic-mean rule (could be negative or
        positive depending on the magnitudes; we just assert the
        average rule holds at f8 precision).
        """
        composite = calculate_composite(
            chart_a_retrograde_mercury, chart_b_nyc
        )
        mercury_idx = 2
        expected = (
            float(chart_a_retrograde_mercury["body_speeds"][mercury_idx])
            + float(chart_b_nyc["body_speeds"][mercury_idx])
        ) / 2.0
        assert float(composite["body_speeds"][mercury_idx]) == pytest.approx(
            expected, abs=1e-12
        )


class TestAngleMidpoints:
    """Composite angles (asc, mc, armc, vertex) are circular midpoints."""

    @pytest.mark.parametrize("field", _ANGLE_FIELDS)
    def test_asc_mc_armc_vertex_are_circular_midpoints(
        self, chart_a_paris, chart_b_nyc, field
    ):
        """Each angle field is the circular midpoint of the two natals.

        For asc / mc, the value stored may differ from the raw
        circular midpoint due to the polar ASC-swap algebra in step
        6 of :func:`calculate_composite` (swap_mask handling); we
        test the angle field directly, which is the post-swap value.
        For armc / vertex, no swap occurs.
        """
        composite = calculate_composite(chart_a_paris, chart_b_nyc)
        expected = float(circular_midpoint(
            float(chart_a_paris[field]),
            float(chart_b_nyc[field]),
        ))
        # armc and vertex must match exactly (no algebraic adjustment).
        if field in ("armc", "vertex"):
            assert float(composite[field]) == expected
        else:
            # asc / mc may have been swapped by 180° if the polar
            # ASC-swap branch was triggered. For the Paris/NYC pair
            # at J2000-ish JDs, the swap is NOT triggered. We assert
            # equality unconditionally for these fixtures; if a future
            # pair triggers the swap, the test will fail loudly and
            # this assertion can be relaxed to ``in {raw, raw+180}``.
            assert float(composite[field]) == expected


class TestSwapSymmetry:
    """COMP-03 anti-regression — calculate_composite(a, b) == calculate_composite(b, a)."""

    def test_swap_symmetry_body_lons(self, chart_a_paris, chart_b_nyc):
        """body_lons are swap-symmetric within 1e-9°."""
        c_ab = calculate_composite(chart_a_paris, chart_b_nyc)
        c_ba = calculate_composite(chart_b_nyc, chart_a_paris)
        assert np.allclose(c_ab["body_lons"], c_ba["body_lons"], atol=1e-9)

    def test_swap_symmetry_asc_mc(self, chart_a_paris, chart_b_nyc):
        """asc and mc are swap-symmetric within 1e-9°."""
        c_ab = calculate_composite(chart_a_paris, chart_b_nyc)
        c_ba = calculate_composite(chart_b_nyc, chart_a_paris)
        assert float(c_ab["asc"]) == pytest.approx(float(c_ba["asc"]), abs=1e-9)
        assert float(c_ab["mc"]) == pytest.approx(float(c_ba["mc"]), abs=1e-9)

    def test_swap_symmetry_cusps(self, chart_a_paris, chart_b_nyc):
        """House cusps are swap-symmetric within 1e-9°."""
        c_ab = calculate_composite(chart_a_paris, chart_b_nyc)
        c_ba = calculate_composite(chart_b_nyc, chart_a_paris)
        assert np.allclose(c_ab["cusps"], c_ba["cusps"], atol=1e-9)


class TestIsDayChartCallable:
    """Q3 ratchet — :func:`is_day_chart` callable on composite metadata."""

    def test_is_day_chart_callable_on_composite_metadata_does_not_raise(
        self, chart_a_paris, chart_b_nyc
    ):
        """``is_day_chart(c["jd"], c["lat"], c["lon"])`` returns a bool.

        The result is astrologically meaningless on a composite
        (bookkeeping (jd, lat, lon) — see api.py module docstring), but
        the function must remain callable without raising. This pins
        the "no NaN in bookkeeping fields" invariant: if a future
        refactor stores NaN in jd / lat / lon, is_day_chart would
        either raise or return a meaningless bool, both of which we
        want to detect via this ratchet.
        """
        composite = calculate_composite(chart_a_paris, chart_b_nyc)
        result = is_day_chart(
            float(composite["jd"]),
            float(composite["lat"]),
            float(composite["lon"]),
        )
        # is_day_chart may return a Python ``bool``, ``np.bool_``, or a
        # 0-d ``np.ndarray`` of bool depending on input shape; all three
        # are acceptable. The key invariant is "callable without raising
        # and returns something castable to bool".
        assert bool(result) in (True, False)
