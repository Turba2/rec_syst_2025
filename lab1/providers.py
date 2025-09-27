# providers.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, Iterable, Optional
import time
import requests
from config import AppConfig


# ============== МОДЕЛИ ==============

@dataclass
class TranslationRequest:
    """Запрос перевода."""
    source_lang: str  # исходный язык (например, "ru" или "auto")
    target_lang: str  # целевой язык (например, "en")
    text: str         # исходный текст


@dataclass
class TranslationResult:
    """Единый формат ответа для GUI и сравнения провайдеров."""
    provider: str               # имя провайдера (для отображения)
    translated_text: str        # переведённый текст (или пустая строка при ошибке/пустом ответе)
    status_code: int            # HTTP-код ответа
    elapsed_ms: int             # время запроса в миллисекундах
    raw_json: Dict[str, Any]    # «сырой» JSON ответа (для анализа в GUI)


# ============== ХЕЛПЕРЫ ==============

def _post_json(url: str, headers: Dict[str, str], body: Dict[str, Any], timeout_s: int) -> requests.Response:
    """Выполняет POST JSON-запрос и возвращает Response."""
    return requests.post(url, headers=headers, json=body, timeout=timeout_s)


def _first_str(items: Iterable[Any]) -> Optional[str]:
    """Возвращает первую непустую строку из итерируемого."""
    for it in items:
        if isinstance(it, str) and it.strip():
            return it
    return None


# ============== DEEP TRANSLATE (RapidAPI) ==============

class DeepTranslateProvider:
    """Адаптер к Deep Translate на RapidAPI."""

    def __init__(self, cfg: AppConfig) -> None:
        self.cfg = cfg

    @property
    def name(self) -> str:
        return "DeepTranslate (RapidAPI)"

    def translate(self, req: TranslationRequest) -> TranslationResult:
        headers = {
            "content-type": "application/json",
            "X-RapidAPI-Key": self.cfg.rapidapi_key,
            "X-RapidAPI-Host": self.cfg.host_deep,
        }
        body = {"q": req.text, "source": req.source_lang, "target": req.target_lang}

        start = time.perf_counter()
        resp = _post_json(self.cfg.url_deep, headers, body, self.cfg.timeout_s)
        elapsed_ms = int((time.perf_counter() - start) * 1000)

        raw: Dict[str, Any] = {}
        translated = ""
        try:
            raw = resp.json()
            # Возможны 2 формата:
            # 1) {"data":{"translations":[{"translatedText":"..."}]}}
            # 2) {"data":{"translations":{"translatedText":["..."]}}}
            data = raw.get("data", {})
            translations = data.get("translations")

            if isinstance(translations, list):
                texts: list[str] = []
                for obj in translations:
                    if isinstance(obj, dict):
                        val = obj.get("translatedText")
                        if isinstance(val, str):
                            texts.append(val)
                        elif isinstance(val, list):
                            texts += [x for x in val if isinstance(x, str)]
                translated = _first_str(texts) or ""

            elif isinstance(translations, dict):
                val = translations.get("translatedText")
                if isinstance(val, str):
                    translated = val
                elif isinstance(val, list):
                    translated = _first_str(val) or ""
        except Exception:
            translated = ""

        return TranslationResult(self.name, translated, resp.status_code, elapsed_ms, raw)


# ============== GOOGLE TRANSLATE (RapidAPI обёртка) ==============

class GoogleTranslateProvider:
    """Адаптер к Google Translate (провайдер на RapidAPI)."""

    def __init__(self, cfg: AppConfig) -> None:
        self.cfg = cfg

    @property
    def name(self) -> str:
        return "GoogleTranslate (RapidAPI)"

    def translate(self, req: TranslationRequest) -> TranslationResult:
        headers = {
            "content-type": "application/json",
            "X-RapidAPI-Key": self.cfg.rapidapi_key,
            "X-RapidAPI-Host": self.cfg.host_google,
        }
        # ⚡ здесь именно from / to / text
        body = {
            "from": req.source_lang,
            "to": req.target_lang,
            "text": req.text,
        }

        start = time.perf_counter()
        resp = _post_json(self.cfg.url_google, headers, body, self.cfg.timeout_s)
        elapsed_ms = int((time.perf_counter() - start) * 1000)

        raw: Dict[str, Any] = {}
        translated = ""
        try:
            raw = resp.json()
            # разные варианты в API
            translated = (
                raw.get("trans", "")
                or raw.get("translatedText", "")
                or raw.get("translation", "")
                or raw.get("translated_text", "")
            )
        except Exception:
            translated = ""

        return TranslationResult(self.name, translated, resp.status_code, elapsed_ms, raw)
