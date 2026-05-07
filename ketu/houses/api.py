"""Public API for the houses subpackage.

Two key public functions:

- :func:`calculate_houses` — Dispatches through :data:`SYSTEMS`, handles
  ``polar_fallback``. Vectorised over ``(jd, lat, lon)`` of any compatible
  broadcast shape.
- :func:`house_of` — Assigns a planet longitude to its 1-indexed house.
  Vectorised over both ``planet_lon`` and ``cusps``.

Both functions are pure NumPy. No swisseph runtime import (the swisseph
oracle lives only in :mod:`tests.houses.conftest`).
"""
from __future__ import annotations

from typing import Literal, Union, cast

import numpy as np

from .ascmc import compute_ascmc
from .core import HOUSES_DTYPE, HighLatitudeError
from .porphyry import is_polar, polar_circle, porphyry_cusps
from .registry import get_system

ArrayLike = Union[float, np.ndarray]


def calculate_houses(
    jd: ArrayLike,
    lat: ArrayLike,
    lon: ArrayLike,
    system: str = "placidus",
    polar_fallback: Literal["raise", "porphyry"] = "raise",
) -> np.ndarray:
    """Compute house cusps for one or many ``(jd, lat, lon)`` inputs.

    Parameters
    ----------
    jd : float or np.ndarray
        Julian Date, UT.
    lat : float or np.ndarray
        Geographic latitude (degrees).
    lon : float or np.ndarray
        Geographic longitude (degrees, east-positive).
    system : str, default "placidus"
        House system name: ``"placidus"``, ``"koch"``, ``"porphyry"``, or any
        name registered via :func:`ketu.houses.registry.register`.
        Case-insensitive.
    polar_fallback : {"raise", "porphyry"}, default "raise"
        Behavior when ``|lat| > polar_circle(jd)`` (≈ 66.56°):

        - ``"raise"`` (default): raise :class:`HighLatitudeError` for those
          elements.
        - ``"porphyry"``: substitute Porphyry cusps for the polar elements;
          non-polar elements get the requested ``system``.

    Returns
    -------
    np.ndarray
        Structured array of :data:`HOUSES_DTYPE`, leading shape == broadcast
        of ``(jd, lat, lon)``.
        Fields: ``jd``, ``lat``, ``lon``, ``system``, ``cusps[12]``, ``asc``,
        ``mc``, ``armc``, ``vertex``.

    Raises
    ------
    HighLatitudeError
        When ``polar_fallback='raise'`` and ``|lat| > polar_circle(jd)`` for
        any input element.
    ValueError
        When ``system`` is not registered or ``polar_fallback`` is invalid.

    Notes
    -----
    The ``out["system"]`` field always reports the user's requested system
    (lowercased), even when ``polar_fallback='porphyry'`` substituted
    Porphyry cusps for polar elements. The ``cusps`` reflect the actual
    computation; the ``system`` field reflects the user's request. Callers
    that need to know whether substitution happened should detect it via
    ``np.isnan`` on the requested system's output (Placidus/Koch return
    NaN at polar latitudes) or by re-checking ``is_polar(lat, jd)``.

    Examples
    --------
    >>> import numpy as np
    >>> r = calculate_houses(2451545.0, 48.8566, 2.3522, system="placidus")
    >>> r["cusps"].shape
    (12,)
    >>> r_batch = calculate_houses(
    ...     np.array([2451545.0, 2470204.0]),
    ...     np.array([48.8566, 64.1466]),
    ...     np.array([2.3522, -21.9426]),
    ...     system="koch", polar_fallback="porphyry",
    ... )
    >>> r_batch.shape, r_batch["cusps"].shape
    ((2,), (2, 12))
    """
    if polar_fallback not in ("raise", "porphyry"):
        raise ValueError(
            f"polar_fallback must be 'raise' or 'porphyry'; "
            f"got {polar_fallback!r}"
        )

    sys_fn = get_system(system)  # raises ValueError on unknown system
    system_lower = system.lower()

    # Broadcast inputs to common shape S.
    jd_a = np.asarray(jd, dtype=np.float64)
    lat_a = np.asarray(lat, dtype=np.float64)
    lon_a = np.asarray(lon, dtype=np.float64)
    jd_b, lat_b, lon_b = np.broadcast_arrays(jd_a, lat_a, lon_a)

    # ASC/MC/ARMC/Vertex/eps closed-form, vectorised.
    ascmc = compute_ascmc(jd_b, lat_b, lon_b)
    armc = np.asarray(ascmc["armc"], dtype=np.float64)
    eps = np.asarray(ascmc["eps"], dtype=np.float64)

    # Detect polar elements (|lat| > polar_circle(jd)). Porphyry is itself
    # the polar fallback path — mathematically defined at all latitudes
    # including 89° — so the polar gate does NOT apply when the user
    # explicitly requested Porphyry. Skipping the gate here lets users
    # call ``calculate_houses(jd, 80, 0, system='porphyry')`` directly
    # without redundant ``polar_fallback='porphyry'`` boilerplate.
    polar_mask_raw = is_polar(lat_b, jd_b)
    polar_mask = np.asarray(polar_mask_raw, dtype=bool)
    any_polar = bool(polar_mask.any()) and system_lower != "porphyry"

    if any_polar and polar_fallback == "raise":
        # First offending element drives the diagnostic.
        polar_lats_arr = np.asarray(polar_circle(jd_b), dtype=np.float64)
        flat_mask = polar_mask.reshape(-1)
        first_idx = int(np.argmax(flat_mask))
        offending_lat = float(lat_b.reshape(-1)[first_idx])
        offending_polar_lat = float(polar_lats_arr.reshape(-1)[first_idx])
        raise HighLatitudeError(
            offending_lat, system_lower, offending_polar_lat
        )

    # Dispatch via SYSTEMS — no inline if/elif ladder anywhere
    # (research §Anti-Pattern 1: registry-based dispatch only).
    cusps = sys_fn(armc, lat_b, eps)  # shape (*S, 12)

    # Polar fallback: substitute Porphyry cusps for polar elements when
    # polar_fallback='porphyry'. Porphyry is mathematically defined at all
    # latitudes (no NaN); see ketu.houses.porphyry.
    if any_polar and polar_fallback == "porphyry":
        cusps_porphyry = porphyry_cusps(armc, lat_b, eps)
        # Broadcast polar_mask to (*S, 1) so np.where with cusps shape (*S, 12)
        # selects per-element across the 12-cusp axis.
        mask_broadcast = polar_mask[..., np.newaxis]
        cusps = np.where(mask_broadcast, cusps_porphyry, cusps)

    # Build the structured output preserving leading shape S.
    out = np.empty(jd_b.shape, dtype=HOUSES_DTYPE)
    out["jd"] = jd_b
    out["lat"] = lat_b
    out["lon"] = lon_b
    out["system"] = system_lower
    out["cusps"] = cusps
    out["asc"] = np.asarray(ascmc["asc"])
    out["mc"] = np.asarray(ascmc["mc"])
    out["armc"] = armc
    out["vertex"] = np.asarray(ascmc["vertex"])

    return out


def house_of(
    planet_lon: ArrayLike,
    cusps: np.ndarray,
) -> np.ndarray:
    """Return the 1-indexed house number containing each planet longitude.

    Parameters
    ----------
    planet_lon : float or np.ndarray
        Planetary ecliptic longitude(s) in degrees. Normalised modulo 360
        internally so callers don't need to pre-clamp.
    cusps : np.ndarray
        Cusp array of shape ``(12,)`` or ``(..., 12)``. ``cusps[..., i]`` is
        the cusp of house ``i + 1`` (i.e. ``cusps[..., 0]`` is the ASC).

    Returns
    -------
    np.ndarray of int32
        Broadcast shape over ``planet_lon`` and the leading dims of
        ``cusps``. Values in ``{1, ..., 12}``.

    Examples
    --------
    >>> import numpy as np
    >>> r = calculate_houses(2451545.0, 48.8566, 2.3522)
    >>> int(house_of(45.0, r["cusps"]))   # 1..12
    2
    >>> # vectorised: 5 planets at once
    >>> planet_lons = np.array([0.0, 45.0, 90.0, 180.0, 270.0])
    >>> house_of(planet_lons, r["cusps"]).shape
    (5,)

    Notes
    -----
    Convention: cusp ``i`` BEGINS house ``i + 1`` going eastward. A planet
    at exactly ``cusps[0]`` (the ASC) is in house 1; at ``cusps[5]`` is in
    house 6. The eastward-distance metric

    .. code-block:: text

        diffs = (planet_lon - cusps + 360) mod 360
        spans = (cusps_next - cusps + 360) mod 360
        in_house = diffs < spans

    yields exactly one ``True`` per row in well-formed cusp arrays. We pick
    that index via :func:`numpy.argmax` (which returns the first ``True``
    when multiple are present, the conventional choice for degenerate
    cusps).
    """
    planet_lon_a = np.asarray(planet_lon, dtype=np.float64) % 360.0
    cusps_a = np.asarray(cusps, dtype=np.float64)

    # planet_lon shape (...,) -> expand to (..., 1) for broadcasting against
    # cusps shape (..., 12) -> result shape (..., 12).
    diffs = (planet_lon_a[..., np.newaxis] - cusps_a + 360.0) % 360.0
    next_cusp = np.roll(cusps_a, -1, axis=-1)
    spans = (next_cusp - cusps_a + 360.0) % 360.0
    in_house = diffs < spans  # shape (..., 12); exactly one True per row

    # argmax returns the first True; if multiple True (degenerate case),
    # the earliest house wins — the conventional choice.
    house_idx = np.argmax(in_house, axis=-1)  # 0..11
    return cast(np.ndarray, (house_idx + 1).astype(np.int32))
