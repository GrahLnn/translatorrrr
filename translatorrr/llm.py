import random
from dataclasses import dataclass, field
from typing import Optional

import ell
import openai
from pydantic_settings import BaseSettings

from .utils import remove_translation_tags

PLATFORM_MAP = {
    "gemini": {
        "models": [
            "gemini-1.5-pro-002",
            "gemini-1.5-pro-001",
            "gemini-1.5-flash-002",
            "gemini-1.5-flash-001",
            "gemini-1.5-flash-8b",
        ],
    },
    "openai": {
        "models": ["gpt-4o", "gpt-4o-mini"],
    },
    # "claude": {
    #     "models": ["claude-3-haiku", "claude-3-5-sonnet", "claude-3-opus"],
    # },
}


class LLMSettings(BaseSettings):
    gemini_api_keys: Optional[str] = None
    gemini_base_url: str
    openai_api_keys: Optional[str] = None
    openai_base_url: str
    # claude_api_keys: Optional[str] = None
    # claude_base_url: str
    mission_model: str

    class Config:
        env_file = ".env"
        extra = "ignore"

    def get_api_keys(self, platform: str) -> list[str]:
        key_value: Optional[str] = getattr(self, f"{platform}_api_keys", None)
        if not key_value:
            raise ValueError(
                f"未配置 {platform}_api_keys，请在 .env 文件中设置, 多个key使用`,`分隔"
            )
        return [k.strip() for k in key_value.split(",")]

    def get_platform(self) -> str:
        for platform, config in PLATFORM_MAP.items():
            if self.mission_model in config["models"]:
                return platform
        raise ValueError(f"Unsupported model: {self.mission_model}")

    def pick_key_and_url(self):
        platform = self.get_platform()
        api_keys = self.get_api_keys(platform)
        base_url = getattr(self, f"{platform}_base_url")
        return random.choice(api_keys), base_url


@dataclass
class LLM:
    settings: LLMSettings = field(default_factory=LLMSettings)
    key: str = field(init=False)
    base_url: str = field(init=False)
    client: openai.Client = field(init=False)

    def __post_init__(self):
        self.key, self.base_url = self.settings.pick_key_and_url()
        self.client = openai.Client(api_key=self.key, base_url=self.base_url)

    def do(self, prompt: str):
        @ell.simple(
            model=self.settings.mission_model,
            client=self.client,
            temperature=1,
            top_p=0.95,
        )
        def _do():
            return prompt

        return remove_translation_tags(_do())
