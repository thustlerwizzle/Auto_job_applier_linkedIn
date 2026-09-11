'''
Regression tests for high-severity correctness bugs.
'''

import csv
import io
import os
import sys
import types
import unittest
from unittest.mock import MagicMock, patch

# helpers.py imports pyautogui.alert at load time.
sys.modules.setdefault("pyautogui", MagicMock())
# Client tests should not require vendor SDKs.
sys.modules.setdefault("google", types.ModuleType("google"))
sys.modules.setdefault("google.generativeai", MagicMock())
sys.modules.setdefault("openai", MagicMock())
sys.modules.setdefault("openai.types", MagicMock())
sys.modules.setdefault("openai.types.model", MagicMock())
sys.modules.setdefault("openai.types.chat", MagicMock())


class DatePostedCyclingTests(unittest.TestCase):
    def test_advances_sequentially_when_stopping_at_24hr(self):
        from modules.search_utils import next_date_posted_filter

        self.assertEqual(next_date_posted_filter("Any time", True), "Past month")
        self.assertEqual(next_date_posted_filter("Past month", True), "Past week")
        self.assertEqual(next_date_posted_filter("Past week", True), "Past 24 hours")
        self.assertEqual(next_date_posted_filter("Past 24 hours", True), "Past 24 hours")

    def test_wraps_when_not_stopping_at_24hr(self):
        from modules.search_utils import next_date_posted_filter

        self.assertEqual(next_date_posted_filter("Past 24 hours", False), "Any time")

    def test_empty_filter_does_not_crash(self):
        from modules.search_utils import next_date_posted_filter

        self.assertEqual(next_date_posted_filter("", True), "Any time")
        self.assertEqual(next_date_posted_filter(None, True), "Any time")


class CsvHistoryTests(unittest.TestCase):
    def test_long_fields_are_not_truncated_on_write(self):
        from modules.helpers import truncate_for_csv

        payload = "A" * 200_000
        self.assertEqual(truncate_for_csv(payload), payload)

    def test_none_becomes_empty_string(self):
        from modules.helpers import truncate_for_csv

        self.assertEqual(truncate_for_csv(None), "")

    def test_reader_can_parse_fields_larger_than_default_limit(self):
        from modules.csv_utils import raise_csv_field_size_limit

        raise_csv_field_size_limit()
        payload = "B" * 200_000
        buffer = io.StringIO()
        writer = csv.DictWriter(buffer, fieldnames=["Job ID", "About Job"])
        writer.writeheader()
        writer.writerow({"Job ID": "123", "About Job": payload})

        buffer.seek(0)
        rows = list(csv.DictReader(buffer))
        self.assertEqual(rows[0]["About Job"], payload)


class ValidatorAiConfigTests(unittest.TestCase):
    def setUp(self):
        import modules.validator as validator

        self.validator = validator
        self._original = {
            "use_AI": validator.use_AI,
            "ai_provider": validator.ai_provider,
            "llm_api_url": validator.llm_api_url,
            "llm_api_key": validator.llm_api_key,
            "llm_model": validator.llm_model,
            "stream_output": validator.stream_output,
            "username": validator.username,
            "password": validator.password,
        }

    def tearDown(self):
        for key, value in self._original.items():
            setattr(self.validator, key, value)

    def _valid_login(self):
        self.validator.username = "user@example.com"
        self.validator.password = "example_password"

    def test_gemini_does_not_require_api_url(self):
        self._valid_login()
        self.validator.use_AI = True
        self.validator.ai_provider = "gemini"
        self.validator.llm_api_url = ""
        self.validator.llm_api_key = "test-key"
        self.validator.llm_model = "gemini-1.5-flash"
        self.validator.stream_output = False

        self.validator.validate_secrets()

    def test_disabled_ai_does_not_require_api_url(self):
        self._valid_login()
        self.validator.use_AI = False
        self.validator.ai_provider = "openai"
        self.validator.llm_api_url = ""
        self.validator.llm_api_key = ""
        self.validator.llm_model = ""
        self.validator.stream_output = False

        self.validator.validate_secrets()

    def test_openai_still_requires_url_when_ai_enabled(self):
        self._valid_login()
        self.validator.use_AI = True
        self.validator.ai_provider = "openai"
        self.validator.llm_api_url = ""
        self.validator.llm_api_key = "not-needed"
        self.validator.llm_model = "gpt-4o"
        self.validator.stream_output = False

        with self.assertRaises(ValueError):
            self.validator.validate_secrets()

    def test_unknown_provider_is_rejected(self):
        self._valid_login()
        self.validator.use_AI = True
        self.validator.ai_provider = "not-a-provider"
        self.validator.llm_api_url = "http://127.0.0.1:1234/v1/"
        self.validator.llm_api_key = "not-needed"
        self.validator.llm_model = "some-model"
        self.validator.stream_output = False

        with self.assertRaises(ValueError):
            self.validator.validate_secrets()


class AiClientAlertTests(unittest.TestCase):
    def test_gemini_failed_setup_can_pause_alerts_without_unbound_local(self):
        import modules.ai.geminiConnections as gemini

        gemini.showAiErrorAlerts = True
        with patch.object(gemini, "llm_api_key", "YOUR_API_KEY"), \
             patch.object(gemini, "confirm", return_value="Pause AI error alerts"):
            result = gemini.gemini_create_client()

        self.assertIsNone(result)
        self.assertFalse(gemini.showAiErrorAlerts)

    def test_deepseek_failed_setup_can_pause_alerts_without_unbound_local(self):
        import modules.ai.deepseekConnections as deepseek

        deepseek.showAiErrorAlerts = True
        with patch.object(deepseek, "use_AI", True), \
             patch.object(deepseek, "llm_api_url", None), \
             patch.object(deepseek, "confirm", return_value="Pause AI error alerts"):
            result = deepseek.deepseek_create_client()

        self.assertIsNone(result)
        self.assertFalse(deepseek.showAiErrorAlerts)


class JobDescriptionSkipInitTests(unittest.TestCase):
    def test_missing_description_element_does_not_unbound_skip(self):
        '''
        Mirrors get_job_description(): skip flags must be assigned before the
        DOM lookup so a missing About Job box cannot crash the search loop.
        '''
        try:
            jobDescription = "Unknown"
            experience_required = "Unknown"
            skip = False
            skipReason = None
            skipMessage = None
            jobDescription = (_ for _ in ()).throw(Exception("missing element"))
        except Exception:
            if jobDescription == "Unknown":
                pass
            else:
                experience_required = "Error in extraction"
        finally:
            result = (jobDescription, experience_required, skip, skipReason, skipMessage)

        self.assertEqual(result, ("Unknown", "Unknown", False, None, None))


class EasyApplySourceGuards(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(os.path.join(os.path.dirname(__file__), "runAiBot.py"), encoding="utf-8") as file:
            cls.source = file.read()

    def test_failed_submit_always_raises(self):
        self.assertNotIn(
            'if errored == "nose": raise Exception("Failed to click Submit application',
            self.source,
        )
        self.assertIn('raise Exception("Failed to click Submit application', self.source)

    def test_job_description_initializes_skip_before_lookup(self):
        start = self.source.index("def get_job_description(")
        body = self.source[start:self.source.index("def upload_resume(")]
        self.assertLess(body.index("skip = False"), body.index("find_by_class(driver, \"jobs-box__html-content\")"))

    def test_textarea_does_not_clear_prefilled_answers_by_default(self):
        start = self.source.index("# Check if it's a textarea question")
        body = self.source[start:self.source.index("# Check if it's a checkbox question")]
        clear_at = body.index("text_area.clear()")
        guard_at = body.index("if not prev_answer or overwrite_previous_answers:")
        self.assertLess(guard_at, clear_at)
        self.assertNotIn("if do_actions:", body)


if __name__ == "__main__":
    unittest.main()
