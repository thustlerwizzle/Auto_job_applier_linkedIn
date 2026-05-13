import unittest
from contextlib import contextmanager

import modules.validator as validator


@contextmanager
def patched_validator_secrets(**overrides):
    names = (
        "username",
        "password",
        "use_AI",
        "llm_api_url",
        "llm_api_key",
        "llm_model",
        "stream_output",
        "ai_provider",
    )
    original_values = {name: getattr(validator, name) for name in names}
    try:
        for name, value in overrides.items():
            setattr(validator, name, value)
        yield
    finally:
        for name, value in original_values.items():
            setattr(validator, name, value)


class ValidateSecretsTests(unittest.TestCase):
    def test_gemini_accepts_empty_api_url(self):
        with patched_validator_secrets(
            username="person@example.com",
            password="password",
            use_AI=True,
            ai_provider="gemini",
            llm_api_url="",
            llm_api_key="gemini-key",
            llm_model="gemini-1.5-flash",
            stream_output=False,
        ):
            validator.validate_secrets()

    def test_openai_still_requires_api_url(self):
        with patched_validator_secrets(
            username="person@example.com",
            password="password",
            use_AI=True,
            ai_provider="openai",
            llm_api_url="",
            llm_api_key="openai-key",
            llm_model="gpt-4o",
            stream_output=False,
        ):
            with self.assertRaises(ValueError):
                validator.validate_secrets()

    def test_deepseek_still_restricts_supported_models(self):
        with patched_validator_secrets(
            username="person@example.com",
            password="password",
            use_AI=True,
            ai_provider="deepseek",
            llm_api_url="https://api.deepseek.com",
            llm_api_key="deepseek-key",
            llm_model="not-a-deepseek-model",
            stream_output=False,
        ):
            with self.assertRaises(ValueError):
                validator.validate_secrets()


if __name__ == "__main__":
    unittest.main()
