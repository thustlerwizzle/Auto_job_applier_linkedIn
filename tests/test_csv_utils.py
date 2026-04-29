import csv
import io
import unittest

from modules.csv_utils import CSV_FIELD_SIZE_LIMIT, configure_csv_field_size_limit, truncate_for_csv


class CsvUtilsTests(unittest.TestCase):
    def test_truncate_for_csv_preserves_fields_under_configured_limit(self):
        value = "x" * (CSV_FIELD_SIZE_LIMIT - 1)

        self.assertEqual(truncate_for_csv(value), value)

    def test_truncate_for_csv_only_truncates_above_configured_limit(self):
        value = "x" * (CSV_FIELD_SIZE_LIMIT + 10)

        result = truncate_for_csv(value)

        self.assertEqual(len(result), CSV_FIELD_SIZE_LIMIT)
        self.assertTrue(result.endswith("...[TRUNCATED]"))

    def test_configured_csv_reader_accepts_fields_the_bot_writes(self):
        configure_csv_field_size_limit()
        value = "x" * (CSV_FIELD_SIZE_LIMIT - 1)
        buffer = io.StringIO()
        csv.writer(buffer).writerow([value])

        row = next(csv.reader(io.StringIO(buffer.getvalue())))

        self.assertEqual(row, [value])


if __name__ == "__main__":
    unittest.main()
