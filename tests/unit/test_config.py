# tests/unit/test_config.py
from src.finanalysis.config import Settings

def test_settings_defaults():
    settings = Settings(
        openai_api_key="test-key",
        openai_base_url="https://api.example.com/v1"
    )

    assert settings.openai_api_key == "test-key"
    assert settings.openai_base_url == "https://api.example.com/v1"
    assert settings.llm_model == "qwen3.5-flash"
    assert settings.llm_temperature == 0.1
