"""
Kepler equation solver and angle normalization utilities.

Pure-compute module — no ketu imports. Only numpy and typing are needed.
"""

import numpy as np
from typing import Union


def normalize_angle(angle: float) -> float:
    """
    Normalize angle to 0-360 degrees range.

    Parameters
    ----------
    angle : float
        Angle in degrees (any value).

    Returns
    -------
    float
        Angle normalized to [0, 360) degrees.
    """
    angle = angle % 360.0
    if angle < 0:
        angle += 360.0
    return angle


def solve_kepler_equation(M: Union[float, np.ndarray], e: Union[float, np.ndarray], tolerance: float = 1e-8) -> Union[float, np.ndarray]:
    """
    Solve Kepler's equation for eccentric anomaly (vectorized).

    Parameters
    ----------
    M : float or np.ndarray
        Mean anomaly in radians (scalar or array).
    e : float or np.ndarray
        Eccentricity (scalar or array).
    tolerance : float, optional
        Convergence tolerance.

    Returns
    -------
    float or np.ndarray
        Eccentric anomaly in radians (scalar or array).

    Notes
    -----
    This function is automatically vectorized via numpy broadcasting.
    It can handle arrays of M and/or e values efficiently.
    """
    # Initial guess (broadcasts automatically if M or e are arrays)
    E = M + e * np.sin(M) * (1.0 + e * np.cos(M))

    # Newton-Raphson iteration (vectorized)
    for _ in range(50):  # Maximum iterations
        sin_E = np.sin(E)
        cos_E = np.cos(E)

        dE = (E - e * sin_E - M) / (1.0 - e * cos_E)
        E = E - dE

        # For arrays, check if all elements have converged
        if np.all(np.abs(dE) < tolerance):
            break

    return E
