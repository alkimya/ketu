"""Returns subpackage test fixtures.

Session-scoped natal fixtures (``natal_diana``, ``natal_charles``,
``natal_marie_curie``, ``natal_pierre_curie``, ``natal_lennon``,
``natal_ono``) have been moved to the root ``tests/conftest.py``
(REF-03, Phase 22 ephemeris refactor) and are discovered automatically
by pytest. No subpackage-specific fixtures are needed here.
"""
from __future__ import annotations
