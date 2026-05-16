import csv
import io
import unittest

from modules.csv_utils import raise_csv_field_size_limit, stringify_for_csv


class CsvUtilsTest(unittest.TestCase):
    def test_raise_csv_field_size_limit_allows_large_fields_without_truncation(self):
        original_limit = csv.field_size_limit()
        try:
            csv.field_size_limit(1024)
            long_value = "x" * 4096
            csv_buffer = io.StringIO()

            writer = csv.writer(csv_buffer)
            writer.writerow(["job-id", long_value])

            csv_buffer.seek(0)
            with self.assertRaises(csv.Error):
                next(csv.reader(csv_buffer))

            raise_csv_field_size_limit()
            csv_buffer.seek(0)
            row = next(csv.reader(csv_buffer))

            self.assertEqual(long_value, row[1])
        finally:
            csv.field_size_limit(original_limit)

    def test_stringify_for_csv_preserves_long_values(self):
        long_value = "x" * 200000

        self.assertEqual(long_value, stringify_for_csv(long_value))


if __name__ == "__main__":
    unittest.main()
