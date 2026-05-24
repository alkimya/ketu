"""Sentinel test ratcheting the returns_coverage_gate pytest marker.

This file exists to ensure:
1. The ``returns_coverage_gate`` marker is registered in
   ``pyproject.toml [tool.pytest.ini_options].markers`` (no
   ``PytestUnknownMarkWarning`` under ``-W error``).
2. The ``ketu.returns`` module imports cleanly (sanity check for
   the coverage gate target).

Run via ``make returns-coverage`` for the full 95% gate sweep (the
gate is not binding until Plan 18-05 close-out — it will report
partial coverage during Plans 18-02 / 18-03 / 18-04 implementation).
"""
from __future__ import annotations

import pytest


@pytest.mark.returns_coverage_gate
def test_returns_coverage_gate_marker_recognized() -> None:
    """Marker is registered in pyproject.toml; no warning under -W error.

    Module import sanity check (the eventual ``solar_return`` and
    ``lunar_return`` public surface lands in Plans 18-02 and 18-03 —
    this test ratchets the marker registration plus the module
    skeleton import).
    """
    import ketu.returns as returns

    # __all__ is empty in Plan 18-01; extended in 18-02 (solar_return) and 18-03 (lunar_return):
    assert isinstance(returns.__all__, list)
    # Module docstring carries the LOUD guard clauses from Plan 18-01:
    assert "API asymmetry" in returns.__doc__
    assert "UTC-only contract" in returns.__doc__
