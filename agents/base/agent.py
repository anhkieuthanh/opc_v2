import asyncio
import os

import yaml
from dotenv import load_dotenv

from shared.message import MessageType, OPCMessage, Payload
from .provider import build_provider, ProviderAdapter
from .queue import RabbitMQClient

load_dotenv()


class BaseAgent:
    def __init__(self, config_path: str):
        with open(config_path) as f:
            self._config = yaml.safe_load(f)

        self._agent_id: str = self._config["agent_id"]
        self._model: str = self._config["model"]
        self._provider_name: str = self._config["provider"]
        self._fallback_model: str | None = self._config.get("fallback_model")
        self._fallback_provider: str | None = self._config.get("fallback_provider")
        self._system_prompt: str = self._config["system_prompt"]
        self._routes: list[dict] = self._config.get("routes", [])
        self._provider: ProviderAdapter = build_provider(self._provider_name)
        self._queue = RabbitMQClient(os.environ["RABBITMQ_URL"])

    async def start(self) -> None:
        await self._queue.connect()
        await self._queue.consume(self._agent_id, self._handle)
        print(f"[{self._agent_id}] listening on queue '{self._agent_id}'")
        await asyncio.Future()

    async def _handle(self, message: OPCMessage) -> None:
        try:
            response_text = await self._provider.complete(
                self._system_prompt, message.payload.content, self._model
            )
        except Exception as exc:
            if self._fallback_model and self._fallback_provider:
                try:
                    fallback = build_provider(self._fallback_provider)
                    response_text = await fallback.complete(
                        self._system_prompt, message.payload.content, self._fallback_model
                    )
                except Exception as fallback_exc:
                    await self._report_error(message, str(fallback_exc))
                    return
            else:
                await self._report_error(message, str(exc))
                return

        await self._on_response(message, response_text)

    async def _on_response(self, original: OPCMessage, response_text: str) -> None:
        reply = OPCMessage(
            from_agent=self._agent_id,
            to=original.from_agent,
            thread_id=original.thread_id,
            type=MessageType.REPORT,
            payload=Payload(content=response_text),
        )
        await self._queue.publish(original.from_agent, reply)

    async def _report_error(self, original: OPCMessage, error: str) -> None:
        reply = OPCMessage(
            from_agent=self._agent_id,
            to=original.from_agent,
            thread_id=original.thread_id,
            type=MessageType.ERROR,
            payload=Payload(content=f"Error: {error}"),
        )
        await self._queue.publish(original.from_agent, reply)

    def _route(self, text: str) -> list[str]:
        return [
            route["queue"]
            for route in self._routes
            if route["trigger"].lower() in text.lower()
        ]
