"""Ketu main tests file"""

from datetime import datetime
from unittest import TestCase
from zoneinfo import ZoneInfo

from ketu.ketu import (
    bodies, maspects, signs, utc_to_julian, local_to_utc, dd_to_dms, dms_to_dd, norm,
    body_properties, distance, lon, calc_orb, body_name, get_swe_id, body_orb, lat, vlon, vlat, is_retrograd,
    is_ascending, body_sign, positions, get_aspect, get_aspect_orb, get_aspects, find_easpect
    )

zoneinfo = ZoneInfo('Europe/Paris')
gdate = datetime(2022, 6, 14, 13, 0, 0, tzinfo=zoneinfo)
jdate = utc_to_julian(gdate)
day_one = datetime(1, 1, 1)


class KetuTest(TestCase):
    """Ketu main class Test"""

    def test_bodies(self):
        """Test bodies data structure"""
        self.assertEqual(len(bodies), 12)
        self.assertEqual(bodies['swe_id'][0], 0)

    def test_aspects(self):
        """Test aspects data structure"""
        self.assertEqual(len(maspects), 5)
        self.assertEqual(maspects['angle'][0], 0)

    def test_signs(self):
        "Test signs data structure"
        self.assertEqual(len(signs), 12)
        self.assertEqual(signs[2], 'Gemini')

    def test_local_to_utc(self):
        """Test local_to_utc function"""
        self.assertEqual(
            local_to_utc(gdate, zoneinfo), datetime(
                2022, 6, 14, 13, 0, tzinfo=zoneinfo)
        )
        self.assertEqual(local_to_utc(day_one), datetime(1, 1, 1, tzinfo=ZoneInfo('UTC')))

    def test_utc_to_julian(self):
        """Test utc_to julian function"""
        self.assertEqual(utc_to_julian(day_one), 1721425.5)

    def test_dd_to_dms(self):
        """Test dd_to_dms function"""
        self.assertEqual(dd_to_dms(271.45), (271, 27, 0))

    def test_dms_to_dd(self):
        """Test dms_to_dd"""
        self.assertAlmostEqual(dms_to_dd([271, 27, 0]), 271.45, delta=0.1)

    def test_norm(self):
        """Test norm function"""
        self.assertEqual(norm(-355), 5)

    def test_distance(self):
        """Test distance function"""
        # Test reflexivity of distance
        props0, props1 = body_properties(jdate, 0), body_properties(jdate, 1)
        self.assertEqual(
            distance(lon(props0) - lon(props1)),
            distance(lon(props1) - lon(props0)),
        )
        self.assertAlmostEqual(
            distance(lon(props0) - lon(props1)), 180, delta=1
        )

    def test_calc_orb(self):
        """Test calc_orb function"""
        self.assertAlmostEqual(calc_orb(0, 1, 3), 8, delta=0.001)

    def test_body_name(self):
        """Test body_name function"""
        self.assertEqual("Sun", body_name(0))

    def test_body_properties(self):
        """Test body_properties function"""
        self.assertAlmostEqual(lon(body_properties(jdate, 2)), 60, delta=1)

    def test_get_swe_id(self):
        """Test get_swe_id function"""
        props1, props2 = body_properties(jdate, 1), body_properties(jdate, 10)
        self.assertEqual(get_swe_id(props1), 1)
        self.assertEqual(get_swe_id(props2), 10)

    def test_body_orb(self):
        """Test body_orb function"""
        self.assertEqual(body_orb(0), 12)

    def test_lon(self):
        """Test lon function"""
        self.assertAlmostEqual(lon(body_properties(jdate, 0)), 83, delta=1)

    def test_lat(self):
        """Test lat function"""
        self.assertAlmostEqual(lat(body_properties(jdate, 1)), -2.7, delta=0.3)

    def test_vlon(self):
        """Test vlon function"""
        self.assertAlmostEqual(vlon(body_properties(jdate, 0)), 1, delta=0.05)

    def test_vlat(self):
        """Test vlat function"""
        self.assertAlmostEqual(vlat(body_properties(jdate, 1)), -1.17, delta=0.1)

    def test_is_retrograd(self):
        """Test is_retrograde function"""
        self.assertTrue(is_retrograd(body_properties(jdate, 6)))
        self.assertTrue(is_retrograd(body_properties(jdate, 10)))

    def test_is_ascending(self):
        """Test is_ascending function"""
        self.assertTrue(is_ascending(body_properties(jdate, 2)))

    def test_body_sign(self):
        """Test body_sign function"""
        self.assertEqual(
            signs[body_sign(*lon(body_properties(jdate, 0)))[0]], 'Gemini')

    def test_positions(self):
        """Test positions function"""
        sign = body_sign(*positions(jdate, bodies)[0])[0]
        self.assertEqual(signs[sign], 'Gemini')

    def test_get_aspect(self):
        """Test get_aspect function"""
        self.assertEqual(get_aspect(jdate, 0, 1)['i_asp'], 4)

    def test_get_aspect_orb(self):
        """Test get_aspect_orb function"""
        self.assertAlmostEqual(get_aspect_orb(get_aspect(jdate, 0, 1)), 1, delta=1)

    def test_get_aspects(self):
        """Test get_aspects function"""
        asps = get_aspects(jdate)
        b_id = get_swe_id
        date, props1, props2, aspect = [
            asp for asp in asps if b_id(asp['props2']) == 4][0]
        orb = distance(lon(props1) - lon(props2))
        self.assertEqual(date, jdate)
        self.assertEqual(get_swe_id(props1), 5)
        self.assertEqual(get_swe_id(props2), 4)
        self.assertEqual(aspect, 0)
        self.assertAlmostEqual(orb, 10, delta=1)

    def test_is_applicative(self):
        """Test is_applicative"""
        # in dev mode

    def test_find_easpect(self):
        """Test find_easpect"""
        # in dev mode
        aspect = get_aspect(jdate, 0, 1)
        print(aspect)
        print(aspect.dtype)
        self.assertAlmostEqual(find_easpect(aspect), 2459745, delta=0.1)
