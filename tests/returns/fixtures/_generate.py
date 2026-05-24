"""One-time fixture generator for Phase 18 oracles (Plan 18-04).

Run once. Output: 6 oracle JSON files. After running, this script is
kept under ``tests/returns/fixtures/`` as the audit trail for how the
numbers were generated -- the file is small (~120 LOC) and
grep-discoverable for future maintainers.

Six fixtures, each with self-consistency oracle data captured from the
live ``solar_return`` / ``lunar_return`` calls:

- ``oracle_solar_diana_1980.json`` -- Standard solar return.
- ``oracle_solar_curie_1900.json`` -- Long-projection solar return.
- ``oracle_solar_aries_seam_1970.json`` -- WRAP-AROUND solar return.
- ``oracle_lunar_diana_2000.json`` -- Standard lunar return.
- ``oracle_lunar_curie_day_after.json`` -- DAY-AFTER-TARGET lunar return.
- ``oracle_lunar_pisces_seam_1990.json`` -- WRAP-AROUND lunar return.

Self-consistency tolerance ``tolerance_deg=0.0001`` is the primary
regression gate. pyswisseph cross-check tolerance
``cross_check_tolerance_deg=0.001`` is the new CI-runnable cross-tool
gate (Phase 18 enhancement vs Phase 16 / 17 which had only Astro.com
deferred).

Usage:

    python tests/returns/fixtures/_generate.py

Idempotent: re-running overwrites existing fixtures with identical
output (modulo float roundoff at the 6th decimal, well below the
0.0001 tolerance). The script is NOT a pytest test -- it is the
generator, run once at fixture-creation time.
"""
from __future__ import annotations

import json
from pathlib import Path

from ketu.ephemeris.planets import calc_planet_position
from ketu.returns import lunar_return, solar_return

FIXTURE_DIR = Path(__file__).parent

# ---------------------------------------------------------------------
# Natal personas -- canonical JDs duplicated from tests/returns/conftest.py
# ---------------------------------------------------------------------
DIANA: dict[str, float | str] = {
    "jd": 2437482.28125,
    "lat": 52.83,
    "lon": 0.50,
    "name": "diana",
}
CURIE: dict[str, float | str] = {
    "jd": 2403277.941667,  # Marie Curie 1867-11-07 10:36 UT, Warsaw
    "lat": 52.23,
    "lon": 21.01,
    "name": "marie_curie",
}

# ---------------------------------------------------------------------
# Synthetic wrap-around natals
# ---------------------------------------------------------------------
# Aries-seam Sun: JD where natal Sun is near 0 deg (verified in
# tests/returns/test_solve_return.py).
ARIES_SEAM: dict[str, float | str] = {
    "jd": 2458930.0417,
    "lat": 0.0,
    "lon": 0.0,
    "name": "aries_seam",
}


def _find_moon_near_seam(year_start_jd: float) -> tuple[float, float]:
    """Scan +/-60 d for a Moon longitude in (0, 5) U (355, 360).

    Parameters
    ----------
    year_start_jd : float
        Julian Date starting point of the scan window.

    Returns
    -------
    tuple[float, float]
        ``(jd, moon_lon_deg)`` -- the first hourly JD whose Moon
        longitude lies within 5 deg of the 0/360 seam.
    """
    for dh in range(0, 60 * 24):
        jd = year_start_jd + dh / 24.0
        lon = float(calc_planet_position(jd, 1)[0])
        if lon < 5.0 or lon > 355.0:
            return jd, lon
    raise RuntimeError("no Moon near seam in 60 d window")


# 1990-01-01T00:00 UT ~ JD 2447892.5 -- scan from here.
pisces_jd, pisces_moon = _find_moon_near_seam(2447892.5)
PISCES_SEAM: dict[str, float | str] = {
    "jd": pisces_jd,
    "lat": 0.0,
    "lon": 0.0,
    "name": "pisces_seam",
}


def _fixture_for_solar(
    natal: dict[str, float | str],
    target_year: int,
    wrap_around: bool,
    notes: str,
) -> dict:
    """Build a solar-return oracle fixture by calling solar_return."""
    chart = solar_return(natal["jd"], natal["lat"], natal["lon"], target_year)
    natal_sun = float(calc_planet_position(natal["jd"], 0)[0])
    return {
        "kind": "solar",
        "natal": {
            "jd": natal["jd"],
            "lat": natal["lat"],
            "lon": natal["lon"],
            "sun_lon_deg": natal_sun,
        },
        "target_year": target_year,
        "return_lat": None,
        "return_lon": None,
        "system": "placidus",
        "expected": {
            "jd_return": float(chart["jd"]),
            "asc_deg": float(chart["asc"]),
            "mc_deg": float(chart["mc"]),
            "body_lons_deg": [float(x) for x in chart["body_lons"]],
            "cusps_deg": [float(x) for x in chart["cusps"]],
        },
        "tolerance_deg": 0.0001,
        "cross_check_tolerance_deg": 0.001,
        "wrap_around": wrap_around,
        "notes": notes,
        "cross_check_astro_com": {
            "performed": False,
            "date_performed": None,
            "delta_max_arcsec": None,
            "astro_com_settings": None,
            "notes": "Deferred follow-up; see 18-04-NOTES.md",
        },
    }


def _fixture_for_lunar(
    natal: dict[str, float | str],
    target_jd: float,
    wrap_around: bool,
    day_after_target: bool,
    notes: str,
) -> dict:
    """Build a lunar-return oracle fixture by calling lunar_return."""
    chart = lunar_return(natal["jd"], natal["lat"], natal["lon"], target_jd)
    natal_moon = float(calc_planet_position(natal["jd"], 1)[0])
    return {
        "kind": "lunar",
        "natal": {
            "jd": natal["jd"],
            "lat": natal["lat"],
            "lon": natal["lon"],
            "moon_lon_deg": natal_moon,
        },
        "target_jd": target_jd,
        "return_lat": None,
        "return_lon": None,
        "system": "placidus",
        "expected": {
            "jd_return": float(chart["jd"]),
            "asc_deg": float(chart["asc"]),
            "mc_deg": float(chart["mc"]),
            "body_lons_deg": [float(x) for x in chart["body_lons"]],
            "cusps_deg": [float(x) for x in chart["cusps"]],
        },
        "tolerance_deg": 0.0001,
        "cross_check_tolerance_deg": 0.001,
        "wrap_around": wrap_around,
        "day_after_target": day_after_target,
        "notes": notes,
        "cross_check_astro_com": {
            "performed": False,
            "date_performed": None,
            "delta_max_arcsec": None,
            "astro_com_settings": None,
            "notes": "Deferred follow-up; see 18-04-NOTES.md",
        },
    }


# ---- Solar fixtures ----
solar_diana = _fixture_for_solar(
    DIANA,
    1980,
    wrap_around=False,
    notes=(
        "Standard solar return -- Diana natal (1961-07-01), target_year=1980; "
        "natal Sun ~9 deg Cancer, far from seam."
    ),
)
solar_curie = _fixture_for_solar(
    CURIE,
    1900,
    wrap_around=False,
    notes=(
        "Long-projection solar return -- Marie Curie natal (1867), "
        "target_year=1900; 33-year span exercises seed-drift robustness."
    ),
)
solar_aries = _fixture_for_solar(
    ARIES_SEAM,
    1970,
    wrap_around=True,
    notes=(
        "WRAP-AROUND solar return -- synthetic natal with Sun near 0 deg "
        "Aries (2020-03-21 ~13:00 UT); target_year=1970 (back-projection). "
        "End-to-end pin of helper-level wrap-around handling (Plan 18-01)."
    ),
)

# ---- Lunar fixtures ----
lunar_diana = _fixture_for_lunar(
    DIANA,
    2451545.0,
    wrap_around=False,
    day_after_target=False,
    notes="Standard lunar return -- Diana natal, target_jd=2451545.0 (2000-01-01T12:00 UT).",
)

# Day-after-target case: first pass finds a return, then set target_jd
# 1 h before it; resolved JD must fall on the NEXT calendar day UTC.
_dayafter_chart_a = lunar_return(CURIE["jd"], CURIE["lat"], CURIE["lon"], 2415000.0)
_dayafter_known_jd = float(_dayafter_chart_a["jd"])
_target_jd_day_before = _dayafter_known_jd - 1.0 / 24.0
lunar_curie_day_after = _fixture_for_lunar(
    CURIE,
    _target_jd_day_before,
    wrap_around=False,
    day_after_target=True,
    notes=(
        f"DAY-AFTER-TARGET lunar return -- Curie natal, "
        f"target_jd={_target_jd_day_before:.6f} set 1h before known return "
        f"jd_return={_dayafter_known_jd:.6f}; resolved JD must fall on the "
        "next calendar day UTC. LRET-04 binding pin."
    ),
)

lunar_pisces = _fixture_for_lunar(
    PISCES_SEAM,
    PISCES_SEAM["jd"] + 14.0,
    wrap_around=True,
    day_after_target=False,
    notes=(
        f"WRAP-AROUND lunar return -- synthetic natal with Moon near 0/360 "
        f"seam (natal_jd={PISCES_SEAM['jd']:.4f}, natal_moon={pisces_moon:.4f} deg); "
        "target_jd 14 d later. End-to-end pin of helper-level wrap-around "
        "handling for Moon."
    ),
)


# ---- Serialize ----
fixtures = {
    "oracle_solar_diana_1980.json": solar_diana,
    "oracle_solar_curie_1900.json": solar_curie,
    "oracle_solar_aries_seam_1970.json": solar_aries,
    "oracle_lunar_diana_2000.json": lunar_diana,
    "oracle_lunar_curie_day_after.json": lunar_curie_day_after,
    "oracle_lunar_pisces_seam_1990.json": lunar_pisces,
}

if __name__ == "__main__":
    for filename, data in fixtures.items():
        path = FIXTURE_DIR / filename
        with path.open("w") as f:
            json.dump(data, f, indent=2)
        print(f"Wrote {path.name} -- jd_return={data['expected']['jd_return']:.6f}")
