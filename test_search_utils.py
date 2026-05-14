import unittest

from modules.search_utils import next_date_posted_filter


class NextDatePostedFilterTest(unittest.TestCase):
    def test_stop_at_24hr_advances_until_final_filter(self):
        self.assertEqual(next_date_posted_filter("Any time", True), "Past month")
        self.assertEqual(next_date_posted_filter("Past month", True), "Past week")
        self.assertEqual(next_date_posted_filter("Past week", True), "Past 24 hours")
        self.assertEqual(next_date_posted_filter("Past 24 hours", True), "Past 24 hours")

    def test_empty_filter_starts_cycle_without_crashing(self):
        self.assertEqual(next_date_posted_filter("", True), "Any time")
        self.assertEqual(next_date_posted_filter("", False), "Any time")

    def test_wraps_when_not_stopping_at_24hr(self):
        self.assertEqual(next_date_posted_filter("Past 24 hours", False), "Any time")


if __name__ == "__main__":
    unittest.main()
