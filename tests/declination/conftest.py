"""Phase-36 declination aspects test fixtures.

Provides shared fixtures for the declination aspect test suite:
oracle seed arrays computed from :func:`ketu.calculations.declination`
at known Julian Dates.
"""
from __future__ import annotations

import numpy as np
import pytest

from ketu.calculations import declination

#: Julian Date for summer solstice 2000-06-21 12:00 UTC.
#: Used as the primary 10-aspect oracle seed (Seed 1).
JD_SOLSTICE_2000: float = 2451717.0


@pytest.fixture
def body_decl_solstice() -> np.ndarray:
    """All 14 body declinations at 2000-06-21 12:00 UTC (oracle seed 1).

    Computes ``declination(JD_SOLSTICE_2000, i)`` for all 14 bodies in
    :data:`ketu.core.bodies` order. Expected to yield exactly 10 declination
    aspects (5 parallels + 5 contra-parallels) as tabulated in RESEARCH.md.

    Returns
    -------
    np.ndarray
        Shape ``(14,)``, dtype ``float64``. Signed declinations in degrees.
    """
    return np.array([declination(JD_SOLSTICE_2000, i) for i in range(14)])


@pytest.fixture
def body_decl_zeros() -> np.ndarray:
    """14 bodies all at delta=0 (zero-sign trap fixture).

    Used to verify the zero-sign guard: ``sign(0) == 0`` means no body at
    delta=0 can form a parallel or contra-parallel aspect.

    Returns
    -------
    np.ndarray
        Shape ``(14,)``, dtype ``float64``. All zeros.
    """
    return np.zeros(14)
