from __future__ import annotations

from openai import OpenAI

from common.config import settings


def build_client() -> OpenAI:
    return OpenAI(api_key=settings.openai_api_key.get_secret_value())


def chat(prompt: str) -> str:
    response = build_client().responses.create(
        model=settings.model,
        input=prompt,
        temperature=settings.temperature,
        max_output_tokens=settings.max_tokens,
    )
    return response.output_text
