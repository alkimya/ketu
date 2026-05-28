"""Sentinel test ratcheting the parts_coverage_gate pytest marker.

This file exists to ensure:
1. The ``parts_coverage_gate`` marker is registered in
   ``pyproject.toml [tool.pytest.ini_options].markers`` (no
   ``PytestUnknownMarkWarning`` under ``-W error``).
2. The ``ketu.parts`` module imports cleanly and exposes its public
   ``__all__`` list (sanity check for the coverage gate target).

Run via ``make parts-coverage`` for the full >=95% gate sweep
(mirror of ``make returns-coverage`` / ``make composite-coverage``,
both two-step patterns that avoid the NumPy ``_NoValueType`` reload
bug from sub-package source narrowing).
"""
from __future__ import annotations

import pytest


@pytest.mark.parts_coverage_gate
def test_parts_coverage_gate_marker_recognized() -> None:
    """Marker is registered in pyproject.toml; no warning under -W error.

    Imports ketu.parts and asserts the 3 built-in entries are registered
    plus that __all__ is a list (the public API surface ratchet).
    """
    import ketu.parts as parts

    # 3 built-in parts registered at import time (PARTS-01).
    assert len(parts.PARTS) == 3, (
        f"Expected 3 built-in parts, got {len(parts.PARTS)}: "
        f"{sorted(parts.PARTS.keys())}"
    )
    # __all__ is a list (public API surface contract).
    assert isinstance(parts.__all__, list), (
        f"ketu.parts.__all__ must be a list, got {type(parts.__all__)}"
    )
