import json
from collections.abc import Callable
from typing import Any

import aio_pika
from aio_pika.abc import AbstractIncomingMessage

from shared.message import OPCMessage


class RabbitMQClient:
    def __init__(self, url: str):
        self._url = url
        self._connection: aio_pika.abc.AbstractConnection | None = None
        self._channel: aio_pika.abc.AbstractChannel | None = None

    async def connect(self) -> None:
        self._connection = await aio_pika.connect_robust(self._url)
        self._channel = await self._connection.channel()

    async def declare_queue(self, name: str) -> aio_pika.Queue:
        dlx_name = "dlx"
        await self._channel.declare_exchange(
            dlx_name, aio_pika.ExchangeType.FANOUT, durable=True
        )
        dlq = await self._channel.declare_queue(f"{name}.dead", durable=True)
        await dlq.bind(dlx_name)
        return await self._channel.declare_queue(
            name,
            durable=True,
            arguments={"x-dead-letter-exchange": dlx_name},
        )

    async def publish(self, queue_name: str, message: OPCMessage) -> None:
        await self._channel.default_exchange.publish(
            aio_pika.Message(
                body=json.dumps(message.to_dict()).encode(),
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            ),
            routing_key=queue_name,
        )

    async def consume(
        self, queue_name: str, callback: Callable[[OPCMessage], Any]
    ) -> None:
        queue = await self.declare_queue(queue_name)

        async def on_message(raw: AbstractIncomingMessage) -> None:
            async with raw.process():
                data = json.loads(raw.body.decode())
                msg = OPCMessage.from_dict(data)
                await callback(msg)

        await queue.consume(on_message)

    async def close(self) -> None:
        if self._connection:
            await self._connection.close()
