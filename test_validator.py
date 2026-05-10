import unittest
from contextlib import contextmanager

import modules.validator as validator


@contextmanager
def patched_validator(**overrides):
    original_values = {name: getattr(validator, name) for name in overrides}
    try:
        for name, value in overrides.items():
            setattr(validator, name, value)
        yield
    finally:
        for name, value in original_values.items():
            setattr(validator, name, value)


class ValidateSecretsTests(unittest.TestCase):
    def test_gemini_does_not_require_llm_api_url(self):
        with patched_validator(
            username="valid@example.com",
            password="valid-password",
            use_AI=True,
            ai_provider="gemini",
            llm_api_url="",
            llm_api_key="fake-gemini-key",
            llm_model="gemini-1.5-flash",
            stream_output=False,
        ):
            self.assertIsNone(validator.validate_secrets())

    def test_openai_still_requires_llm_api_url(self):
        with patched_validator(
            username="valid@example.com",
            password="valid-password",
            use_AI=True,
            ai_provider="openai",
            llm_api_url="",
            llm_api_key="fake-openai-key",
            llm_model="gpt-4o-mini",
            stream_output=False,
        ):
            with self.assertRaises(ValueError):
                validator.validate_secrets()


if __name__ == "__main__":
    unittest.main()
