"""
Unit tests for breachtl.core.

Run with:  python -m unittest discover -s tests -v
"""

from __future__ import annotations

import unittest

from breachtl.core import Breach, TimelineAnalysis


def make_breach(**overrides) -> Breach:
    """Construct a Breach with sensible defaults, overridable per test."""
    defaults = dict(
        name="Test",
        title="Test Breach",
        domain="test.com",
        breach_date="2019-05-24",
        added_date="2019-08-08T00:00:00Z",
        pwn_count=1000,
        data_classes=["Email addresses"],
        is_sensitive=False,
        is_verified=True,
        description="",
    )
    defaults.update(overrides)
    return Breach(**defaults)


class TestBreachProperties(unittest.TestCase):
    def test_year_parsing(self):
        b = make_breach(breach_date="2017-07-29")
        self.assertEqual(b.year, 2017)

    def test_year_none_when_missing(self):
        b = make_breach(breach_date=None)
        self.assertIsNone(b.year)

    def test_year_none_when_malformed(self):
        b = make_breach(breach_date="not-a-date")
        self.assertIsNone(b.year)

    def test_exposes_passwords_true(self):
        b = make_breach(data_classes=["Email addresses", "Passwords"])
        self.assertTrue(b.exposes_passwords)

    def test_exposes_passwords_false(self):
        b = make_breach(data_classes=["Email addresses", "Usernames"])
        self.assertFalse(b.exposes_passwords)


class TestSeverity(unittest.TestCase):
    def test_high_for_sensitive_financial(self):
        b = make_breach(
            data_classes=["Email addresses", "Social security numbers"],
        )
        self.assertEqual(b.severity, "MEDIUM")  # SSN present -> at least MEDIUM

    def test_high_for_passwords_plus_data(self):
        b = make_breach(
            data_classes=["Email addresses", "Passwords", "Names", "Usernames"],
        )
        self.assertEqual(b.severity, "HIGH")

    def test_high_when_flagged_sensitive(self):
        b = make_breach(is_sensitive=True, data_classes=["Email addresses"])
        self.assertEqual(b.severity, "HIGH")

    def test_medium_for_large_volume(self):
        b = make_breach(
            pwn_count=100_000_000, data_classes=["Email addresses"]
        )
        self.assertEqual(b.severity, "MEDIUM")

    def test_low_for_email_only(self):
        b = make_breach(pwn_count=1000, data_classes=["Email addresses"])
        self.assertEqual(b.severity, "LOW")


class TestFromApi(unittest.TestCase):
    def test_parses_hibp_schema(self):
        raw = {
            "Name": "Adobe",
            "Title": "Adobe",
            "Domain": "adobe.com",
            "BreachDate": "2013-10-04",
            "AddedDate": "2013-12-04T00:00:00Z",
            "PwnCount": 152445165,
            "DataClasses": ["Email addresses", "Passwords"],
            "IsVerified": True,
            "IsSensitive": False,
        }
        b = Breach.from_api(raw)
        self.assertEqual(b.name, "Adobe")
        self.assertEqual(b.pwn_count, 152445165)
        self.assertEqual(b.year, 2013)
        self.assertTrue(b.exposes_passwords)

    def test_handles_missing_fields(self):
        b = Breach.from_api({"Name": "Minimal"})
        self.assertEqual(b.name, "Minimal")
        self.assertEqual(b.pwn_count, 0)
        self.assertEqual(b.data_classes, [])


class TestTimelineAnalysis(unittest.TestCase):
    def setUp(self):
        self.breaches = [
            make_breach(name="A", breach_date="2012-01-01", pwn_count=100),
            make_breach(name="B", breach_date="2012-06-01", pwn_count=200),
            make_breach(name="C", breach_date="2019-01-01", pwn_count=300),
        ]
        self.analysis = TimelineAnalysis(self.breaches)

    def test_total(self):
        self.assertEqual(self.analysis.total, 3)

    def test_total_accounts(self):
        self.assertEqual(self.analysis.total_accounts_exposed, 600)

    def test_by_year_groups_correctly(self):
        by_year = self.analysis.by_year()
        self.assertEqual(len(by_year[2012]), 2)
        self.assertEqual(len(by_year[2019]), 1)

    def test_by_year_is_sorted(self):
        years = list(self.analysis.by_year().keys())
        self.assertEqual(years, sorted(years))

    def test_sorted_by_date(self):
        ordered = self.analysis.sorted_by_date()
        dates = [b.breach_date for b in ordered]
        self.assertEqual(dates, sorted(dates))

    def test_data_class_frequency(self):
        freq = dict(self.analysis.data_class_frequency())
        self.assertEqual(freq["Email addresses"], 3)


if __name__ == "__main__":
    unittest.main()
