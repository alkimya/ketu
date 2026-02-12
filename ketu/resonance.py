"""
Resonance Field Calculations.

This module unifies the calculation of "3D Resonance" fields:
1. Longitude Resonance (Harmonic Aspects)
2. Declination Resonance (Parallels/Contra-Parallels)
3. Latitude Resonance (Nodal Crossings)

It transforms discrete planetary positions into continuous "Pressure Fields"
using Gaussian scoring, providing a fluid signal for the AI agent.
"""

import numpy as np
from datetime import datetime, timezone
from typing import List, Dict, Optional, Union

from .ephemeris.time import utc_to_julian
from .ephemeris.planets import calc_planet_position, calc_planet_position_batch, BODY_INDICES
from .ephemeris.coordinates import (
    spherical_to_rectangular,
    ecliptic_to_equatorial,
    rectangular_to_spherical,
    mean_obliquity
)

# Standard Planetary Set for Resonance
# Includes Sun, Moon and Nodes (Rahu) for full "Astral Weather" computation.
DEFAULT_BODIES = [
    "Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", 
    "Saturn", "Uranus", "Neptune", "Pluto", "Rahu"
]

# Harmonic Series (H9, H10, H12 + Multiples)
# Base H1 = 360
# H9 = 40, H10 = 36, H12 = 30
HARMONICS_H9_H10_H12 = [
    0,    # Conjunction
    180,  # Opposition
    120,  # Trine (H3)
    90,   # Square (H4)
    # H9 Series (40 deg)
    40, 80, 160,
    # H10 Series (36 deg)
    36, 72, 108, 144,
    # H12 Series (30 deg)
    30, 60, 150
]

# NumPy structured array dtype for resonance field
RESONANCE_DTYPE = np.dtype([
    ('timestamp', 'datetime64[s]'),
    ('res_lon', 'f8'),
    ('res_lat', 'f8'),
    ('res_dec', 'f8'),
])

class ResonanceField:
    """
    Computes continuous resonance scores for planetary configurations.
    """
    
    def __init__(self,
                 bodies: List[str] = DEFAULT_BODIES,
                 harmonics: List[float] = HARMONICS_H9_H10_H12,
                 sigma_lon: float = 3.0,
                 sigma_lat: float = 0.5,
                 sigma_dec: float = 1.0):
        """Initialize ResonanceField with configuration parameters

        Parameters
        ----------
        bodies : list of str, optional
            List of body names to include (default: DEFAULT_BODIES)
        harmonics : list of float, optional
            List of aspect angles to score for Longitude (default: HARMONICS_H9_H10_H12)
        sigma_lon : float, optional
            Std dev for Longitude Gaussian in degrees (default: 3.0)
        sigma_lat : float, optional
            Std dev for Latitude Gaussian in degrees (default: 0.5)
        sigma_dec : float, optional
            Std dev for Declination Gaussian in degrees (default: 1.0)
        """
        self.bodies = bodies
        self.body_indices = [BODY_INDICES[b] for b in bodies]
        self.harmonics = np.array(harmonics)
        self.sigma_lon = sigma_lon
        self.sigma_lat = sigma_lat
        self.sigma_dec = sigma_dec

    def compute_field(self, start_dt: datetime, end_dt: datetime, step_hours: int = 1) -> np.ndarray:
        """
        Generate the resonance field as NumPy structured array for a time range.

        Returns:
            NumPy structured array with columns ['timestamp', 'res_lon', 'res_lat', 'res_dec']
        """
        # Generate timestamps using NumPy
        # Ensure timezone-naive for numpy datetime64
        start_naive = start_dt.replace(tzinfo=None) if start_dt.tzinfo else start_dt
        end_naive = end_dt.replace(tzinfo=None) if end_dt.tzinfo else end_dt
        timestamps = np.arange(
            np.datetime64(start_naive),
            np.datetime64(end_naive),
            np.timedelta64(step_hours, 'h')
        )

        # Convert numpy datetime64 to Julian dates
        # timestamps are datetime64, need to convert to python datetime for utc_to_julian
        timestamps_dt = [ts.astype('datetime64[us]').astype(datetime) for ts in timestamps]
        # Vectorize timestamp conversion
        jds = np.array([utc_to_julian(t) for t in timestamps_dt])
        
        n_points = len(jds)
        
        # Pre-allocate arrays
        # Shape: (n_bodies, n_points)
        lons = np.zeros((len(self.bodies), n_points))
        lats = np.zeros((len(self.bodies), n_points))
        decs = np.zeros((len(self.bodies), n_points))
        
        # 1. Calculate Positions (3D)
        for i, pid in enumerate(self.body_indices):
            p_lons, p_lats, p_decs = self._get_trace(pid, jds)
            lons[i, :] = p_lons
            lats[i, :] = p_lats
            decs[i, :] = p_decs
            
        # 2. Compute Longitude Resonance (Aspects)
        res_lon = np.zeros(n_points)
        for i in range(len(self.bodies)):
            for j in range(i + 1, len(self.bodies)):
                diff = np.abs(lons[i] - lons[j])
                diff = np.where(diff > 180, 360 - diff, diff)
                
                # Check against all harmonics
                # Vectorized over harmonics? diff is (n_points,)
                # broadcasting: diff[:, None] - harmonics[None, :]
                delta = diff[:, np.newaxis] - self.harmonics[np.newaxis, :]
                
                # Sum of Gaussians
                score = np.sum(np.exp(-(delta**2)/(2 * self.sigma_lon**2)), axis=1)
                res_lon += score

        # 3. Compute Declination Resonance (Parallels/Contra)
        res_dec = np.zeros(n_points)
        for i in range(len(self.bodies)):
            for j in range(i + 1, len(self.bodies)):
                d1 = decs[i]
                d2 = decs[j]
                
                # Parallel
                diff_p = np.abs(d1 - d2)
                score_p = np.exp(-(diff_p**2)/(2 * self.sigma_dec**2))
                
                # Contra-Parallel
                diff_cp = np.abs(d1 + d2)
                score_cp = np.exp(-(diff_cp**2)/(2 * self.sigma_dec**2))
                
                res_dec += (score_p + score_cp)
                
        # 4. Compute Latitude Resonance (Nodal Crossings)
        # Score is high when planet is near 0 latitude (Ecliptic plane)
        res_lat = np.zeros(n_points)
        for i in range(len(self.bodies)):
            lat_dist = np.abs(lats[i])
            score = np.exp(-(lat_dist**2)/(2 * self.sigma_lat**2))
            res_lat += score

        # Create NumPy structured array
        result = np.zeros(n_points, dtype=RESONANCE_DTYPE)
        result['timestamp'] = timestamps
        result['res_lon'] = res_lon
        result['res_lat'] = res_lat
        result['res_dec'] = res_dec

        return result

    def _get_trace(self, pid: int, jds: np.ndarray):
        """Calculate 3D trace for a single body over many JDs (vectorized)."""
        # Uses batch API (bypasses LRU cache, faster for arrays)
        # Batch ephemeris: shape (n, 6) = [lon, lat, dist, lon_speed, lat_speed, dist_speed]
        positions = calc_planet_position_batch(jds, pid)
        lons = positions[:, 0]
        lats = positions[:, 1]
        dists = positions[:, 2]

        # Vectorized coordinate transformation
        xs, ys, zs = spherical_to_rectangular(lons, lats, dists)
        obliquities = mean_obliquity(jds)  # Now accepts arrays
        xes, yes_, zes = ecliptic_to_equatorial(xs, ys, zs, obliquities)
        _, decs, _ = rectangular_to_spherical(xes, yes_, zes)

        return lons, lats, decs
