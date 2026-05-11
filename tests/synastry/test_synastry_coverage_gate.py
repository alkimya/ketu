"""Sentinel test for the synastry_coverage_gate marker (Phase 16 SYN-05).

Ensures the marker registered in ``pyproject.toml``
``[tool.pytest.ini_options].markers`` is recognised by pytest (no
``PytestUnknownMarkWarning``) and that the :mod:`ketu.synastry` module
imports cleanly.

The 95% line-coverage threshold itself is enforced by the
``make synastry-coverage`` Makefile target (CI-mirrored), not by this
sentinel — this file only ratchets marker recognition + module import.
"""
from __future__ import annotations

import pytest


@pytest.mark.synastry_coverage_gate
def test_synastry_module_loads_and_marker_recognized() -> None:
    """Marker is registered; the synastry module imports cleanly.

    If pytest emits ``PytestUnknownMarkWarning`` for
    ``synastry_coverage_gate``, this test will still pass but the
    warning surfaces in CI / local runs as a regression signal that
    the marker entry was dropped from ``pyproject.toml``.
    """
    import ketu.synastry  # noqa: F401 — import is the assertion

    # Smoke-check the public surface so the test is meaningful even
    # without the marker.
    assert hasattr(ketu.synastry, "calculate_synastry")
    assert hasattr(ketu.synastry, "SYNASTRY_DTYPE")
