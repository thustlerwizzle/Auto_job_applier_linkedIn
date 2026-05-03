import unittest

import modules.validator as validator


class ValidateSecretsTests(unittest.TestCase):
    def setUp(self):
        self.originals = {
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

        validator.username = "username@example.com"
        validator.password = "example_password"
        validator.use_AI = True
        validator.llm_api_key = "not-needed"
        validator.llm_model = "gpt-4o"
        validator.stream_output = False

    def tearDown(self):
        for name, value in self.originals.items():
            setattr(validator, name, value)

    def test_gemini_does_not_require_llm_api_url(self):
        validator.ai_provider = "gemini"
        validator.llm_api_url = ""
        validator.llm_model = "gemini-2.5-flash"

        self.assertTrue(validator.validate_secrets() is None)

    def test_openai_requires_llm_api_url(self):
        validator.ai_provider = "openai"
        validator.llm_api_url = ""

        with self.assertRaises(ValueError):
            validator.validate_secrets()

    def test_deepseek_allows_supported_models(self):
        validator.ai_provider = "deepseek"
        validator.llm_api_url = "https://api.deepseek.com"
        validator.llm_model = "deepseek-chat"

        self.assertTrue(validator.validate_secrets() is None)

    def test_invalid_provider_is_rejected(self):
        validator.ai_provider = "unknown"
        validator.llm_api_url = "https://example.com/v1/"

        with self.assertRaises(ValueError):
            validator.validate_secrets()


if __name__ == "__main__":
    unittest.main()
