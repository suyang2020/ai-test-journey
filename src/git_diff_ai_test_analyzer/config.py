from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    """Centralized runtime settings for easy future extension."""

    openai_api_key: str
    openai_model: str = "gpt-4o-mini"
    max_diff_chars: int = 12_000


def load_settings() -> Settings:
    """Load config from environment variables."""

    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise ValueError("OPENAI_API_KEY is required.")

    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip() or "gpt-4o-mini"
    return Settings(openai_api_key=api_key, openai_model=model)

