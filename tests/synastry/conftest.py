"""Phase-16 synastry test fixtures.

Provides synastry-specific oracle fixtures for :func:`oracle_fixture`
parametrization. The six ``chart_*`` CHART_DTYPE session fixtures
(``chart_a_paris``, ``chart_b_reykjavik``, etc.) have been moved to the
root ``tests/conftest.py`` (REF-03, Phase 22 ephemeris refactor) and are
discovered automatically by pytest without any import here.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest


_FIXTURES_DIR = Path(__file__).parent / "fixtures"

#: Oracle fixture slugs in canonical alphabetical order (single source of
#: truth for :func:`oracle_fixture` parametrization).
ORACLE_SLUGS = ["curie", "diana_charles", "lennon_ono"]


def load_oracle_fixture(slug: str) -> dict:
    """Load a synastry oracle fixture by slug from ``tests/synastry/fixtures/``.

    Parameters
    ----------
    slug : str
        Fixture slug, one of :data:`ORACLE_SLUGS` (e.g. ``'curie'``,
        ``'diana_charles'``, ``'lennon_ono'``).

    Returns
    -------
    dict
        Parsed JSON fixture with mandatory keys ``schema_version``,
        ``name``, ``rodden_a``, ``rodden_b``, ``chart_a``, ``chart_b``,
        ``expected_aspects``, ``validation_source``, ``tolerance_deg``.

    Raises
    ------
    FileNotFoundError
        If ``tests/synastry/fixtures/oracle_{slug}.json`` does not exist.
    """
    path = _FIXTURES_DIR / f"oracle_{slug}.json"
    with path.open() as fh:
        result: dict = json.load(fh)
    return result


@pytest.fixture(params=ORACLE_SLUGS, ids=ORACLE_SLUGS)
def oracle_fixture(request: pytest.FixtureRequest) -> dict:
    """Yield each oracle fixture in turn, parametrized over the 3 couples.

    Drives :mod:`tests.synastry.test_oracle` — one test invocation per
    fixture slug. The fixture dict is loaded fresh per parameter to avoid
    accidental cross-test mutation.

    Parameters
    ----------
    request : pytest.FixtureRequest
        Pytest's fixture-request handle; ``request.param`` is one of
        :data:`ORACLE_SLUGS`.

    Returns
    -------
    dict
        Parsed JSON oracle fixture for the current slug, as returned by
        :func:`load_oracle_fixture`.
    """
    return load_oracle_fixture(request.param)
