import csv
import os
import tempfile
import unittest

from modules import validator
from modules.csv_utils import csv_file_lock, write_dict_rows_atomically
from modules.search_utils import next_date_posted_filter


class DatePostedCycleTests(unittest.TestCase):
    def test_stop_at_24hr_advances_one_step_and_clamps(self):
        self.assertEqual(next_date_posted_filter("Any time", True), "Past month")
        self.assertEqual(next_date_posted_filter("Past month", True), "Past week")
        self.assertEqual(next_date_posted_filter("Past week", True), "Past 24 hours")
        self.assertEqual(next_date_posted_filter("Past 24 hours", True), "Past 24 hours")

    def test_empty_date_filter_resets_to_any_time(self):
        self.assertEqual(next_date_posted_filter("", True), "Any time")

    def test_non_stop_cycle_wraps_when_not_clamped(self):
        self.assertEqual(next_date_posted_filter("Past 24 hours", False), "Any time")


class ValidatorSecretTests(unittest.TestCase):
    def setUp(self):
        self.original_values = {
            name: getattr(validator, name)
            for name in (
                "use_AI",
                "llm_api_url",
                "llm_api_key",
                "stream_output",
                "ai_provider",
                "llm_model",
            )
        }

    def tearDown(self):
        for name, value in self.original_values.items():
            setattr(validator, name, value)

    def test_ai_disabled_does_not_require_llm_connection_details(self):
        validator.use_AI = False
        validator.llm_api_url = ""
        validator.llm_api_key = ""
        validator.llm_model = ""
        validator.ai_provider = "openai"

        validator.validate_secrets()

    def test_gemini_does_not_require_openai_compatible_url(self):
        validator.use_AI = True
        validator.llm_api_url = ""
        validator.llm_api_key = "gemini-api-key"
        validator.llm_model = "gemini-2.5-flash"
        validator.ai_provider = "gemini"

        validator.validate_secrets()

    def test_openai_provider_still_requires_api_url_when_ai_enabled(self):
        validator.use_AI = True
        validator.llm_api_url = ""
        validator.llm_api_key = "not-needed"
        validator.llm_model = "gpt-4o"
        validator.ai_provider = "openai"

        with self.assertRaises(ValueError):
            validator.validate_secrets()


class CsvUtilityTests(unittest.TestCase):
    def test_atomic_dict_write_replaces_csv_contents(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            csv_path = os.path.join(temp_dir, "history.csv")
            fieldnames = ["Job ID", "Date Applied"]
            rows = [{"Job ID": "123", "Date Applied": "Pending"}]

            with csv_file_lock(csv_path):
                write_dict_rows_atomically(csv_path, fieldnames, rows)

            with open(csv_path, newline="", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                self.assertEqual(reader.fieldnames, fieldnames)
                self.assertEqual(list(reader), rows)


if __name__ == "__main__":
    unittest.main()
