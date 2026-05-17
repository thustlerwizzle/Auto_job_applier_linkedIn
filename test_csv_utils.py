import csv
import os
import tempfile
import unittest

from modules.csv_utils import raise_csv_field_size_limit


class CsvUtilsTests(unittest.TestCase):
    def test_large_fields_round_trip_after_raising_reader_limit(self):
        original_limit = csv.field_size_limit()
        large_field = "x" * 512

        with tempfile.TemporaryDirectory() as temp_dir:
            csv_path = os.path.join(temp_dir, "history.csv")
            with open(csv_path, "w", encoding="utf-8", newline="") as file:
                writer = csv.DictWriter(file, fieldnames=["Job ID", "About Job"])
                writer.writeheader()
                writer.writerow({"Job ID": "123", "About Job": large_field})

            try:
                csv.field_size_limit(128)
                with self.assertRaises(csv.Error):
                    with open(csv_path, "r", encoding="utf-8", newline="") as file:
                        list(csv.DictReader(file))

                applied_limit = raise_csv_field_size_limit(1024)

                self.assertEqual(applied_limit, 1024)
                with open(csv_path, "r", encoding="utf-8", newline="") as file:
                    rows = list(csv.DictReader(file))
                self.assertEqual(rows[0]["About Job"], large_field)
            finally:
                csv.field_size_limit(original_limit)


if __name__ == "__main__":
    unittest.main()
