"""COMP-03 ratchet — composite houses derived from composite ASC + MC.

Pins the Porphyry-style trisection algebra applied in
:func:`ketu.composite.calculate_composite` step 6 and ensures the
function does NOT call :func:`ketu.houses.calculate_houses` or
:func:`ketu.charts.compute_chart` anywhere (Pitfall 2 + Pitfall 3
anti-regression via source-level grep).

Polar-safe ratchet — pairing a high-latitude natal (Reykjavik,
lat 64°N) with a moderate natal must produce finite cusps (Approach
A: Porphyry trisection has no tan(lat) singularity).
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from ketu.composite import calculate_composite, circular_midpoint


_API_PATH = Path(__file__).resolve().parents[2] / "ketu" / "composite" / "api.py"


class TestCuspEndpoints:
    """Cusps 0/3/6/9 are ASC / IC / DESC / MC (and oppositions thereof)."""

    def test_cusp_0_equals_composite_asc(self, chart_a_paris, chart_b_nyc):
        """Cusp index 0 IS the composite ASC (1st house cusp)."""
        result = calculate_composite(chart_a_paris, chart_b_nyc)
        assert float(result["cusps"][0]) == float(result["asc"])

    def test_cusp_9_equals_composite_mc(self, chart_a_paris, chart_b_nyc):
        """Cusp index 9 IS the composite MC (10th house cusp)."""
        result = calculate_composite(chart_a_paris, chart_b_nyc)
        assert float(result["cusps"][9]) == float(result["mc"])

    def test_cusp_6_equals_composite_desc(self, chart_a_paris, chart_b_nyc):
        """Cusp index 6 (DESC) equals ASC + 180° (mod 360°)."""
        result = calculate_composite(chart_a_paris, chart_b_nyc)
        expected_desc = (float(result["asc"]) + 180.0) % 360.0
        assert float(result["cusps"][6]) == pytest.approx(expected_desc, abs=1e-9)

    def test_cusp_3_equals_composite_ic(self, chart_a_paris, chart_b_nyc):
        """Cusp index 3 (IC) equals MC + 180° (mod 360°)."""
        result = calculate_composite(chart_a_paris, chart_b_nyc)
        expected_ic = (float(result["mc"]) + 180.0) % 360.0
        assert float(result["cusps"][3]) == pytest.approx(expected_ic, abs=1e-9)


class TestPorphyryTrisection:
    """Cusps 2/3/11/12 are trisections of the composite arcs."""

    def test_cusps_2_3_trisect_lower_arc(self, chart_a_paris, chart_b_nyc):
        """Cusps 2 and 3 lie at (ASC + step) and (ASC + 2*step) for the lower trisection.

        ``step = (180 - acmc) / 3`` where ``acmc`` is the short-arc
        signed distance ASC - MC in ``(0, +180]`` (post polar-swap).
        """
        result = calculate_composite(chart_a_paris, chart_b_nyc)
        asc = float(result["asc"])
        mc = float(result["mc"])
        # Re-derive the post-swap acmc (matches step 6 of api.py).
        acmc_signed = ((asc - mc + 540.0) % 360.0) - 180.0
        if acmc_signed < 0.0:
            acmc = acmc_signed + 180.0
        else:
            acmc = acmc_signed
        lower_step = (180.0 - acmc) / 3.0
        expected_cusp_2 = (asc + lower_step) % 360.0
        expected_cusp_3 = (asc + 2.0 * lower_step) % 360.0
        assert float(result["cusps"][1]) == pytest.approx(
            expected_cusp_2, abs=1e-9
        )
        assert float(result["cusps"][2]) == pytest.approx(
            expected_cusp_3, abs=1e-9
        )

    def test_cusps_11_12_trisect_upper_arc(self, chart_a_paris, chart_b_nyc):
        """Cusps 11 and 12 lie at (MC + step) and (MC + 2*step) for the upper trisection.

        ``step = acmc / 3`` where ``acmc`` is the post-swap short-arc
        signed distance ASC - MC.
        """
        result = calculate_composite(chart_a_paris, chart_b_nyc)
        asc = float(result["asc"])
        mc = float(result["mc"])
        acmc_signed = ((asc - mc + 540.0) % 360.0) - 180.0
        if acmc_signed < 0.0:
            acmc = acmc_signed + 180.0
        else:
            acmc = acmc_signed
        upper_step = acmc / 3.0
        expected_cusp_11 = (mc + upper_step) % 360.0
        expected_cusp_12 = (mc + 2.0 * upper_step) % 360.0
        assert float(result["cusps"][10]) == pytest.approx(
            expected_cusp_11, abs=1e-9
        )
        assert float(result["cusps"][11]) == pytest.approx(
            expected_cusp_12, abs=1e-9
        )

    def test_cusps_5_6_8_9_are_oppositions(self, chart_a_paris, chart_b_nyc):
        """Cusps 5/6/8/9 are 180° from cusps 11/12/2/3 respectively."""
        result = calculate_composite(chart_a_paris, chart_b_nyc)
        cusps = result["cusps"]
        # cusps[4] = cusps[10] + 180; cusps[5] = cusps[11] + 180;
        # cusps[7] = cusps[1] + 180;  cusps[8] = cusps[2] + 180.
        assert float(cusps[4]) == pytest.approx(
            (float(cusps[10]) + 180.0) % 360.0, abs=1e-9
        )
        assert float(cusps[5]) == pytest.approx(
            (float(cusps[11]) + 180.0) % 360.0, abs=1e-9
        )
        assert float(cusps[7]) == pytest.approx(
            (float(cusps[1]) + 180.0) % 360.0, abs=1e-9
        )
        assert float(cusps[8]) == pytest.approx(
            (float(cusps[2]) + 180.0) % 360.0, abs=1e-9
        )


class TestSwapSymmetry:
    """COMP-03 anti-regression — composite cusps don't drift on swap."""

    def test_composite_houses_swap_symmetric(self, chart_a_paris, chart_b_nyc):
        """All 12 cusps are swap-symmetric within 1e-9°."""
        c_ab = calculate_composite(chart_a_paris, chart_b_nyc)
        c_ba = calculate_composite(chart_b_nyc, chart_a_paris)
        assert np.allclose(c_ab["cusps"], c_ba["cusps"], atol=1e-9)


class TestGrepRatchets:
    """Source-level anti-regression — Pitfall 2 + Pitfall 3 guards.

    Reads :mod:`ketu.composite.api` as text and asserts the forbidden
    function-call patterns DO NOT appear. A future contributor who
    accidentally adds ``calculate_houses(...)`` or ``compute_chart(...)``
    will fail one of these tests before any behavioural test surfaces
    the symptom.
    """

    def test_no_calculate_houses_call_smoke(self):
        """Pitfall 3 ratchet — ``calculate_houses(`` must not appear in api.py."""
        source = _API_PATH.read_text()
        assert "calculate_houses(" not in source

    def test_no_compute_chart_call_smoke(self):
        """Pitfall 2 ratchet — ``compute_chart(`` must not appear in api.py
        as a runtime call (i.e. outside docstring/doctest examples).

        A Davison implementation would call :func:`compute_chart` with
        the mid-Julian-Date and geographic midpoint; pinning the
        absence of this substring in non-doctest lines is the cheapest
        anti-conflation guard.
        """
        # Filter out docstring example lines (starting with '>>>')
        # to allow `compute_chart(` in Examples sections without triggering
        # the ratchet.  Only runtime calls (non-doctest code lines) matter.
        lines = _API_PATH.read_text().splitlines()
        non_doctest = [
            line for line in lines
            if not line.lstrip().startswith(">>>")
        ]
        assert "compute_chart(" not in "\n".join(non_doctest)

    def test_no_calculate_aspects_vectorized_call_smoke(self):
        """Pitfall ratchet — the inline aspect loop must not delegate to the engine.

        :func:`ketu.aspects.calculator.calculate_aspects_vectorized`
        takes a ``jd`` and recomputes bodies internally; the composite
        has no canonical Julian Date. Phase 17 inlines the matching
        algebra; this test pins that decision so a future "tidy" doesn't
        accidentally re-introduce a jd-based call.
        """
        source = _API_PATH.read_text()
        assert "calculate_aspects_vectorized(" not in source


class TestPolarSafe:
    """Approach A polar-safe ratchet — high-latitude pair produces finite cusps."""

    def test_polar_pair_does_not_nan(self, chart_a_paris, chart_b_reykjavik):
        """Paris (48°N) + Reykjavik (64°N) composite: all cusps + asc/mc finite.

        Approach A uses Porphyry trisection on the composite ASC + MC
        directly — no ``tan(lat)`` singularity, no
        :class:`HighLatitudeError`, no NaN propagation. This pins the
        polar safety as a behavioural ratchet rather than relying only
        on the algebraic argument.
        """
        result = calculate_composite(chart_a_paris, chart_b_reykjavik)
        assert np.all(np.isfinite(result["cusps"]))
        assert np.isfinite(float(result["asc"]))
        assert np.isfinite(float(result["mc"]))
        assert np.isfinite(float(result["armc"]))
        assert np.isfinite(float(result["vertex"]))


class TestAngleMidpointConsistency:
    """The composite ASC / MC are the short-arc midpoints of the natal angles.

    Sanity check that step 5 of :func:`calculate_composite` uses
    :func:`circular_midpoint` on the asc / mc fields. Step 6's polar
    ASC swap may flip asc by 180°, so we compare the post-swap value
    to the swap-adjusted expectation.
    """

    def test_composite_asc_matches_post_swap_midpoint(
        self, chart_a_paris, chart_b_nyc
    ):
        """Composite ASC is the natal midpoint (possibly +180° after polar-swap)."""
        result = calculate_composite(chart_a_paris, chart_b_nyc)
        raw_mid = float(circular_midpoint(
            float(chart_a_paris["asc"]),
            float(chart_b_nyc["asc"]),
        ))
        observed = float(result["asc"])
        # Either equal raw_mid (no swap) or raw_mid+180 (swap fired).
        assert (
            observed == pytest.approx(raw_mid, abs=1e-9)
            or observed == pytest.approx((raw_mid + 180.0) % 360.0, abs=1e-9)
        )

    def test_composite_mc_matches_midpoint(self, chart_a_paris, chart_b_nyc):
        """Composite MC equals the natal circular midpoint exactly.

        MC is never swapped in step 6 (the polar ASC-swap only touches
        ``composite_asc``). The stored MC must match the raw circular
        midpoint of the two natal MCs.
        """
        result = calculate_composite(chart_a_paris, chart_b_nyc)
        expected = float(circular_midpoint(
            float(chart_a_paris["mc"]),
            float(chart_b_nyc["mc"]),
        ))
        assert float(result["mc"]) == pytest.approx(expected, abs=1e-9)
