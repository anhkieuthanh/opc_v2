import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from agents.base.provider import build_provider, OpenAIAdapter, AnthropicAdapter


def test_build_provider_openai():
    with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
        adapter = build_provider("openai")
    assert isinstance(adapter, OpenAIAdapter)


def test_build_provider_anthropic():
    with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"}):
        adapter = build_provider("anthropic")
    assert isinstance(adapter, AnthropicAdapter)


def test_build_provider_openai_compatible():
    with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
        adapter = build_provider("openai_compatible", base_url="http://localhost:11434/v1")
    assert isinstance(adapter, OpenAIAdapter)


def test_build_provider_unknown_raises():
    with pytest.raises(ValueError, match="Unknown provider"):
        build_provider("unknown_provider")


@pytest.mark.asyncio
async def test_openai_adapter_complete():
    with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
        adapter = OpenAIAdapter()

    mock_response = MagicMock()
    mock_response.choices[0].message.content = "Marketing response"
    adapter._client.chat.completions.create = AsyncMock(return_value=mock_response)

    result = await adapter.complete(
        system_prompt="You are a marketing agent",
        user_message="Create a campaign",
        model="gpt-4o",
    )
    assert result == "Marketing response"


@pytest.mark.asyncio
async def test_anthropic_adapter_complete():
    with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"}):
        adapter = AnthropicAdapter()

    mock_response = MagicMock()
    mock_response.content[0].text = "CEO response"
    adapter._client.messages.create = AsyncMock(return_value=mock_response)

    result = await adapter.complete(
        system_prompt="You are the CEO",
        user_message="Increase revenue",
        model="claude-opus-4-7",
    )
    assert result == "CEO response"
