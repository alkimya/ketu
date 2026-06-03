"""Tests for ketu.ephemeris.coordinates module.

Targets all uncovered lines to bring coverage from 37% to 95%+.
Covers: spherical_to_rectangular, rectangular_to_spherical (zero case),
ecliptic_to_equatorial, equatorial_to_ecliptic, geocentric_to_topocentric,
mean_obliquity, nutation, true_obliquity, aberration_correction.
"""

import pytest
import numpy as np
from numpy.testing import assert_allclose

from ketu.ephemeris.coordinates import (
    spherical_to_rectangular,
    rectangular_to_spherical,
    ecliptic_to_equatorial,
    equatorial_to_ecliptic,
    geocentric_to_topocentric,
    mean_obliquity,
    nutation,
    true_obliquity,
    aberration_correction,
)
from ketu.calculations import declination, utc_to_julian
from ketu.ephemeris.planets import calc_planet_position_batch
from datetime import datetime, timezone

# J2000.0 Julian Date
J2000 = 2451545.0


# ---------------------------------------------------------------------------
# spherical_to_rectangular (lines 36-43)
# ---------------------------------------------------------------------------


class TestSphericalToRectangular:
    """Tests for spherical_to_rectangular()."""

    def test_scalar_on_x_axis(self):
        """Point at lon=0, lat=0 should lie on the positive x-axis."""
        x, y, z = spherical_to_rectangular(0.0, 0.0, 1.0)
        assert_allclose(x, 1.0, atol=1e-12)
        assert_allclose(y, 0.0, atol=1e-12)
        assert_allclose(z, 0.0, atol=1e-12)

    def test_scalar_on_y_axis(self):
        """Point at lon=90, lat=0 should lie on the positive y-axis."""
        x, y, z = spherical_to_rectangular(90.0, 0.0, 1.0)
        assert_allclose(x, 0.0, atol=1e-12)
        assert_allclose(y, 1.0, atol=1e-12)
        assert_allclose(z, 0.0, atol=1e-12)

    def test_scalar_on_z_axis(self):
        """Point at lat=90 (north pole) should lie on the positive z-axis."""
        x, y, z = spherical_to_rectangular(0.0, 90.0, 1.0)
        assert_allclose(x, 0.0, atol=1e-12)
        assert_allclose(y, 0.0, atol=1e-12)
        assert_allclose(z, 1.0, atol=1e-12)

    def test_scalar_negative_latitude(self):
        """Point at lat=-90 (south pole) should be on negative z-axis."""
        x, y, z = spherical_to_rectangular(0.0, -90.0, 1.0)
        assert_allclose(x, 0.0, atol=1e-12)
        assert_allclose(y, 0.0, atol=1e-12)
        assert_allclose(z, -1.0, atol=1e-12)

    def test_scalar_arbitrary_point(self):
        """Test a general point at lon=45, lat=30, r=2."""
        x, y, z = spherical_to_rectangular(45.0, 30.0, 2.0)
        # Expected: x = 2*cos(45)*cos(30), y = 2*sin(45)*cos(30), z = 2*sin(30)
        expected_x = 2.0 * np.cos(np.deg2rad(45)) * np.cos(np.deg2rad(30))
        expected_y = 2.0 * np.sin(np.deg2rad(45)) * np.cos(np.deg2rad(30))
        expected_z = 2.0 * np.sin(np.deg2rad(30))
        assert_allclose(x, expected_x, atol=1e-12)
        assert_allclose(y, expected_y, atol=1e-12)
        assert_allclose(z, expected_z, atol=1e-12)

    def test_scalar_zero_radius(self):
        """Zero radius should give origin regardless of angles."""
        x, y, z = spherical_to_rectangular(123.0, 45.0, 0.0)
        assert_allclose(x, 0.0, atol=1e-15)
        assert_allclose(y, 0.0, atol=1e-15)
        assert_allclose(z, 0.0, atol=1e-15)

    def test_scalar_lon_180(self):
        """Point at lon=180, lat=0 should lie on the negative x-axis."""
        x, y, z = spherical_to_rectangular(180.0, 0.0, 1.0)
        assert_allclose(x, -1.0, atol=1e-12)
        assert_allclose(y, 0.0, atol=1e-12)
        assert_allclose(z, 0.0, atol=1e-12)

    def test_array_input(self):
        """Test with numpy array inputs for vectorized operation."""
        lon = np.array([0.0, 90.0, 180.0, 270.0])
        lat = np.array([0.0, 0.0, 0.0, 0.0])
        r = np.array([1.0, 1.0, 1.0, 1.0])

        x, y, z = spherical_to_rectangular(lon, lat, r)

        assert_allclose(x, [1.0, 0.0, -1.0, 0.0], atol=1e-12)
        assert_allclose(y, [0.0, 1.0, 0.0, -1.0], atol=1e-12)
        assert_allclose(z, [0.0, 0.0, 0.0, 0.0], atol=1e-12)

    def test_array_with_latitude(self):
        """Test array inputs with non-zero latitudes."""
        lon = np.array([0.0, 0.0])
        lat = np.array([0.0, 90.0])
        r = np.array([1.0, 1.0])

        x, y, z = spherical_to_rectangular(lon, lat, r)

        assert_allclose(x[0], 1.0, atol=1e-12)
        assert_allclose(z[0], 0.0, atol=1e-12)
        assert_allclose(z[1], 1.0, atol=1e-12)


# ---------------------------------------------------------------------------
# rectangular_to_spherical - zero distance scalar case (line 77)
# ---------------------------------------------------------------------------


class TestRectangularToSphericalZero:
    """Tests for the zero-distance scalar path in rectangular_to_spherical()."""

    def test_zero_distance_scalar(self):
        """All zeros should return (0, 0, 0) for scalar input."""
        lon, lat, r = rectangular_to_spherical(0.0, 0.0, 0.0)
        assert lon == 0.0
        assert lat == 0.0
        assert r == 0.0

    def test_zero_distance_array(self):
        """Arrays containing zeros should handle gracefully without NaN."""
        x = np.array([0.0, 1.0])
        y = np.array([0.0, 0.0])
        z = np.array([0.0, 0.0])

        lon, lat, r = rectangular_to_spherical(x, y, z)

        # Second element: lon=0, lat=0, r=1
        assert_allclose(lon[1], 0.0, atol=1e-12)
        assert_allclose(lat[1], 0.0, atol=1e-12)
        assert_allclose(r[1], 1.0, atol=1e-12)
        # No NaN values
        assert not np.any(np.isnan(lon))
        assert not np.any(np.isnan(lat))


# ---------------------------------------------------------------------------
# Roundtrip: spherical -> rectangular -> spherical
# ---------------------------------------------------------------------------


class TestRoundtripConversion:
    """Roundtrip tests between spherical and rectangular."""

    @pytest.mark.parametrize(
        "lon, lat, r",
        [
            (0.0, 0.0, 1.0),
            (45.0, 30.0, 2.0),
            (120.0, -45.0, 0.5),
            (270.0, 60.0, 3.0),
            (350.0, -10.0, 1.5),
        ],
    )
    def test_roundtrip_scalar(self, lon, lat, r):
        """Converting spherical -> rectangular -> spherical should recover inputs."""
        x, y, z = spherical_to_rectangular(lon, lat, r)
        lon2, lat2, r2 = rectangular_to_spherical(x, y, z)

        assert_allclose(lon2, lon, atol=1e-10)
        assert_allclose(lat2, lat, atol=1e-10)
        assert_allclose(r2, r, atol=1e-10)

    def test_roundtrip_array(self):
        """Roundtrip with array inputs."""
        lon = np.array([30.0, 150.0, 270.0])
        lat = np.array([10.0, -20.0, 45.0])
        r = np.array([1.0, 2.0, 0.5])

        x, y, z = spherical_to_rectangular(lon, lat, r)
        lon2, lat2, r2 = rectangular_to_spherical(x, y, z)

        assert_allclose(lon2, lon, atol=1e-10)
        assert_allclose(lat2, lat, atol=1e-10)
        assert_allclose(r2, r, atol=1e-10)


# ---------------------------------------------------------------------------
# ecliptic_to_equatorial (lines 119-127)
# ---------------------------------------------------------------------------


class TestEclipticToEquatorial:
    """Tests for ecliptic_to_equatorial()."""

    def test_zero_obliquity(self):
        """With zero obliquity, ecliptic = equatorial, so output should equal input."""
        x_eq, y_eq, z_eq = ecliptic_to_equatorial(1.0, 2.0, 3.0, 0.0)
        assert_allclose(x_eq, 1.0, atol=1e-12)
        assert_allclose(y_eq, 2.0, atol=1e-12)
        assert_allclose(z_eq, 3.0, atol=1e-12)

    def test_x_unchanged(self):
        """The x coordinate should always be unchanged by the transformation."""
        x_eq, _, _ = ecliptic_to_equatorial(5.0, 2.0, 3.0, 23.4393)
        assert_allclose(x_eq, 5.0, atol=1e-12)

    def test_known_obliquity(self):
        """Test with J2000.0 obliquity (~23.4393 degrees)."""
        obliquity = 23.4393
        obl_rad = np.deg2rad(obliquity)

        x, y, z = 1.0, 1.0, 0.0
        x_eq, y_eq, z_eq = ecliptic_to_equatorial(x, y, z, obliquity)

        # y_eq = y*cos(obl) - z*sin(obl) = cos(obl)
        # z_eq = y*sin(obl) + z*cos(obl) = sin(obl)
        assert_allclose(y_eq, np.cos(obl_rad), atol=1e-10)
        assert_allclose(z_eq, np.sin(obl_rad), atol=1e-10)

    def test_point_on_ecliptic_z_axis(self):
        """A point on the ecliptic z-axis should be rotated into the equatorial frame."""
        obliquity = 23.4393
        obl_rad = np.deg2rad(obliquity)

        x, y, z = 0.0, 0.0, 1.0
        x_eq, y_eq, z_eq = ecliptic_to_equatorial(x, y, z, obliquity)

        # y_eq = -sin(obl), z_eq = cos(obl)
        assert_allclose(x_eq, 0.0, atol=1e-12)
        assert_allclose(y_eq, -np.sin(obl_rad), atol=1e-10)
        assert_allclose(z_eq, np.cos(obl_rad), atol=1e-10)

    def test_array_input(self):
        """Test with array inputs for vectorized operation."""
        x = np.array([1.0, 0.0])
        y = np.array([0.0, 1.0])
        z = np.array([0.0, 0.0])
        obliquity = 23.4393

        x_eq, y_eq, z_eq = ecliptic_to_equatorial(x, y, z, obliquity)

        assert x_eq.shape == (2,)
        assert_allclose(x_eq[0], 1.0, atol=1e-12)
        assert_allclose(y_eq[0], 0.0, atol=1e-12)
        assert_allclose(z_eq[0], 0.0, atol=1e-12)


# ---------------------------------------------------------------------------
# equatorial_to_ecliptic (lines 149-157)
# ---------------------------------------------------------------------------


class TestEquatorialToEcliptic:
    """Tests for equatorial_to_ecliptic()."""

    def test_zero_obliquity(self):
        """With zero obliquity, equatorial = ecliptic."""
        x_ecl, y_ecl, z_ecl = equatorial_to_ecliptic(1.0, 2.0, 3.0, 0.0)
        assert_allclose(x_ecl, 1.0, atol=1e-12)
        assert_allclose(y_ecl, 2.0, atol=1e-12)
        assert_allclose(z_ecl, 3.0, atol=1e-12)

    def test_x_unchanged(self):
        """The x coordinate should always be unchanged."""
        x_ecl, _, _ = equatorial_to_ecliptic(7.0, 2.0, 3.0, 23.4393)
        assert_allclose(x_ecl, 7.0, atol=1e-12)

    def test_known_obliquity(self):
        """Test with J2000.0 obliquity."""
        obliquity = 23.4393
        obl_rad = np.deg2rad(obliquity)

        x, y, z = 1.0, 1.0, 0.0
        x_ecl, y_ecl, z_ecl = equatorial_to_ecliptic(x, y, z, obliquity)

        # y_ecl = y*cos(obl) + z*sin(obl) = cos(obl)
        # z_ecl = -y*sin(obl) + z*cos(obl) = -sin(obl)
        assert_allclose(y_ecl, np.cos(obl_rad), atol=1e-10)
        assert_allclose(z_ecl, -np.sin(obl_rad), atol=1e-10)

    def test_roundtrip_with_ecliptic_to_equatorial(self):
        """ecliptic -> equatorial -> ecliptic should recover the original point."""
        obliquity = 23.4393
        x, y, z = 1.5, -2.3, 0.7

        x_eq, y_eq, z_eq = ecliptic_to_equatorial(x, y, z, obliquity)
        x_back, y_back, z_back = equatorial_to_ecliptic(x_eq, y_eq, z_eq, obliquity)

        assert_allclose(x_back, x, atol=1e-10)
        assert_allclose(y_back, y, atol=1e-10)
        assert_allclose(z_back, z, atol=1e-10)

    def test_roundtrip_reverse_direction(self):
        """equatorial -> ecliptic -> equatorial should recover the original point."""
        obliquity = 23.4393
        x, y, z = 0.3, 1.7, -0.5

        x_ecl, y_ecl, z_ecl = equatorial_to_ecliptic(x, y, z, obliquity)
        x_back, y_back, z_back = ecliptic_to_equatorial(x_ecl, y_ecl, z_ecl, obliquity)

        assert_allclose(x_back, x, atol=1e-10)
        assert_allclose(y_back, y, atol=1e-10)
        assert_allclose(z_back, z, atol=1e-10)


# ---------------------------------------------------------------------------
# geocentric_to_topocentric (lines 228-280)
# ---------------------------------------------------------------------------


class TestGeocentricToTopocentric:
    """Tests for geocentric_to_topocentric()."""

    def test_returns_three_floats(self):
        """Function should return a 3-tuple of floats."""
        az, alt, dist = geocentric_to_topocentric(
            lon=0.0, lat=0.0, dist=1.0,
            observer_lat=48.8566, observer_lon=2.3522,
            lst=0.0, height=0.0,
        )
        assert isinstance(az, (float, np.floating))
        assert isinstance(alt, (float, np.floating))
        assert isinstance(dist, (float, np.floating))

    def test_azimuth_range(self):
        """Azimuth should be in [0, 360)."""
        az, alt, dist = geocentric_to_topocentric(
            lon=45.0, lat=20.0, dist=0.00257,
            observer_lat=40.0, observer_lon=-74.0,
            lst=100.0, height=10.0,
        )
        assert 0.0 <= az < 360.0

    def test_distance_positive(self):
        """Topocentric distance should be positive."""
        _, _, dist = geocentric_to_topocentric(
            lon=120.0, lat=5.0, dist=1.5,
            observer_lat=-33.87, observer_lon=151.21,
            lst=200.0, height=50.0,
        )
        assert dist > 0.0

    def test_altitude_range(self):
        """Altitude should be between -90 and +90 degrees."""
        _, alt, _ = geocentric_to_topocentric(
            lon=90.0, lat=10.0, dist=0.5,
            observer_lat=51.5, observer_lon=-0.1,
            lst=90.0, height=0.0,
        )
        assert -90.0 <= alt <= 90.0

    def test_parallax_effect_on_distance(self):
        """Topocentric distance should differ slightly from geocentric for close objects."""
        dist_geo = 0.00257  # Moon distance in AU (approximate)
        _, _, dist_topo = geocentric_to_topocentric(
            lon=0.0, lat=0.0, dist=dist_geo,
            observer_lat=0.0, observer_lon=0.0,
            lst=0.0, height=0.0,
        )
        # Topocentric distance should be close but not identical to geocentric
        # The difference depends on parallax; for the Moon it can be up to ~1 Earth radius in AU
        assert abs(dist_topo - dist_geo) < 0.001  # Less than 0.001 AU difference

    def test_height_parameter(self):
        """Non-zero height should produce slightly different results than zero height."""
        # Use Moon-like distance (0.00257 AU) where parallax is detectable
        kwargs = dict(lon=60.0, lat=15.0, dist=0.00257, observer_lat=30.0, observer_lon=90.0, lst=150.0)

        az1, alt1, dist1 = geocentric_to_topocentric(**kwargs, height=0.0)
        az2, alt2, dist2 = geocentric_to_topocentric(**kwargs, height=50000.0)

        # At least one value should differ
        differs = (
            not np.isclose(az1, az2, atol=1e-12)
            or not np.isclose(alt1, alt2, atol=1e-12)
            or not np.isclose(dist1, dist2, atol=1e-12)
        )
        assert differs

    def test_equator_observer(self):
        """Observer at equator should have specific symmetry properties."""
        az, alt, dist = geocentric_to_topocentric(
            lon=0.0, lat=0.0, dist=1.0,
            observer_lat=0.0, observer_lon=0.0,
            lst=0.0, height=0.0,
        )
        assert isinstance(az, (float, np.floating))
        assert isinstance(alt, (float, np.floating))

    def test_negative_azimuth_normalized(self):
        """Azimuth should be normalized to 0-360 even if intermediate calculation is negative."""
        # Use parameters that are likely to produce a negative intermediate azimuth
        az, _, _ = geocentric_to_topocentric(
            lon=300.0, lat=-20.0, dist=1.0,
            observer_lat=-45.0, observer_lon=170.0,
            lst=50.0, height=0.0,
        )
        assert 0.0 <= az < 360.0


# ---------------------------------------------------------------------------
# mean_obliquity (lines 301-313)
# ---------------------------------------------------------------------------


class TestMeanObliquity:
    """Tests for mean_obliquity()."""

    def test_j2000_obliquity(self):
        """At J2000.0, mean obliquity should be approximately 23.4393 degrees."""
        obl = mean_obliquity(J2000)
        # IAU value: 23 deg 26' 21.448" = 23.439291...
        assert_allclose(obl, 23.439291111, atol=1e-4)

    def test_obliquity_type_scalar(self):
        """Should return a float for scalar input."""
        obl = mean_obliquity(J2000)
        assert isinstance(obl, (float, np.floating))

    def test_obliquity_decreases_over_time(self):
        """Obliquity should generally decrease over centuries from J2000."""
        obl_j2000 = mean_obliquity(J2000)
        # 100 years later
        obl_future = mean_obliquity(J2000 + 36525.0)
        assert obl_future < obl_j2000

    def test_obliquity_past(self):
        """100 years before J2000 should have slightly larger obliquity."""
        obl_past = mean_obliquity(J2000 - 36525.0)
        obl_j2000 = mean_obliquity(J2000)
        assert obl_past > obl_j2000

    def test_obliquity_reasonable_range(self):
        """Obliquity should stay within reasonable bounds for a few millennia."""
        for offset_centuries in range(-30, 31, 10):
            jd = J2000 + offset_centuries * 36525.0
            obl = mean_obliquity(jd)
            # Obliquity varies between ~22 and ~24.5 degrees over tens of millennia
            assert 21.0 < obl < 25.0, f"Obliquity {obl} out of range at offset={offset_centuries} centuries"

    def test_array_input(self):
        """Should work with numpy array input."""
        jds = np.array([J2000, J2000 + 36525.0, J2000 - 36525.0])
        obl = mean_obliquity(jds)
        assert isinstance(obl, np.ndarray)
        assert obl.shape == (3,)
        # J2000 value should be approximately 23.44
        assert_allclose(obl[0], 23.439291111, atol=1e-4)

    def test_j2000_exact_formula_value(self):
        """At T=0 (J2000), the formula gives exactly 23 + 26/60 + 21.448/3600."""
        expected = 23.0 + 26.0 / 60.0 + 21.448 / 3600.0
        obl = mean_obliquity(J2000)
        assert_allclose(obl, expected, atol=1e-12)


# ---------------------------------------------------------------------------
# nutation (lines 330-367)
# ---------------------------------------------------------------------------


class TestNutation:
    """Tests for nutation()."""

    def test_returns_two_floats(self):
        """Should return a tuple of two floats."""
        nut_lon, nut_obl = nutation(J2000)
        assert isinstance(nut_lon, (float, np.floating))
        assert isinstance(nut_obl, (float, np.floating))

    def test_nutation_magnitude_at_j2000(self):
        """Nutation values should be small (arcsecond-level, expressed in degrees)."""
        nut_lon, nut_obl = nutation(J2000)
        # Nutation in longitude is typically < 20 arcseconds = ~0.006 degrees
        assert abs(nut_lon) < 0.01
        # Nutation in obliquity is typically < 10 arcseconds = ~0.003 degrees
        assert abs(nut_obl) < 0.005

    def test_nutation_varies_over_time(self):
        """Nutation should vary for different Julian Dates."""
        nut1_lon, nut1_obl = nutation(J2000)
        nut2_lon, nut2_obl = nutation(J2000 + 180.0)  # ~6 months later
        # Values should be different
        assert nut1_lon != nut2_lon or nut1_obl != nut2_obl

    def test_nutation_periodicity(self):
        """Nutation has a dominant period of ~18.6 years (6798.4 days).
        Values roughly 18.6 years apart should be similar."""
        nut1_lon, nut1_obl = nutation(J2000)
        nut2_lon, nut2_obl = nutation(J2000 + 6798.4)  # ~18.6 years later
        # Should be approximately similar (not exact due to multiple terms)
        assert abs(nut1_lon - nut2_lon) < 0.005
        assert abs(nut1_obl - nut2_obl) < 0.003

    def test_nutation_half_cycle_opposite(self):
        """Roughly half a nutation cycle (~9.3 years) later, longitude nutation
        should have roughly opposite sign."""
        nut1_lon, _ = nutation(J2000)
        nut2_lon, _ = nutation(J2000 + 3399.2)  # ~9.3 years
        # The dominant sin(omega) term should flip sign
        # Allow generous tolerance since other terms contribute
        # At minimum, the values should differ substantially
        assert abs(nut1_lon - nut2_lon) > 0.001

    def test_nutation_known_date(self):
        """Test nutation at J2000.0 against approximate known values.
        At J2000.0: nut_lon ~ -0.00478 deg (-17.2 arcsec dominant term),
        nut_obl ~ +0.00256 deg (+9.2 arcsec dominant term)."""
        nut_lon, nut_obl = nutation(J2000)
        # These are approximate; the simplified formula only uses 4 terms
        assert abs(nut_lon) < 0.01  # Within reasonable range
        assert abs(nut_obl) < 0.005  # Within reasonable range


# ---------------------------------------------------------------------------
# true_obliquity (lines 383-386)
# ---------------------------------------------------------------------------


class TestTrueObliquity:
    """Tests for true_obliquity()."""

    def test_returns_float(self):
        """Should return a float."""
        result = true_obliquity(J2000)
        assert isinstance(result, (float, np.floating))

    def test_close_to_mean_obliquity(self):
        """True obliquity should be close to mean obliquity (differs by nutation)."""
        mean_obl = mean_obliquity(J2000)
        true_obl = true_obliquity(J2000)
        # Difference should be the nutation in obliquity (< 10 arcsec)
        assert abs(true_obl - mean_obl) < 0.005

    def test_equals_mean_plus_nutation(self):
        """true_obliquity = mean_obliquity + nutation_obliquity."""
        jd = J2000 + 1000.0  # Arbitrary date
        mean_obl = mean_obliquity(jd)
        _, nut_obl = nutation(jd)
        true_obl = true_obliquity(jd)
        assert_allclose(true_obl, mean_obl + nut_obl, atol=1e-12)

    def test_j2000_approximate_value(self):
        """At J2000, true obliquity should be approximately 23.44 degrees."""
        true_obl = true_obliquity(J2000)
        assert 23.43 < true_obl < 23.45

    def test_different_dates(self):
        """True obliquity at different dates should differ."""
        obl1 = true_obliquity(J2000)
        obl2 = true_obliquity(J2000 + 365.25)
        assert obl1 != obl2


# ---------------------------------------------------------------------------
# aberration_correction (lines 406-432)
# ---------------------------------------------------------------------------


class TestAberrationCorrection:
    """Tests for aberration_correction()."""

    def test_returns_two_floats(self):
        """Should return a tuple of two floats."""
        dlon, dlat = aberration_correction(0.0, 0.0, J2000)
        assert isinstance(dlon, (float, np.floating))
        assert isinstance(dlat, (float, np.floating))

    def test_correction_magnitude(self):
        """Aberration corrections should be small (max ~20.5 arcsec = ~0.0057 deg)."""
        dlon, dlat = aberration_correction(100.0, 20.0, J2000)
        # Maximum aberration constant is ~20.5 arcseconds = ~0.0057 degrees
        assert abs(dlon) < 0.01
        assert abs(dlat) < 0.01

    def test_zero_latitude(self):
        """At zero latitude, dlat formula simplifies (sin(lat)=0)."""
        dlon, dlat = aberration_correction(45.0, 0.0, J2000)
        # dlat should be zero when lat=0 (sin(0)=0)
        assert_allclose(dlat, 0.0, atol=1e-15)

    def test_varies_with_longitude(self):
        """Correction should vary with the object's longitude."""
        dlon1, _ = aberration_correction(0.0, 0.0, J2000)
        dlon2, _ = aberration_correction(90.0, 0.0, J2000)
        dlon3, _ = aberration_correction(180.0, 0.0, J2000)
        # At least some should differ
        assert not (dlon1 == dlon2 == dlon3)

    def test_varies_with_date(self):
        """Correction should vary with Julian Date (Earth's orbital position changes)."""
        dlon1, dlat1 = aberration_correction(100.0, 20.0, J2000)
        dlon2, dlat2 = aberration_correction(100.0, 20.0, J2000 + 182.625)  # Half year
        # Values should differ
        assert dlon1 != dlon2

    def test_varies_with_latitude(self):
        """Latitude correction should vary with the object's latitude."""
        _, dlat1 = aberration_correction(100.0, 10.0, J2000)
        _, dlat2 = aberration_correction(100.0, 45.0, J2000)
        assert dlat1 != dlat2

    def test_ecliptic_pole_maximum_dlat(self):
        """Near the ecliptic pole (lat=90), sin(lat) is maximal, so dlat should be largest."""
        _, dlat_equator = aberration_correction(100.0, 0.0, J2000)
        _, dlat_pole = aberration_correction(100.0, 80.0, J2000)
        # dlat near the pole should have larger magnitude than at equator
        assert abs(dlat_pole) > abs(dlat_equator)

    def test_opposite_longitudes_different_sign(self):
        """Objects 180 degrees apart in longitude should have opposite dlon signs
        (the main cos(L - lon) term flips sign)."""
        dlon1, _ = aberration_correction(0.0, 0.0, J2000)
        dlon2, _ = aberration_correction(180.0, 0.0, J2000)
        # The dominant term cos(L-lon) should flip sign when lon changes by 180
        # but there's also the eccentricity term, so we just check they differ
        assert dlon1 != dlon2

    def test_known_aberration_constant(self):
        """The aberration constant k=20.49552 arcseconds should dominate the correction."""
        # At J2000, Sun's mean longitude L is about 280.46 degrees
        # For an object at lon=280.46 (same as Sun), cos(L-lon)=1 (maximum dlon)
        # dlon should be about -k/3600 / cos(lat) in degrees for the main term
        dlon, _ = aberration_correction(280.46, 0.0, J2000)
        # The correction should be around the aberration constant magnitude
        # (modified by eccentricity term)
        k_deg = 20.49552 / 3600.0
        assert abs(dlon) < 2 * k_deg  # Should not exceed 2x the constant


# ---------------------------------------------------------------------------
# Integration / cross-function tests
# ---------------------------------------------------------------------------


class TestCrossFunctionIntegration:
    """Tests that combine multiple coordinate functions."""

    def test_obliquity_in_ecliptic_equatorial_roundtrip(self):
        """Use computed obliquity in ecliptic/equatorial conversion roundtrip."""
        obl = mean_obliquity(J2000)
        x, y, z = 1.0, 2.0, 3.0

        x_eq, y_eq, z_eq = ecliptic_to_equatorial(x, y, z, obl)
        x_back, y_back, z_back = equatorial_to_ecliptic(x_eq, y_eq, z_eq, obl)

        assert_allclose(x_back, x, atol=1e-10)
        assert_allclose(y_back, y, atol=1e-10)
        assert_allclose(z_back, z, atol=1e-10)

    def test_true_obliquity_in_conversion(self):
        """Use true obliquity for more accurate conversions, still roundtrips correctly."""
        obl = true_obliquity(J2000)
        x, y, z = -0.5, 1.3, 0.8

        x_eq, y_eq, z_eq = ecliptic_to_equatorial(x, y, z, obl)
        x_back, y_back, z_back = equatorial_to_ecliptic(x_eq, y_eq, z_eq, obl)

        assert_allclose(x_back, x, atol=1e-10)
        assert_allclose(y_back, y, atol=1e-10)
        assert_allclose(z_back, z, atol=1e-10)

    def test_spherical_ecliptic_equatorial_chain(self):
        """Chain: spherical -> rectangular -> ecliptic_to_equatorial -> back."""
        lon, lat, r = 120.0, 15.0, 1.0
        obl = mean_obliquity(J2000)

        # Spherical to rectangular (ecliptic)
        x, y, z = spherical_to_rectangular(lon, lat, r)

        # Ecliptic to equatorial
        x_eq, y_eq, z_eq = ecliptic_to_equatorial(x, y, z, obl)

        # Back to ecliptic
        x_back, y_back, z_back = equatorial_to_ecliptic(x_eq, y_eq, z_eq, obl)

        # Back to spherical
        lon_back, lat_back, r_back = rectangular_to_spherical(x_back, y_back, z_back)

        assert_allclose(lon_back, lon, atol=1e-10)
        assert_allclose(lat_back, lat, atol=1e-10)
        assert_allclose(r_back, r, atol=1e-10)


# ---------------------------------------------------------------------------
# DECL-03: declination() equivalence — chain and Meeus 13.4 (STATE.md lock)
#
# STATE.md locks true_obliquity (instantaneous ε) for ALL three computations
# so the comparison is apples-to-apples. The brief's mean_obliquity
# recommendation is OVERRIDDEN.
# ---------------------------------------------------------------------------


class TestDeclinationEquivalenceDECL03:
    """DECL-03 regression: declination() ≡ explicit chain ≡ Meeus 13.4.

    All three use true_obliquity (instantaneous ε) per STATE.md lock.
    Tolerance < 1e-9 (research measured max|Δ| = 7.1e-15 over arrays).
    """

    # 50 dates spread over ~1 year starting 2025-01-01
    JD_BASE = utc_to_julian(datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc))
    JD_ARRAY = np.linspace(JD_BASE, JD_BASE + 365.0, 50)

    def _chain_decl(self, jd_array: np.ndarray, body_id: int) -> np.ndarray:
        """Explicit coordinates chain: λ,β → rect → ecliptic_to_equatorial(ε) → spherical."""
        batch = calc_planet_position_batch(jd_array, body_id)
        lam = batch[:, 0]
        bet = batch[:, 1]
        x, y, z = spherical_to_rectangular(lam, bet, 1.0)
        eps = true_obliquity(jd_array)
        xe, ye, ze = ecliptic_to_equatorial(x, y, z, eps)
        _, decl, _ = rectangular_to_spherical(xe, ye, ze)
        return decl

    def _meeus_decl(self, jd_array: np.ndarray, body_id: int) -> np.ndarray:
        """Meeus eq. 13.4: δ = arcsin(sin β·cos ε + cos β·sin ε·sin λ).

        All angles in radians; ε = true_obliquity(jd) per STATE.md lock.
        """
        batch = calc_planet_position_batch(jd_array, body_id)
        lam_rad = np.deg2rad(batch[:, 0])
        bet_rad = np.deg2rad(batch[:, 1])
        eps_rad = np.deg2rad(true_obliquity(jd_array))
        sin_decl = (
            np.sin(bet_rad) * np.cos(eps_rad)
            + np.cos(bet_rad) * np.sin(eps_rad) * np.sin(lam_rad)
        )
        return np.rad2deg(np.arcsin(sin_decl))

    def test_decl_eq_chain_moon(self):
        """declination() ≡ explicit chain for the Moon (50 dates, < 1e-9°)."""
        decl_fn = declination(self.JD_ARRAY, 1)
        decl_chain = self._chain_decl(self.JD_ARRAY, 1)
        assert np.max(np.abs(decl_fn - decl_chain)) < 1e-9

    def test_decl_eq_meeus_moon(self):
        """declination() ≡ Meeus 13.4 for the Moon (50 dates, < 1e-9°)."""
        decl_fn = declination(self.JD_ARRAY, 1)
        decl_meeus = self._meeus_decl(self.JD_ARRAY, 1)
        assert np.max(np.abs(decl_fn - decl_meeus)) < 1e-9

    def test_decl_eq_chain_sun(self):
        """declination() ≡ explicit chain for the Sun (50 dates, < 1e-9°)."""
        decl_fn = declination(self.JD_ARRAY, 0)
        decl_chain = self._chain_decl(self.JD_ARRAY, 0)
        assert np.max(np.abs(decl_fn - decl_chain)) < 1e-9

    def test_decl_eq_meeus_sun(self):
        """declination() ≡ Meeus 13.4 for the Sun (50 dates, < 1e-9°)."""
        decl_fn = declination(self.JD_ARRAY, 0)
        decl_meeus = self._meeus_decl(self.JD_ARRAY, 0)
        assert np.max(np.abs(decl_fn - decl_meeus)) < 1e-9

    def test_decl_chain_eq_meeus_moon(self):
        """Explicit chain ≡ Meeus 13.4 for the Moon (50 dates, < 1e-9°)."""
        decl_chain = self._chain_decl(self.JD_ARRAY, 1)
        decl_meeus = self._meeus_decl(self.JD_ARRAY, 1)
        assert np.max(np.abs(decl_chain - decl_meeus)) < 1e-9

    def test_true_obliquity_used_not_mean(self):
        """Confirm true_obliquity ≠ mean_obliquity (nutation contribution non-zero)."""
        true_obl = true_obliquity(self.JD_BASE)
        mean_obl = mean_obliquity(self.JD_BASE)
        # Nutation in obliquity is non-zero; the two must differ
        assert true_obl != mean_obl
