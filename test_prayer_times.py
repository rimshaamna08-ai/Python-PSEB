import io
import unittest
from contextlib import redirect_stdout
from datetime import datetime, timezone
from unittest.mock import patch

from prayer_times import fetch_prayer_data, get_next_prayer


class GetNextPrayerTests(unittest.TestCase):
    def setUp(self):
        self.timings = {
            "Fajr": "05:00 (PKT)",
            "Sunrise": "06:30 (PKT)",
            "Dhuhr": "12:00 (PKT)",
            "Asr": "15:30 (PKT)",
            "Maghrib": "18:00 (PKT)",
            "Isha": "19:30 (PKT)",
        }

    def test_returns_next_prayer_today(self):
        now = datetime(2026, 1, 1, 12, 15, tzinfo=timezone.utc)

        prayer, prayer_time = get_next_prayer(self.timings, now)

        self.assertEqual(prayer, "Asr")
        self.assertEqual(prayer_time, datetime(2026, 1, 1, 15, 30, tzinfo=timezone.utc))

    def test_returns_tomorrows_fajr_after_last_prayer(self):
        now = datetime(2026, 1, 1, 23, 0, tzinfo=timezone.utc)

        prayer, prayer_time = get_next_prayer(self.timings, now)

        self.assertEqual(prayer, "Fajr")
        self.assertEqual(prayer_time, datetime(2026, 1, 2, 5, 0, tzinfo=timezone.utc))






if __name__ == "__main__":
    unittest.main()