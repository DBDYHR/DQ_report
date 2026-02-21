from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel

# Load environment variables from a local .env file (if present)
# This allows you to configure YEYSAI_BASE_URL / YEYSAI_API_KEY / YEYSAI_MODEL
# once in server/.env without retyping them in the terminal.
load_dotenv()


class Settings(BaseModel):
    """Application settings, mostly driven by environment variables."""

    # THUNLP / yeysai style OpenAI-compatible endpoint
    # Example:
    #   YEYSAI_BASE_URL=https://yeysai.com/v1
    #   YEYSAI_API_KEY=sk-xxxxxxxx
    #   YEYSAI_MODEL=your-model-name
    ai_base_url: str = os.getenv("YEYSAI_BASE_URL", "https://yeysai.com/v1")
    ai_api_key: str | None = os.getenv("YEYSAI_API_KEY")
    ai_model: str = os.getenv("YEYSAI_MODEL", "gpt-4o-mini")

    # Data directory for JSON storage and uploaded files
    data_dir: Path = Path(
        os.getenv("DQ_REPORT_DATA_DIR")
        or (Path(__file__).resolve().parents[2] / "data")
    )

    class Config:
        arbitrary_types_allowed = True


@lru_cache()
def get_settings() -> Settings:
    """Return a singleton Settings instance and ensure data directories exist."""
    settings = Settings()
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    (settings.data_dir / "uploads").mkdir(parents=True, exist_ok=True)
    return settings

