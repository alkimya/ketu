"""Composite chart core helpers.

Hosts :func:`circular_midpoint`, the only public helper introduced by this
subpackage. The composite computation itself lives in
:mod:`ketu.composite.api`.
"""
from __future__ import annotations

from typing import Union

import numpy as np
import numpy.typing as npt

ArrayLike = Union[float, npt.NDArray[np.float64]]


def circular_midpoint(lon_a: ArrayLike, lon_b: ArrayLike) -> np.ndarray:
    """Short-arc midpoint on the unit circle, modulo 360°.

    Vectorised over inputs. ``circular_midpoint(359.0, 1.0) == 0.0``
    (NOT 180.0) — the wraparound case is pinned as a regression test
    (COMP-02 binding).

    Parameters
    ----------
    lon_a : float or array-like
        Longitude A in degrees. Inputs are normalised to ``[0, 360)``
        defensively inside the function (negative or >360° inputs are
        accepted; behaviour is the same as the equivalent normalised
        inputs).
    lon_b : float or array-like
        Longitude B in degrees. Same normalisation contract as ``lon_a``.

    Returns
    -------
    np.ndarray
        Short-arc midpoint(s) in degrees, in ``[0, 360)``. Output shape
        is the broadcast shape of the inputs. Scalar inputs return a
        0-d array (caller can call ``.item()`` if a Python float is
        required).

    Notes
    -----
    Implementation uses the signed short-arc-difference formulation:
    compute the signed delta ``b - a`` in ``(-180, +180]`` via modular
    arithmetic, then add half of that delta to ``a`` (modulo 360°).
    This is algebraically equivalent to the complex-exponential
    ``np.angle(exp(i*a) + exp(i*b))`` formulation but exact in
    floating-point for representable-mean inputs like
    ``circular_midpoint(10°, 20°) == 15°`` (the trig route introduces
    ~1 ulp of rounding error via ``np.deg2rad`` / ``np.rad2deg``).

    **Antipodal edge case.** When ``lon_a`` and ``lon_b`` are exactly
    180° apart, both candidate midpoints are equally valid. The
    documented convention returns ``0.0`` (matches
    ``np.angle(0+0j) == 0.0``). Composite charts rarely encounter this
    in practice (it requires two partners with exactly opposing
    bodies); the behaviour is pinned in tests so future refactors
    don't silently change it.

    See Also
    --------
    ketu.composite.api.calculate_composite : Consumes this helper for
        every per-body and per-angle midpoint in the composite chart.

    Examples
    --------
    >>> import numpy as np
    >>> from ketu.composite import circular_midpoint
    >>> float(circular_midpoint(359.0, 1.0))
    0.0
    >>> float(circular_midpoint(10.0, 20.0))
    15.0
    >>> circular_midpoint(np.array([359.0, 10.0]), np.array([1.0, 20.0]))
    array([ 0., 15.])
    """
    a = np.asarray(lon_a, dtype=np.float64) % 360.0
    b = np.asarray(lon_b, dtype=np.float64) % 360.0
    # Signed short-arc difference in (-180, +180].
    diff_ab = (b - a) % 360.0  # in [0, 360)
    short = np.where(diff_ab <= 180.0, diff_ab, diff_ab - 360.0)
    mid = (a + short / 2.0) % 360.0
    # Antipodal pin (|short| == 180): both midpoints equally valid;
    # documented convention returns 0.0 (matches np.angle(0+0j)).
    is_antipodal = np.isclose(np.abs(short), 180.0)
    mid = np.where(is_antipodal, 0.0, mid)
    return np.asarray(mid)
