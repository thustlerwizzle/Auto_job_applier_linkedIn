import csv
import io
import unittest
from pathlib import Path

from modules.csv_utils import raise_csv_field_size_limit


class CsvUtilsTests(unittest.TestCase):
    def test_large_fields_round_trip_without_truncation(self):
        old_limit = csv.field_size_limit()
        large_value = "x" * 1024
        output = io.StringIO()
        csv.writer(output).writerow(["job-1", large_value])
        row = output.getvalue()

        try:
            csv.field_size_limit(128)
            with self.assertRaises(csv.Error):
                next(csv.reader(io.StringIO(row)))

            raise_csv_field_size_limit()
            parsed = next(csv.reader(io.StringIO(row)))
        finally:
            csv.field_size_limit(old_limit)

        self.assertEqual(parsed[1], large_value)

    def test_application_history_writes_do_not_use_truncating_helper(self):
        run_ai_bot = Path(__file__).with_name("runAiBot.py").read_text(encoding="utf-8")

        self.assertNotIn("truncate_for_csv(", run_ai_bot)


if __name__ == "__main__":
    unittest.main()
