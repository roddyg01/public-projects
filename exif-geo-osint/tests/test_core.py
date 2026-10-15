"""
Unit tests for exifgeo.core.

Run with:  python -m pytest    (or)    python -m unittest
"""

from __future__ import annotations

import unittest

from exifgeo.core import GPSData, _dms_to_decimal, _ratio_to_float


class TestRatioConversion(unittest.TestCase):
    def test_tuple_ratio(self):
        self.assertEqual(_ratio_to_float((33000, 100)), 330.0)

    def test_plain_number(self):
        self.assertEqual(_ratio_to_float(42), 42.0)

    def test_zero_denominator_is_safe(self):
        # Should not raise; returns 0.0 on division error.
        self.assertEqual(_ratio_to_float((1, 0)), 0.0)


class TestDMSConversion(unittest.TestCase):
    def test_north_is_positive(self):
        # 48 deg 51' 30.24" N  ->  ~48.8584
        dms = ((48, 1), (51, 1), (3024, 100))
        result = _dms_to_decimal(dms, "N")
        self.assertAlmostEqual(result, 48.8584, places=3)

    def test_west_is_negative(self):
        # 74 deg 02' 40.20" W  ->  ~-74.0445
        dms = ((74, 1), (2, 1), (4020, 100))
        result = _dms_to_decimal(dms, "W")
        self.assertLess(result, 0)
        self.assertAlmostEqual(result, -74.0445, places=3)

    def test_south_is_negative(self):
        dms = ((33, 1), (52, 1), (0, 1))
        result = _dms_to_decimal(dms, "S")
        self.assertLess(result, 0)

    def test_malformed_input_returns_none(self):
        self.assertIsNone(_dms_to_decimal(None, "N"))


class TestGPSData(unittest.TestCase):
    def test_has_coordinates_true(self):
        gps = GPSData(latitude=48.8584, longitude=2.2945)
        self.assertTrue(gps.has_coordinates)

    def test_has_coordinates_false_when_partial(self):
        gps = GPSData(latitude=48.8584, longitude=None)
        self.assertFalse(gps.has_coordinates)

    def test_decimal_string_format(self):
        gps = GPSData(latitude=48.8584, longitude=2.2945)
        self.assertEqual(gps.decimal_string, "48.858400, 2.294500")

    def test_maps_url_generation(self):
        gps = GPSData(latitude=48.8584, longitude=2.2945)
        self.assertIn("maps?q=48.858400,2.294500", gps.maps_url)

    def test_no_coordinates_yields_none(self):
        gps = GPSData()
        self.assertIsNone(gps.decimal_string)
        self.assertIsNone(gps.maps_url)


if __name__ == "__main__":
    unittest.main()
