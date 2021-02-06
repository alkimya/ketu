from unittest import TestCase

from ketu.ketu import *

bodies = np.arange(11)
jday = utc_to_julian(*local_to_utc(2020, 12, 21, 18, 30, 0, 1))
zero_day = utc_to_julian(-4713, 11, 24, 12, 0, 0)


class KetuTest(TestCase):

    def test_local_to_utc(self):
        self.assertAlmostEqual(local_to_utc(2020, 12, 21, 18, 30, 0, 1)[-1]
                               % -60, (2020, 12, 21, 17, 30, 0)[-1])

    def test_utc_to_julian(self):
        self.assertEqual(zero_day, 0)

    def test_dd_to_dms(self):
        self.assertEqual(dd_to_dms(271.45).all(), np.array((271, 27, 0)).all())

    def test_distance(self):
        # Test reflexivity of distance
        self.assertEqual(
            distance(body_long(jday, 0), body_long(jday, 1)),
            distance(body_long(jday, 1), body_long(jday, 0)))
        self.assertAlmostEqual(distance(body_long(jday, 0),
                                        body_long(jday, 1)), 90, delta=3)

    def test_get_orb(self):
        self.assertEqual(get_orb(0, 1, 120), 8)

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

    def test_get_aspect(self):
        self.assertEqual(get_aspect(jday, 5, 6)[2], 0)
        self.assertAlmostEqual(get_aspect(jday, 5, 6)[3], 0, delta=0.1)

    def test_get_aspects(self):
        asps = get_aspects(jday, bodies)
        asps2 = asps[np.where(asps['body1'] == 5)]
        body1, body2, aspect, orb = asps2[np.where(asps2['body2'] == 6)][0]
        self.assertEqual(aspect, 0)
        self.assertAlmostEqual(orb, 0, delta=1)

    def test_is_applicative(self):
        pass

    def test_bodies_positions(self):
        sign = body_sign(positions(jday, bodies)[0])[0]
        self.assertEqual(signs[sign], 'Capricorn')

    def test_get_all_aspects(self):
        pass
