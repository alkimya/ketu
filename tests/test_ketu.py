from unittest import TestCase

import numpy as np

from ketu.ketu import (bodies, aspects, signs, dd_to_dms, distance, get_orb,
                       local_to_utc, utc_to_julian, body_name, body_properties,
                       body_id, body_long, body_lat, body_distance, body_vlong,
                       body_vlat, body_vdistance, is_retrograde, is_ascending,
                       body_sign, positions, get_aspect, get_aspects)

jday = utc_to_julian(*local_to_utc(2020, 12, 21, 19, 20, 0, 1))
zero_day = utc_to_julian(-4713, 11, 24, 12, 0, 0)


class KetuTest(TestCase):

    def test_bodies(self):
        self.assertEqual(len(bodies), 11)
        self.assertEqual(bodies['id'][0], 0)

    def test_aspects(self):
        self.assertEqual(len(aspects), 5)
        self.assertEqual(aspects['value'][0], 0)

    def test_signs(self):
        self.assertEqual(len(signs), 12)
        self.assertEqual(signs[2], 'Gemini')

    def test_local_to_utc(self):
        self.assertAlmostEqual(local_to_utc(2020, 12, 21, 19, 20, 0, 1)[-1]
                               % -60, (2020, 12, 21, 18, 20, 0)[-1])

    def test_utc_to_julian(self):
        self.assertEqual(zero_day, 0)

    def test_dd_to_dms(self):
        self.assertEqual(dd_to_dms(271.45).all(), np.array((271, 27, 0)).all())

    def test_distance(self):
        # Test reflexivity of distance
        dist, long = distance, body_long
        self.assertEqual(dist(long(jday, 0), long(jday, 1)),
                         dist(long(jday, 1), long(jday, 0)))
        self.assertAlmostEqual(dist(long(jday, 0), long(jday, 1)), 90, delta=3)

    def test_get_orb(self):
        self.assertAlmostEqual(get_orb(0, 1, 3), 8, delta=0.001)

    def test_body_name(self):
        self.assertEqual('Sun', body_name(0))

    def test_body_properties(self):
        self.assertAlmostEqual(body_properties(jday, 0)[0], 270, delta=1)

    def test_body_id(self):
        self.assertEqual(body_id('Moon'), 1)
        self.assertEqual(body_id('Rahu'), 10)

    def test_body_long(self):
        self.assertAlmostEqual(body_long(jday, 0), 270, delta=1)

    def test_body_lat(self):
        self.assertAlmostEqual(body_lat(jday, 1), -5, delta=0.3)

    def test_body_distance(self):
        self.assertAlmostEqual(body_distance(jday, 4), 0.8, delta=0.1)

    def test_body_vlong(self):
        self.assertAlmostEqual(body_vlong(jday, 0), 1, delta=0.05)

    def test_body_vlat(self):
        self.assertAlmostEqual(body_vlat(jday, 1), 0.1, delta=0.1)

    def test_body_vdistance(self):
        self.assertAlmostEqual(body_vdistance(jday, 0), 0, delta=0.1)

    def test_is_retrograde(self):
        self.assertTrue(is_retrograde(jday, 7))
        self.assertTrue(is_retrograde(jday, 10))

    def test_is_ascending(self):
        self.assertTrue(is_ascending(jday, 1))

    def test_body_sign(self):
        self.assertEqual(signs[body_sign(body_long(jday, 0))[0]], 'Capricorn')

    def test_positions(self):
        sign = body_sign(positions(jday, bodies)[0])[0]
        self.assertEqual(signs[sign], 'Capricorn')

    def test_get_aspect(self):
        self.assertEqual(get_aspect(jday, 5, 6)[2], 0)
        self.assertAlmostEqual(get_aspect(jday, 5, 6)[3], 0, delta=0.1)

    def test_get_aspects(self):
        asps = get_aspects(jday)
        asps2 = asps[np.where(asps['body1'] == 5)]
        body1, body2, aspect, orb = asps2[np.where(asps2['body2'] == 6)][0]
        self.assertEqual(body1, 5)
        self.assertEqual(body2, 6)
        self.assertEqual(aspect, 0)
        self.assertAlmostEqual(orb, 0, delta=1)

    def test_is_applicative(self):
        pass  # in dev mode
