"""Ketu main tests file"""

from datetime import datetime
from unittest import TestCase
from zoneinfo import ZoneInfo

import sys

sys.path.append('/home/loc/workspace/ketu/')

from ketu.ketu import (
    bodies, aspects, signs, utc_to_julian, local_to_utc, dd_to_dms, dms_to_dd, norm,
    properties, distance, calc_orb, bodies_name, bodies_orb, is_retrograd,
    is_ascending, sign, get_aspect_orb, get_aspects, find_easpect, get_chart
    )

zoneinfo = ZoneInfo('Europe/Paris')
gdate = datetime(2022, 6, 14, 13, 0, 0, tzinfo=zoneinfo)
date = utc_to_julian(gdate)
day_one = datetime(1, 1, 1)


class KetuTest(TestCase):
    """Ketu main class Test"""

    def test_bodies(self):
        """Test bodies data structure"""
        self.assertEqual(len(bodies), 12)
        self.assertEqual(bodies['swe_id'][0], 0)

    def test_aspects(self):
        """Test aspects data structure"""
        self.assertEqual(len(aspects), 7)
        self.assertEqual(aspects['angle'][0], 0)

    def test_signs(self):
        "Test signs data structure"
        self.assertEqual(len(signs), 12)
        self.assertEqual(signs[2], 'Gemini')

    def test_local_to_utc(self):
        """Test local_to_utc function"""
        self.assertEqual(
            local_to_utc(gdate), datetime(
                2022, 6, 14, 11, 0, tzinfo=ZoneInfo(key='Europe/Paris'))
        )
        print(local_to_utc(day_one))
        self.assertEqual(local_to_utc(day_one), datetime(1, 1, 1).replace(tzinfo=ZoneInfo('UTC')))

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
        props0, props1 = properties(date, 0), properties(date, 1)
        self.assertEqual(distance(props0['lon'] - props1['lon']), distance(props1['lon'] - props0['lon']))
        self.assertAlmostEqual(distance(props0['lon'] - props1['lon']), 180, delta=1)

    def test_calc_orb(self):
        """Test calc_orb function"""
        self.assertAlmostEqual(calc_orb(0, 1, 4), 8, delta=0.001)

    def test_body_name(self):
        """Test body_name function"""
        self.assertEqual("Sun", body_name(0))
        self.assertEqual("Rahu", body_name(10))

    def test_properties(self):
        """Test body_properties function"""
        self.assertAlmostEqual(properties(date, 2).lon, 60, delta=1)

    def test_body_orb(self):
        """Test body_orb function"""
        self.assertEqual(body_orb(0), 12)

    def test_is_retrograd(self):
        """Test is_retrograde function"""
        self.assertTrue(is_retrograd(properties(date, 6)))
        self.assertTrue(is_retrograd(properties(date, 10)))

    def test_is_ascending(self):
        """Test is_ascending function"""
        self.assertTrue(is_ascending(properties(date, 2)))

    def test_body_sign(self):
        """Test body_sign function"""
        self.assertEqual(
            signs[sign(properties(date, 0).lon).sign], 'Gemini')

    def test_get_aspect_orb(self):
        """Test get_aspect_orb function"""
        #self.assertAlmostEqual(get_aspect_orb(get_aspect(jdate, 0, 1)), 1, delta=1)

    def test_get_aspects(self):
        """Test get_aspects function"""
        #aspects = get_aspects(get_chart(jdate))
        #date, props, aspect, score = [
        #    asp for asp in asps if asp.swe_id[1]) == 4][0]
        #orb = distance(lon(props[0]) - lon(props[1]))
        #self.assertEqual(date, jdate)
        #self.assertEqual(get_swe_id(props[0]), 5)
        #self.assertEqual(get_swe_id(props[1]), 4)
        #self.assertEqual(aspect, 0)
        #self.assertAlmostEqual(orb, 10, delta=1)

    def test_is_applicative(self):
        """Test is_applicative"""
        # in dev mode

    def test_find_easpect(self):
        """Test find_easpect"""
        # in dev mode
        #aspect = get_aspect(date, 0, 1)
        #print(aspect)
        #print(aspect.dtype)
        #self.assertAlmostEqual(find_easpect(aspect), 2459745, delta=0.1)
