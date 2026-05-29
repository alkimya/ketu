"""
Planetary perturbation corrections.

Applies perturbation corrections to heliocentric positions for Jupiter,
Saturn, and Uranus. Moved verbatim from orbital.py; the Jupiter/Saturn/Uranus
if-elif is intentionally left unchanged (strategy-ification is a Phase 24
concern for Chiron perturbations).

Imports ORBITAL_ELEMENTS from _elements; does NOT import from orbital.py.
"""

import numpy as np
from typing import Tuple

from ._elements import ORBITAL_ELEMENTS


def apply_perturbations(body_id: int, jd: float, x: float, y: float, z: float) -> Tuple[float, float, float]:
    """
    Apply perturbation corrections to planetary positions.

    Parameters
    ----------
    body_id : int
        Body index.
    jd : float
        Julian Date.
    x : float
        Unperturbed X coordinate.
    y : float
        Unperturbed Y coordinate.
    z : float
        Unperturbed Z coordinate.

    Returns
    -------
    tuple of (float, float, float)
        Perturbed coordinates (x, y, z).
    """
    # For now, only apply major perturbations to outer planets
    # This is a simplified version - full implementation would include
    # more terms from perturbation theory

    d = jd - 2451545.0

    if ORBITAL_ELEMENTS[body_id]["name"] == "Jupiter":
        # Saturn perturbations on Jupiter
        M_jup = np.deg2rad(19.8950 + 0.0830853001 * d)
        M_sat = np.deg2rad(316.9670 + 0.0334442282 * d)

        # Longitude perturbations (in degrees)
        dL = (
            -0.332 * np.sin(2 * M_jup - 5 * M_sat - np.deg2rad(67.6))
            - 0.056 * np.sin(2 * M_jup - 2 * M_sat + np.deg2rad(21))
            + 0.042 * np.sin(3 * M_jup - 5 * M_sat + np.deg2rad(21))
            - 0.036 * np.sin(M_jup - 2 * M_sat)
            + 0.022 * np.cos(M_jup - M_sat)
            + 0.023 * np.sin(2 * M_jup - 3 * M_sat + np.deg2rad(52))
            - 0.016 * np.sin(M_jup - 5 * M_sat - np.deg2rad(69))
        )

        # Apply correction to longitude
        r = np.sqrt(x**2 + y**2 + z**2)
        lon = np.arctan2(y, x)
        lat = np.arcsin(z / np.maximum(r, 1e-10))  # floor r to avoid div/0 (QAL-11)

        lon += np.deg2rad(dL)

        # Convert back to rectangular
        x = r * np.cos(lon) * np.cos(lat)
        y = r * np.sin(lon) * np.cos(lat)
        z = r * np.sin(lat)

    elif ORBITAL_ELEMENTS[body_id]["name"] == "Saturn":
        # Jupiter perturbations on Saturn
        M_jup = np.deg2rad(19.8950 + 0.0830853001 * d)
        M_sat = np.deg2rad(316.9670 + 0.0334442282 * d)

        # Longitude perturbations
        dL = (
            0.812 * np.sin(2 * M_jup - 5 * M_sat - np.deg2rad(67.6))
            - 0.229 * np.cos(2 * M_jup - 4 * M_sat - np.deg2rad(2))
            + 0.119 * np.sin(M_jup - 2 * M_sat - np.deg2rad(3))
            + 0.046 * np.sin(2 * M_jup - 6 * M_sat - np.deg2rad(69))
            + 0.014 * np.sin(M_jup - 3 * M_sat + np.deg2rad(32))
        )

        # Latitude perturbations
        dB = -0.020 * np.cos(2 * M_jup - 4 * M_sat - np.deg2rad(2)) + 0.018 * np.sin(
            2 * M_jup - 6 * M_sat - np.deg2rad(49)
        )

        # Apply corrections
        r = np.sqrt(x**2 + y**2 + z**2)
        lon = np.arctan2(y, x)
        lat = np.arcsin(z / np.maximum(r, 1e-10))  # floor r to avoid div/0 (QAL-11)

        lon += np.deg2rad(dL)
        lat += np.deg2rad(dB)

        # Convert back to rectangular
        x = r * np.cos(lon) * np.cos(lat)
        y = r * np.sin(lon) * np.cos(lat)
        z = r * np.sin(lat)

    elif ORBITAL_ELEMENTS[body_id]["name"] == "Uranus":
        # Jupiter and Saturn perturbations on Uranus
        M_jup = np.deg2rad(19.8950 + 0.0830853001 * d)
        M_sat = np.deg2rad(316.9670 + 0.0334442282 * d)
        M_ura = np.deg2rad(142.5905 + 0.011725806 * d)

        # Longitude perturbations
        dL = (
            0.040 * np.sin(M_sat - 2 * M_ura + np.deg2rad(6))
            + 0.035 * np.sin(M_sat - 3 * M_ura + np.deg2rad(33))
            - 0.015 * np.sin(M_jup - M_ura + np.deg2rad(20))
        )

        # Apply correction
        r = np.sqrt(x**2 + y**2 + z**2)
        lon = np.arctan2(y, x)
        lat = np.arcsin(z / np.maximum(r, 1e-10))  # floor r to avoid div/0 (QAL-11)

        lon += np.deg2rad(dL)

        # Convert back to rectangular
        x = r * np.cos(lon) * np.cos(lat)
        y = r * np.sin(lon) * np.cos(lat)
        z = r * np.sin(lat)

    return x, y, z
