"""Registry pattern tests — register decorator, dispatch, case-insensitivity.

Pure structural tests with cleanup so test ordering does not leak into
:data:`SYSTEMS`. Plans 10-04/10-05 will populate the registry with real
systems; this file asserts the mechanism only.
"""
from __future__ import annotations

import numpy as np
import pytest

from ketu.houses.registry import SYSTEMS, get_system, register


def test_register_inserts_into_systems_dict() -> None:
    """@register('name') adds the function to SYSTEMS[name]."""
    @register("test_register_demo")
    def demo_fn(armc: np.ndarray, lat: np.ndarray, eps: np.ndarray) -> np.ndarray:
        return np.zeros((12,))
    try:
        assert "test_register_demo" in SYSTEMS
        assert SYSTEMS["test_register_demo"] is demo_fn
    finally:
        del SYSTEMS["test_register_demo"]  # cleanup so order does not matter


def test_register_lowercases_name() -> None:
    """Registration normalizes the name to lowercase."""
    @register("Test_Case_INSENSITIVE")
    def fn(armc: np.ndarray, lat: np.ndarray, eps: np.ndarray) -> np.ndarray:
        return np.zeros((12,))
    try:
        assert "test_case_insensitive" in SYSTEMS
        assert "Test_Case_INSENSITIVE" not in SYSTEMS
    finally:
        del SYSTEMS["test_case_insensitive"]


def test_get_system_lookup_is_case_insensitive() -> None:
    """get_system('TEST') returns the same function as get_system('test')."""
    @register("test_lookup")
    def fn(armc: np.ndarray, lat: np.ndarray, eps: np.ndarray) -> np.ndarray:
        return np.zeros((12,))
    try:
        assert get_system("TEST_LOOKUP") is fn
        assert get_system("test_lookup") is fn
        assert get_system("Test_Lookup") is fn
    finally:
        del SYSTEMS["test_lookup"]


def test_get_system_raises_value_error_with_helpful_message() -> None:
    """Unknown system name raises ValueError listing received name + available."""
    with pytest.raises(ValueError) as exc_info:
        get_system("nonexistent_system_xyz")
    msg = str(exc_info.value)
    assert "nonexistent_system_xyz" in msg
    assert "available" in msg


def test_systems_dict_is_initialised() -> None:
    """SYSTEMS exists as a dict; population is owned by Plans 04/05.

    Plan 10-03 boundary leaves SYSTEMS empty (or, if Plans 04/05 already ran
    and were imported, with their entries — this test does not require
    emptiness, only dict-ness).
    """
    assert isinstance(SYSTEMS, dict)
