"""Composite test fixtures.

Provides composite-specific oracle fixtures for :func:`oracle_fixture`
parametrization. The six ``chart_*`` CHART_DTYPE session fixtures
(``chart_a_paris``, ``chart_b_reykjavik``, etc.) have been moved to the
root ``tests/conftest.py`` (REF-03, Phase 22 ephemeris refactor) and are
discovered automatically by pytest without any import here.

Note: ``_FIXTURES_DIR`` points to ``tests/composite/fixtures/`` — different
from the synastry fixtures directory — and the mandatory JSON keys for
composite oracles differ from synastry's. That is why ``oracle_fixture``
and ``load_oracle_fixture`` are kept here rather than merged into root.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest


_FIXTURES_DIR = Path(__file__).parent / "fixtures"

#: Composite oracle fixture slugs in canonical alphabetical order (single
#: source of truth for :func:`oracle_fixture` parametrization). Mirrors
#: :data:`tests.synastry.conftest.ORACLE_SLUGS` — same three couples
#: (Curie, Diana/Charles, Lennon/Ono) reused for composite self-consistency
#: oracles per 17-RESEARCH §"Astro.com Oracle Pairs".
ORACLE_SLUGS = ("curie", "diana_charles", "lennon_ono")


def load_oracle_fixture(slug: str) -> dict:
    """Load a composite oracle fixture JSON by slug.

    Parameters
    ----------
    slug : str
        One of :data:`ORACLE_SLUGS` (``"curie"``, ``"diana_charles"``,
        ``"lennon_ono"``).

    Returns
    -------
    dict
        Parsed JSON contents with mandatory keys ``schema_version``,
        ``name``, ``rodden_a``, ``rodden_b``, ``chart_a``, ``chart_b``,
        ``expected_composite``, ``validation_source``,
        ``cross_check_astro_com``.

    Raises
    ------
    FileNotFoundError
        If ``tests/composite/fixtures/oracle_{slug}.json`` does not exist.
    """
    path = _FIXTURES_DIR / f"oracle_{slug}.json"
    with path.open() as fh:
        result: dict = json.load(fh)
    return result


@pytest.fixture(params=ORACLE_SLUGS, ids=ORACLE_SLUGS)
def oracle_fixture(request: pytest.FixtureRequest) -> dict:
    """Yield each composite oracle fixture in turn, parametrized over 3 couples.

    Drives :mod:`tests.composite.test_oracle` — one test invocation per
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
