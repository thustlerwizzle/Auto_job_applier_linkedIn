import csv
import unittest

from modules.csv_utils import raise_csv_field_size_limit, stringify_for_csv


class CsvUtilsTest(unittest.TestCase):
    def test_stringify_for_csv_preserves_large_fields(self):
        field = "x" * 140000

        self.assertEqual(stringify_for_csv(field), field)

    def test_raise_csv_field_size_limit_above_default(self):
        raise_csv_field_size_limit()

        self.assertGreater(csv.field_size_limit(), 140000)


if __name__ == "__main__":
    unittest.main()
