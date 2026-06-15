"""Tests for ketu.synastry.orbs — formula, preset resolver, edge cases.

Pure data assertions on the orb formula and resolver. No chart computation.
Pins the formula values (Sun-Moon = 6 deg, Rahu-Rahu = 1 deg, Venus-Mars
trine = 3 deg, ASC-Sun = 5 deg) as ratchet against drift, and verifies the
resolver error paths.

v1.7 ratchet: Rahu/Ketu/Lilith natal orb is 2° (ORB-01, phase 38).
Synastry self-pair: (2+2)/2 * coef_conj(1) * factor(0.5) = 1.0 deg.
"""
from __future__ import annotations

import numpy as np
import pytest

from ketu.core import bodies as _BODIES
from ketu.synastry.orbs import (
    ASC_MC_NATAL_ORB_DEG,
    SYNASTRY_FACTOR,
    _BODY_ORBS_16,
    _PRESET_BY_NAME,
    resolve_orb_set,
    synastry_orb_limit,
)

# Alias for test readability (v1.3 ratchet: 14 canonical + ASC + MC = 16)
_BODY_ORBS_15 = _BODY_ORBS_16


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
# _BODY_ORBS_16 internal table (v1.3: 14 canonical + ASC + MC = 16)
# ---------------------------------------------------------------------------

def test_body_orbs_15_shape_and_dtype() -> None:
    """_BODY_ORBS_16 is shape (16,) and dtype float32 (14 canonical + ASC + MC)."""
    assert _BODY_ORBS_16.shape == (16,)
    assert _BODY_ORBS_16.dtype == np.float32


def test_body_orbs_15_canonical_entries_match_bodies() -> None:
    """Entries 0..13 mirror ketu.core.bodies['orb'] (14 canonical incl. Chiron)."""
    expected = _BODIES["orb"].astype(np.float32)
    np.testing.assert_array_equal(_BODY_ORBS_16[:14], expected)


def test_body_orbs_15_asc_mc_entries() -> None:
    """Entries 14..15 hold ASC_MC_NATAL_ORB_DEG (= 8.0) for ASC and MC."""
    assert _BODY_ORBS_16[14] == np.float32(ASC_MC_NATAL_ORB_DEG)
    assert _BODY_ORBS_16[15] == np.float32(ASC_MC_NATAL_ORB_DEG)


def test_body_orbs_15_frozen() -> None:
    """Mutation guard: _BODY_ORBS_16.flags.writeable is False."""
    assert _BODY_ORBS_16.flags.writeable is False, (
        "_BODY_ORBS_16 must be frozen to ratchet against accidental mutation"
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


def test_synastry_orb_limit_rahu_rahu_two_degree_orb() -> None:
    """Rahu-Rahu conjunction == 1.0 deg (Rahu natal orb is 2° since ORB-01, phase 38).

    Math: (2+2)/2 * coef_conj(1) * factor(0.5) = 1.0 deg.
    v1.7 ratchet: Rahu/Ketu/Lilith orb was 0°, now 2° — self-pairs are detectable
    in synastry (self-synastry dist==0 is still detected via non-strict <=).
    """
    assert synastry_orb_limit(10, 10, 0) == 1.0


def test_synastry_orb_limit_ketu_ketu_two_degree_orb() -> None:
    """Ketu-Ketu conjunction == 1.0 deg (natal orb 2° since ORB-01, phase 38).

    Math: (2+2)/2 * coef_conj(1) * factor(0.5) = 1.0 deg.
    """
    assert synastry_orb_limit(11, 11, 0) == 1.0


def test_synastry_orb_limit_lilith_lilith_two_degree_orb() -> None:
    """Lilith-Lilith conjunction == 1.0 deg (natal orb 2° since ORB-01, phase 38).

    Math: (2+2)/2 * coef_conj(1) * factor(0.5) = 1.0 deg.
    """
    assert synastry_orb_limit(12, 12, 0) == 1.0


def test_synastry_orb_limit_chiron_chiron_parity_pluto() -> None:
    """Chiron-Chiron conjunction == 2.0 deg (orb=4 x factor=0.5, Pluto parity).

    Pins Chiron natal orb = 4 deg in synastry (``_BODY_ORBS_16[13] == 4.0``).
    Chiron (id=13) is no longer in the zero-orb group (Rahu/Ketu/Lilith).
    """
    # Chiron-Chiron: (4+4)/2 * coef_conj(1) * factor(0.5) = 4 * 1 * 0.5 = 2.0
    assert synastry_orb_limit(13, 13, 0) == pytest.approx(2.0, abs=1e-5)


def test_synastry_orb_limit_asc_sun_conjunction() -> None:
    """ASC-Sun conjunction: (8+12)/2 * 1 * 0.5 == 5.0 (matches astro.com 4-5 deg practice)."""
    # ASC is index 14 in the 16-body axis (v1.3: Chiron at 13 shifts ASC to 14)
    result = synastry_orb_limit(14, 0, 0)
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
