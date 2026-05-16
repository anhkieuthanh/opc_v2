import os
from abc import ABC, abstractmethod

import anthropic
import openai


class ProviderAdapter(ABC):
    @abstractmethod
    async def complete(self, system_prompt: str, user_message: str, model: str) -> str:
        ...


class OpenAIAdapter(ProviderAdapter):
    def __init__(self, api_key: str | None = None, base_url: str | None = None):
        self._client = openai.AsyncOpenAI(
            api_key=api_key or os.environ["OPENAI_API_KEY"],
            base_url=base_url,
        )

    async def complete(self, system_prompt: str, user_message: str, model: str) -> str:
        resp = await self._client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
        )
        return resp.choices[0].message.content


class AnthropicAdapter(ProviderAdapter):
    def __init__(self, api_key: str | None = None):
        self._client = anthropic.AsyncAnthropic(
            api_key=api_key or os.environ["ANTHROPIC_API_KEY"]
        )

    async def complete(self, system_prompt: str, user_message: str, model: str) -> str:
        resp = await self._client.messages.create(
            model=model,
            max_tokens=4096,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
        )
        return resp.content[0].text


def build_provider(provider: str, **kwargs) -> ProviderAdapter:
    if provider == "anthropic":
        return AnthropicAdapter(**kwargs)
    if provider in ("openai", "openai_compatible", "codex"):
        return OpenAIAdapter(**kwargs)
    raise ValueError(f"Unknown provider: {provider}")
