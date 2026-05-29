"""
Orbital element data and Lilith constants — shared data layer.

This module is the single source of truth for ORBITAL_ELEMENTS and the
five ``_LILITH_*`` constants. All other ephemeris sub-modules import from
here; nothing in this module imports from any other ketu sub-module, which
guarantees zero circular-import risk.
"""

import numpy as np


# -----------------------------------------------------------------------------
# Lilith (Mean Black Moon Lilith = mean lunar apogee) constants.
#
# Fitted in v1.1 (Phase 8) by joint nonlinear least squares against
# ``swe.calc_ut(jd, swe.MEAN_APOG)`` over 1900-2050 (daily sampling, 55K
# points). The model is a linear secular term plus a single sinusoidal
# perturbation:
#
#   lilith = (EPOCH + RATE * d
#            + PERTURB_AMP * sin(deg(PERTURB_RATE * d + PERTURB_PHASE))) mod 360
#
# where ``d = JD_UT - 2451545.0`` (days since J2000.0).
#
# Empirical residual versus ``swe.MEAN_APOG``:
#   - max  |delta| over the 5 cross-check dates : 0.002693 deg
#   - max  |delta| over the 55K daily samples   : 0.007815 deg
#   - mean |delta| over the 55K daily samples   : 0.003190 deg
#
# All values comfortably below the 0.01 deg tolerance defined in
# docs/LILITH_DEFINITION.md Section 7.
#
# v1.0 legacy constants (pre-Phase-8) were:
#   epoch = 83.3532 deg          (off by ~180 deg: was perigee, not apogee)
#   rate  = 0.1114040803 deg/day (off in 7th+ decimal; rate-correction tiny)
# Pre-fix max |delta| against ``swe.MEAN_APOG`` was 179.94 deg on every date.
#
# These constants are PRIVATE (single source of truth). The same numerical
# values flow into:
#   - ``get_lilith_position`` body (_body_getters.py, by name)
#   - ``ORBITAL_ELEMENTS`` Lilith row (this module, M_dot column = RATE)
#   - ``ketu/ephemeris/planets.py`` ``calc_planet_position`` Lilith branch
#     (lon_speed = RATE)
#   - ``ketu/ephemeris/planets.py`` ``avg_speeds[12]`` (= round(RATE, 6))
#
# See docs/LILITH_DEFINITION.md History section for the full v1.0 -> v1.1
# story and ``tests/test_lilith_cross_check.py`` for the regression baseline.
# -----------------------------------------------------------------------------
_LILITH_MEAN_EPOCH_DEG: float = 263.3521188770
_LILITH_MEAN_RATE_DEG_PER_DAY: float = 0.1114036699
_LILITH_PERTURB_AMP_DEG: float = 0.1156754590
_LILITH_PERTURB_RATE_DEG_PER_DAY: float = 0.3287143373
_LILITH_PERTURB_PHASE_DEG: float = 96.6084061482


# Orbital elements for planets (J2000.0 epoch)
# Format: name, N, i, w, a, e, M, N_dot, i_dot, w_dot, e_dot, M_dot
# Where:
#   N = longitude of ascending node (degrees)
#   i = inclination (degrees)
#   w = argument of perihelion (degrees)
#   a = semi-major axis (AU)
#   e = eccentricity
#   M = mean anomaly at epoch (degrees)
#   *_dot = rate of change per day

ORBITAL_ELEMENTS = np.array(
    [
        # Sun (Earth's orbit) - JPL J2000.0 values (L0=100.46435, w=102.94719, M0=L0-w=357.51716)
        ("Sun", 0.0, 0.0, 102.9404, 1.000000, 0.016709, 357.5172, 0.0, 0.0, 4.70935e-5, -1.151e-9, 0.9856002585),
        # Moon - Meeus values (Ω=125.04452, M'=134.9633964)
        (
            "Moon",
            125.04452,
            5.1454,
            318.0634,
            0.002569,
            0.0549,
            134.9634,
            -0.0529538083,
            0.0,
            0.1643573223,
            0.0,
            13.0649929509,
        ),
        # Planets - JPL J2000.0 with high-precision rates
        (
            "Mercury",
            48.33076593,
            7.00497902,
            29.12703035,
            0.3870992700,
            0.2056359300,
            174.79252722,
            -3.431644353183e-06,
            -1.628334017796e-07,
            7.825262149213e-06,
            5.218343600274e-10,
            4.092334391098e+00,
        ),
        (
            "Venus",
            76.67984255,
            3.39467605,
            54.92262463,
            0.7233356600,
            0.0067767200,
            50.37663232,
            -7.602852292950e-06,
            -2.159890485969e-08,
            7.676316769336e-06,
            -1.124435318275e-09,
            1.602130395729e+00,
        ),
        (
            "Mars",
            49.55953891,
            1.84969142,
            286.50069504,
            1.5237103400,
            0.0933941000,
            19.37304145,
            -8.010223956194e-06,
            -2.226231348392e-07,
            2.017753073238e-05,
            2.157973990418e-09,
            0.524020760414e+00,
        ),
        (
            "Jupiter",
            100.47390909,
            1.30439695,
            274.25457074,
            5.2028870000,
            0.0483862400,
            19.66796068,
            5.604135797399e-06,
            -5.029815195072e-08,
            2.145275838467e-07,
            -3.628473648186e-09,
            8.308100208268e-02,
        ),
        (
            "Saturn",
            113.66242448,
            2.48599187,
            338.93645383,
            9.5366759400,
            0.0538617900,
            317.35536592,
            -7.903571252567e-06,
            5.300725530459e-08,
            -3.567261327858e-06,
            -1.396057494867e-08,
            3.348152208542e-02,
        ),
        (
            "Uranus",
            74.01692503,
            0.77263783,
            96.93735127,
            19.1891646400,
            0.0472574400,
            142.28382821,
            1.161009993155e-06,
            -6.651307323751e-08,
            1.001086707734e-05,
            -1.203832991102e-09,
            1.172002669514e-02,
        ),
        (
            "Neptune",
            131.78422574,
            1.77004347,
            273.18053653,
            30.0699227600,
            0.0085904800,
            259.91526801,
            -1.392646132786e-07,
            9.684325804244e-09,
            -8.687967145791e-06,
            1.397672826831e-09,
            5.989921092129e-03,
        ),
        # Pluto - JPL J2000.0 values (L=238.92881, w_bar=224.06676, M=L-w_bar=14.86205)
        ("Pluto", 110.30347, 17.14175, 113.76329, 39.48168677, 0.24880766, 14.86205, 0.0, 0.0, 0.0, 0.0, 0.003964),
        # Lunar nodes
        ("Rahu", 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.0529538083),  # Mean node
        ("NorthNode", 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.0529538083),  # True node
        # Lilith (Mean lunar apogee) -- M_dot = mean motion in deg/day; v1.1 value
        # sourced from _LILITH_MEAN_RATE_DEG_PER_DAY (see module-level constant).
        ("Lilith", 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, _LILITH_MEAN_RATE_DEG_PER_DAY),
    ],
    dtype=[
        ("name", "U12"),
        ("N", "f8"),
        ("i", "f8"),
        ("w", "f8"),
        ("a", "f8"),
        ("e", "f8"),
        ("M", "f8"),
        ("N_dot", "f8"),
        ("i_dot", "f8"),
        ("w_dot", "f8"),
        ("e_dot", "f8"),
        ("M_dot", "f8"),
    ],
)
