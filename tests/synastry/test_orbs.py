"""Tests for ketu.synastry.orbs — formula, preset resolver, edge cases.

Pure data assertions on the orb formula and resolver. No chart computation.
Pins the formula values (Sun-Moon = 6 deg, Rahu-Rahu = 0 deg, Venus-Mars
trine = 3 deg, ASC-Sun = 5 deg) as ratchet against drift, and verifies the
resolver error paths.
"""
from __future__ import annotations

import numpy as np
import pytest

from ketu.core import bodies as _BODIES
from ketu.synastry.orbs import (
    ASC_MC_NATAL_ORB_DEG,
    SYNASTRY_FACTOR,
    _BODY_ORBS_15,
    _PRESET_BY_NAME,
    resolve_orb_set,
    synastry_orb_limit,
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

def test_synastry_factor_value() -> None:
    """SYNASTRY_FACTOR is 0.5 (astro.com convention — natal orb halved)."""
    assert SYNASTRY_FACTOR == 0.5


def test_asc_mc_natal_orb_deg_value() -> None:
    """ASC_MC_NATAL_ORB_DEG is 8.0 deg (mid-tier; halved to 4 deg with factor)."""
    assert ASC_MC_NATAL_ORB_DEG == 8.0


# ---------------------------------------------------------------------------
# _BODY_ORBS_15 internal table
# ---------------------------------------------------------------------------

def test_body_orbs_15_shape_and_dtype() -> None:
    """_BODY_ORBS_15 is shape (15,) and dtype float32 (matches bodies['orb'])."""
    assert _BODY_ORBS_15.shape == (15,)
    assert _BODY_ORBS_15.dtype == np.float32


def test_body_orbs_15_canonical_entries_match_bodies() -> None:
    """Entries 0..12 mirror ketu.core.bodies['orb'] (single source of truth)."""
    expected = _BODIES["orb"].astype(np.float32)
    np.testing.assert_array_equal(_BODY_ORBS_15[:13], expected)


def test_body_orbs_15_asc_mc_entries() -> None:
    """Entries 13..14 hold ASC_MC_NATAL_ORB_DEG (= 8.0)."""
    assert _BODY_ORBS_15[13] == np.float32(ASC_MC_NATAL_ORB_DEG)
    assert _BODY_ORBS_15[14] == np.float32(ASC_MC_NATAL_ORB_DEG)


def test_body_orbs_15_frozen() -> None:
    """Mutation guard: _BODY_ORBS_15.flags.writeable is False."""
    assert _BODY_ORBS_15.flags.writeable is False, (
        "_BODY_ORBS_15 must be frozen to ratchet against accidental mutation"
    )


# ---------------------------------------------------------------------------
# synastry_orb_limit — formula values
# ---------------------------------------------------------------------------

def test_synastry_orb_limit_sun_moon_conjunction() -> None:
    """Sun-Moon conjunction: (12+12)/2 * 1 * 0.5 == 6.0 (astro.com headline)."""
    assert synastry_orb_limit(0, 1, 0) == 6.0


def test_synastry_orb_limit_sun_sun_conjunction() -> None:
    """Sun-Sun self-pair conjunction: (12+12)/2 * 1 * 0.5 == 6.0 (matches Sun-Moon)."""
    assert synastry_orb_limit(0, 0, 0) == 6.0


def test_synastry_orb_limit_venus_mars_trine() -> None:
    """Venus-Mars trine: (10+8)/2 * (2/3) * 0.5 == 3.0 (formula derivation pin)."""
    result = synastry_orb_limit(3, 4, 9)  # Venus=3, Mars=4, Trine=9
    assert result == pytest.approx(3.0, abs=1e-5)


def test_synastry_orb_limit_rahu_rahu_zero_orb() -> None:
    """Rahu-Rahu conjunction == 0.0 deg (Rahu has zero natal orb in bodies['orb']).

    Documented edge case — pre-empts user surprise when Rahu/Ketu/Lilith
    self-pairs never trigger an orbed aspect (Pitfall 2 in 16-RESEARCH.md).
    """
    assert synastry_orb_limit(10, 10, 0) == 0.0


def test_synastry_orb_limit_ketu_ketu_zero_orb() -> None:
    """Ketu-Ketu conjunction == 0.0 deg (zero-orb body)."""
    assert synastry_orb_limit(11, 11, 0) == 0.0


def test_synastry_orb_limit_lilith_lilith_zero_orb() -> None:
    """Lilith-Lilith conjunction == 0.0 deg (zero-orb body)."""
    assert synastry_orb_limit(12, 12, 0) == 0.0


def test_synastry_orb_limit_asc_sun_conjunction() -> None:
    """ASC-Sun conjunction: (8+12)/2 * 1 * 0.5 == 5.0 (matches astro.com 4-5 deg practice)."""
    # ASC is index 13 in the 15-body axis, Sun is index 0
    result = synastry_orb_limit(13, 0, 0)
    assert result == pytest.approx(5.0, abs=1e-5)


def test_synastry_orb_limit_with_classical_factor() -> None:
    """Sun-Moon conjunction with classical factor (1.0) == 12.0 deg (natal orb)."""
    result = synastry_orb_limit(0, 1, 0, factor=1.0)
    assert result == 12.0


def test_orb_limit_returns_pure_python_float() -> None:
    """Return value is isinstance(result, float), not a numpy scalar."""
    result = synastry_orb_limit(0, 1, 0)
    assert isinstance(result, float), (
        f"synastry_orb_limit must return a pure-Python float; got {type(result)!r}"
    )
    assert not isinstance(result, np.floating), (
        "synastry_orb_limit leaked a numpy scalar to its caller"
    )


# ---------------------------------------------------------------------------
# resolve_orb_set — preset resolution
# ---------------------------------------------------------------------------

def test_resolve_orb_set_synastry() -> None:
    """resolve_orb_set('synastry') == 0.5."""
    assert resolve_orb_set("synastry") == 0.5


def test_resolve_orb_set_classical() -> None:
    """resolve_orb_set('classical') == 1.0 (natal orbs unchanged)."""
    assert resolve_orb_set("classical") == 1.0


def test_resolve_orb_set_none_defaults_to_synastry() -> None:
    """resolve_orb_set(None) == 0.5 (default is the tightened synastry factor)."""
    assert resolve_orb_set(None) == 0.5


def test_resolve_orb_set_case_insensitive() -> None:
    """resolve_orb_set lowercases the input string before lookup."""
    assert resolve_orb_set("SYNASTRY") == 0.5
    assert resolve_orb_set("Classical") == 1.0


def test_resolve_orb_set_unknown_string_raises_with_valid_list() -> None:
    """Unknown preset raises ValueError enumerating valid presets."""
    with pytest.raises(ValueError, match="synastry"):
        resolve_orb_set("xyzzy")
    # Enumeration also mentions classical
    with pytest.raises(ValueError, match="classical"):
        resolve_orb_set("xyzzy")


def test_resolve_orb_set_invalid_type_raises() -> None:
    """Non-string non-None type raises ValueError naming the offending type."""
    with pytest.raises(ValueError, match="int"):
        resolve_orb_set(42)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# _PRESET_BY_NAME registry — naming convention ratchet
# ---------------------------------------------------------------------------

def test_preset_registry_singular_naming() -> None:
    """_PRESET_BY_NAME (singular) matches ketu/aspects/presets.py convention.

    Ratchets against accidental pluralisation drift to `_PRESETS_BY_NAME`.
    """
    assert sorted(_PRESET_BY_NAME) == ["classical", "synastry"]


def test_preset_registry_values() -> None:
    """_PRESET_BY_NAME maps to expected multiplicative factors."""
    assert _PRESET_BY_NAME["synastry"] == 0.5
    assert _PRESET_BY_NAME["classical"] == 1.0
