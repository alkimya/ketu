"""Test infrastructure for ``tests/charts/``.

Re-exports the houses oracle fixtures so chart-level tests can validate the
inline houses portion of :data:`CHART_DTYPE` against the same Swiss
Ephemeris reference used by :mod:`tests.houses`. The chart-level tests do
not introduce a *new* swisseph oracle: ``compute_chart`` delegates to
:func:`ketu.houses.calculate_houses` for its houses block, so reusing the
houses oracle directly is the cleanest cross-check (D-03 inline houses).

``swisseph`` is a test-only AGPL-licensed dep — :func:`pytest.importorskip`
gates the entire ``tests/charts/`` directory the same way it gates
``tests/houses/``. Same numpy-before-swisseph import discipline as
``tests/houses/conftest.py:32-60`` (see that conftest's docstring for the
``_NoValueType`` rationale).

Public surface (consumed by Plans 14-02..05):

- :data:`SYSTEM_BYTES` — re-export of ``tests.houses.conftest.SYSTEM_BYTES``.
- :func:`swe_oracle` — re-export of the houses oracle helper.
- ``reference_charts`` — pytest fixture (re-exported).
- ``loaded_reference_snapshot`` — pytest fixture (re-exported).
"""
from __future__ import annotations

# IMPORTANT: numpy MUST be imported BEFORE swisseph (see
# tests/houses/conftest.py:32-43 for the ``_NoValueType`` rationale).
import numpy as np  # noqa: F401  (kept first for import-order discipline)
import pytest

pytest.importorskip("swisseph")
import swisseph as swe  # noqa: F401, E402  (after importorskip per project convention)

# Re-export the houses oracle fixtures verbatim. Pytest discovers fixtures
# in any conftest.py up the directory tree; importing them at the
# tests/charts/ scope makes them available without redefinition.
from tests.houses.conftest import (  # noqa: F401, E402
    SYSTEM_BYTES,
    loaded_reference_snapshot,
    reference_charts,
    swe_oracle,
)
