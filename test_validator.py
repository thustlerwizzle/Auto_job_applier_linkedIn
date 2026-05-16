import unittest

import modules.validator as validator


class ValidateSecretsTest(unittest.TestCase):
    def setUp(self):
        self._original_values = {
            name: getattr(validator, name)
            for name in (
                "username",
                "password",
                "use_AI",
                "ai_provider",
                "llm_api_url",
                "llm_api_key",
                "llm_model",
                "stream_output",
            )
        }
        validator.username = "user@example.com"
        validator.password = "password"
        validator.llm_api_key = "test-key"
        validator.stream_output = False

    def tearDown(self):
        for name, value in self._original_values.items():
            setattr(validator, name, value)

    def test_gemini_allows_empty_api_url(self):
        validator.use_AI = True
        validator.ai_provider = "gemini"
        validator.llm_api_url = ""
        validator.llm_model = "gemini-2.5-flash"

        self.assertIsNone(validator.validate_secrets())

    def test_openai_still_requires_api_url_when_ai_is_enabled(self):
        validator.use_AI = True
        validator.ai_provider = "openai"
        validator.llm_api_url = ""
        validator.llm_model = "gpt-4o"

        with self.assertRaises(ValueError):
            validator.validate_secrets()

    def test_disabled_ai_allows_empty_api_url(self):
        validator.use_AI = False
        validator.ai_provider = "openai"
        validator.llm_api_url = ""
        validator.llm_model = ""

        self.assertIsNone(validator.validate_secrets())


if __name__ == "__main__":
    unittest.main()
