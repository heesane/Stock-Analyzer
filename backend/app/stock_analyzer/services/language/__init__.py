from __future__ import annotations

from .base import LanguagePack
from .english import LANGUAGE_EN
from .korean import LANGUAGE_KO

LANGUAGES = {
    LANGUAGE_EN.code: LANGUAGE_EN,
    LANGUAGE_KO.code: LANGUAGE_KO,
}


def get_language(code: str | None) -> LanguagePack:
    if code and code.lower() == LANGUAGE_KO.code:
        return LANGUAGE_KO
    return LANGUAGE_EN


__all__ = ["LanguagePack", "get_language"]
