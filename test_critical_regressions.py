import csv
import io
import sys
import unittest
from contextlib import contextmanager
from pathlib import Path
from unittest.mock import MagicMock

# helpers.py imports pyautogui at module load; stub it so tests can run headless.
sys.modules.setdefault("pyautogui", MagicMock())

import modules.validator as validator
from modules.csv_utils import raise_csv_field_size_limit
from modules.helpers import truncate_for_csv
from modules.search_utils import next_date_posted_filter


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

    def test_truncate_for_csv_preserves_long_history_fields(self):
        long_description = "job-description-" + ("x" * 200_000)

        self.assertEqual(truncate_for_csv(long_description), long_description)
        self.assertNotIn("[TRUNCATED]", truncate_for_csv(long_description))
        self.assertEqual(truncate_for_csv(None), "")

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

    def test_validator_skips_llm_url_when_ai_disabled(self):
        with patched_validator_secrets(
            username="user@example.com",
            password="password123",
            use_AI=False,
            ai_provider="openai",
            llm_api_url="",
            llm_api_key="not-needed",
            llm_model="",
            stream_output=False,
        ):
            validator.validate_secrets()

    def test_date_posted_cycle_does_not_skip_to_24_hours(self):
        self.assertEqual(next_date_posted_filter("Any time", True), "Past month")
        self.assertEqual(next_date_posted_filter("Past month", True), "Past week")
        self.assertEqual(next_date_posted_filter("Past week", True), "Past 24 hours")
        self.assertEqual(next_date_posted_filter("Past 24 hours", True), "Past 24 hours")

    def test_date_posted_cycle_wraps_when_not_stopping_at_24hr(self):
        self.assertEqual(next_date_posted_filter("Past 24 hours", False), "Any time")

    def test_date_posted_cycle_handles_empty_filter(self):
        self.assertEqual(next_date_posted_filter("", True), "Any time")
        self.assertEqual(next_date_posted_filter("", False), "Any time")

    def test_textarea_branch_no_longer_uses_text_input_autocomplete_flag(self):
        source = (ROOT / "runAiBot.py").read_text(encoding="utf-8")
        textarea_block = source.split("# Check if it's a textarea question", 1)[1]
        textarea_block = textarea_block.split("# Check if it's a checkbox question", 1)[0]

        self.assertNotIn("if do_actions:", textarea_block)
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

    def test_ai_error_alert_paths_declare_global_flag(self):
        gemini_source = (ROOT / "modules/ai/geminiConnections.py").read_text(encoding="utf-8")
        deepseek_source = (ROOT / "modules/ai/deepseekConnections.py").read_text(encoding="utf-8")

        self.assertIn("global showAiErrorAlerts", gemini_source)
        self.assertIn("global showAiErrorAlerts", deepseek_source)


if __name__ == "__main__":
    unittest.main()
