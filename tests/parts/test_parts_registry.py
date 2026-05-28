"""Registry behaviour and extensibility tests for ketu.parts.

Tests verify PARTS-01 (registry round-trip + additivity without dispatch
change), PARTS-02 (ValueError on unknown), PARTS-07 (Marriage
sect-invariance via callable identity), and the exactly-3 constraint for
the v1.2 built-in set (Fortune + Spirit + Marriage).

All tests run OFFLINE — no network access.
"""
from __future__ import annotations

import pytest

from ketu.charts.api import compute_chart
from ketu.parts import PARTS, calculate_all_parts, calculate_part, get_part, register

#: Paris, J2000 noon — day chart fixture (confirmed day in test_parts_oracle.py).
_CHART = compute_chart(2451545.0, 48.8566, 2.3522)


class TestPartsHasExactlyThree:
    """v1.2 constraint: exactly 3 built-in parts registered at import time."""

    def test_parts_has_exactly_three(self) -> None:
        """PARTS has exactly the 3 expected built-in entries at import time.

        Catches accidental over- or under-registration in __init__.py.
        """
        assert set(PARTS.keys()) == {"fortune", "spirit", "marriage"}


class TestGetPartCaseInsensitive:
    """get_part normalises the name to lowercase (RESEARCH Pitfall 3)."""

    def test_title_case_returns_same_object(self) -> None:
        """get_part('Fortune') and get_part('fortune') return the same PartSpec."""
        assert get_part("Fortune") is get_part("fortune")

    def test_upper_case_name_field(self) -> None:
        """get_part('FORTUNE').name == 'fortune' (stored lowercase)."""
        assert get_part("FORTUNE").name == "fortune"

    def test_mixed_case_spirit(self) -> None:
        """get_part('Spirit') resolves to the same spec as get_part('spirit')."""
        assert get_part("Spirit") is get_part("spirit")


class TestGetPartUnknownRaises:
    """ValueError on unknown part name, message lists sorted available parts."""

    def test_unknown_part_raises_value_error(self) -> None:
        """get_part('nope') raises ValueError matching 'unknown part'."""
        with pytest.raises(ValueError, match="unknown part 'nope'"):
            get_part("nope")

    def test_error_message_lists_available_parts(self) -> None:
        """Error message includes the list of available parts."""
        with pytest.raises(ValueError) as exc_info:
            get_part("nope")
        msg = str(exc_info.value)
        assert "fortune" in msg
        assert "marriage" in msg
        assert "spirit" in msg


class TestRegistryIsExtensible:
    """PARTS-01: a 4th part can be registered without touching dispatch.

    Proves additivity — calculate_part('test_lot', chart) works after
    register() with no change to api.py or any dispatch ladder.
    The test cleans up via a try/finally block to avoid polluting the
    global PARTS dict for other tests.
    """

    def test_register_fourth_part_and_use_without_dispatch_change(self) -> None:
        """Register a throwaway 4th lot; get_part + calculate_part both work."""
        try:
            register(
                "test_lot",
                day_formula=lambda asc, sun, moon, venus: (asc + moon) % 360.0,
                night_formula=lambda asc, sun, moon, venus: (asc + sun) % 360.0,
                description="ephemeral test lot",
            )
            spec = get_part("test_lot")
            assert spec.name == "test_lot"
            # calculate_part delegates to the registry — no dispatch change needed.
            result = calculate_part("test_lot", _CHART)
            assert 0.0 <= result < 360.0
        finally:
            PARTS.pop("test_lot", None)

    def test_cleanup_restores_exactly_three(self) -> None:
        """After the extensibility test, the registry is back to exactly 3 entries."""
        assert set(PARTS.keys()) == {"fortune", "spirit", "marriage"}


class TestCalculateAllParts:
    """calculate_all_parts: default (parts=None) + explicit parts=[...] filter."""

    def test_default_returns_all_three(self) -> None:
        """calculate_all_parts(chart) (parts=None) returns all 3 parts alphabetically."""
        result = calculate_all_parts(_CHART)
        assert set(result.keys()) == {"fortune", "spirit", "marriage"}

    def test_explicit_filter_single_part(self) -> None:
        """calculate_all_parts(chart, parts=['fortune']) returns only fortune."""
        result = calculate_all_parts(_CHART, parts=["fortune"])
        assert list(result.keys()) == ["fortune"]
        assert 0.0 <= result["fortune"] < 360.0

    def test_explicit_filter_two_parts(self) -> None:
        """calculate_all_parts(chart, parts=['fortune', 'spirit']) returns two entries."""
        result = calculate_all_parts(_CHART, parts=["fortune", "spirit"])
        assert set(result.keys()) == {"fortune", "spirit"}

    def test_all_values_in_range(self) -> None:
        """All longitudes returned by calculate_all_parts are in [0, 360)."""
        result = calculate_all_parts(_CHART)
        for name, lon in result.items():
            assert 0.0 <= lon < 360.0, f"{name}: longitude {lon} out of [0, 360)"


class TestMarriageIdentity:
    """PARTS-07: Marriage day_formula IS night_formula (callable identity).

    The sect-invariant contract is expressed at the object level — same
    callable, NOT a ``sect_aware=False`` flag.  Dispatch is always
    ``spec.day_formula if is_day else spec.night_formula``; when both
    point to the same callable, the dispatch is unconditional by construction.
    """

    def test_marriage_night_formula_is_day_formula(self) -> None:
        """Marriage spec: day_formula is night_formula (identity, not just equality)."""
        spec = get_part("marriage")
        assert spec.day_formula is spec.night_formula
