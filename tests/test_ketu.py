"""Ketu main tests file"""

from datetime import datetime
from unittest import TestCase
from zoneinfo import ZoneInfo

from numpy import array, where

from ketu.ketu import (
    bodies,
    aspects,
    signs,
    dd_to_dms,
    distance,
    get_orb,
    local_to_utc,
    utc_to_julian,
    body_name,
    body_properties as props,
    body_id,
    body_orb,
    lon,
    lat,
    dist,
    vlon,
    vlat,
    vdist,
    is_retrograde,
    is_ascending,
    body_sign,
    positions,
    get_aspect,
    get_aspects,
)

zoneinfo = ZoneInfo("Europe/Paris")
gday = datetime(2020, 12, 21, 19, 20, 0, tzinfo=zoneinfo)
jday = utc_to_julian(gday)
day_one = datetime(1, 1, 1)


class KetuTest(TestCase):
    """Ketu main class Test"""

    def test_bodies(self):
        """Test bodies data structure"""
        self.assertEqual(len(bodies), 11)
        self.assertEqual(bodies["id"][0], 0)

    def test_aspects(self):
        """Test aspects data structure"""
        self.assertEqual(len(aspects), 5)
        self.assertEqual(aspects["value"][0], 0)

    def test_signs(self):
        "Test signs data structure"
        self.assertEqual(len(signs), 12)
        self.assertEqual(signs[2], "Gemini")

    def test_local_to_utc(self):
        """Test local_to_utc function"""
        self.assertEqual(
            local_to_utc(gday), datetime(2020, 12, 21, 18, 20, tzinfo=zoneinfo)
        )
        self.assertEqual(local_to_utc(day_one), datetime(1, 1, 1))

    def test_utc_to_julian(self):
        """Test utc_to julian function"""
        self.assertEqual(utc_to_julian(day_one), 1721425.5)

    def test_dd_to_dms(self):
        """Test dd_to_dms function"""
        self.assertEqual(dd_to_dms(271.45).all(), array((271, 27, 0)).all())

    def test_distance(self):
        """Test distance function"""
        # Test reflexivity of distance
        props0, props1 = props(jday, 0), props(jday, 1)
        self.assertEqual(
            distance(lon(props0), lon(props1)),
            distance(lon(props1), lon(props0)),
        )
        self.assertAlmostEqual(distance(lon(props0), lon(props1)), 90, delta=3)

    def test_get_orb(self):
        """Test get_orb function"""
        self.assertAlmostEqual(get_orb(0, 1, 3), 8, delta=0.001)

    def test_body_name(self):
        """Test body_name function"""
        self.assertEqual("Sun", body_name(0))

    def test_body_properties(self):
        """Test body_properties function"""
        self.assertAlmostEqual(lon(props(jday, 0)), 270, delta=1)

    def test_body_id(self):
        """Test body_id function"""
        self.assertEqual(body_id("Moon"), 1)
        self.assertEqual(body_id("Rahu"), 10)

    def test_body_orb(self):
        """Test body_orb function"""
        self.assertEqual(body_orb(0), 12)

    def test_lon(self):
        """Test lon function"""
        self.assertAlmostEqual(lon(props(jday, 0)), 270, delta=1)

    def test_lat(self):
        """Test lat function"""
        self.assertAlmostEqual(lat(props(jday, 1)), -5, delta=0.3)

    def test_dist(self):
        """Test dist function"""
        self.assertAlmostEqual(dist(props(jday, 4)), 0.8, delta=0.1)

    def test_vlon(self):
        """Test vlon function"""
        self.assertAlmostEqual(vlon(props(jday, 0)), 1, delta=0.05)

    def test_vlat(self):
        """Test vlat function"""
        self.assertAlmostEqual(vlat(props(jday, 1)), 0.1, delta=0.1)

    def test_vdist(self):
        """Test vdist"""
        self.assertAlmostEqual(vdist(props(jday, 0)), 0, delta=0.1)

    def test_is_retrograde(self):
        """Test is_retrograde function"""
        self.assertTrue(is_retrograde(props(jday, 7)))
        self.assertTrue(is_retrograde(props(jday, 10)))

    def test_is_ascending(self):
        """Test is_ascending function"""
        self.assertTrue(is_ascending(props(jday, 1)))

    def test_body_sign(self):
        """Test body_sign function"""
        self.assertEqual(signs[body_sign(lon(props(jday, 0)))[0]], "Capricorn")

    def test_positions(self):
        """Test positions function"""
        sign = body_sign(positions(jday, bodies)[0])[0]
        self.assertEqual(signs[sign], "Capricorn")

    def test_get_aspect(self):
        """Test get_aspect function"""
        self.assertEqual(get_aspect(jday, 5, 6)[2], 0)
        self.assertAlmostEqual(get_aspect(jday, 5, 6)[3], 0, delta=0.1)

    def test_get_aspects(self):
        """Test get_aspects function"""
        asps = get_aspects(jday)
        asps2 = asps[where(asps["body1"] == 5)]
        body1, body2, aspect, orb = asps2[where(asps2["body2"] == 6)][0]
        self.assertEqual(body1, 5)
        self.assertEqual(body2, 6)
        self.assertEqual(aspect, 0)
        self.assertAlmostEqual(orb, 0, delta=1)

    def test_is_applicative(self):
        """Test is_applicative"""
        # in dev mode
