from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    """Centralized runtime settings for easy future extension."""

    openai_api_key: str
    openai_model: str = "gpt-4o-mini"
    # For OpenAI-compatible providers (e.g. Alibaba DashScope), set this to their base URL.
    # Example: https://dashscope.aliyuncs.com/compatible-mode/v1
    openai_base_url: str | None = None
    max_diff_chars: int = 12_000


def load_settings() -> Settings:
    """Load config from environment variables."""

    _load_dotenv_if_exists()
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY (provider api key) is required. "
            "Set it in environment variables or in a .env file at project root."
        )

    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip() or "gpt-4o-mini"
    base_url = os.getenv("OPENAI_BASE_URL", "").strip() or None
    return Settings(openai_api_key=api_key, openai_model=model, openai_base_url=base_url)


def _load_dotenv_if_exists() -> None:
    """Load key/value pairs from project-root .env into process env."""

    project_root = Path(__file__).resolve().parents[2]
    dotenv_path = project_root / ".env"
    if not dotenv_path.exists():
        return

    for line in dotenv_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value

