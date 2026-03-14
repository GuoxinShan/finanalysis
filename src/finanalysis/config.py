# src/finanalysis/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    """Application settings"""

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
