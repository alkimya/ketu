"""ISO 8601 date parsing for the CLI.

Two responsibilities, both delegating to standard library + existing Ketu
helpers:

1. Parse the ``--date ISO`` argument into a timezone-aware UTC datetime.
2. Convert that datetime into a Julian Date via
   :func:`ketu.ephemeris.time.utc_to_julian`.

The trailing ``Z`` suffix is handled defensively for Python 3.10 (where
``datetime.fromisoformat`` rejects ``Z``; Python 3.11+ accepts it
natively; see :ref:`What's New in Python 3.11`).
"""
from __future__ import annotations

from datetime import datetime, timezone

from ketu.ephemeris.time import utc_to_julian


def parse_iso_utc(value: str) -> float:
    """Parse an ISO-8601 datetime string and return its Julian Date.

    Parameters
    ----------
    value : str
        ISO-8601 datetime, e.g. ``"2026-05-06T12:00:00Z"`` or
        ``"2026-05-06T12:00:00+00:00"``. Naive datetimes (no offset)
        are assumed to be UTC.

    Returns
    -------
    float
        Julian Date (UTC), via :func:`ketu.ephemeris.time.utc_to_julian`.

    Raises
    ------
    SystemExit
        If the input is not a valid ISO-8601 datetime. Raises with a
        helpful message; argparse-friendly.

    Notes
    -----
    Python 3.10 trap: ``datetime.fromisoformat("2026-05-06T12:00:00Z")``
    raises ``ValueError`` on 3.10 (only accepts ``+00:00``). 3.11+
    accepts ``Z`` natively. We unconditionally replace trailing ``Z``
    with ``+00:00`` before parsing — works on both.
    """
    if not isinstance(value, str) or not value.strip():
        raise SystemExit(
            f"error: --date {value!r} is empty or not a string"
        )
    s = value.strip()
    # Python 3.10 'Z' shim: replace trailing Z with +00:00 BEFORE parsing.
    # Idempotent on Python 3.11+ (which accepts Z natively).
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(s)
    except ValueError as e:
        raise SystemExit(
            f"error: --date {value!r} is not a valid ISO-8601 datetime "
            f"(expected e.g. '2026-05-06T12:00:00Z' or "
            f"'2026-05-06T12:00:00+00:00'); {e}"
        )
    if dt.tzinfo is None:
        # Naive datetime → assume UTC (matches utc_to_julian's convention).
        dt = dt.replace(tzinfo=timezone.utc)
    # Convert to UTC explicitly (in case of non-UTC offset).
    dt_utc = dt.astimezone(timezone.utc)
    return utc_to_julian(dt_utc)
