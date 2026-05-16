# tests/integration/test_agent_flow.py
"""
Chạy test này với RabbitMQ đang chạy:
  docker compose -f docker-compose.test.yml up -d
  RABBITMQ_URL=amqp://guest:guest@localhost:5673/ pytest tests/integration/ -v
  docker compose -f docker-compose.test.yml down
"""
import asyncio
import os
import pytest
from shared.message import MessageType, OPCMessage, Payload
from agents.base.queue import RabbitMQClient

RABBITMQ_URL = os.environ.get("RABBITMQ_URL", "amqp://guest:guest@localhost:5673/")


@pytest.mark.asyncio
async def test_message_publish_and_consume():
    publisher = RabbitMQClient(RABBITMQ_URL)
    consumer = RabbitMQClient(RABBITMQ_URL)
    await publisher.connect()
    await consumer.connect()

    received: list[OPCMessage] = []
    ready = asyncio.Event()

    async def on_msg(msg: OPCMessage) -> None:
        received.append(msg)
        ready.set()

    await consumer.consume("test-queue", on_msg)

    msg = OPCMessage(
        from_agent="test",
        to="test-queue",
        type=MessageType.TASK,
        payload=Payload(content="hello integration"),
    )
    await publisher.publish("test-queue", msg)

    await asyncio.wait_for(ready.wait(), timeout=5.0)

    assert len(received) == 1
    assert received[0].payload.content == "hello integration"
    assert received[0].type == MessageType.TASK

    await publisher.close()
    await consumer.close()
