import importlib
import sys
import unittest
from types import ModuleType


def stub_module(name, **values):
    module = ModuleType(name)
    for key, value in values.items():
        setattr(module, key, value)
    return module


PERSONALS = {
    "first_name": "Jane",
    "middle_name": "",
    "last_name": "Doe",
    "phone_number": "1234567890",
    "current_city": "",
    "street": "",
    "state": "",
    "zipcode": "",
    "country": "",
    "ethnicity": "Decline",
    "gender": "",
    "disability_status": "Decline",
    "veteran_status": "Decline",
}

QUESTIONS = {
    "default_resume_path": "",
    "years_of_experience": "",
    "require_visa": "No",
    "website": "",
    "linkedIn": "",
    "desired_salary": 0,
    "us_citizenship": "Other",
    "linkedin_headline": "",
    "notice_period": 0,
    "current_ctc": 0,
    "linkedin_summary": "",
    "cover_letter": "",
    "recent_employer": "",
    "confidence_level": "",
    "pause_before_submit": False,
    "pause_at_failed_question": False,
    "overwrite_previous_answers": False,
}

SEARCH = {
    "search_terms": ["python"],
    "search_location": "",
    "switch_number": 1,
    "randomize_search_order": False,
    "sort_by": "",
    "date_posted": "",
    "salary": "",
    "easy_apply_only": False,
    "experience_level": [],
    "job_type": [],
    "on_site": [],
    "companies": [],
    "location": [],
    "industry": [],
    "job_function": [],
    "job_titles": [],
    "benefits": [],
    "commitments": [],
    "under_10_applicants": False,
    "in_your_network": False,
    "fair_chance_employer": False,
    "pause_after_filters": False,
    "about_company_bad_words": [],
    "about_company_good_words": [],
    "bad_words": [],
    "security_clearance": False,
    "did_masters": False,
    "current_experience": -1,
}

SETTINGS = {
    "close_tabs": False,
    "follow_companies": False,
    "run_non_stop": False,
    "alternate_sortby": False,
    "cycle_date_posted": False,
    "stop_date_cycle_at_24hr": False,
    "file_name": "all excels/all_applied_applications_history.csv",
    "failed_file_name": "all excels/all_failed_applications_history.csv",
    "logs_folder_path": "logs/",
    "click_gap": 0,
    "run_in_background": False,
    "disable_extensions": False,
    "safe_mode": True,
    "smooth_scroll": False,
    "keep_screen_awake": False,
    "stealth_mode": False,
}

BASE_SECRETS = {
    "username": "username@example.com",
    "password": "example_password",
    "use_AI": False,
    "ai_provider": "openai",
    "llm_api_url": "",
    "llm_api_key": "not-needed",
    "llm_model": "",
    "llm_spec": "openai",
    "stream_output": False,
}


class ValidatorSecretsTest(unittest.TestCase):
    def setUp(self):
        self.original_modules = {}
        for name in [
            "modules.validator",
            "config.personals",
            "config.questions",
            "config.search",
            "config.secrets",
            "config.settings",
        ]:
            self.original_modules[name] = sys.modules.pop(name, None)

    def tearDown(self):
        for name in [
            "modules.validator",
            "config.personals",
            "config.questions",
            "config.search",
            "config.secrets",
            "config.settings",
        ]:
            sys.modules.pop(name, None)
            if self.original_modules[name] is not None:
                sys.modules[name] = self.original_modules[name]

    def load_validator(self, **secret_overrides):
        secrets = {**BASE_SECRETS, **secret_overrides}
        sys.modules["config.personals"] = stub_module("config.personals", **PERSONALS)
        sys.modules["config.questions"] = stub_module("config.questions", **QUESTIONS)
        sys.modules["config.search"] = stub_module("config.search", **SEARCH)
        sys.modules["config.secrets"] = stub_module("config.secrets", **secrets)
        sys.modules["config.settings"] = stub_module("config.settings", **SETTINGS)
        return importlib.import_module("modules.validator")

    def test_ai_disabled_allows_blank_llm_configuration(self):
        validator = self.load_validator(use_AI=False, llm_api_url="", llm_model="")

        self.assertTrue(validator.validate_config())

    def test_ai_enabled_requires_llm_configuration(self):
        validator = self.load_validator(use_AI=True, llm_api_url="", llm_model="")

        with self.assertRaises(ValueError):
            validator.validate_secrets()

    def test_gemini_provider_is_validated(self):
        validator = self.load_validator(
            use_AI=True,
            ai_provider="gemini",
            llm_api_url="unused",
            llm_api_key="test-key",
            llm_model="gemini-1.5-flash",
        )

        validator.validate_secrets()


if __name__ == "__main__":
    unittest.main()
