from fastapi import Depends

from .config import Settings, get_settings
from .services.ai_client import AiClient
from .services.reports_store import ReportsStore


def get_settings_dep() -> Settings:
    """Expose settings as a FastAPI dependency."""
    return get_settings()


def get_ai_client(
    settings: Settings = Depends(get_settings_dep),
) -> AiClient:
    """Provide a configured AI client."""
    return AiClient(settings=settings)


def get_reports_store(
    settings: Settings = Depends(get_settings_dep),
) -> ReportsStore:
    """Provide a JSON-file–backed reports store."""
    return ReportsStore(data_dir=settings.data_dir)

