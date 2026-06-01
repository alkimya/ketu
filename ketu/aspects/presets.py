"""
Aspect set presets and resolver for configurable aspect filtering.

Four named presets select subsets of the 14 aspects in :mod:`ketu.core.aspects`:

- ``CLASSICAL`` — 5 majors (conjunction, sextile, square, trine, opposition).
  A curated index-based preset (NOT harmonic-derived; keeps Sextile H3 but
  drops Semi-sextile/Quincunx H6).
- ``TRADITIONAL`` — 7 half-circle aspects (harmonics 1, 2, 3, 6). Harmonic-derived
  from the ``core.aspects["harmonic"]`` column. This is the library default for
  ``resolve_aspect_set(None)``.
- ``EXTENDED`` — 14 aspects (all harmonics 1,2,3,5,6,9,10). Harmonic-derived.
  Legacy v1.0 behaviour; all aspects including full-circle minors (H5/H9/H10).

``TRADITIONAL`` and ``EXTENDED`` are redefined on top of the harmonic table
(single source of truth via :func:`aspects_for_harmonics`). ``CLASSICAL``
stays a curated 5-aspect index list.

``aspects_for_harmonics(harmonics)`` builds a frozen length-14 ``np.bool_``
mask from a list of harmonic numbers, using the ``core.aspects["harmonic"]``
column. Valid harmonics: ``{1, 2, 3, 5, 6, 9, 10}`` (derived data-driven
from the table). Use this API to compose custom aspect sets without
hard-coding indices.

Each preset is a length-14 ``np.bool_`` array indexable into ``core.aspects``.
The row order is canonical and append-only (Phase 9 invariant)::

    0=Conjunction, 1=Semi-sextile, 2=Decile, 3=Novile, 4=Sextile,
    5=Quintile, 6=Binovile, 7=Square, 8=Tredecile, 9=Trine,
    10=Biquintile, 11=Quincunx, 12=Quadrinovile, 13=Opposition

Notes
-----
Public API: ``CLASSICAL``, ``TRADITIONAL``, ``EXTENDED`` are frozen
length-14 ``np.bool_`` masks. ``AspectSetSpec`` is the type alias for
the resolver input. ``resolve_aspect_set`` is the single-call resolver
that returns a length-14 mask. ``aspects_for_harmonics`` composes a mask
from harmonic numbers.

The default for ``resolve_aspect_set(None)`` is the 7 half-circle set
(``TRADITIONAL``, harmonics 1/2/3/6). The CLI bare ``--harmonics``
default stays ``"classical"`` (5 aspects) for v1.0/v1.1 byte-stability.

ASP-06 forward-looking rule: no current LRU cache
(``ketu.calculations:body_properties``,
``ketu.aspects.core:_cached_planet_position_batch``) materializes filtered
aspect output, so cache keys today do NOT need to include the aspect-set
hash. If a future cache memoizes a function whose return value depends on
``aspects=``, its key MUST include ``mask.tobytes()`` (or equivalent) to
avoid stale results across different aspect sets.
See Phase 9 RESEARCH.md, Pitfall 4.
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

# Valid harmonic numbers — derived data-driven from the table so this stays
# correct if the table changes. Yields {1, 2, 3, 5, 6, 9, 10} for the
# current 14-aspect layout (Phase 26 harmonic column).
_VALID_HARMONICS: frozenset[int] = frozenset(int(h) for h in _ASPECTS["harmonic"])

# Preset masks: length-14 np.bool_ arrays selecting rows of core.aspects.
# Indices follow ketu/core.py row order:
#   0=Conjunction, 1=Semi-sextile, 2=Decile, 3=Novile, 4=Sextile,
#   5=Quintile, 6=Binovile, 7=Square, 8=Tredecile, 9=Trine,
#   10=Biquintile, 11=Quincunx, 12=Quadrinovile, 13=Opposition
_CLASSICAL_INDICES: npt.NDArray[np.intp] = np.array(
    [0, 4, 7, 9, 13], dtype=np.intp
)


def _indices_to_mask(indices: npt.NDArray[np.intp]) -> npt.NDArray[np.bool_]:
    """
    Build a frozen length-14 boolean mask from an index array.

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
# CLASSICAL: 5 majors (curated index list — NOT harmonic-derived).
# Keeps Sextile (H3) but drops Semi-sextile/Quincunx (H6); CLASSICAL is
# therefore not a pure harmonic set and cannot be produced by
# aspects_for_harmonics. Leave it as a curated index list (Pitfall 7).
CLASSICAL: npt.NDArray[np.bool_] = _indices_to_mask(_CLASSICAL_INDICES)

def aspects_for_harmonics(
    harmonics: Sequence[int],
) -> npt.NDArray[np.bool_]:
    """
    Build a frozen length-14 boolean mask from a list of harmonic numbers.

    Selects all rows of :data:`ketu.core.aspects` whose ``"harmonic"`` field
    equals one of the requested harmonic numbers. The result is a drop-in
    replacement for any preset constant: same shape ``(14,)``, same dtype
    ``np.bool_``, same frozen contract (``writeable=False``).

    Valid harmonics are derived data-driven from the table:
    ``{1, 2, 3, 5, 6, 9, 10}`` for the current 14-aspect layout.
    Requesting an unknown harmonic (e.g. ``7``) raises :exc:`ValueError`
    with the list of valid harmonics.

    ``bool`` items are rejected explicitly (``bool`` is a subclass of ``int``
    in Python); passing ``[True, False, ...]`` would silently be treated as
    ``[1, 0, ...]`` without this guard.

    Parameters
    ----------
    harmonics : Sequence[int]
        List (or any sequence) of harmonic numbers to include. May be empty
        (returns an all-False frozen mask). Duplicates are allowed and
        collapsed automatically by ``np.isin``.

    Returns
    -------
    np.ndarray of np.bool_, shape (14,)
        Frozen boolean mask. ``mask[i]`` is ``True`` when
        ``core.aspects["harmonic"][i]`` is in ``harmonics``.

    Raises
    ------
    ValueError
        If any item is not an ``int`` (including ``bool``), or if any
        integer is not in the valid-harmonic set.

    Examples
    --------
    >>> int(aspects_for_harmonics([1, 2, 3, 6]).sum())
    7
    >>> int(aspects_for_harmonics([5, 9, 10]).sum())
    7
    >>> int(aspects_for_harmonics([1]).sum())
    2
    """
    requested: list[int] = []
    for item in harmonics:
        # bool is a subclass of int in Python; reject explicitly to avoid
        # silently accepting [True, False, ...] as harmonic numbers [1, 0, ...].
        if isinstance(item, bool):
            raise ValueError(
                f"invalid harmonic {item!r} (expected int, got bool)"
            )
        if not isinstance(item, (int, np.integer)):
            raise ValueError(
                f"invalid harmonic {item!r} (expected int)"
            )
        h = int(item)
        if h not in _VALID_HARMONICS:
            valid_str = ", ".join(str(v) for v in sorted(_VALID_HARMONICS))
            raise ValueError(
                f"unknown harmonic: {h}. Valid harmonics: {valid_str}"
            )
        requested.append(h)

    # Build mask via field access — data-driven, stays correct if table grows.
    raw_mask = np.isin(_ASPECTS["harmonic"], requested)
    indices = np.nonzero(raw_mask)[0].astype(np.intp)
    return _indices_to_mask(indices)


# TRADITIONAL and EXTENDED are harmonic-derived (single source of truth).
# TRADITIONAL: 7 half-circle aspects — harmonics 1 (0°/180°), 2 (90°),
#   3 (60°/120°), 6 (30°/150°). Bit-identical to the former index-based
#   _TRADITIONAL_INDICES = [0, 1, 4, 7, 9, 11, 13].
# EXTENDED: all 14 aspects — harmonics 1,2,3,5,6,9,10 (all values in table).
#   Bit-identical to the former np.arange(14).
TRADITIONAL: npt.NDArray[np.bool_] = aspects_for_harmonics([1, 2, 3, 6])
EXTENDED: npt.NDArray[np.bool_] = aspects_for_harmonics([1, 2, 3, 5, 6, 9, 10])

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
    default: npt.NDArray[np.bool_] = TRADITIONAL,
) -> npt.NDArray[np.bool_]:
    """
    Resolve an aspect-set spec into a length-14 boolean mask.

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
        - ``None`` : use ``default`` (the 7 half-circle set, ``TRADITIONAL``,
          by default — harmonics 1/2/3/6).
        - ``str`` : preset name (``"classical"``, ``"traditional"``,
          ``"extended"``) — case-insensitive.
        - ``Sequence[str]`` : aspect names matched against
          ``core.aspects["name"]`` (case-sensitive, exact bytes).
        - ``Sequence[int]`` : aspect indices in ``[0, 14)``.
        - ``np.ndarray[bool]`` of shape ``(14,)`` : passed through unchanged.
        - ``np.ndarray[int]`` : indices in ``[0, 14)``, converted to mask.
    default : np.ndarray of np.bool_, shape (14,), optional
        Mask returned when ``spec is None``. Defaults to
        :data:`TRADITIONAL` (the 7 half-circle aspects). The default
        itself is a frozen array.

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
    >>> from ketu.aspects.presets import resolve_aspect_set, TRADITIONAL
    >>> np.array_equal(resolve_aspect_set(None), TRADITIONAL)
    True
    >>> from ketu.aspects.presets import CLASSICAL
    >>> np.array_equal(resolve_aspect_set("classical"), CLASSICAL)
    True
    >>> int(resolve_aspect_set([0, 4, 7, 9, 13]).sum())
    5
    >>> int(resolve_aspect_set(["Conjunction", "Trine"]).sum())
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
    "aspects_for_harmonics",
    "resolve_aspect_set",
]
