from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LanguagePack:
    code: str
    name: str
    messages: dict[str, str]

    def t(self, key: str, **kwargs) -> str:
        template = self.messages.get(key)
        if template is None:
            return key
        return template.format(**kwargs)
