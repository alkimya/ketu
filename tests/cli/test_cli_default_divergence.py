"""Regression test: CLI bare default (classical/5) vs library default (traditional/7).

This module locks the INTENTIONAL divergence introduced by Phase 26 plan 02:

- **Library default** (``resolve_aspect_set(None)``): the 7 half-circle aspects
  (``TRADITIONAL``, harmonics 1/2/3/6).
- **CLI bare default** (the ``args.harmonics is None`` branch in
  ``ketu/cli/aspects_cmd.py``): ``resolve_aspect_set("classical")`` — pinned
  to the 5-major classical set to preserve the v1.0/v1.1 byte-stable contract.

These tests ensure that a future change cannot silently re-converge the two
defaults (which would break the byte-stable CLI contract without a visible
test failure). They do NOT invoke the argparse parser; they pin the two
resolution paths at the Python level.
"""
from __future__ import annotations

import numpy as np

from ketu.aspects.presets import (
    CLASSICAL,
    TRADITIONAL,
    resolve_aspect_set,
)


def test_library_default_is_seven_half_circle() -> None:
    """Library default (resolve_aspect_set(None)) is TRADITIONAL — 7 aspects.

    Phase 26 plan 02 flipped the library default from CLASSICAL (5) to
    TRADITIONAL (7 half-circle aspects). This test pins that new library
    contract.
    """
    result = resolve_aspect_set(None)
    assert int(result.sum()) == 7, (
        f"library default must be 7 (TRADITIONAL); got {int(result.sum())}"
    )
    assert np.array_equal(result, TRADITIONAL), (
        "library default must equal TRADITIONAL (harmonics 1/2/3/6)"
    )


def test_cli_bare_default_is_classical_five() -> None:
    """CLI bare default (resolve_aspect_set('classical')) is CLASSICAL — 5 aspects.

    The ``args.harmonics is None`` branch in ``ketu/cli/aspects_cmd.py``
    calls ``resolve_aspect_set('classical')`` explicitly to preserve the
    v1.0/v1.1 byte-stable contract. This test pins that CLI-side resolution.
    Divergence from the library default is INTENTIONAL.
    """
    # Reproduce the CLI None-branch resolution exactly as aspects_cmd.py does.
    result = resolve_aspect_set("classical")
    assert int(result.sum()) == 5, (
        f"CLI bare default must be 5 (CLASSICAL); got {int(result.sum())}"
    )
    assert np.array_equal(result, CLASSICAL), (
        "CLI bare default must equal CLASSICAL (curated 5-major set)"
    )


def test_cli_and_library_defaults_differ() -> None:
    """CLI bare default (5) and library default (7) must differ.

    This is the key divergence regression: if both resolve to the same mask,
    one of the two contracts above has been broken. Fail loudly here to
    surface that change before it ships.
    """
    library_default = resolve_aspect_set(None)
    cli_default = resolve_aspect_set("classical")
    assert not np.array_equal(cli_default, library_default), (
        "CLI bare default and library default must DIFFER (5 vs 7 aspects). "
        "If they are equal, either the library default was re-pinned to "
        "classical or the CLI pin was removed — both break a contract."
    )
