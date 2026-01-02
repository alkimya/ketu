"""Complex number representation for planetary cycles.

This module provides a complex number representation of planetary positions
and cycles, where each position on the zodiac circle is represented as a
point on the unit circle in the complex plane.

Mathematical Foundation:
    A longitude θ (in radians) is represented as z = e^(iθ) = cos(θ) + i·sin(θ)

    This representation has several advantages:
    - Angular operations become algebraic: z₁/z₂ = e^(i(θ₁-θ₂))
    - Circular mean is simply: arg(Σzᵢ)
    - No discontinuity at 0°/360°
    - ML-friendly: (Re(z), Im(z)) are linear features
    - Aspects are roots of unity

Convention:
    - Internal calculations use radians
    - User-facing functions accept/return degrees
    - Complex numbers are always on the unit circle (|z| = 1)

Example:
    >>> from ketu.complex import ZodiacPoint, CycleRatio
    >>>
    >>> # Create points from degrees
    >>> moon = ZodiacPoint.from_degrees(120)  # Moon at 120°
    >>> sun = ZodiacPoint.from_degrees(90)    # Sun at 90°
    >>>
    >>> # Compute cycle ratio
    >>> cycle = moon / sun  # or CycleRatio(moon, sun)
    >>> print(cycle.aspect_degrees)  # 30.0 (sextile approaching)
    >>> print(cycle.nearest_aspect)  # 'sextile'
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional, Sequence, Union
import numpy as np

__all__ = [
    "ZodiacPoint",
    "CycleRatio",
    "Aspect",
    "ASPECTS",
    "circular_mean",
    "circular_std",
    "phase_locking_value",
]


# Major aspects as complex numbers (roots of unity)
# Each aspect is e^(iθ) where θ is the aspect angle in radians
@dataclass(frozen=True)
class Aspect:
    """A major aspect defined as a root of unity.

    Attributes:
        name: Human-readable name
        degrees: Angle in degrees (for display)
        radians: Angle in radians (for calculation)
        z: Complex representation on unit circle
        orb_default: Default orb tolerance in degrees
    """
    name: str
    degrees: float
    radians: float
    z: complex
    orb_default: float

    @classmethod
    def from_degrees(cls, name: str, degrees: float, orb: float = 8.0) -> Aspect:
        """Create an aspect from degrees."""
        radians = math.radians(degrees)
        z = complex(math.cos(radians), math.sin(radians))
        return cls(name=name, degrees=degrees, radians=radians, z=z, orb_default=orb)


# Standard major aspects
ASPECTS = {
    "conjunction": Aspect.from_degrees("conjunction", 0, orb=10.0),
    "sextile": Aspect.from_degrees("sextile", 60, orb=6.0),
    "square": Aspect.from_degrees("square", 90, orb=8.0),
    "trine": Aspect.from_degrees("trine", 120, orb=8.0),
    "opposition": Aspect.from_degrees("opposition", 180, orb=10.0),
}

# Extended aspects (less commonly used)
ASPECTS_EXTENDED = {
    **ASPECTS,
    "semi-sextile": Aspect.from_degrees("semi-sextile", 30, orb=2.0),
    "semi-square": Aspect.from_degrees("semi-square", 45, orb=2.0),
    "sesquiquadrate": Aspect.from_degrees("sesquiquadrate", 135, orb=2.0),
    "quincunx": Aspect.from_degrees("quincunx", 150, orb=3.0),
}


@dataclass
class ZodiacPoint:
    """A point on the zodiac circle represented as a complex number.

    The point is always on the unit circle: |z| = 1.

    Attributes:
        z: Complex number on unit circle
        radians: Angle in radians [0, 2π)
        degrees: Angle in degrees [0, 360) - computed property
    """
    z: complex
    radians: float

    def __post_init__(self):
        # Normalize to unit circle
        if abs(abs(self.z) - 1.0) > 1e-10:
            self.z = self.z / abs(self.z)

    @classmethod
    def from_degrees(cls, degrees: float) -> ZodiacPoint:
        """Create a ZodiacPoint from degrees.

        Args:
            degrees: Longitude in degrees (0-360, or any value - will be normalized)

        Returns:
            ZodiacPoint on unit circle
        """
        # Normalize to [0, 360)
        degrees = degrees % 360
        radians = math.radians(degrees)
        z = complex(math.cos(radians), math.sin(radians))
        return cls(z=z, radians=radians)

    @classmethod
    def from_radians(cls, radians: float) -> ZodiacPoint:
        """Create a ZodiacPoint from radians.

        Args:
            radians: Longitude in radians (will be normalized to [0, 2π))

        Returns:
            ZodiacPoint on unit circle
        """
        # Normalize to [0, 2π)
        radians = radians % (2 * math.pi)
        z = complex(math.cos(radians), math.sin(radians))
        return cls(z=z, radians=radians)

    @classmethod
    def from_complex(cls, z: complex) -> ZodiacPoint:
        """Create a ZodiacPoint from a complex number.

        The complex number will be normalized to the unit circle.

        Args:
            z: Complex number (will be normalized to |z| = 1)

        Returns:
            ZodiacPoint on unit circle
        """
        radians = math.atan2(z.imag, z.real)
        if radians < 0:
            radians += 2 * math.pi
        return cls(z=z, radians=radians)

    @property
    def degrees(self) -> float:
        """Get longitude in degrees [0, 360)."""
        return math.degrees(self.radians)

    @property
    def real(self) -> float:
        """Real part (cosine of angle)."""
        return self.z.real

    @property
    def imag(self) -> float:
        """Imaginary part (sine of angle)."""
        return self.z.imag

    def __truediv__(self, other: ZodiacPoint) -> CycleRatio:
        """Divide two points to get cycle ratio: self / other."""
        return CycleRatio(self, other)

    def __mul__(self, other: ZodiacPoint) -> ZodiacPoint:
        """Multiply two points (add angles)."""
        return ZodiacPoint.from_complex(self.z * other.z)

    def __repr__(self) -> str:
        return f"ZodiacPoint({self.degrees:.2f}°)"

    def to_ml_features(self) -> tuple[float, float]:
        """Convert to ML-friendly features (cos, sin).

        Returns:
            Tuple of (cos(θ), sin(θ)) - linear features without discontinuity
        """
        return (self.z.real, self.z.imag)

    def distance_to(self, other: ZodiacPoint) -> float:
        """Angular distance to another point in radians [0, π].

        This is the shortest arc distance on the circle.

        Args:
            other: Another ZodiacPoint

        Returns:
            Distance in radians [0, π]
        """
        # Use the angle of the ratio
        ratio = self.z / other.z
        angle = abs(math.atan2(ratio.imag, ratio.real))
        return angle


@dataclass
class CycleRatio:
    """The ratio between two zodiac points, representing a cycle phase.

    For a cycle between body1 (faster) and body2 (slower), the ratio is:
        z_ratio = z_body1 / z_body2 = e^(i(θ₁ - θ₂))

    This directly encodes the angular separation and cycle phase.

    Attributes:
        point1: First zodiac point (typically faster body)
        point2: Second zodiac point (typically slower body)
        z: Complex ratio on unit circle
        radians: Phase angle in radians (-π, π]
    """
    point1: ZodiacPoint
    point2: ZodiacPoint
    z: complex = None
    radians: float = None

    def __post_init__(self):
        if self.z is None:
            self.z = self.point1.z / self.point2.z
            # Normalize (should already be on unit circle, but ensure)
            if abs(abs(self.z) - 1.0) > 1e-10:
                self.z = self.z / abs(self.z)
        if self.radians is None:
            self.radians = math.atan2(self.z.imag, self.z.real)

    @classmethod
    def from_degrees(cls, separation_degrees: float) -> CycleRatio:
        """Create a CycleRatio directly from angular separation.

        Args:
            separation_degrees: Angular separation in degrees

        Returns:
            CycleRatio representing the separation
        """
        radians = math.radians(separation_degrees)
        z = complex(math.cos(radians), math.sin(radians))
        # Create dummy points
        p1 = ZodiacPoint.from_degrees(separation_degrees)
        p2 = ZodiacPoint.from_degrees(0)
        return cls(point1=p1, point2=p2, z=z, radians=radians)

    @classmethod
    def from_radians(cls, separation_radians: float) -> CycleRatio:
        """Create a CycleRatio directly from angular separation in radians.

        Args:
            separation_radians: Angular separation in radians

        Returns:
            CycleRatio representing the separation
        """
        z = complex(math.cos(separation_radians), math.sin(separation_radians))
        p1 = ZodiacPoint.from_radians(separation_radians)
        p2 = ZodiacPoint.from_radians(0)
        return cls(point1=p1, point2=p2, z=z, radians=separation_radians)

    @property
    def degrees(self) -> float:
        """Phase angle in degrees (-180, 180]."""
        return math.degrees(self.radians)

    @property
    def separation_degrees(self) -> float:
        """Angular separation in degrees [0, 360).

        This is the separation measured in the positive direction
        (counterclockwise on the zodiac).
        """
        deg = math.degrees(self.radians)
        if deg < 0:
            deg += 360
        return deg

    @property
    def separation_radians(self) -> float:
        """Angular separation in radians [0, 2π)."""
        if self.radians < 0:
            return self.radians + 2 * math.pi
        return self.radians

    @property
    def aspect_degrees(self) -> float:
        """Absolute aspect angle in degrees [0, 180].

        This is always the smaller of the two possible arcs.
        """
        return abs(self.degrees)

    @property
    def is_waxing(self) -> bool:
        """True if in waxing phase (0° to 180°)."""
        return 0 <= self.separation_degrees < 180

    @property
    def is_waning(self) -> bool:
        """True if in waning phase (180° to 360°)."""
        return self.separation_degrees >= 180

    @property
    def cycle_progress(self) -> float:
        """Progress through cycle [0, 1)."""
        return self.separation_degrees / 360

    def distance_to_aspect(self, aspect: Union[Aspect, str]) -> float:
        """Distance to a specific aspect in radians.

        Args:
            aspect: Aspect object or name (e.g., 'conjunction', 'trine')

        Returns:
            Signed distance in radians. Negative = approaching, positive = separating.
        """
        if isinstance(aspect, str):
            aspect = ASPECTS.get(aspect) or ASPECTS_EXTENDED.get(aspect)
            if aspect is None:
                raise ValueError(f"Unknown aspect: {aspect}")

        # Distance is the angle between z_ratio and z_aspect
        ratio = self.z / aspect.z
        return math.atan2(ratio.imag, ratio.real)

    def is_in_aspect(self, aspect: Union[Aspect, str], orb: Optional[float] = None) -> bool:
        """Check if currently in aspect within orb.

        Args:
            aspect: Aspect object or name
            orb: Orb tolerance in degrees (uses default if None)

        Returns:
            True if within orb of the aspect
        """
        if isinstance(aspect, str):
            aspect_obj = ASPECTS.get(aspect) or ASPECTS_EXTENDED.get(aspect)
            if aspect_obj is None:
                raise ValueError(f"Unknown aspect: {aspect}")
            aspect = aspect_obj

        if orb is None:
            orb = aspect.orb_default

        distance = abs(self.distance_to_aspect(aspect))
        return distance <= math.radians(orb)

    @property
    def nearest_aspect(self) -> tuple[Aspect, float]:
        """Find the nearest major aspect.

        Returns:
            Tuple of (Aspect, signed_distance_radians)
        """
        nearest = None
        min_distance = float('inf')

        for aspect in ASPECTS.values():
            dist = self.distance_to_aspect(aspect)
            if abs(dist) < abs(min_distance):
                min_distance = dist
                nearest = aspect

        return nearest, min_distance

    @property
    def nearest_aspect_name(self) -> str:
        """Name of the nearest major aspect."""
        aspect, _ = self.nearest_aspect
        return aspect.name

    def to_ml_features(self) -> dict[str, float]:
        """Convert to ML-friendly features.

        Returns:
            Dict with features suitable for ML models:
            - cos_phase: Real part of z (cos of separation)
            - sin_phase: Imaginary part of z (sin of separation)
            - cycle_progress: Normalized progress [0, 1)
            - is_waxing: 1 if waxing, 0 if waning
            - dist_conjunction: Distance to conjunction in radians
            - dist_opposition: Distance to opposition in radians
        """
        return {
            "cos_phase": self.z.real,
            "sin_phase": self.z.imag,
            "cycle_progress": self.cycle_progress,
            "is_waxing": 1.0 if self.is_waxing else 0.0,
            "dist_conjunction": abs(self.distance_to_aspect("conjunction")),
            "dist_opposition": abs(self.distance_to_aspect("opposition")),
        }

    def __repr__(self) -> str:
        aspect, dist = self.nearest_aspect
        dist_deg = math.degrees(dist)
        direction = "separating" if dist > 0 else "approaching"
        return f"CycleRatio({self.separation_degrees:.1f}°, near {aspect.name} {direction} {abs(dist_deg):.1f}°)"


# =============================================================================
# Vectorized Operations
# =============================================================================

def circular_mean(points: Sequence[ZodiacPoint]) -> ZodiacPoint:
    """Compute the circular mean of multiple zodiac points.

    The circular mean is the direction of the resultant vector
    when all unit vectors are summed.

    Args:
        points: Sequence of ZodiacPoint objects

    Returns:
        ZodiacPoint representing the circular mean
    """
    if not points:
        raise ValueError("Cannot compute mean of empty sequence")

    z_sum = sum(p.z for p in points)
    return ZodiacPoint.from_complex(z_sum)


def circular_std(points: Sequence[ZodiacPoint]) -> float:
    """Compute the circular standard deviation.

    Based on the resultant length R = |Σzᵢ|/n.
    Circular std = √(-2·ln(R))

    Args:
        points: Sequence of ZodiacPoint objects

    Returns:
        Circular standard deviation in radians
    """
    if not points:
        raise ValueError("Cannot compute std of empty sequence")

    n = len(points)
    z_sum = sum(p.z for p in points)
    R = abs(z_sum) / n  # Resultant length

    if R >= 1.0:
        return 0.0  # All points coincide
    if R <= 0.0:
        return float('inf')  # Points are uniformly distributed

    return math.sqrt(-2 * math.log(R))


def phase_locking_value(
    series1: Sequence[ZodiacPoint],
    series2: Sequence[ZodiacPoint]
) -> float:
    """Compute Phase Locking Value (PLV) between two series.

    PLV measures phase synchronization:
    PLV = |⟨e^(i(φ₁-φ₂))⟩| = |mean(z₁/z₂)|

    Args:
        series1: First time series of ZodiacPoints
        series2: Second time series of ZodiacPoints

    Returns:
        PLV in range [0, 1]. 0 = no sync, 1 = perfect sync
    """
    if len(series1) != len(series2):
        raise ValueError("Series must have same length")
    if not series1:
        raise ValueError("Cannot compute PLV of empty series")

    # Compute phase differences
    phase_diffs = [p1.z / p2.z for p1, p2 in zip(series1, series2)]

    # PLV is the magnitude of the mean phase difference
    mean_diff = sum(phase_diffs) / len(phase_diffs)
    return abs(mean_diff)


# =============================================================================
# NumPy Vectorized Functions (for performance with large arrays)
# =============================================================================

def degrees_to_complex(degrees: np.ndarray) -> np.ndarray:
    """Convert array of degrees to complex numbers on unit circle.

    Args:
        degrees: NumPy array of longitudes in degrees

    Returns:
        NumPy array of complex numbers
    """
    radians = np.deg2rad(degrees)
    return np.exp(1j * radians)


def radians_to_complex(radians: np.ndarray) -> np.ndarray:
    """Convert array of radians to complex numbers on unit circle.

    Args:
        radians: NumPy array of angles in radians

    Returns:
        NumPy array of complex numbers
    """
    return np.exp(1j * radians)


def complex_to_degrees(z: np.ndarray) -> np.ndarray:
    """Convert complex numbers to degrees [0, 360).

    Args:
        z: NumPy array of complex numbers

    Returns:
        NumPy array of degrees
    """
    return np.rad2deg(np.angle(z)) % 360


def complex_to_radians(z: np.ndarray) -> np.ndarray:
    """Convert complex numbers to radians [0, 2π).

    Args:
        z: NumPy array of complex numbers

    Returns:
        NumPy array of radians
    """
    angles = np.angle(z)
    return np.where(angles < 0, angles + 2 * np.pi, angles)


def cycle_ratio_vectorized(
    body1_degrees: np.ndarray,
    body2_degrees: np.ndarray
) -> np.ndarray:
    """Compute cycle ratios for arrays of positions.

    Args:
        body1_degrees: Array of body 1 longitudes in degrees
        body2_degrees: Array of body 2 longitudes in degrees

    Returns:
        Array of complex cycle ratios
    """
    z1 = degrees_to_complex(body1_degrees)
    z2 = degrees_to_complex(body2_degrees)
    return z1 / z2


def nearest_aspect_vectorized(
    z_ratios: np.ndarray,
    aspects: dict[str, Aspect] = None
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Find nearest aspect for array of cycle ratios.

    Args:
        z_ratios: Array of complex cycle ratios
        aspects: Dict of aspects to check (default: ASPECTS)

    Returns:
        Tuple of (aspect_indices, aspect_angles_deg, distances_rad)
    """
    if aspects is None:
        aspects = ASPECTS

    aspect_list = list(aspects.values())
    aspect_z = np.array([a.z for a in aspect_list])
    aspect_angles = np.array([a.degrees for a in aspect_list])

    # Compute distance to each aspect for each ratio
    # Shape: (n_ratios, n_aspects)
    distances = np.angle(z_ratios[:, np.newaxis] / aspect_z[np.newaxis, :])
    abs_distances = np.abs(distances)

    # Find nearest
    nearest_idx = np.argmin(abs_distances, axis=1)
    nearest_angles = aspect_angles[nearest_idx]
    nearest_distances = distances[np.arange(len(z_ratios)), nearest_idx]

    return nearest_idx, nearest_angles, nearest_distances


def to_ml_features_vectorized(z_ratios: np.ndarray) -> np.ndarray:
    """Convert array of cycle ratios to ML features.

    Args:
        z_ratios: Array of complex cycle ratios

    Returns:
        Array of shape (n, 6) with columns:
        [cos_phase, sin_phase, cycle_progress, is_waxing, dist_conj, dist_opp]
    """
    n = len(z_ratios)
    features = np.zeros((n, 6))

    # cos and sin of phase
    features[:, 0] = z_ratios.real
    features[:, 1] = z_ratios.imag

    # Cycle progress [0, 1)
    angles = np.angle(z_ratios)
    separation = np.where(angles < 0, angles + 2 * np.pi, angles)
    features[:, 2] = separation / (2 * np.pi)

    # Is waxing
    features[:, 3] = (separation < np.pi).astype(float)

    # Distance to conjunction (angle to 1+0j)
    features[:, 4] = np.abs(np.angle(z_ratios))

    # Distance to opposition (angle to -1+0j)
    features[:, 5] = np.abs(np.angle(z_ratios / (-1+0j)))

    return features
