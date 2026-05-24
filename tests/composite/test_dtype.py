"""Composite output dtype contract — no schema regression, frozen 13-body axis.

Pitfall 8 ratchet (the body axis is FROZEN at 13, Sun first, NOT
alphabetical) is pinned by index-0 / index-1 spot checks against
:func:`ketu.composite.circular_midpoint` applied to the natal
``body_lons`` at the same indices.
"""
from __future__ import annotations

import numpy as np

from ketu.charts import CHART_DTYPE
from ketu.composite import calculate_composite, circular_midpoint


class TestOutputDtype:
    """Output is a scalar CHART_DTYPE — no schema regression."""

    def test_output_is_chart_dtype(self, chart_a_paris, chart_b_nyc):
        """Composite output dtype IS :data:`ketu.charts.CHART_DTYPE`."""
        result = calculate_composite(chart_a_paris, chart_b_nyc)
        assert result.dtype == CHART_DTYPE

    def test_output_is_scalar(self, chart_a_paris, chart_b_nyc):
        """Composite output is a scalar (0-d) structured array."""
        result = calculate_composite(chart_a_paris, chart_b_nyc)
        assert result.shape == ()

    def test_body_axis_shape_frozen_13(self, chart_a_paris, chart_b_nyc):
        """All three body sub-arrays carry the frozen ``(13,)`` axis."""
        result = calculate_composite(chart_a_paris, chart_b_nyc)
        assert result["body_lons"].shape == (13,)
        assert result["body_lats"].shape == (13,)
        assert result["body_speeds"].shape == (13,)

    def test_cusps_shape_12(self, chart_a_paris, chart_b_nyc):
        """Cusps sub-array has shape ``(12,)``."""
        result = calculate_composite(chart_a_paris, chart_b_nyc)
        assert result["cusps"].shape == (12,)

    def test_aspect_matrix_shape(self, chart_a_paris, chart_b_nyc):
        """Aspect matrix and orbs both have shape ``(13, 13)``."""
        result = calculate_composite(chart_a_paris, chart_b_nyc)
        assert result["aspect_matrix"].shape == (13, 13)
        assert result["aspect_orbs"].shape == (13, 13)


class TestBodyAxisOrderingPitfall8:
    """Pitfall 8 ratchet — Sun is index 0, NOT alphabetical."""

    def test_sun_index_0_matches_circular_midpoint(
        self, chart_a_paris, chart_b_nyc
    ):
        """Index 0 (Sun) of composite equals circular_midpoint of natals' index 0."""
        result = calculate_composite(chart_a_paris, chart_b_nyc)
        expected_sun = float(circular_midpoint(
            float(chart_a_paris["body_lons"][0]),
            float(chart_b_nyc["body_lons"][0]),
        ))
        assert float(result["body_lons"][0]) == expected_sun

    def test_moon_index_1(self, chart_a_paris, chart_b_nyc):
        """Index 1 (Moon) of composite equals circular_midpoint of natals' index 1."""
        result = calculate_composite(chart_a_paris, chart_b_nyc)
        expected_moon = float(circular_midpoint(
            float(chart_a_paris["body_lons"][1]),
            float(chart_b_nyc["body_lons"][1]),
        ))
        assert float(result["body_lons"][1]) == expected_moon
