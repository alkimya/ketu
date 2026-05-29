"""
Ephemeris cache for fast planetary position lookups.

Pre-computes daily planetary positions and provides fast O(1) lookups
with linear interpolation for intra-day times.

Performance:
    - Cache miss (compute): ~10ms per day per body
    - Cache hit (lookup): ~0.01ms (1000x faster)
    - Interpolation overhead: ~0.005ms

Storage:
    - ~19 KB per month (13 bodies × 31 days × 6 floats × 4 bytes)
    - ~230 KB per year
    - Memory: keeps current month + adjacent months loaded
"""

import calendar
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional, Dict, Tuple, Union, List
import numpy as np

from ketu.ephemeris.time import utc_to_julian
from ketu.ephemeris.planets import calc_planet_position_batch, BODY_INDICES


# Constants
BODY_COUNT = 14  # Sun through Chiron
POSITION_FIELDS = 6  # lon, lat, dist, lon_speed, lat_speed, dist_speed

# Body IDs for reference
BODY_IDS = {
    "Sun": 0, "Moon": 1, "Mercury": 2, "Venus": 3, "Mars": 4,
    "Jupiter": 5, "Saturn": 6, "Uranus": 7, "Neptune": 8, "Pluto": 9,
    "Rahu": 10, "Ketu": 11, "Lilith": 12, "Chiron": 13,
}


class EphemerisCache:
    """
    Cache for pre-computed planetary ephemeris data.

    Stores daily positions for all 13 celestial bodies and provides
    fast lookups with linear interpolation for any timestamp.

    Parameters
    ----------
    cache_dir : str or Path, optional
        Directory for persistent cache files (.npy).
        Defaults to ``~/.ketu/ephemeris_cache``.

    Attributes
    ----------
    cache_dir : Path
        Directory for persistent cache files (.npy).

    Examples
    --------
    >>> cache = EphemerisCache()
    >>> cache.ensure_range(2025, 1, 2025, 12)
    >>> from datetime import datetime
    >>> pos = cache.get_position(datetime(2025, 6, 15, 14, 30), body_id=0)
    >>> bool(0.0 <= pos[0] < 360.0)  # Sun longitude in valid range
    True
    """

    def __init__(self, cache_dir: Optional[Union[str, Path]] = None):
        """
        Initialize the ephemeris cache

        Parameters
        ----------
        cache_dir : str or Path, optional
            Directory for cache files. Defaults to ~/.ketu/ephemeris_cache.
        """
        if cache_dir is None:
            cache_dir = Path.home() / ".ketu" / "ephemeris_cache"
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # In-memory cache: {(year, month): np.ndarray shape (days, bodies, fields)}
        self._memory_cache: Dict[Tuple[int, int], np.ndarray] = {}

        # Track which months are loaded
        self._loaded_months: set[Tuple[int, int]] = set()

    def _cache_path(self, year: int, month: int) -> Path:
        """
        Get path to cache file for a given month."""
        return self.cache_dir / f"{year:04d}-{month:02d}-ephemeris.npy"

    def _compute_month(self, year: int, month: int) -> np.ndarray:
        """
        Compute ephemeris data for an entire month

        Parameters
        ----------
        year : int
            Year (e.g., 2025).
        month : int
            Month (1-12).

        Returns
        -------
        np.ndarray
            Array of shape (days_in_month, BODY_COUNT, POSITION_FIELDS)
            where POSITION_FIELDS = [lon, lat, dist, lon_speed, lat_speed, dist_speed].
        """
        days_in_month = calendar.monthrange(year, month)[1]

        # Generate dates at midnight UTC for each day
        dates = [
            datetime(year, month, day, 0, 0, 0, tzinfo=timezone.utc)
            for day in range(1, days_in_month + 1)
        ]

        # Convert to Julian dates
        jds = np.array([utc_to_julian(d) for d in dates], dtype=np.float64)

        # Result array: (days, bodies, 6 fields)
        result = np.zeros((days_in_month, BODY_COUNT, POSITION_FIELDS), dtype=np.float32)

        # Compute positions for each body
        for body_id in range(BODY_COUNT):
            positions = calc_planet_position_batch(jds, body_id)
            # positions shape: (days, 6)
            result[:, body_id, :] = positions.astype(np.float32)

        return result

    def ensure_month(self, year: int, month: int, force_recompute: bool = False) -> None:
        """
        Ensure a month is cached (compute if needed).

        Parameters
        ----------
        year : int
            Year.
        month : int
            Month (1-12).
        force_recompute : bool, optional
            If True, recompute even if cached.
        """
        cache_key = (year, month)
        cache_path = self._cache_path(year, month)

        # Check if already in memory
        if cache_key in self._memory_cache and not force_recompute:
            return

        # Check if on disk — validate body count (stale files built pre-Chiron
        # have shape (days, 13, 6); recompute transparently if mismatched).
        if cache_path.exists() and not force_recompute:
            data = np.load(cache_path)
            if data.shape[1] != BODY_COUNT:
                # Stale cache: body-count mismatch — recompute and overwrite.
                data = self._compute_month(year, month)
                np.save(cache_path, data)
            self._memory_cache[cache_key] = data
            self._loaded_months.add(cache_key)
            return

        # Compute and save
        data = self._compute_month(year, month)
        np.save(cache_path, data)
        self._memory_cache[cache_key] = data
        self._loaded_months.add(cache_key)

    def ensure_range(
        self,
        start_year: int,
        start_month: int,
        end_year: int,
        end_month: int,
        force_recompute: bool = False,
    ) -> None:
        """
        Ensure a range of months is cached.

        Parameters
        ----------
        start_year : int
            Start year.
        start_month : int
            Start month (1-12).
        end_year : int
            End year.
        end_month : int
            End month (1-12).
        force_recompute : bool, optional
            If True, recompute all months.
        """
        current = datetime(start_year, start_month, 1)
        end = datetime(end_year, end_month, 1)

        while current <= end:
            self.ensure_month(current.year, current.month, force_recompute)
            # Move to next month
            if current.month == 12:
                current = datetime(current.year + 1, 1, 1)
            else:
                current = datetime(current.year, current.month + 1, 1)

    def get_position(
        self,
        timestamp: datetime,
        body_id: int,
        interpolate: bool = True,
    ) -> np.ndarray:
        """
        Get position for a single body at a specific time.

        Parameters
        ----------
        timestamp : datetime
            UTC datetime.
        body_id : int
            Body ID (0-12).
        interpolate : bool, optional
            If True, interpolate between daily values.

        Returns
        -------
        np.ndarray
            Array of [lon, lat, dist, lon_speed, lat_speed, dist_speed].
        """
        # Ensure UTC
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)

        year, month, day = timestamp.year, timestamp.month, timestamp.day
        cache_key = (year, month)

        # Load month if not in memory
        if cache_key not in self._memory_cache:
            self.ensure_month(year, month)

        data = self._memory_cache[cache_key]
        day_index = day - 1  # 0-indexed

        if not interpolate:
            return data[day_index, body_id, :]

        # Linear interpolation for intra-day times
        fraction = (
            timestamp.hour + timestamp.minute / 60 + timestamp.second / 3600
        ) / 24.0

        if fraction == 0.0:
            return data[day_index, body_id, :]

        # Get next day's data
        if day_index < len(data) - 1:
            next_data = data[day_index + 1, body_id, :]
        else:
            # Cross month boundary - load next month
            if month == 12:
                next_key = (year + 1, 1)
            else:
                next_key = (year, month + 1)

            if next_key not in self._memory_cache:
                self.ensure_month(next_key[0], next_key[1])

            next_data = self._memory_cache[next_key][0, body_id, :]

        current_data = data[day_index, body_id, :]

        # Interpolate (handle longitude wrap-around for 0/360)
        result = np.zeros(POSITION_FIELDS, dtype=np.float32)

        for i in range(POSITION_FIELDS):
            if i == 0:  # Longitude - handle wrap
                lon1, lon2 = current_data[0], next_data[0]
                # Check if crossing 0/360 boundary
                if abs(lon2 - lon1) > 180:
                    if lon2 > lon1:
                        lon1 += 360
                    else:
                        lon2 += 360
                result[i] = (lon1 + (lon2 - lon1) * fraction) % 360
            else:
                result[i] = current_data[i] + (next_data[i] - current_data[i]) * fraction

        return result

    def get_all_positions(
        self,
        timestamp: datetime,
        interpolate: bool = True,
    ) -> np.ndarray:
        """
        Get positions for all bodies at a specific time.

        Parameters
        ----------
        timestamp : datetime
            UTC datetime.
        interpolate : bool, optional
            If True, interpolate between daily values.

        Returns
        -------
        np.ndarray
            Array of shape (BODY_COUNT, POSITION_FIELDS).
        """
        result = np.zeros((BODY_COUNT, POSITION_FIELDS), dtype=np.float32)
        for body_id in range(BODY_COUNT):
            result[body_id, :] = self.get_position(timestamp, body_id, interpolate)
        return result

    def get_positions_batch(
        self,
        timestamps: List[datetime],
        body_id: int,
        interpolate: bool = True,
    ) -> np.ndarray:
        """
        Get positions for a single body across multiple timestamps (slow path).

        For better performance, use get_positions_vectorized().

        Parameters
        ----------
        timestamps : list
            List of UTC datetimes.
        body_id : int
            Body ID (0-12).
        interpolate : bool, optional
            If True, interpolate between daily values.

        Returns
        -------
        np.ndarray
            Array of shape (len(timestamps), POSITION_FIELDS).
        """
        result = np.zeros((len(timestamps), POSITION_FIELDS), dtype=np.float32)
        for i, ts in enumerate(timestamps):
            result[i, :] = self.get_position(ts, body_id, interpolate)
        return result

    def get_positions_vectorized(
        self,
        timestamps: List[datetime],
        body_id: int,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Get longitude and velocity for a body across timestamps (vectorized).

        This is the fast path - uses numpy vectorized operations instead of
        Python loops. ~10x faster than get_positions_batch for large arrays.

        Parameters
        ----------
        timestamps : list or array-like
            List/array of UTC datetimes.
        body_id : int
            Body ID (0-12).

        Returns
        -------
        tuple of (np.ndarray, np.ndarray)
            Tuple of (longitudes, velocities) arrays, each shape (n,).
        """
        n = len(timestamps)
        if n == 0:
            return np.array([], dtype=np.float32), np.array([], dtype=np.float32)

        # Convert timestamps to components for vectorized processing
        years = np.array([ts.year for ts in timestamps], dtype=np.int32)
        months = np.array([ts.month for ts in timestamps], dtype=np.int32)
        days = np.array([ts.day for ts in timestamps], dtype=np.int32)
        fractions = np.array([
            (ts.hour + ts.minute / 60 + ts.second / 3600) / 24.0
            for ts in timestamps
        ], dtype=np.float32)

        # Find unique months to load
        unique_months = set(zip(years, months))
        for year, month in unique_months:
            if (year, month) not in self._memory_cache:
                self.ensure_month(year, month)

        # Also ensure next months for interpolation at month boundaries
        for year, month in list(unique_months):
            next_year, next_month = (year + 1, 1) if month == 12 else (year, month + 1)
            if (next_year, next_month) not in self._memory_cache:
                self.ensure_month(next_year, next_month)

        # Allocate result arrays
        longitudes = np.zeros(n, dtype=np.float32)
        velocities = np.zeros(n, dtype=np.float32)

        # Process each unique month in batch
        for (year, month) in unique_months:
            mask = (years == year) & (months == month)
            if not np.any(mask):
                continue

            indices = np.where(mask)[0]
            month_days = days[mask] - 1  # 0-indexed
            month_fractions = fractions[mask]

            # Get cached data for this month
            data = self._memory_cache[(year, month)]
            days_in_month = len(data)

            # Get next month data for boundary interpolation
            next_year, next_month = (year + 1, 1) if month == 12 else (year, month + 1)
            next_data = self._memory_cache.get((next_year, next_month))

            # Current day values
            current_lon = data[month_days, body_id, 0]
            current_vel = data[month_days, body_id, 3]

            # Next day values (handle month boundary)
            next_day_indices = month_days + 1
            within_month = next_day_indices < days_in_month

            next_lon = np.zeros(len(indices), dtype=np.float32)
            next_vel = np.zeros(len(indices), dtype=np.float32)

            # Days within same month
            if np.any(within_month):
                next_lon[within_month] = data[next_day_indices[within_month], body_id, 0]
                next_vel[within_month] = data[next_day_indices[within_month], body_id, 3]

            # Days crossing month boundary
            if np.any(~within_month) and next_data is not None:
                next_lon[~within_month] = next_data[0, body_id, 0]
                next_vel[~within_month] = next_data[0, body_id, 3]

            # Handle longitude wrap-around (0/360 boundary)
            lon_diff = next_lon - current_lon
            wrap_mask = np.abs(lon_diff) > 180
            current_lon_adj = current_lon.copy()
            next_lon_adj = next_lon.copy()

            # Adjust for wrap
            current_lon_adj[wrap_mask & (next_lon > current_lon)] += 360
            next_lon_adj[wrap_mask & (next_lon <= current_lon)] += 360

            # Vectorized linear interpolation
            interp_lon = current_lon_adj + (next_lon_adj - current_lon_adj) * month_fractions
            interp_lon = interp_lon % 360  # Normalize back to 0-360
            interp_vel = current_vel + (next_vel - current_vel) * month_fractions

            # Store results
            longitudes[indices] = interp_lon
            velocities[indices] = interp_vel

        return longitudes, velocities

    def get_longitudes_batch(
        self,
        timestamps: List[datetime],
        body_id: int,
    ) -> np.ndarray:
        """
        Get longitudes only for a single body (fast path).

        Parameters
        ----------
        timestamps : list
            List of UTC datetimes.
        body_id : int
            Body ID (0-12).

        Returns
        -------
        np.ndarray
            Array of longitudes (len(timestamps),).
        """
        longitudes, _ = self.get_positions_vectorized(timestamps, body_id)
        return longitudes

    def clear_memory(self) -> None:
        """
        Clear in-memory cache (disk cache remains).
        """
        self._memory_cache.clear()
        self._loaded_months.clear()

    def cache_stats(self) -> Dict[str, Union[int, float, List[str]]]:
        """
        Get cache statistics.

        Returns
        -------
        dict
            Dictionary with keys: ``months_in_memory``, ``months_on_disk``,
            ``memory_bytes``, ``memory_mb``, ``disk_files``.
        """
        disk_files = list(self.cache_dir.glob("*-ephemeris.npy"))
        memory_size = sum(
            arr.nbytes for arr in self._memory_cache.values()
        )

        return {
            "months_in_memory": len(self._memory_cache),
            "months_on_disk": len(disk_files),
            "memory_bytes": memory_size,
            "memory_mb": memory_size / (1024 * 1024),
            "disk_files": [f.name for f in disk_files],
        }


# Global singleton for convenience
_default_cache: Optional[EphemerisCache] = None


def get_default_cache() -> EphemerisCache:
    """
    Get the default global cache instance.

    Returns
    -------
    EphemerisCache
        The module-level singleton, created on first call.
    """
    global _default_cache
    if _default_cache is None:
        _default_cache = EphemerisCache()
    return _default_cache
