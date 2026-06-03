"""
Resolved-config header — CLI-06.

Emitted to STDERR (NOT stdout) so the byte-identical CLI-03 escape hatch
(`--harmonics all` matching v1.0 stdout) is preserved. Stdout = data,
stderr = diagnostics — standard Unix split.
"""
from __future__ import annotations

import sys
from typing import Optional

import numpy as np
import numpy.typing as npt

from ketu.core import aspects as _CORE_ASPECTS


def emit_resolved_config(
    mask: npt.NDArray[np.bool_] | None,
    preset_name: str | None,
    house_system: str | None = None,
    dynamic_label: Optional[str] = None,
) -> None:
    """
    Echo the resolved CLI configuration to STDERR.

    Parameters
    ----------
    mask : np.ndarray of np.bool_ or None
        Length-14 boolean mask selecting rows of ``ketu.core.aspects``.
        ``None`` means "no aspect filter applied" (e.g. ``ketu houses``
        with no aspects subcommand).
    preset_name : str or None
        Human-readable label for the aspect set (e.g. ``"classical"``,
        ``"all"``, or ``"custom"`` for explicit-list spec). ``None`` if
        no aspect command was invoked.
    house_system : str or None
        Selected house system (e.g. ``"placidus"``), or None if the
        command isn't house-related.
    dynamic_label : str or None, default None
        When provided, overrides the mask-derived detail string in the
        ``# Aspect set:`` header.  Used for ``h<N>`` harmonic tokens where
        the mask is all-False (which would otherwise emit ``(0 aspects: )``).
        Example: ``"3 aspects: H7-1 51°, H7-2 103°, H7-3 154°"``.
        When ``None``, the existing mask-iteration path is used unchanged
        (v1.1 byte-stable behaviour for all classical/traditional/extended
        invocations).

    Notes
    -----
    Format is intentionally simple, parseable line-by-line, and
    discoverable: every line starts with ``# `` so downstream tools
    can grep/strip with ``sed '/^# /d'``.
    """
    print("# Ketu v1.1.0", file=sys.stderr)
    if mask is not None and preset_name is not None:
        if dynamic_label is not None:
            # Override: bypass mask-iteration for h<N> harmonic selections.
            print(
                f"# Aspect set: {preset_name} ({dynamic_label})",
                file=sys.stderr,
            )
        else:
            names = [n.decode() if isinstance(n, bytes) else str(n)
                     for n in _CORE_ASPECTS["name"][mask]]
            angles = [int(a) for a in _CORE_ASPECTS["angle"][mask]]
            details = ", ".join(f"{name} {ang}°" for name, ang in zip(names, angles))
            print(
                f"# Aspect set: {preset_name} ({len(names)} aspects: {details})",
                file=sys.stderr,
            )
    if house_system is not None:
        print(f"# House system: {house_system}", file=sys.stderr)
