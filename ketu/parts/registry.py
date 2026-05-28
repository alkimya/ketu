"""
Registry pattern for Arabic Parts (Hermetic Lots).

Analogous to :mod:`ketu.houses.registry`: a :class:`PartSpec` frozen
dataclass replaces the bare :data:`ketu.houses.registry.HouseSystemFn`
callable because a part carries TWO callables — one for day charts and
one for night charts.  New Lots plug in with a single :func:`register`
call; no dispatch logic needs to change (PARTS-01, PARTS-02).

:data:`PARTS` is populated at import time of :mod:`ketu.parts` via
:func:`register` calls in :mod:`ketu.parts.__init__`.  It is empty when
this module is first imported in isolation.

See Also
--------
ketu.parts.__init__ : Trigger-import that registers the 3 built-in parts.
ketu.parts.api.calculate_part : Dispatch helper that calls
    ``spec.day_formula`` or ``spec.night_formula`` based on sect.

Examples
--------
Registering a custom part without touching dispatch:

>>> from ketu.parts.registry import register, get_part
>>> register(
...     "my_lot",
...     day_formula=lambda asc, sun, moon, venus: (asc + moon - venus) % 360.0,
...     night_formula=lambda asc, sun, moon, venus: (asc + sun - venus) % 360.0,
...     description="custom lot for demonstration",
... )
>>> spec = get_part("my_lot")
>>> spec.name
'my_lot'
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

#: Formula signature contract: ``(asc_lon, sun_lon, moon_lon, venus_lon) -> longitude in [0, 360)``.
#:
#: All four values are always passed; a formula that does not use an arg
#: simply ignores it.  This concrete 4-arg signature (NOT an abstract
#: ``body_lons`` dict) keeps each formula self-documenting and
#: argument-explicit (RESEARCH Q1/Q3).
PartFormula = Callable[[float, float, float, float], float]


@dataclass(frozen=True)
class PartSpec:
    """
    Immutable specification for one Arabic Part / Hermetic Lot.

    Attributes
    ----------
    name : str
        Lowercase canonical name (e.g. ``"fortune"``).
    day_formula : PartFormula
        Callable ``(asc, sun, moon, venus) -> float`` applied for day charts.
    night_formula : PartFormula
        Callable ``(asc, sun, moon, venus) -> float`` applied for night
        charts.  Set equal to ``day_formula`` for sect-invariant parts
        (e.g. Marriage) — no ``sect_aware`` flag is needed: dispatch is
        always ``spec.day_formula if is_day else spec.night_formula``.
    description : str
        Human-readable description for ``--list-parts`` output and docs.
        Defaults to an empty string.
    """

    name: str
    day_formula: PartFormula
    night_formula: PartFormula
    description: str = ""


#: Registry of Arabic Part implementations.
#:
#: Keys are lowercase names (``str``); values are :class:`PartSpec` instances.
#: Populated at import time of :mod:`ketu.parts` via :func:`register`.
#: Analogue of :data:`ketu.houses.registry.SYSTEMS`.
#:
#: Empty when this module is imported in isolation; :mod:`ketu.parts.__init__`
#: triggers registration of the 3 built-in parts (RESEARCH Pitfall 2).
PARTS: dict[str, PartSpec] = {}


def register(
    name: str,
    *,
    day_formula: PartFormula,
    night_formula: PartFormula,
    description: str = "",
) -> None:
    """
    Register a new Arabic Part in :data:`PARTS`.

    Unlike :func:`ketu.houses.registry.register` which is a decorator
    (one function per system), this is a plain keyword-only function call
    because a :class:`PartSpec` carries *two* callables.  A v1.3 Lot is
    therefore one ``register(...)`` call with no dispatch change (PARTS-01).

    Parameters
    ----------
    name : str
        Canonical name (case-insensitive; stored lowercase).
        Examples: ``"fortune"``, ``"spirit"``, ``"marriage"``.
    day_formula : PartFormula
        Callable ``(asc_lon, sun_lon, moon_lon, venus_lon) -> float``
        for day charts.  Must return a longitude in ``[0, 360)``.
    night_formula : PartFormula
        Callable with the same signature for night charts.  Pass the
        *same* object as ``day_formula`` for sect-invariant parts.
    description : str, optional
        Human-readable label (used by ``--list-parts`` output).

    Examples
    --------
    >>> register(
    ...     "example",
    ...     day_formula=lambda asc, sun, moon, venus: (asc + moon - sun) % 360.0,
    ...     night_formula=lambda asc, sun, moon, venus: (asc + sun - moon) % 360.0,
    ...     description="example part",
    ... )
    >>> "example" in PARTS
    True
    """
    PARTS[name.lower()] = PartSpec(
        name=name.lower(),
        day_formula=day_formula,
        night_formula=night_formula,
        description=description,
    )


def get_part(name: str) -> PartSpec:
    """
    Look up an Arabic Part by name (case-insensitive).

    Parameters
    ----------
    name : str
        Part name; lookup is case-insensitive (stored lowercase).

    Returns
    -------
    PartSpec
        The registered specification.

    Raises
    ------
    ValueError
        If ``name`` is not registered.  Error message includes the
        received value and the sorted list of available parts (per Ketu
        error-message convention — mirrors :func:`ketu.houses.registry.get_system`).

    Examples
    --------
    >>> spec = get_part("fortune")  # doctest: +SKIP
    >>> spec.name
    'fortune'
    >>> get_part("nope")  # doctest: +SKIP
    Traceback (most recent call last):
        ...
    ValueError: unknown part 'nope'; available: ['fortune', 'marriage', 'spirit']
    """
    key = name.lower()
    if key not in PARTS:
        available = sorted(PARTS.keys())
        raise ValueError(f"unknown part {name!r}; available: {available}")
    return PARTS[key]
