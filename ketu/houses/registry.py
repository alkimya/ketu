"""
Registry pattern for house systems.

Plans 10-04 (Placidus) and 10-05 (Koch + Porphyry) register their
implementations via the :func:`register` decorator. New house systems plug in
without modifying :func:`calculate_houses` dispatch — that's HOU-02.

Plan 10-03 leaves :data:`SYSTEMS` empty; downstream plans populate it.
The dispatch helper :func:`get_system` provides a uniform error message
("ValueError with received value + valid options") consistent with the
broader Ketu error-message convention.

Examples
--------
A custom system can be registered without touching this module:

>>> import numpy as np
>>> from ketu.houses.registry import register, SYSTEMS
>>> @register("equal")
... def equal_cusps(armc: np.ndarray, lat: np.ndarray, eps: np.ndarray) -> np.ndarray:
...     return np.stack([(armc + 30 * i) % 360 for i in range(12)], axis=-1)
>>> "equal" in SYSTEMS
True
"""
from __future__ import annotations

from typing import Callable

import numpy as np

# Signature contract: (armc, lat, eps) -> cusps array of shape (..., 12),
# where leading dims of armc/lat/eps are broadcast together. Plans 10-04 / 10-05
# implementations conform to this signature; calculate_houses dispatch in
# Plan 10-06 will broadcast inputs before calling the registered function.
HouseSystemFn = Callable[[np.ndarray, np.ndarray, np.ndarray], np.ndarray]

#: Registry of house-system implementations.
#:
#: Keys are lowercase system names (str); values are callables conforming
#: to :data:`HouseSystemFn`. Populated lazily via :func:`register`. Empty at
#: import time of Plan 10-03; Plans 10-04/10-05 add entries on import.
SYSTEMS: dict[str, HouseSystemFn] = {}


def register(name: str) -> Callable[[HouseSystemFn], HouseSystemFn]:
    """
    Decorator that registers a house-system implementation in :data:`SYSTEMS`.

    The registered name is normalized to lowercase, so registration and
    lookup are case-insensitive.

    Parameters
    ----------
    name : str
        Public name (case-insensitive; stored lowercase). Examples:
        ``"placidus"``, ``"koch"``, ``"porphyry"``.

    Returns
    -------
    Callable[[HouseSystemFn], HouseSystemFn]
        A decorator that wraps a function with signature
        ``(armc, lat, eps) -> cusps[..., 12]`` and inserts it into
        :data:`SYSTEMS`. The decorated function is returned unchanged so
        it remains directly callable.

    Examples
    --------
    >>> import numpy as np
    >>> @register("noop")
    ... def noop(armc: np.ndarray, lat: np.ndarray, eps: np.ndarray) -> np.ndarray:
    ...     return np.zeros(armc.shape + (12,))
    >>> "noop" in SYSTEMS
    True
    """
    key = name.lower()

    def _wrap(fn: HouseSystemFn) -> HouseSystemFn:
        SYSTEMS[key] = fn
        return fn

    return _wrap


def get_system(name: str) -> HouseSystemFn:
    """
    Look up a house system by name (case-insensitive).

    Parameters
    ----------
    name : str
        System name; lookup is case-insensitive.

    Returns
    -------
    HouseSystemFn
        The registered implementation.

    Raises
    ------
    ValueError
        If ``name`` is not registered. Error message includes the received
        value and the sorted list of available systems (per Ketu convention).
    """
    key = name.lower()
    if key not in SYSTEMS:
        available = sorted(SYSTEMS.keys())
        raise ValueError(
            f"unknown house system {name!r}; available: {available}"
        )
    return SYSTEMS[key]
