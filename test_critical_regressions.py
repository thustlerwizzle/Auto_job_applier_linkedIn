import csv
import io
import unittest
from contextlib import contextmanager
from pathlib import Path

import modules.validator as validator
from modules.csv_utils import raise_csv_field_size_limit


ROOT = Path(__file__).resolve().parent


@contextmanager
def patched_validator_secrets(**overrides):
    original_values = {name: getattr(validator, name) for name in overrides}
    try:
        for name, value in overrides.items():
            setattr(validator, name, value)
        yield
    finally:
        for name, value in original_values.items():
            setattr(validator, name, value)


class CriticalRegressionTests(unittest.TestCase):
    def test_csv_reader_accepts_large_fields_without_truncating_written_data(self):
        long_description = "x" * 200_000
        buffer = io.StringIO()

        writer = csv.writer(buffer)
        writer.writerow(["job-1", long_description])

        raise_csv_field_size_limit()
        buffer.seek(0)
        row = next(csv.reader(buffer))

        self.assertEqual(row[1], long_description)
        self.assertNotIn("[TRUNCATED]", row[1])

    def test_bot_history_writes_do_not_use_truncation_helper(self):
        source = (ROOT / "runAiBot.py").read_text(encoding="utf-8")

        self.assertNotIn("truncate_for_csv", source)

    def test_validator_allows_gemini_without_llm_api_url(self):
        with patched_validator_secrets(
            username="user@example.com",
            password="password123",
            use_AI=True,
            ai_provider="gemini",
            llm_api_url="",
            llm_api_key="gemini-api-key",
            llm_model="gemini-1.5-flash",
            stream_output=False,
        ):
            validator.validate_secrets()

    def test_validator_still_requires_llm_api_url_for_openai(self):
        with patched_validator_secrets(
            username="user@example.com",
            password="password123",
            use_AI=True,
            ai_provider="openai",
            llm_api_url="",
            llm_api_key="openai-api-key",
            llm_model="gpt-4o",
            stream_output=False,
        ):
            with self.assertRaises(ValueError):
                validator.validate_secrets()

    def test_textarea_branch_no_longer_uses_text_input_autocomplete_flag(self):
        source = (ROOT / "runAiBot.py").read_text(encoding="utf-8")

        self.assertEqual(source.count("if do_actions:"), 1)

    def test_failed_submit_path_raises_before_success_logging(self):
        source = (ROOT / "runAiBot.py").read_text(encoding="utf-8")

        self.assertNotIn(
            'if errored == "nose": raise Exception("Failed to click Submit application',
            source,
        )
        self.assertIn(
            'raise Exception("Failed to click Submit application',
            source,
        )


if __name__ == "__main__":
    unittest.main()
