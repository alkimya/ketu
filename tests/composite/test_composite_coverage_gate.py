"""Sentinel test ratcheting the composite_coverage_gate pytest marker.

This file exists to ensure:
1. The ``composite_coverage_gate`` marker is registered in
   ``pyproject.toml [tool.pytest.ini_options].markers`` (no
   ``PytestUnknownMarkWarning`` under ``-W error``).
2. The ``ketu.composite`` module imports cleanly (sanity check for
   the coverage gate target).

Run via ``make composite-coverage`` for the full 95% gate sweep.
"""
from __future__ import annotations

import pytest


@pytest.mark.composite_coverage_gate
def test_composite_coverage_gate_marker_recognized() -> None:
    """Marker is registered in pyproject.toml; no warning under -W error.

    If pytest emits ``PytestUnknownMarkWarning`` for
    ``composite_coverage_gate``, this test will still pass but the
    warning surfaces in CI / local runs as a regression signal that
    the marker entry was dropped from ``pyproject.toml``.
    """
    # Marker recognition itself is asserted by the pytest collection step
    # under -W error::pytest.PytestUnknownMarkWarning (CI config).
    # This test body is a sanity import + a single assertion that the
    # module surface is in place.
    import ketu.composite as composite

    assert hasattr(composite, "calculate_composite")
    assert hasattr(composite, "circular_midpoint")
    assert "calculate_composite" in composite.__all__
    assert "circular_midpoint" in composite.__all__
