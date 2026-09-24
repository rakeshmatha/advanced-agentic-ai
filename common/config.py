from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, ConfigDict, Field, SecretStr


def _project_root() -> Path:
    return Path(__file__).resolve().parents[1]


load_dotenv(_project_root() / ".env")


class Settings(BaseModel):
    model_config = ConfigDict(extra="forbid")

    openai_api_key: SecretStr = Field(..., alias="OPENAI_API_KEY")
    openweathermap_api_key: SecretStr | None = Field(
        default=None, alias="OPENWEATHERMAP_API_KEY"
    )
    tavily_api_key: SecretStr | None = Field(default=None, alias="TAVILY_API_KEY")
    model: str = "gpt-4o-mini"
    temperature: float = 0.4
    max_tokens: int = 200

    @classmethod
    def from_env(cls) -> "Settings":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY is missing. Add it to the .env file.")
        return cls(
            OPENAI_API_KEY=api_key,
            OPENWEATHERMAP_API_KEY=os.getenv("OPENWEATHERMAP_API_KEY"),
            TAVILY_API_KEY=os.getenv("TAVILY_API_KEY"),
        )


settings = Settings.from_env()
