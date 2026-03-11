"""Application configuration."""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache


@dataclass(frozen=True)
class Settings:
    interpreter_mode: str = "mock"
    openai_api_key: str | None = None
    openai_model: str = "gpt-5.4"
    market_data_mode: str = "mock"
    market_data_api_key: str | None = None
    market_data_provider_name: str | None = None


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    interpreter_mode = os.getenv("INTERPRETER_MODE", "mock").strip().lower() or "mock"
    if interpreter_mode not in {"mock", "openai"}:
        interpreter_mode = "mock"

    market_data_mode = os.getenv("MARKET_DATA_MODE", "mock").strip().lower() or "mock"
    if market_data_mode not in {"mock", "provider"}:
        market_data_mode = "mock"

    return Settings(
        interpreter_mode=interpreter_mode,
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        openai_model=os.getenv("OPENAI_MODEL", "gpt-5.4").strip() or "gpt-5.4",
        market_data_mode=market_data_mode,
        market_data_api_key=os.getenv("MARKET_DATA_API_KEY"),
        market_data_provider_name=os.getenv("MARKET_DATA_PROVIDER_NAME"),
    )
