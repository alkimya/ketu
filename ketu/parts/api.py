"""
Sect-aware dispatch for Arabic Parts: :func:`calculate_part` + :func:`calculate_all_parts`.

Both functions take a scalar :data:`ketu.charts.CHART_DTYPE` record (produced
by :func:`ketu.charts.compute_chart`) and delegate formula selection to the
:data:`ketu.parts.registry.PARTS` registry.  No if/elif dispatch ladder —
the registry IS the dispatch mechanism (PARTS-03, PARTS-04).

See Also
--------
ketu.parts.registry.get_part : Registry lookup; raises ValueError on unknown name.
ketu.charts.api.is_day_chart : Sect helper called fresh per chart (D-12 — not
    stored in CHART_DTYPE to avoid double source-of-truth).
ketu.parts.__init__ : Public re-export surface.
"""
from __future__ import annotations

from typing import Optional

import numpy as np

from ketu.charts.api import is_day_chart

from .registry import PARTS, get_part


def calculate_part(part_name: str, chart: np.ndarray) -> float:
    """
    Return the ecliptic longitude of one Arabic Part for a given chart.

    Sect (day vs night) is determined fresh from the chart's ``jd``,
    ``lat``, ``lon`` fields via :func:`ketu.charts.api.is_day_chart`
    (D-12: sect is never stored in :data:`ketu.charts.CHART_DTYPE`).
    Formula selection is a pure registry lookup — no if/elif ladder.

    Parameters
    ----------
    part_name : str
        Case-insensitive name of the Arabic Part (e.g. ``"fortune"``,
        ``"Fortune"``).  Delegated to :func:`ketu.parts.registry.get_part`
        which normalises to lowercase.
    chart : np.ndarray
        Scalar (0-d or shape ``()``) structured array of
        :data:`ketu.charts.CHART_DTYPE`.  Must contain fields ``jd``,
        ``lat``, ``lon``, ``asc``, and ``body_lons``.  Produced by
        :func:`ketu.charts.compute_chart`.

    Returns
    -------
    float
        Ecliptic longitude of the part in ``[0, 360)``.

    Raises
    ------
    ValueError
        Propagated from :func:`ketu.parts.registry.get_part` when
        ``part_name`` is not registered.

    See Also
    --------
    ketu.parts.calculate_all_parts : Compute all (or a filtered subset of)
        registered parts in one call.
    ketu.parts.registry.PartSpec : The spec whose ``day_formula`` /
        ``night_formula`` is selected here.

    Notes
    -----
    **Accuracy vs Swiss Ephemeris.** Arabic Part longitudes depend on
    body longitudes from :func:`ketu.charts.compute_chart` (±0.1°
    inner planets, ±0.5° outer) plus the Ascendant (±0.01°). The
    resulting Part longitude is accurate to approximately ±0.2° for
    Fortune/Spirit (Sun/Moon-based) and ±0.5° for parts that include
    outer planets. Swiss-based tools may differ by a similar margin.

    **Supported date range.** 1800–2200 CE (inherits from the
    underlying ephemeris). Accuracy degrades outside this range.

    **Sect edge cases.** Sect is re-evaluated fresh from ``(jd, lat,
    lon)`` via :func:`ketu.charts.api.is_day_chart` each call (D-12).
    At exact sunrise/sunset (Sun on ASC/DESC), the sunrise-inclusive
    convention applies: Sun exactly on ASC → day chart. Callers
    relocating the chart (non-natal ``lat``/``lon``) will get the
    correct sect for the relocation.

    Body-axis indices are FROZEN per decision D-08
    (``body_lons[0]`` = Sun, ``body_lons[1]`` = Moon,
    ``body_lons[3]`` = Venus).  A v1.3 grow-the-axis change would require
    updating these constants.

    Examples
    --------
    >>> import numpy as np
    >>> from ketu.charts import compute_chart
    >>> from ketu.parts import calculate_part
    >>> chart = compute_chart(2451545.0, 48.8566, 2.3522)
    >>> 0.0 <= calculate_part("fortune", chart) < 360.0
    True
    """
    spec = get_part(part_name)
    # D-12: sect is NOT stored in CHART_DTYPE — call is_day_chart fresh
    # from jd/lat/lon.  is_day_chart returns a 0-d np.ndarray for scalar
    # input; bool() unwraps it.
    is_day = bool(is_day_chart(float(chart["jd"]), float(chart["lat"]), float(chart["lon"])))
    formula = spec.day_formula if is_day else spec.night_formula
    asc   = float(chart["asc"])
    sun   = float(chart["body_lons"][0])   # body axis FROZEN (D-08): 0=Sun
    moon  = float(chart["body_lons"][1])   # 1=Moon
    venus = float(chart["body_lons"][3])   # 3=Venus
    return float(formula(asc, sun, moon, venus))


def calculate_all_parts(
    chart: np.ndarray,
    parts: Optional[list[str]] = None,
) -> dict[str, float]:
    """
    Return ecliptic longitudes for all (or a filtered subset of) Arabic Parts.

    Iterates over the registered parts and delegates each to
    :func:`calculate_part`.  Default iteration order is
    ``sorted(PARTS.keys())`` (alphabetical), ensuring deterministic output
    for ML pipelines and oracle tests (RESEARCH Pitfall 5).

    Parameters
    ----------
    chart : np.ndarray
        Scalar structured array of :data:`ketu.charts.CHART_DTYPE`.
        Passed through unchanged to :func:`calculate_part` for each part.
    parts : list of str, optional
        Explicit list of part names to compute.  When ``None`` (default),
        all registered parts are computed in alphabetical order.
        Names are case-insensitive (delegated to
        :func:`ketu.parts.registry.get_part`).

    Returns
    -------
    dict of str to float
        Mapping ``{part_name: longitude_in_0_360}`` for the requested
        parts.  Keys are the **input** names (lowercased by
        :func:`ketu.parts.registry.get_part` internally).

    Raises
    ------
    ValueError
        Propagated from :func:`calculate_part` / :func:`ketu.parts.registry.get_part`
        if any name in ``parts`` is not registered.

    See Also
    --------
    ketu.parts.calculate_part : Single-part computation; called for each name.
    ketu.parts.registry.PARTS : The registry iterated when ``parts=None``.

    Notes
    -----
    **Accuracy vs Swiss Ephemeris.** Inherits from
    :func:`calculate_part` — see its Notes block for per-body error
    budgets. Results are deterministic for fixed ``(jd, lat, lon)``.

    **Supported date range.** 1800–2200 CE. Degrades outside this
    range along with the underlying ephemeris.

    **Edge cases.** Passing an empty ``parts=[]`` returns an empty
    dict. Case-insensitive part names are normalised to lowercase in
    the returned dict keys (via :func:`ketu.parts.registry.get_part`).
    All three built-in parts (fortune, spirit, marriage) use
    sect-symmetric formulas; marriage is the same formula for day and
    night charts.

    Examples
    --------
    >>> import numpy as np
    >>> from ketu.charts import compute_chart
    >>> from ketu.parts import calculate_all_parts
    >>> chart = compute_chart(2451545.0, 48.8566, 2.3522)
    >>> result = calculate_all_parts(chart)
    >>> sorted(result.keys())
    ['fortune', 'marriage', 'spirit']
    >>> result2 = calculate_all_parts(chart, parts=["fortune"])
    >>> list(result2.keys())
    ['fortune']
    """
    names = parts if parts is not None else sorted(PARTS.keys())
    return {name: calculate_part(name, chart) for name in names}
