import csv
import importlib
import io
import sys
import types
import unittest


class ValidatorSecretsTests(unittest.TestCase):
    def setUp(self):
        self.validator = importlib.import_module("modules.validator")
        self.original_values = {
            name: getattr(self.validator, name)
            for name in (
                "username",
                "password",
                "use_AI",
                "llm_api_url",
                "llm_api_key",
                "llm_model",
                "stream_output",
                "ai_provider",
            )
        }

    def tearDown(self):
        for name, value in self.original_values.items():
            setattr(self.validator, name, value)

    def configure_valid_base_secrets(self):
        self.validator.username = "person@example.com"
        self.validator.password = "example-password"
        self.validator.use_AI = True
        self.validator.llm_api_url = "https://api.openai.com/v1/"
        self.validator.llm_api_key = "test-key"
        self.validator.llm_model = "gpt-4o"
        self.validator.stream_output = False
        self.validator.ai_provider = "openai"

    def test_validate_secrets_allows_gemini_without_api_url(self):
        self.configure_valid_base_secrets()
        self.validator.ai_provider = "gemini"
        self.validator.llm_api_url = ""
        self.validator.llm_model = "gemini-1.5-flash"

        self.validator.validate_secrets()

    def test_validate_secrets_still_requires_api_url_for_openai(self):
        self.configure_valid_base_secrets()
        self.validator.llm_api_url = ""

        with self.assertRaises(ValueError):
            self.validator.validate_secrets()


class CsvRegressionTests(unittest.TestCase):
    def test_csv_formatter_preserves_large_fields(self):
        sys.modules.setdefault(
            "pyautogui",
            types.SimpleNamespace(alert=lambda *args, **kwargs: None),
        )
        helpers = importlib.import_module("modules.helpers")
        large_value = "x" * 200_000

        self.assertEqual(helpers.truncate_for_csv(large_value), large_value)

    def test_raised_csv_limit_reads_large_preserved_fields(self):
        from modules.csv_utils import raise_csv_field_size_limit

        large_value = "x" * 200_000
        raise_csv_field_size_limit()
        rows = list(csv.reader(io.StringIO(f"Job ID,About Job\n1,{large_value}\n")))

        self.assertEqual(rows[1][1], large_value)


if __name__ == "__main__":
    unittest.main()
