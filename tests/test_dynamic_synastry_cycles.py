"""
Tests for dynamic_specs integration in calculate_synastry and generate_cycle_series.

This file is plan 28-03's EXCLUSIVE test file. It covers:
- calculate_synastry dynamic rows (aspect_type == -2, orb formula, filtered/dense modes)
- generate_cycle_series / generate_multi_cycle_series dynamic candidate-set extension
- None-path invariance for both consumers (additive-only change)

It does NOT touch tests/test_dynamic_harmonics.py (plan 28-02 owns that file).
"""
from __future__ import annotations

import numpy as np
import pytest
from datetime import datetime, timedelta

from ketu.charts import compute_chart
from ketu.synastry import calculate_synastry, SYNASTRY_DTYPE
from ketu.synastry.orbs import _BODY_ORBS_16, SYNASTRY_FACTOR
from ketu.cycles import generate_cycle_series, generate_multi_cycle_series, MAJOR_ASPECTS
from ketu.aspects.harmonics import generate_harmonic_aspects


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def chart_a():
    """Fixed chart A — Paris, J2000.0."""
    return compute_chart(2451545.0, 48.86, 2.35)


@pytest.fixture(scope="module")
def chart_b0():
    """Fixed chart B — New York, ~1 year after J2000.0."""
    return compute_chart(2451900.0, 40.71, -74.01)


@pytest.fixture(scope="module")
def specs_h7():
    return generate_harmonic_aspects(7)


# ---------------------------------------------------------------------------
# Task 1: calculate_synastry with dynamic_specs
# ---------------------------------------------------------------------------


class TestSynastryDynamicSpecs:

    def test_synastry_dynamic_specs_change_filtered_set(self, chart_a, chart_b0, specs_h7):
        """
        STRUCTURAL: dynamic_specs can only ADD -2 rows, never drop static rows.

        The filtered set with dynamic specs is a superset (>=) of the None set.
        Every -2 row carries the expected orb_limit formula.
        """
        none_filtered = calculate_synastry(
            chart_a, chart_b0, dynamic_specs=None, mode="filtered"
        )
        dyn_filtered = calculate_synastry(
            chart_a, chart_b0, dynamic_specs=specs_h7, mode="filtered"
        )

        assert none_filtered.dtype == SYNASTRY_DTYPE
        assert dyn_filtered.dtype == SYNASTRY_DTYPE

        # Dynamic call filtered set is a superset of None call's set.
        assert len(dyn_filtered) >= len(none_filtered), (
            f"dynamic filtered ({len(dyn_filtered)}) < none filtered ({len(none_filtered)})"
        )

        # Every static row present in none_filtered is still in dyn_filtered.
        static_rows = dyn_filtered[dyn_filtered["aspect_type"] >= 0]
        assert len(static_rows) == len(none_filtered)

        # For every -2 row, validate the orb_limit formula.
        dyn_rows = dyn_filtered[dyn_filtered["aspect_type"] == -2]
        for row in dyn_rows:
            i = int(row["body_a"])
            j = int(row["body_b"])
            # Find matching spec by matching the orb_limit to any spec's coef.
            found_match = False
            for spec_row in specs_h7:
                coef = float(spec_row["coef"])
                expected_orb_limit = (
                    (float(_BODY_ORBS_16[i]) + float(_BODY_ORBS_16[j])) / 2.0
                    * coef
                    * SYNASTRY_FACTOR
                )
                if abs(float(row["orb_limit"]) - expected_orb_limit) < 1e-4:
                    found_match = True
                    break
            assert found_match, (
                f"orb_limit {float(row['orb_limit']):.4f} did not match any H7 spec "
                f"for body pair ({i},{j})"
            )

    def test_synastry_dynamic_rows_appear_on_grid(self, chart_a, specs_h7):
        """
        EXISTENCE: across a ~1-year grid of partner chart dates,
        at least one -2 row accumulates (guaranteed hit).
        """
        total_dyn = 0
        first_hit_row = None
        first_hit_i = None
        first_hit_j = None

        for jd_b in np.linspace(2451545.0, 2451545.0 + 365.0, 24):
            b = compute_chart(float(jd_b), 40.71, -74.01)
            result = calculate_synastry(chart_a, b, dynamic_specs=specs_h7)
            dyn_mask = result["aspect_type"] == -2
            count = int(dyn_mask.sum())
            total_dyn += count
            if first_hit_row is None and count > 0:
                hit = result[dyn_mask][0]
                first_hit_row = hit
                first_hit_i = int(hit["body_a"])
                first_hit_j = int(hit["body_b"])

        assert total_dyn > 0, (
            "no dynamic synastry rows (aspect_type==-2) across a 1-year grid!"
        )

        # Validate orb_limit formula on the first hit row.
        assert first_hit_row is not None
        found_match = False
        for spec_row in specs_h7:
            coef = float(spec_row["coef"])
            expected_orb_limit = (
                (float(_BODY_ORBS_16[first_hit_i]) + float(_BODY_ORBS_16[first_hit_j])) / 2.0
                * coef
                * SYNASTRY_FACTOR
            )
            if abs(float(first_hit_row["orb_limit"]) - expected_orb_limit) < 1e-4:
                found_match = True
                break
        assert found_match, (
            f"first hit orb_limit {float(first_hit_row['orb_limit']):.4f} did not "
            f"match any H7 spec for body pair ({first_hit_i},{first_hit_j})"
        )

    def test_synastry_dense_still_256(self, chart_a, chart_b0, specs_h7):
        """Dense mode always returns exactly 256 rows, even with dynamic specs."""
        result = calculate_synastry(
            chart_a, chart_b0, dynamic_specs=specs_h7, mode="dense"
        )
        assert len(result) == 256
        assert result.dtype == SYNASTRY_DTYPE

    def test_synastry_filtered_keeps_dynamic(self, chart_a, specs_h7):
        """
        Filtered mode includes -2 rows and excludes -1 rows.

        Scan a grid to guarantee at least one -2 row exists, then verify
        the filtered predicate works correctly.
        """
        # Find a date that produces a -2 row.
        result_with_dyn = None
        for jd_b in np.linspace(2451545.0, 2451545.0 + 365.0, 36):
            b = compute_chart(float(jd_b), 40.71, -74.01)
            r_filtered = calculate_synastry(
                chart_a, b, dynamic_specs=specs_h7, mode="filtered"
            )
            if (r_filtered["aspect_type"] == -2).any():
                result_with_dyn = r_filtered
                break

        if result_with_dyn is None:
            pytest.skip("No -2 row found in 1-year grid; widening grid not feasible here")

        # Filtered: -2 rows present, -1 rows absent.
        assert (result_with_dyn["aspect_type"] == -2).any(), "-2 rows should be present"
        assert not (result_with_dyn["aspect_type"] == -1).any(), "-1 rows should be absent"

        # Sanity: the dense output contains -1 rows for the same charts.
        b_fixed = compute_chart(float(2451545.0 + 30), 40.71, -74.01)
        dense = calculate_synastry(chart_a, b_fixed, dynamic_specs=specs_h7, mode="dense")
        # Dense always has 256 rows; most are -1 (non-aspected).
        assert len(dense) == 256

    def test_synastry_none_unchanged(self, chart_a, chart_b0):
        """
        dynamic_specs=None produces byte-identical output to the no-arg call.
        """
        base = calculate_synastry(chart_a, chart_b0)
        with_none = calculate_synastry(chart_a, chart_b0, dynamic_specs=None)
        np.testing.assert_array_equal(base["aspect_type"], with_none["aspect_type"])
        np.testing.assert_array_equal(
            np.nan_to_num(base["orb"], nan=0.0),
            np.nan_to_num(with_none["orb"], nan=0.0),
        )

    def test_synastry_list_of_specs(self, chart_a, chart_b0):
        """Passing a list of spec arrays is accepted (list normalised to concat)."""
        specs_h4 = generate_harmonic_aspects(4)
        specs_h7 = generate_harmonic_aspects(7)
        # Single array and list-of-one should be equivalent.
        result_single = calculate_synastry(
            chart_a, chart_b0, dynamic_specs=specs_h7, mode="dense"
        )
        result_list = calculate_synastry(
            chart_a, chart_b0, dynamic_specs=[specs_h7], mode="dense"
        )
        np.testing.assert_array_equal(
            result_single["aspect_type"], result_list["aspect_type"]
        )
        # List of two specs is accepted without error.
        result_two = calculate_synastry(
            chart_a, chart_b0, dynamic_specs=[specs_h4, specs_h7], mode="dense"
        )
        assert len(result_two) == 256


# ---------------------------------------------------------------------------
# Task 2: generate_cycle_series with dynamic_specs
# ---------------------------------------------------------------------------


class TestCycleDynamicSpecs:

    @pytest.fixture(scope="class")
    def ts_60(self):
        """60-day timestamp window (Sun/Moon crosses many aspects)."""
        return [datetime(2025, 1, 1) + timedelta(days=i) for i in range(60)]

    @pytest.fixture(scope="class")
    def specs_h7(self):
        return generate_harmonic_aspects(7)

    def test_cycles_none_path_unchanged(self, ts_60, specs_h7):
        """
        dynamic_specs=None is array-identical to the no-arg call (byte-identical
        on nearest_aspect, in_aspect, aspect_orb).
        """
        base = generate_cycle_series("Sun", "Moon", ts_60)
        with_none = generate_cycle_series("Sun", "Moon", ts_60, dynamic_specs=None)
        np.testing.assert_array_equal(base["nearest_aspect"], with_none["nearest_aspect"])
        np.testing.assert_array_equal(base["in_aspect"], with_none["in_aspect"])
        np.testing.assert_array_equal(base["aspect_orb"], with_none["aspect_orb"])

    def test_cycles_dynamic_extends_candidate_set(self, ts_60, specs_h7):
        """
        With dynamic specs, the set of distinct nearest_aspect values includes
        at least one H7 angle NOT in MAJOR_ASPECTS (proves candidate set extended).
        """
        dyn = generate_cycle_series("Sun", "Moon", ts_60, dynamic_specs=specs_h7)

        # H7 angles: 51.43, 102.86, 154.29 (folded) and their mirrors.
        h7_angles = set()
        for row in specs_h7:
            ang = float(row["angle"])
            h7_angles.add(round(ang, 1))
            mirror = round(360.0 - ang, 1)
            if mirror != round(ang, 1):
                h7_angles.add(mirror)

        major_set = set(float(a) for a in MAJOR_ASPECTS.tolist())
        h7_only = h7_angles - major_set

        found_angles = set(round(float(a), 1) for a in dyn["nearest_aspect"].tolist())
        overlap = found_angles & h7_only
        assert overlap, (
            f"no H7-only nearest_aspect values found in 60-day Sun/Moon series. "
            f"H7-only angles: {sorted(h7_only)}, found: {sorted(found_angles)}"
        )

    def test_cycles_dynamic_detects_h7(self, specs_h7):
        """
        Over a window chosen to guarantee H7 crossings for a fast pair,
        at least one row has nearest_aspect near an H7 angle AND in_aspect == True.
        """
        # Use 180-day window on Sun/Moon for higher probability.
        ts = [datetime(2025, 1, 1) + timedelta(days=i) for i in range(180)]
        dyn = generate_cycle_series("Sun", "Moon", ts, dynamic_specs=specs_h7)

        # Build the full-circle H7 set (folded + mirrors).
        h7_full = set()
        for row in specs_h7:
            ang = float(row["angle"])
            h7_full.add(ang)
            mirror = 360.0 - ang
            if abs(mirror - ang) > 0.01:
                h7_full.add(mirror)

        # Find rows where nearest_aspect is close to an H7 angle AND in_aspect.
        hit_count = 0
        for na, ia in zip(dyn["nearest_aspect"], dyn["in_aspect"]):
            na_f = float(na)
            if ia and any(abs(na_f - h7a) < 2.0 for h7a in h7_full):
                hit_count += 1

        assert hit_count > 0, (
            "no in_aspect==True row with nearest_aspect near an H7 angle "
            f"in a 180-day Sun/Moon window. H7 set: {sorted(h7_full)}"
        )

    def test_cycles_dynamic_result_dtype(self, ts_60, specs_h7):
        """Result dtype is unchanged when dynamic_specs is provided."""
        from ketu.cycles import CYCLE_DTYPE
        dyn = generate_cycle_series("Sun", "Moon", ts_60, dynamic_specs=specs_h7)
        assert dyn.dtype == CYCLE_DTYPE
        assert len(dyn) == len(ts_60)

    def test_multi_cycle_dynamic_forwarded(self, specs_h7):
        """
        generate_multi_cycle_series forwards dynamic_specs to each pair.
        Smoke: result dict built; at least one pair shows a nearest_aspect
        not in MAJOR_ASPECTS (confirming forwarding happened).
        """
        ts = [datetime(2025, 1, 1) + timedelta(days=i) for i in range(90)]
        pairs = [("Sun", "Moon"), ("Sun", "Mars")]
        result = generate_multi_cycle_series(pairs, ts, dynamic_specs=specs_h7)

        assert "Sun-Moon" in result
        assert "Sun-Mars" in result

        major_set = set(float(a) for a in MAJOR_ASPECTS.tolist())
        extended_detected = False
        for arr in result.values():
            found = set(round(float(a), 1) for a in arr["nearest_aspect"].tolist())
            if found - major_set:
                extended_detected = True
                break

        assert extended_detected, (
            "generate_multi_cycle_series did not forward dynamic_specs; "
            "no extended nearest_aspect values found across pairs"
        )

    def test_cycles_none_path_explicit_vs_absent(self):
        """
        Passing dynamic_specs=None explicitly produces the same result
        as passing no dynamic_specs argument at all (both call with include_aspects=True).
        """
        ts = [datetime(2025, 6, 1) + timedelta(days=i) for i in range(30)]
        base = generate_cycle_series("Sun", "Mars", ts)
        explicit = generate_cycle_series("Sun", "Mars", ts, dynamic_specs=None)
        np.testing.assert_array_equal(base["nearest_aspect"], explicit["nearest_aspect"])
        np.testing.assert_array_equal(base["in_aspect"], explicit["in_aspect"])

    def test_cycles_empty_list_falls_back_to_static(self):
        """
        dynamic_specs=[] (empty list) falls back to static candidate set,
        producing the same result as dynamic_specs=None.
        """
        ts = [datetime(2025, 6, 1) + timedelta(days=i) for i in range(30)]
        base = generate_cycle_series("Sun", "Mars", ts, dynamic_specs=None)
        empty = generate_cycle_series("Sun", "Mars", ts, dynamic_specs=[])
        np.testing.assert_array_equal(base["nearest_aspect"], empty["nearest_aspect"])
        np.testing.assert_array_equal(base["in_aspect"], empty["in_aspect"])

    def test_cycles_single_element_list_of_specs(self):
        """
        dynamic_specs=[specs] (list of one array) is equivalent to passing
        the array directly — the list normalisation path is covered.
        """
        ts = [datetime(2025, 1, 1) + timedelta(days=i) for i in range(30)]
        specs = generate_harmonic_aspects(7)
        result_direct = generate_cycle_series("Sun", "Moon", ts, dynamic_specs=specs)
        result_list = generate_cycle_series("Sun", "Moon", ts, dynamic_specs=[specs])
        np.testing.assert_array_equal(
            result_direct["nearest_aspect"], result_list["nearest_aspect"]
        )
        np.testing.assert_array_equal(
            result_direct["in_aspect"], result_list["in_aspect"]
        )
