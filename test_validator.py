import unittest

import modules.validator as validator


class ValidateSecretsTest(unittest.TestCase):
    def setUp(self):
        self.original_values = {
            "username": validator.username,
            "password": validator.password,
            "use_AI": validator.use_AI,
            "ai_provider": validator.ai_provider,
            "llm_api_url": validator.llm_api_url,
            "llm_api_key": validator.llm_api_key,
            "llm_model": validator.llm_model,
            "stream_output": validator.stream_output,
        }

        validator.username = "user@example.com"
        validator.password = "valid_password"
        validator.use_AI = True
        validator.llm_api_key = "test-api-key"
        validator.llm_model = "gemini-2.5-flash"
        validator.stream_output = False

    def tearDown(self):
        for name, value in self.original_values.items():
            setattr(validator, name, value)

    def test_gemini_provider_does_not_require_llm_api_url(self):
        validator.ai_provider = "gemini"
        validator.llm_api_url = ""

        self.assertIsNone(validator.validate_secrets())

    def test_openai_provider_still_requires_llm_api_url(self):
        validator.ai_provider = "openai"
        validator.llm_api_url = ""

        with self.assertRaises(ValueError):
            validator.validate_secrets()


if __name__ == "__main__":
    unittest.main()
