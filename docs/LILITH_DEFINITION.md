# Lilith (Mean Black Moon Lilith) -- Definition

> Reference document for `ketu.ephemeris.orbital.get_lilith_position`.

This document is the contract for Phase 8 (v1.1) Lilith verification. It states
which quantity Ketu computes, the exact formula it uses, the reference frame,
the source theory, and the cross-check tolerance against Swiss Ephemeris.
The History section closes with a placeholder filled in by Plan 04 once the
empirical comparison runs.

## What Ketu Computes

Ketu's "Lilith" is body index `12` with label `"Lilith"`. It is defined as the
**Mean Apogee of the Moon's orbit** -- the point on the Moon's mean orbital
ellipse furthest from Earth's centre -- projected onto the ecliptic.

This corresponds **exactly** to Swiss Ephemeris's `SE_MEAN_APOG` (Swiss
Ephemeris constant value `12`). The body-index alignment between Ketu (`12`)
and `SE_MEAN_APOG` (`12`) is intentional and frozen for the v1.x line.

What Ketu does **not** compute, and what is explicitly **out of scope for
v1.1** (deferred to v2 per requirement LIL2-01):

- True / Osculating Apogee (Swiss Ephemeris `SE_OSCU_APOG`, body index `13`).
  This is a separate quantity that includes short-period perturbations and
  oscillates around the Mean Apogee with an amplitude of up to ~30 deg.
- Asteroid Lilith #1181 (LIL2-02).
- Sidereal Lilith (any ayanamsa-shifted variant).

## Formula

The exact formula currently shipping in Ketu, quoted verbatim from
`ketu/ephemeris/orbital.py:591`:

```python
# ketu/ephemeris/orbital.py:591
lilith = normalize_angle(83.3532 + 0.1114040803 * d)
# where d = jd - 2451545.0  (days since J2000.0)
```

In algebraic form:

```text
lilith_lon = (83.3532 + 0.1114040803 * d) mod 360 degrees
where d = JD_UT - 2451545.0  (days since J2000.0)
```

Constants explained:

- `83.3532 deg`: mean longitude at J2000.0 (1 January 2000 12:00 UT).
- `0.1114040803 deg/day`: mean prograde rate, approximately `40.69 deg/year`.
- Full revolution period: approximately `8.85 years` (about `3232.6 days`),
  matching the canonical anomalistic month period of the lunar perigee/apogee
  axis.

### Where the rate `0.1114040803` appears in the codebase

The same rate constant is duplicated across three call sites. Any future
correction (Plan 04) must update all three to keep `calc_planet_position`,
`get_lilith_position`, and the structured `ORBITAL_ELEMENTS` table consistent:

1. `ketu/ephemeris/orbital.py:591` -- the longitude formula itself
   (`0.1114040803 * d`).
2. `ketu/ephemeris/orbital.py:146` -- the `ORBITAL_ELEMENTS` row for Lilith
   (last column, `0.1114040803`).
3. `ketu/ephemeris/planets.py:153` -- the `lon_speed` returned by
   `calc_planet_position` for `planet_name == "Lilith"` (`0.1114040803`).
4. `ketu/ephemeris/planets.py:458` -- the truncated `avg_speeds[12]` entry
   used by speed-ratio code (`0.111404`, six digits).

The truncation in site 4 (`0.111404` vs `0.1114040803`) is acceptable for
its purpose (heuristic average speed); it is **not** the longitude formula.

## Reference Frame

Ketu's Lilith longitude is returned in:

- **Tropical** coordinates (mean equinox of date).
- **Ecliptic of date** (mean ecliptic of date), not ICRS, not equatorial.
- **Geocentric** -- referred to Earth's centre, not topocentric.
- **Mean orbit**, projected onto the ecliptic plane (latitude is treated as
  zero; see `ketu/ephemeris/planets.py:149`).
- **Mean** (smoothed). Short-period perturbations from solar attraction are
  excluded -- those would be the True / Osculating Apogee, which is not
  implemented.

The input is **JD-UT** (Julian Date in Universal Time, no Delta-T applied).
This matches `swe.calc_ut` (the `_ut` suffix), **not** `swe.calc` (which
expects JD-TT, Terrestrial Time). The cross-check in Plan 03 must use
`swe.calc_ut` exclusively; mixing `swe.calc` would inject a Delta-T error of
roughly 70 seconds in modern dates, equivalent to about `9e-5 deg` of mean
apogee drift.

## Source

The formula derives from the **ELP-2000 lunar theory** of:

- **Chapront-Touze, M.; Chapront, J.; Francou, G.** -- Bureau des Longitudes
  (Paris).

The Mean Apogee orbital elements (mean longitude at epoch, mean rate) are
taken from this theory. Swiss Ephemeris uses **Moshier's reduction of
ELP-2000-85** to a polynomial form valid over the interval 3000 BCE to 3000
CE. Because the Mean Apogee is purely analytical, **no `.se1` ephemeris data
files are required** for `swe.calc_ut(jd, swe.MEAN_APOG)`. The Python wrapper
(`pysweph` or `pyswisseph`) ships everything needed.

Astrodienst (the Swiss Ephemeris author) describes the Mean Apogee as derived
from "the mean lunar orbit using the formula derived by Chapront,
Chapront-Touze and Francou of the Observatoire de Paris" -- the same source
attribution used here.

## Cross-Check

Plan 03 of this phase introduces a parametrized pytest harness verifying
Ketu's `get_lilith_position` against Swiss Ephemeris's `SE_MEAN_APOG`:

- **Test file:** `tests/test_lilith_cross_check.py`
- **Reference call:** `swe.calc_ut(jd, swe.MEAN_APOG)` (returns
  `(xx, retflag)`; ecliptic longitude is `xx[0]`).
- **Tolerance:** `0.01 deg` (36 arcseconds). Justified arithmetically below.
- **Sample dates:** five dates, mid-month and mid-day, spanning the years
  `1900, 1950, 2000, 2025, 2050` to expose any rate drift across the
  150-year window.
- **How to run:**

```bash
pip install -e .[test]
pytest tests/test_lilith_cross_check.py -v
```

- **Skip behaviour:** the test module begins with
  `pytest.importorskip("swisseph", minversion="2.10.3.6")`. If `pysweph` is
  not installed (e.g. user ran `pip install -e .` with no extras), the entire
  module is skipped cleanly. CI runs both with and without the `[test]`
  extra to verify the skip path works.

## Tolerance Justification

The `0.01 deg` tolerance is **not** chosen as a round number. It is derived
from the rate constant and compared to the user-facing precision contract:

- `0.01 deg = 36 arcseconds` (since `1 deg = 3600 arcseconds`).
- Mean Apogee rate: `0.111404 deg/day = 0.00464 deg/hour`.
- Rate-equivalent drift:
  `0.01 deg / (0.111404 deg/day) ~= 0.0898 days ~= 2.15 hours ~= 129 minutes`.

So `0.01 deg` is the amount the Mean Apogee moves in roughly two hours of
real time. Compare to the user contract:

- Most published printed astrological ephemerides quote Lilith to the nearest
  `0.1 deg` (six arcminutes) -- one **order of magnitude** coarser than this
  tolerance.
- Zodiac sign boundaries are `30 deg` wide -- three orders of magnitude
  coarser still.
- Aspect orbs in the Ketu default set range from 1 deg (semisextile) to 8 deg
  (conjunction/opposition) -- two to three orders of magnitude coarser than
  `0.01 deg`.

Conclusion: `0.01 deg` is **conservative** (tighter than any real consumer
needs) without being absurdly tight. A harness that fails at `0.01 deg`
indicates a systematic formula issue, not numerical noise.

## AGPL and Test-Only Dependency Note

Swiss Ephemeris (the underlying C library wrapped by `pysweph`) is licensed
under **AGPL or commercial** terms by Astrodienst AG. Ketu itself is
MIT-licensed; pulling AGPL code into Ketu's runtime wheel would force all
downstream consumers into AGPL terms, violating the project's MIT contract.

Ketu therefore uses `pysweph` **strictly as a test-only dependency**:

```toml
# pyproject.toml -- added by Plan 02 (LIL-04)
[project.optional-dependencies]
test = [
    "pysweph>=2.10.3.6",
]
```

It is **never** in `[project].dependencies`. The published wheel
(`pip install ketu`) does not pull `pysweph` and never imports `swisseph` at
runtime. This is verified empirically by Plan 02's two-venv runtime-isolation
test:

1. Fresh venv, `pip install -e .` -- `python -c "import swisseph"` MUST fail
   with `ModuleNotFoundError`.
2. Fresh venv, `pip install -e .[test]` -- `python -c "import swisseph"`
   MUST succeed and print `12` for `swisseph.MEAN_APOG`.

If step 1 succeeds, the dependency leaked into runtime and the release is
blocked. AGPL terms apply only to "the work" (the AGPL-licensed code itself);
a test-only development tool that never ships in the published wheel does
not transmit the license to downstream users -- this is standard OSS
practice (NumPy and other MIT-licensed scientific libraries follow the same
pattern for AGPL-licensed verification tools).

## History

- **v0.x -- v1.0**: formula `83.3532 + 0.1114040803 * d` shipped on PyPI.
  The constants were taken from widely circulated astrology-software
  approximations consistent with ELP-2000; the formula was **never
  externally verified** against an independent reference implementation
  (Swiss Ephemeris or otherwise).
- **v1.1 (Phase 8)**: formula verified against Swiss Ephemeris's
  `SE_MEAN_APOG` on five dates spanning 1900-2050.
  **Result: [TO BE FILLED BY PLAN 04 -- either "agreement within X.XXXX deg
  on all sampled dates, no formula change" or "formula corrected to
  A + B*d, max error reduced from M to N deg"]**.
