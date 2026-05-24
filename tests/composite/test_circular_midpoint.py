"""COMP-02 ratchet — circular_midpoint short-arc behaviour.

The headline regression is the wraparound case: ``circular_midpoint(359.0,
1.0)`` MUST equal ``0.0``, NOT ``180.0``. Naive arithmetic mean would
return the antipodal midpoint and silently put composite bodies on the
opposite side of the chart from their geometric truth (17-RESEARCH.md
Pitfall 1).
"""
from __future__ import annotations

import numpy as np
import pytest

from ketu.composite import circular_midpoint


class TestCircularMidpointWraparound:
    """COMP-02 binding tests."""

    def test_wraparound_359_1_returns_zero(self):
        """The single most important regression: mid(359°, 1°) == 0.0.

        Naive ``(359 + 1) / 2 == 180.0`` is the antipodal midpoint
        (geometrically WRONG). 17-RESEARCH.md Pitfall 1.
        """
        assert float(circular_midpoint(359.0, 1.0)) == 0.0

    @pytest.mark.parametrize(
        ("lon_a", "lon_b", "expected"),
        [
            (359.0, 1.0, 0.0),       # the headline case
            (1.0, 359.0, 0.0),       # commutative
            (0.0, 358.0, 359.0),     # span the 0/360 boundary, mid=359
            (358.0, 0.0, 359.0),     # commutative on boundary span
            (270.0, 90.0, 0.0),      # 90° apart spanning the wrap (short arc through 0)
            (90.0, 270.0, 0.0),      # commutative
            (45.0, 315.0, 0.0),      # 90° apart spanning the wrap (short arc through 0, len 90°)
            (10.0, 20.0, 15.0),      # plain linear case (no wrap)
            (20.0, 10.0, 15.0),      # commutative plain linear
        ],
    )
    def test_parametrized_short_arc_midpoints(self, lon_a, lon_b, expected):
        """Exhaustive short-arc midpoint contract across the wraparound boundary."""
        result = float(circular_midpoint(lon_a, lon_b))
        # Use almost-equal for the cases that don't land exactly on a
        # representable float (the wraparound modulo math is exact for
        # these inputs but we keep the safety net).
        assert result == pytest.approx(expected, abs=1e-9), (
            f"circular_midpoint({lon_a}, {lon_b}) = {result}, expected {expected}"
        )

    def test_antipodal_pinned_convention(self):
        """The (0°, 180°) antipodal case is ambiguous — pin the documented behaviour.

        ``np.angle(0+0j) == 0.0``, so ``circular_midpoint(0.0, 180.0) == 0.0``.
        This is a tripwire test — its job is to fail loudly if a future
        refactor changes the convention without updating the docstring.
        """
        result = float(circular_midpoint(0.0, 180.0))
        # Documented convention: returns 0.0 (the np.angle(0+0j) default).
        assert result == 0.0, (
            f"Antipodal midpoint convention changed: got {result}, "
            "docstring says 0.0. Update both or revert."
        )


class TestCircularMidpointVectorisation:
    """Vectorisation contract (COMP-02 binding: vectorisable)."""

    def test_1d_array_inputs(self):
        """1-d array inputs produce 1-d array output of the same length."""
        a = np.array([359.0, 10.0, 270.0, 45.0])
        b = np.array([1.0, 20.0, 90.0, 315.0])
        result = circular_midpoint(a, b)
        assert result.shape == (4,)
        assert result[0] == pytest.approx(0.0)
        assert result[1] == pytest.approx(15.0)
        assert result[2] == pytest.approx(0.0)
        assert result[3] == pytest.approx(0.0)

    def test_2d_array_inputs(self):
        """2-d array inputs produce 2-d array output (broadcasting)."""
        a = np.array([[10.0, 20.0], [30.0, 40.0]])
        b = np.array([[20.0, 30.0], [40.0, 50.0]])
        result = circular_midpoint(a, b)
        assert result.shape == (2, 2)
        assert result[0, 0] == pytest.approx(15.0)
        assert result[1, 1] == pytest.approx(45.0)

    def test_scalar_returns_ndarray(self):
        """Scalar inputs return a 0-d ndarray (not a Python float).

        Matches Ketu's API style — callers do ``.item()`` for Python float.
        """
        result = circular_midpoint(10.0, 20.0)
        assert isinstance(result, np.ndarray)


class TestCircularMidpointDefensiveNormalisation:
    """Negative-input + >360° normalisation contract (Pitfall 4)."""

    def test_negative_input_normalised(self):
        """``circular_midpoint(-1.0, 1.0)`` equals ``circular_midpoint(359.0, 1.0)``."""
        assert float(circular_midpoint(-1.0, 1.0)) == pytest.approx(
            float(circular_midpoint(359.0, 1.0)), abs=1e-9,
        )

    def test_over_360_input_normalised(self):
        """``circular_midpoint(719.0, 1.0)`` equals ``circular_midpoint(359.0, 1.0)``."""
        assert float(circular_midpoint(719.0, 1.0)) == pytest.approx(
            float(circular_midpoint(359.0, 1.0)), abs=1e-9,
        )


class TestCircularMidpointNanPropagation:
    """NaN inputs propagate naturally through np.exp / np.angle."""

    def test_nan_lon_a(self):
        """NaN in lon_a yields NaN output."""
        result = float(circular_midpoint(np.nan, 1.0))
        assert np.isnan(result)

    def test_nan_lon_b(self):
        """NaN in lon_b yields NaN output."""
        result = float(circular_midpoint(1.0, np.nan))
        assert np.isnan(result)
