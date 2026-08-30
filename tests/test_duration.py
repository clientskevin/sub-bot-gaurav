#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Minimal tests for DurationUtils.parse_days_float."""

import unittest
from decimal import Decimal

from utils.duration import DurationUtils, duration_utils


class TestParseDaysFloat(unittest.TestCase):
    def setUp(self):
        self.utils = DurationUtils()

    def test_integer_days(self):
        result = self.utils.parse_days_float("7")
        self.assertIsNotNone(result)
        self.assertEqual(result.duration_seconds, 7 * 86400)
        self.assertEqual(result.breakdown, "7 days")

    def test_float_days_one_and_half(self):
        result = self.utils.parse_days_float("1.5")
        self.assertIsNotNone(result)
        self.assertEqual(result.duration_seconds, 129600)
        self.assertEqual(result.breakdown, "1 day, 12 hours")

    def test_truncates_long_fraction(self):
        # Digits beyond 6 fractional places are discarded (not rounded).
        # 2.000011574 → truncate 2.000011 (172800s); round-up would be 2.000012 (172801s).
        result = self.utils.parse_days_float("2.000011574")
        self.assertIsNotNone(result)
        expected = int(Decimal("2.000011") * 86400)
        rounded_up = int(Decimal("2.000012") * 86400)
        self.assertEqual(result.duration_seconds, expected)
        self.assertEqual(result.duration_seconds, 172800)
        self.assertEqual(rounded_up, 172801)

    def test_rejects_zero_negative_garbage(self):
        for bad in ("0", "-1", "-0.5", "", "  ", "abc", "NaN", "inf", "-inf"):
            with self.subTest(bad=bad):
                self.assertIsNone(self.utils.parse_days_float(bad))

    def test_half_day_breakdown(self):
        result = self.utils.parse_days_float("0.5")
        self.assertIsNotNone(result)
        self.assertEqual(result.duration_seconds, 43200)
        self.assertEqual(result.breakdown, "12 hours")

    def test_singleton_matches_class(self):
        self.assertEqual(
            duration_utils.parse_days_float("1").duration_seconds,
            self.utils.parse_days_float("1").duration_seconds,
        )


if __name__ == "__main__":
    unittest.main()
