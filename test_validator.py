import unittest

import modules.validator as validator


class ValidateSecretsTests(unittest.TestCase):
    def setUp(self):
        self._original_values = {
            name: getattr(validator, name)
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
        for name, value in self._original_values.items():
            setattr(validator, name, value)

    def configure_valid_secrets(self, provider: str = "openai") -> None:
        validator.username = "user@example.com"
        validator.password = "example_password"
        validator.use_AI = True
        validator.llm_api_url = "https://api.openai.com/v1/"
        validator.llm_api_key = "test-key"
        validator.llm_model = "gpt-4o"
        validator.stream_output = False
        validator.ai_provider = provider

    def test_gemini_provider_allows_empty_api_url(self):
        self.configure_valid_secrets("gemini")
        validator.llm_api_url = ""
        validator.llm_model = "gemini-1.5-flash"

        validator.validate_secrets()

    def test_openai_provider_still_requires_api_url(self):
        self.configure_valid_secrets("openai")
        validator.llm_api_url = ""

        with self.assertRaises(ValueError):
            validator.validate_secrets()

    def test_unsupported_provider_is_rejected(self):
        self.configure_valid_secrets("claude")

        with self.assertRaises(ValueError):
            validator.validate_secrets()


if __name__ == "__main__":
    unittest.main()
