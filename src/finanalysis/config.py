# src/finanalysis/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    """Application settings"""

    # LLM Configuration
    openai_api_key: str = "test-key"  # Default for testing
    openai_base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    llm_model: str = "qwen3.5-flash"
    llm_temperature: float = 0.1
    llm_max_tokens: int = 4000

    # Processing Configuration
    cache_enabled: bool = True
    cache_dir: str = "./cache"
    output_dir: str = "./output"

    # Extraction Configuration
    text_min_length: int = 20  # Minimum text block length
    table_area_threshold: float = 0.5  # Table area ratio threshold

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )
