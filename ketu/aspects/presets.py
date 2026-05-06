"""Aspect set presets and resolver for configurable aspect filtering.

Three named presets select subsets of the 14 aspects in :mod:`ketu.core.aspects`:

- ``CLASSICAL`` — 5 majors (conjunction, sextile, square, trine, opposition).
- ``TRADITIONAL`` — 7 (CLASSICAL + semi-sextile, quincunx).
- ``EXTENDED`` — 14 (legacy v1.0 default — all aspects, including harmonics 5/9/10).

Each preset is a length-14 ``np.bool_`` array indexable into ``core.aspects``.
The row order is canonical and append-only (Phase 9 invariant)::

    0=Conjunction, 1=Semi-sextile, 2=Decile, 3=Novile, 4=Sextile,
    5=Quintile, 6=Binovile, 7=Square, 8=Tredecile, 9=Trine,
    10=Biquintile, 11=Quincunx, 12=Quadrinovile, 13=Opposition

Public API
----------
- ``CLASSICAL``, ``TRADITIONAL``, ``EXTENDED`` : frozen length-14 ``np.bool_`` masks.
- ``AspectSetSpec`` : type alias for the resolver input.
- ``resolve_aspect_set`` : single-call resolver that returns a length-14 mask.

ASP-06 forward-looking rule
----------------------------
No current LRU cache (``ketu.calculations:body_properties``,
``ketu.aspects.core:_cached_planet_position_batch``) materializes filtered aspect
output, so cache keys today do NOT need to include the aspect-set hash. If a
future cache memoizes a function whose return value depends on ``aspects=``,
its key MUST include ``mask.tobytes()`` (or equivalent) to avoid stale results
across different aspect sets. See Phase 9 RESEARCH.md, Pitfall 4.
"""
from __future__ import annotations

from typing import Sequence, Union

import numpy as np
import numpy.typing as npt

from ketu.core import aspects as _ASPECTS

# Sanity-check that core.aspects has length 14 (defensive; the invariant test
# also enforces this).
assert len(_ASPECTS) == 14, (
    f"core.aspects length changed to {len(_ASPECTS)}; "
    "aspect presets are pinned to 14"
)

# Preset masks: length-14 np.bool_ arrays selecting rows of core.aspects.
# Indices follow ketu/core.py row order:
#   0=Conjunction, 1=Semi-sextile, 2=Decile, 3=Novile, 4=Sextile,
#   5=Quintile, 6=Binovile, 7=Square, 8=Tredecile, 9=Trine,
#   10=Biquintile, 11=Quincunx, 12=Quadrinovile, 13=Opposition
_CLASSICAL_INDICES: npt.NDArray[np.intp] = np.array(
    [0, 4, 7, 9, 13], dtype=np.intp
)
_TRADITIONAL_INDICES: npt.NDArray[np.intp] = np.array(
    [0, 1, 4, 7, 9, 11, 13], dtype=np.intp
)
_EXTENDED_INDICES: npt.NDArray[np.intp] = np.arange(14, dtype=np.intp)


def _indices_to_mask(indices: npt.NDArray[np.intp]) -> npt.NDArray[np.bool_]:
    """Build a frozen length-14 boolean mask from an index array.

    Parameters
    ----------
    indices : np.ndarray of np.intp
        Indices into the 14-row ``core.aspects`` registry. Each index must
        satisfy ``0 <= i < 14`` (caller's responsibility to range-check).

    Returns
    -------
    np.ndarray of np.bool_, shape (14,)
        Boolean mask with True at the given positions. The returned array
        has ``writeable=False`` to prevent accidental mutation.
    """
    mask: npt.NDArray[np.bool_] = np.zeros(14, dtype=np.bool_)
    mask[indices] = True
    mask.flags.writeable = False  # Frozen — accidental mutation raises ValueError
    return mask


# Public preset constants — frozen length-14 bool masks
# CLASSICAL: 5 majors — 0 deg, 60 deg, 90 deg, 120 deg, 180 deg
CLASSICAL: npt.NDArray[np.bool_] = _indices_to_mask(_CLASSICAL_INDICES)
# TRADITIONAL: CLASSICAL + 30 deg (semi-sextile) + 150 deg (quincunx)
TRADITIONAL: npt.NDArray[np.bool_] = _indices_to_mask(_TRADITIONAL_INDICES)
# EXTENDED: all 14 aspects — legacy v1.0 default
EXTENDED: npt.NDArray[np.bool_] = _indices_to_mask(_EXTENDED_INDICES)

# Internal preset name registry (lowercase keys; resolver lowercases input).
_PRESET_BY_NAME: dict[str, npt.NDArray[np.bool_]] = {
    "classical": CLASSICAL,
    "traditional": TRADITIONAL,
    "extended": EXTENDED,
}

#: Type alias for the ``resolve_aspect_set`` input parameter.
AspectSetSpec = Union[None, str, Sequence[Union[str, int]], np.ndarray]


def resolve_aspect_set(
    spec: AspectSetSpec,
    default: npt.NDArray[np.bool_] = CLASSICAL,
) -> npt.NDArray[np.bool_]:
    """Resolve an aspect-set spec into a length-14 boolean mask.

    Single-call resolver: every public aspect API should call this exactly
    once at entry and pass the resulting mask down to hot loops. The mask
    indexes into :data:`ketu.core.aspects` (rows 0-13).

    ASP-06 forward-looking rule: no current LRU cache memoizes filtered
    aspect output, so this resolver does not need to be cached itself. If
    a future cache wraps a function whose return value depends on
    ``aspects=``, its key MUST include the resolved mask's bytes
    (``mask.tobytes()``) to prevent stale results across aspect sets.

    Parameters
    ----------
    spec : None, str, Sequence[str | int], or np.ndarray
        - ``None`` : use ``default`` (``CLASSICAL`` by default).
        - ``str`` : preset name (``"classical"``, ``"traditional"``,
          ``"extended"``) — case-insensitive.
        - ``Sequence[str]`` : aspect names matched against
          ``core.aspects["name"]`` (case-sensitive, exact bytes).
        - ``Sequence[int]`` : aspect indices in ``[0, 14)``.
        - ``np.ndarray[bool]`` of shape ``(14,)`` : passed through unchanged.
        - ``np.ndarray[int]`` : indices in ``[0, 14)``, converted to mask.
    default : np.ndarray of np.bool_, shape (14,), optional
        Mask returned when ``spec is None``. Defaults to
        :data:`CLASSICAL`. The default itself is a frozen array.

    Returns
    -------
    np.ndarray of np.bool_, shape (14,)
        Boolean mask selecting rows from ``core.aspects``.

    Raises
    ------
    ValueError
        If ``spec`` is an unknown preset name, contains an unknown aspect
        name, contains an out-of-range index, is a wrong-length boolean
        array, or contains an item of an invalid type.

    Examples
    --------
    >>> import numpy as np
    >>> from ketu.aspects.presets import resolve_aspect_set, CLASSICAL
    >>> np.array_equal(resolve_aspect_set(None), CLASSICAL)
    True
    >>> np.array_equal(resolve_aspect_set("classical"), CLASSICAL)
    True
    >>> resolve_aspect_set([0, 4, 7, 9, 13]).sum()
    5
    >>> resolve_aspect_set(["Conjunction", "Trine"]).sum()
    2
    """
    if spec is None:
        return default

    if isinstance(spec, str):
        key = spec.lower()
        if key not in _PRESET_BY_NAME:
            valid = ", ".join(_PRESET_BY_NAME)
            raise ValueError(
                f"unknown aspect preset: '{spec}'. Valid presets: {valid}"
            )
        return _PRESET_BY_NAME[key]

    if isinstance(spec, np.ndarray):
        if spec.dtype == np.bool_:
            if spec.shape != (14,):
                raise ValueError(
                    "boolean aspect mask must have shape (14,), "
                    f"got {spec.shape}"
                )
            return spec
        # Treat as int indices
        idx_array = np.asarray(spec, dtype=np.intp)
        if idx_array.ndim != 1:
            raise ValueError(
                f"integer aspect index array must be 1-D, got shape {spec.shape}"
            )
        for i in idx_array.tolist():
            if not 0 <= int(i) < 14:
                raise ValueError(
                    f"aspect index out of range: {int(i)} (valid: 0-13)"
                )
        return _indices_to_mask(idx_array)

    # Sequence (list/tuple) of strings or ints. Iterate manually so we
    # preserve canonical 0-13 order and detect bad item types.
    indices: list[int] = []
    for item in spec:
        # bool is a subclass of int in Python; reject explicitly to avoid
        # silently accepting [True, False, ...] as indices [1, 0, ...].
        if isinstance(item, bool):
            raise ValueError(
                f"invalid aspect spec item: {item!r} (expected str or int)"
            )
        if isinstance(item, str):
            idx = np.where(_ASPECTS["name"] == item.encode())[0]
            if len(idx) == 0:
                valid = ", ".join(a.decode() for a in _ASPECTS["name"])
                raise ValueError(
                    f"unknown aspect name: '{item}'. Valid aspects: {valid}"
                )
            indices.append(int(idx[0]))
        elif isinstance(item, (int, np.integer)):
            i = int(item)
            if not 0 <= i < 14:
                raise ValueError(
                    f"aspect index out of range: {i} (valid: 0-13)"
                )
            indices.append(i)
        else:
            raise ValueError(
                f"invalid aspect spec item: {item!r} (expected str or int)"
            )

    return _indices_to_mask(np.array(indices, dtype=np.intp))


__all__ = [
    "CLASSICAL",
    "TRADITIONAL",
    "EXTENDED",
    "AspectSetSpec",
    "resolve_aspect_set",
]
