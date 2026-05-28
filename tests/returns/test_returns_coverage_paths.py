"""Targeted coverage-gap tests for ketu.returns error/edge branches.

Plan 18-05 close-out: ratchet the ≥95% ``make returns-coverage`` gate by
exercising the defense-in-depth branches that the surface suites
(test_solar_return.py, test_lunar_return.py, test_solve_return.py,
test_returns_oracle.py) leave uncovered because they only happen on
pathological / FP-floor inputs:

- ``_solve.py:231`` — ``tol_days`` bracket-width early-return (the
  FP-noise floor that fires only when ``tol_deg`` cannot).
- ``_solve.py:238`` — ``max_iter`` runaway-guard fall-through (neither
  tolerance fires within the iteration cap).
- ``lunar.py:250-252`` — cycle-fallback ``except ValueError: continue``
  (the n=0 bracket fails, a later cycle succeeds).
- ``lunar.py:265`` — no-return-found ``ValueError`` (every seed in the
  cycle search fails its bracket).

The first two use real ephemeris calls with degenerate tolerances; the
last two monkeypatch the shared ``_solve_return`` helper to drive the
``lunar_return`` cycle-search control flow deterministically (the
branches are physically unreachable with a real monotonic Moon, so
mocking is the only honest way to pin them).
"""
from __future__ import annotations

import numpy as np
import pytest

from ketu.ephemeris.planets import calc_planet_position
import ketu.returns.lunar as lunar_mod
from ketu.returns import lunar_return
from ketu.returns._solve import (
    _TROPICAL_MONTH_D,
    _TROPICAL_YEAR_D,
    _solve_return,
)


class TestSolveReturnToleranceFloors:
    """Pin the two non-default stopping branches of ``_solve_return``."""

    def test_tol_days_bracket_floor_returns_midpoint(self) -> None:
        """``_solve.py:231`` — ``tol_days`` fires when ``tol_deg`` cannot.

        Force ``tol_deg=0.0`` so the residual threshold is unreachable;
        the bisection must then terminate on the ``tol_days`` bracket-
        width floor and return the bracket midpoint. With a generous
        ``tol_days`` the floor fires after only a handful of halvings.
        """
        natal_jd = 2451545.0  # 2000-01-01T12:00 UT
        natal_sun = float(calc_planet_position(natal_jd, 0)[0])
        t_seed = natal_jd + _TROPICAL_YEAR_D

        # tol_deg=0.0 is unreachable; tol_days=0.5 d makes the bracket
        # floor fire within ~3 halvings of the ±1.5 d bracket.
        jd_return = _solve_return(
            0,
            natal_sun,
            t_seed,
            1.5,
            tol_deg=0.0,
            tol_days=0.5,
        )
        # Still lands within the original bracket near the true return:
        assert abs(jd_return - t_seed) <= 1.5

    def test_max_iter_runaway_guard_returns_midpoint(self) -> None:
        """``_solve.py:238`` — fall through the loop when neither tol fires.

        Force both tolerances to ``0.0`` and cap ``max_iter=2`` so the
        ``for`` loop exhausts without an early return; the function must
        fall through to the final ``return 0.5 * (t_lo + t_hi)``.
        """
        natal_jd = 2451545.0
        natal_moon = float(calc_planet_position(natal_jd, 1)[0])
        t_seed = natal_jd + _TROPICAL_MONTH_D

        jd_return = _solve_return(
            1,
            natal_moon,
            t_seed,
            1.5,
            max_iter=2,
            tol_deg=0.0,
            tol_days=0.0,
        )
        # The runaway guard still returns a JD inside the bracket:
        assert abs(jd_return - t_seed) <= 1.5


class TestLunarReturnCycleFallback:
    """Pin the cycle-search control flow in ``lunar_return``.

    These branches are physically unreachable with a real monotonic
    Moon (a return ALWAYS exists within one sidereal period and the
    mean-motion seed always brackets it), so the only honest way to
    exercise them is to monkeypatch the shared ``_solve_return`` helper
    and drive the control flow directly.
    """

    def test_first_bracket_raises_then_next_cycle_succeeds(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """``lunar.py:250-252`` — ``except ValueError: continue`` then succeed.

        Make the n=0 seed bracket raise ``ValueError`` (no sign change),
        forcing the loop to ``continue`` to n=1, which succeeds and
        clears the first-return->= target_jd guard.
        """
        natal_jd = 2451545.0
        target_jd = 2455197.5  # 2010-01-01T00:00 UT

        calls: list[float] = []

        def fake_solve(*, body_id: int, natal_lon_ref: float, t_seed: float, half_window_days: float) -> float:
            calls.append(t_seed)
            if len(calls) == 1:
                # n=0 bracket: simulate "no sign change".
                raise ValueError("No return in bracket (simulated n=0 failure)")
            # n=1 bracket: succeed, returning a JD comfortably >= target_jd.
            return target_jd + 5.0

        monkeypatch.setattr(lunar_mod, "_solve_return", fake_solve)

        chart = lunar_return(natal_jd, 48.85, 2.35, target_jd)
        # The n=1 candidate (target_jd + 5) was accepted:
        assert float(chart["jd"]) == pytest.approx(target_jd + 5.0)
        # Confirms the n=0 branch raised and the loop advanced:
        assert len(calls) >= 2

    def test_undershoot_candidate_skipped_until_at_or_after_target(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """``lunar.py:259/262`` — candidate < target_jd is skipped (LRET-01).

        The n=0 candidate resolves BEFORE ``target_jd`` (mean-motion
        undershoot); the loop must reject it and advance to n=1 whose
        candidate is >= ``target_jd``.
        """
        natal_jd = 2451545.0
        target_jd = 2455197.5

        candidates = iter([target_jd - 10.0, target_jd + 2.0])

        def fake_solve(*, body_id: int, natal_lon_ref: float, t_seed: float, half_window_days: float) -> float:
            return next(candidates)

        monkeypatch.setattr(lunar_mod, "_solve_return", fake_solve)

        chart = lunar_return(natal_jd, 48.85, 2.35, target_jd)
        assert float(chart["jd"]) == pytest.approx(target_jd + 2.0)

    def test_all_cycles_fail_raises_no_return_found(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """``lunar.py:265`` — every cycle fails its bracket → ValueError.

        Make ``_solve_return`` raise for all three seeds; the loop
        leaves ``jd_return is None`` and the public API raises the
        pathological "No lunar return found" ``ValueError``.
        """
        natal_jd = 2451545.0
        target_jd = 2455197.5

        def fake_solve(*, body_id: int, natal_lon_ref: float, t_seed: float, half_window_days: float) -> float:
            raise ValueError("No return in bracket (simulated total failure)")

        monkeypatch.setattr(lunar_mod, "_solve_return", fake_solve)

        with pytest.raises(ValueError, match=r"No lunar return found"):
            lunar_return(natal_jd, 48.85, 2.35, target_jd)
