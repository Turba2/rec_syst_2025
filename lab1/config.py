from __future__ import annotations
from dataclasses import dataclass
import os
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class AppConfig:
    """Конфигурация приложения из .env"""
    rapidapi_key: str
    host_deep: str
    host_google: str
    url_deep: str
    url_google: str
    timeout_s: int

def load_config() -> AppConfig:
    key = os.getenv("RAPIDAPI_KEY", "")
    if not key:
        raise RuntimeError("RAPIDAPI_KEY не задан в .env")

    return AppConfig(
        rapidapi_key=key,
        host_deep=os.getenv("RAPIDAPI_HOST_DEEP_TRANSLATE", ""),
        host_google=os.getenv("RAPIDAPI_HOST_GOOGLE", ""),
        url_deep=os.getenv("DEEP_TRANSLATE_BASE_URL", ""),
        url_google=os.getenv("GOOGLE_TRANSLATE_BASE_URL", ""),
        timeout_s=int(os.getenv("DEFAULT_TIMEOUT_SECONDS", "15")),
    )
