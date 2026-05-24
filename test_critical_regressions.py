import csv
import importlib
import io
import sys
import types
import unittest

from modules import validator
from modules.csv_utils import raise_csv_field_size_limit


class ValidatorRegressionTests(unittest.TestCase):
    def setUp(self):
        self.original_values = {
            name: getattr(validator, name)
            for name in (
                "username",
                "password",
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

    def test_gemini_provider_allows_empty_api_url(self):
        validator.username = "person@example.com"
        validator.password = "valid_password"
        validator.use_AI = True
        validator.ai_provider = "gemini"
        validator.llm_api_url = ""
        validator.llm_api_key = "gemini-api-key"
        validator.llm_model = "gemini-1.5-flash"
        validator.stream_output = False

        validator.validate_secrets()

    def test_ai_disabled_does_not_require_provider_config(self):
        validator.username = "person@example.com"
        validator.password = "valid_password"
        validator.use_AI = False
        validator.ai_provider = "unsupported-provider"
        validator.llm_api_url = ""
        validator.llm_api_key = ""
        validator.llm_model = ""
        validator.stream_output = False

        validator.validate_secrets()

    def test_openai_provider_still_requires_api_url(self):
        validator.username = "person@example.com"
        validator.password = "valid_password"
        validator.use_AI = True
        validator.ai_provider = "openai"
        validator.llm_api_url = ""
        validator.llm_api_key = "api-key"
        validator.llm_model = "gpt-4o"
        validator.stream_output = False

        with self.assertRaises(ValueError):
            validator.validate_secrets()


class CsvRegressionTests(unittest.TestCase):
    def test_csv_converter_preserves_large_values(self):
        sys.modules.setdefault("pyautogui", types.SimpleNamespace(alert=lambda *args, **kwargs: None))
        helpers = importlib.import_module("modules.helpers")

        large_value = "x" * 140000

        self.assertEqual(helpers.truncate_for_csv(large_value), large_value)
        self.assertNotIn("[TRUNCATED]", helpers.truncate_for_csv(large_value))

    def test_raised_csv_field_limit_reads_large_fields(self):
        old_limit = csv.field_size_limit()
        try:
            csv.field_size_limit(1000)
            raise_csv_field_size_limit()

            rows = list(csv.DictReader(io.StringIO("Job ID,About Job\n1,{}\n".format("x" * 2000))))

            self.assertEqual(rows[0]["About Job"], "x" * 2000)
        finally:
            csv.field_size_limit(old_limit)


if __name__ == "__main__":
    unittest.main()
