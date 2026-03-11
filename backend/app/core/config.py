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


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    mode = os.getenv("INTERPRETER_MODE", "mock").strip().lower() or "mock"
    if mode not in {"mock", "openai"}:
        mode = "mock"
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL", "gpt-5.4").strip() or "gpt-5.4"
    return Settings(
        interpreter_mode=mode,
        openai_api_key=api_key,
        openai_model=model,
    )
