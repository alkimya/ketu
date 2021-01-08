from unittest import TestCase

from ketu import body_name, local_to_utc, utc_to_julian, body_sign, \
    body_speed, body_longitude, distance, get_orb, is_retrograde, \
    get_aspect, signs

date = utc_to_julian(2020, 12, 30, 3, 0, 0)
fany_bday = utc_to_julian(*local_to_utc(1989, 1, 3, 21, 0, 0, 2))
zero_day = utc_to_julian(-4712, 1, 1, 12, 0, 0)


class KetuTest(TestCase):

    def test_get_body_name(self):
        self.assertEqual('Sun', body_name(0))

    def test_get_body_position(self):
        self.assertAlmostEqual(body_longitude(date, 0), 280, delta=2)

    def test_local_to_utc(self):
        self.assertAlmostEqual(local_to_utc(1975, 6, 6, 15, 10, 0, 1)[-1] % -60,
                               (1975, 6, 6, 14, 10, 0)[-1])

    def test_utc_to_julian(self):
        self.assertEqual(zero_day, 38)

    def test_get_sign(self):
        self.assertEqual(signs[body_sign(fany_bday, 0)[0]], 'Capricorn')

    def test_get_body_speed(self):
        self.assertAlmostEqual(body_speed(fany_bday, 0), 1, delta=0.02)

    def test_get_orb(self):
        self.assertEqual(get_orb(0, 1, 4), 8)

    def test_distance_is_reflexive(self):
        self.assertEqual(
            distance(body_longitude(date, 0), body_longitude(date, 1)),
            distance(body_longitude(date, 1), body_longitude(date, 0)))

    def test_distance(self):
        self.assertAlmostEqual(distance(body_longitude(date, 0),
                                        body_longitude(date, 1)),
                               180, delta=1)

    def test_is_retrograde(self):
        self.assertTrue(is_retrograde(date, 7))

    def test_get_aspect(self):
        aspect, orb = get_aspect(date, 0, 1)
        self.assertEqual(aspect, 180)
        self.assertAlmostEqual(orb, 0, delta=1)
