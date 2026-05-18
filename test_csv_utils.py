import csv
import tempfile
import unittest

from modules.csv_utils import raise_csv_field_size_limit


class CsvUtilsTest(unittest.TestCase):
    def test_raise_csv_field_size_limit_allows_large_fields_without_truncation(self):
        long_value = "x" * 200_000

        with tempfile.NamedTemporaryFile("w+", newline="", encoding="utf-8") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(["Job ID", "About Job"])
            writer.writerow(["123", long_value])
            csv_file.flush()

            original_limit = csv.field_size_limit()
            try:
                csv.field_size_limit(1024)

                with open(csv_file.name, newline="", encoding="utf-8") as read_file:
                    reader = csv.DictReader(read_file)
                    with self.assertRaises(csv.Error):
                        next(reader)

                raise_csv_field_size_limit()

                with open(csv_file.name, newline="", encoding="utf-8") as read_file:
                    reader = csv.DictReader(read_file)
                    self.assertEqual(long_value, next(reader)["About Job"])
            finally:
                csv.field_size_limit(original_limit)


if __name__ == "__main__":
    unittest.main()
