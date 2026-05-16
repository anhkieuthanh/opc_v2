import json
import pytest
from unittest.mock import AsyncMock, MagicMock
from agents.base.queue import RabbitMQClient
from shared.message import MessageType, OPCMessage, Payload


@pytest.fixture
def client():
    return RabbitMQClient("amqp://guest:guest@localhost:5672/")


@pytest.mark.asyncio
async def test_publish_serializes_message(client):
    msg = OPCMessage(
        from_agent="ceo",
        to="marketing",
        type=MessageType.TASK,
        payload=Payload(content="Test task"),
    )
    mock_exchange = AsyncMock()
    mock_channel = MagicMock()
    mock_channel.default_exchange = mock_exchange
    client._channel = mock_channel

    await client.publish("marketing", msg)

    mock_exchange.publish.assert_called_once()
    call_args = mock_exchange.publish.call_args
    published_body = json.loads(call_args[0][0].body.decode())
    assert published_body["from"] == "ceo"
    assert published_body["to"] == "marketing"
    assert published_body["payload"]["content"] == "Test task"
