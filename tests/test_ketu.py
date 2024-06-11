from datetime import datetime
from unittest import TestCase
from zoneinfo import ZoneInfo

from numpy import array, where, dtype

from ketu.ketu import (
    bodies,
    aspects,
    signs,
    degrees_to_dms,
    local_to_utc,
    utc_to_julian,
    julian_to_utc,
    is_retrograd,
    is_ascending,
)

zoneinfo = ZoneInfo("Europe/Paris")
gday = datetime(2020, 12, 21, 19, 20, 0, tzinfo=zoneinfo)
jday = utc_to_julian(gday)
day_one = datetime(1, 1, 1)
utc = ZoneInfo("UTC")


class KetuTest(TestCase):

    def test_bodies(self):
        self.assertEqual(len(bodies), 12)
        self.assertEqual(bodies["swe_id"][0], 0)

    def test_aspects(self):
        self.assertEqual(len(aspects), 7)
        self.assertEqual(aspects["angle"][0], 0)

    def test_signs(self):
        self.assertEqual(len(signs), 12)
        self.assertEqual(signs[2], "Gemini")

    def test_local_to_utc(self):
        self.assertEqual(local_to_utc(gday), datetime(2020, 12, 21, 18, 20, tzinfo=zoneinfo))
        self.assertEqual(local_to_utc(day_one), datetime(1, 1, 1, tzinfo=utc))

    def test_utc_to_julian(self):
        self.assertEqual(utc_to_julian(day_one), 1721425.5)

    def test_degrees_to_dms(self):
        datatype = dtype([("degs", "i4"), ("mins", "i4"), ("secs", "i4")])
        self.assertEqual(degrees_to_dms(271.45), array((271, 27, 0), dtype=datatype))
