# OPC Backend Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Xây dựng backend microservices hoàn chỉnh — 4 AI agents (CEO, Marketing, Sales, Support) giao tiếp qua RabbitMQ, phục vụ qua FastAPI Gateway với WebSocket real-time.

**Architecture:** Mỗi agent là một Python process độc lập, đọc config từ YAML, kết nối RabbitMQ để nhận/gửi message, gọi LLM qua provider adapter. FastAPI Gateway là điểm vào duy nhất từ bên ngoài, expose REST + WebSocket, lắng nghe queue "gateway" để push kết quả về client.

**Tech Stack:** Python 3.11+, aio-pika, openai SDK, anthropic SDK, pyyaml, FastAPI, uvicorn, pydantic, pytest, pytest-asyncio, Docker, RabbitMQ 3.

---

## File Map

```
opc_v2/
├── shared/
│   ├── __init__.py
│   └── message.py              # OPCMessage dataclass + MessageType enum + Payload
├── agents/
│   ├── __init__.py
│   ├── base/
│   │   ├── __init__.py
│   │   ├── agent.py            # BaseAgent: load config, connect queue, core loop
│   │   ├── provider.py         # ProviderAdapter ABC + OpenAIAdapter + AnthropicAdapter + build_provider()
│   │   └── queue.py            # RabbitMQClient: connect, declare_queue, publish, consume, close
│   ├── ceo/
│   │   ├── __init__.py
│   │   ├── config.yaml
│   │   └── agent.py            # CEOAgent(BaseAgent): routing + fan-out + report to gateway
│   ├── marketing/
│   │   ├── __init__.py
│   │   ├── config.yaml
│   │   └── agent.py            # MarketingAgent(BaseAgent): overrides system prompt only
│   ├── sales/
│   │   ├── __init__.py
│   │   ├── config.yaml
│   │   └── agent.py            # SalesAgent(BaseAgent)
│   └── support/
│       ├── __init__.py
│       ├── config.yaml
│       └── agent.py            # SupportAgent(BaseAgent)
├── gateway/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app, lifespan, CORS, /agents/status, /ws
│   └── ws.py                   # ConnectionManager: connect, disconnect, broadcast
├── tests/
│   ├── __init__.py
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── test_message.py     # OPCMessage serialization round-trip
│   │   ├── test_provider.py    # build_provider() dispatch, adapter.complete() mocked
│   │   ├── test_queue.py       # RabbitMQClient publish/consume with aio-pika mock
│   │   └── test_ceo_routing.py # CEOAgent._route() logic
│   └── integration/
│       ├── __init__.py
│       └── test_agent_flow.py  # CEO → Marketing via real RabbitMQ (docker-compose.test.yml)
├── docker/
│   ├── agent.Dockerfile
│   └── gateway.Dockerfile
├── docker-compose.yml
├── docker-compose.test.yml
├── pyproject.toml
├── .env.example
└── .gitignore
```

---

## Task 1: Project scaffolding

**Files:**
- Create: `pyproject.toml`
- Create: `.env.example`
- Create: `.gitignore`
- Create: `shared/__init__.py`
- Create: `agents/__init__.py`
- Create: `agents/base/__init__.py`
- Create: `agents/ceo/__init__.py`
- Create: `agents/marketing/__init__.py`
- Create: `agents/sales/__init__.py`
- Create: `agents/support/__init__.py`
- Create: `gateway/__init__.py`
- Create: `tests/__init__.py`
- Create: `tests/unit/__init__.py`
- Create: `tests/integration/__init__.py`

- [ ] **Step 1: Tạo pyproject.toml**

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "opc"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "aio-pika>=9.0",
    "openai>=1.0",
    "anthropic>=0.30",
    "pyyaml>=6.0",
    "fastapi>=0.110",
    "uvicorn[standard]>=0.29",
    "pydantic>=2.0",
    "python-dotenv>=1.0",
]

[project.optional-dependencies]
test = [
    "pytest>=8.0",
    "pytest-asyncio>=0.23",
    "pytest-mock>=3.12",
    "httpx>=0.27",
]

[tool.pytest.ini_options]
asyncio_mode = "auto"
```

- [ ] **Step 2: Tạo .env.example**

```bash
RABBITMQ_URL=amqp://guest:guest@localhost:5672/
ANTHROPIC_API_KEY=your_anthropic_key_here
OPENAI_API_KEY=your_openai_key_here
```

- [ ] **Step 3: Tạo .gitignore**

```
.env
__pycache__/
*.pyc
.pytest_cache/
*.egg-info/
dist/
.venv/
```

- [ ] **Step 4: Tạo tất cả file `__init__.py` trống**

```bash
mkdir -p shared agents/base agents/ceo agents/marketing agents/sales agents/support gateway tests/unit tests/integration
touch shared/__init__.py agents/__init__.py agents/base/__init__.py \
  agents/ceo/__init__.py agents/marketing/__init__.py \
  agents/sales/__init__.py agents/support/__init__.py \
  gateway/__init__.py tests/__init__.py tests/unit/__init__.py \
  tests/integration/__init__.py
```

- [ ] **Step 5: Cài dependencies**

```bash
pip install -e ".[test]"
```

Expected: Successfully installed opc-0.1.0 và các dependencies.

- [ ] **Step 6: Commit**

```bash
git add pyproject.toml .env.example .gitignore shared/ agents/ gateway/ tests/
git commit -m "chore: project scaffolding and dependencies"
```

---

## Task 2: Shared message schema

**Files:**
- Create: `shared/message.py`
- Test: `tests/unit/test_message.py`

- [ ] **Step 1: Viết failing test**

```python
# tests/unit/test_message.py
from shared.message import MessageType, OPCMessage, Payload


def test_message_round_trip():
    msg = OPCMessage(
        from_agent="ceo",
        to="marketing",
        type=MessageType.TASK,
        payload=Payload(content="Run a campaign", priority="high"),
    )
    data = msg.to_dict()
    restored = OPCMessage.from_dict(data)

    assert restored.from_agent == "ceo"
    assert restored.to == "marketing"
    assert restored.type == MessageType.TASK
    assert restored.payload.content == "Run a campaign"
    assert restored.payload.priority == "high"
    assert restored.message_id == msg.message_id
    assert restored.thread_id == msg.thread_id


def test_message_default_priority():
    msg = OPCMessage(
        from_agent="sales",
        to="ceo",
        type=MessageType.REPORT,
        payload=Payload(content="Done"),
    )
    assert msg.payload.priority == "normal"


def test_message_type_values():
    assert MessageType.TASK == "task"
    assert MessageType.REPORT == "report"
    assert MessageType.ERROR == "error"
```

- [ ] **Step 2: Chạy test để xác nhận fail**

```bash
pytest tests/unit/test_message.py -v
```

Expected: FAILED — `ModuleNotFoundError: No module named 'shared.message'`

- [ ] **Step 3: Implement shared/message.py**

```python
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4


class MessageType(str, Enum):
    TASK = "task"
    REPORT = "report"
    ERROR = "error"


@dataclass
class Payload:
    content: str
    context: dict = field(default_factory=dict)
    priority: str = "normal"


@dataclass
class OPCMessage:
    from_agent: str
    to: str
    type: MessageType
    payload: Payload
    message_id: str = field(default_factory=lambda: str(uuid4()))
    thread_id: str = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> dict:
        return {
            "message_id": self.message_id,
            "from": self.from_agent,
            "to": self.to,
            "thread_id": self.thread_id,
            "type": self.type.value,
            "payload": {
                "content": self.payload.content,
                "context": self.payload.context,
                "priority": self.payload.priority,
            },
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "OPCMessage":
        return cls(
            message_id=data["message_id"],
            from_agent=data["from"],
            to=data["to"],
            thread_id=data["thread_id"],
            type=MessageType(data["type"]),
            payload=Payload(
                content=data["payload"]["content"],
                context=data["payload"].get("context", {}),
                priority=data["payload"].get("priority", "normal"),
            ),
            created_at=data["created_at"],
        )
```

- [ ] **Step 4: Chạy test để xác nhận pass**

```bash
pytest tests/unit/test_message.py -v
```

Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
git add shared/message.py tests/unit/test_message.py
git commit -m "feat: shared OPCMessage schema with serialization"
```

---

## Task 3: RabbitMQ client

**Files:**
- Create: `agents/base/queue.py`
- Test: `tests/unit/test_queue.py`

- [ ] **Step 1: Viết failing test**

```python
# tests/unit/test_queue.py
import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
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
```

- [ ] **Step 2: Chạy test để xác nhận fail**

```bash
pytest tests/unit/test_queue.py -v
```

Expected: FAILED — `ModuleNotFoundError: No module named 'agents.base.queue'`

- [ ] **Step 3: Implement agents/base/queue.py**

```python
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
```

- [ ] **Step 4: Chạy test để xác nhận pass**

```bash
pytest tests/unit/test_queue.py -v
```

Expected: 1 passed.

- [ ] **Step 5: Commit**

```bash
git add agents/base/queue.py tests/unit/test_queue.py
git commit -m "feat: RabbitMQ client with DLQ support"
```

---

## Task 4: Provider adapters

**Files:**
- Create: `agents/base/provider.py`
- Test: `tests/unit/test_provider.py`

- [ ] **Step 1: Viết failing test**

```python
# tests/unit/test_provider.py
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
```

- [ ] **Step 2: Chạy test để xác nhận fail**

```bash
pytest tests/unit/test_provider.py -v
```

Expected: FAILED — `ModuleNotFoundError: No module named 'agents.base.provider'`

- [ ] **Step 3: Implement agents/base/provider.py**

```python
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
```

- [ ] **Step 4: Chạy test để xác nhận pass**

```bash
pytest tests/unit/test_provider.py -v
```

Expected: 5 passed.

- [ ] **Step 5: Commit**

```bash
git add agents/base/provider.py tests/unit/test_provider.py
git commit -m "feat: multi-provider adapter (OpenAI-compatible + Anthropic)"
```

---

## Task 5: BaseAgent core loop

**Files:**
- Create: `agents/base/agent.py`

- [ ] **Step 1: Implement agents/base/agent.py**

```python
import asyncio
import os
from pathlib import Path

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
                fallback = build_provider(self._fallback_provider)
                response_text = await fallback.complete(
                    self._system_prompt, message.payload.content, self._fallback_model
                )
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
```

- [ ] **Step 2: Commit**

```bash
git add agents/base/agent.py
git commit -m "feat: BaseAgent core loop with fallback and error handling"
```

---

## Task 6: CEO agent + routing tests

**Files:**
- Create: `agents/ceo/config.yaml`
- Create: `agents/ceo/agent.py`
- Test: `tests/unit/test_ceo_routing.py`

- [ ] **Step 1: Viết failing test**

```python
# tests/unit/test_ceo_routing.py
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import yaml, os


def make_ceo():
    from agents.ceo.agent import CEOAgent
    with patch("agents.base.agent.RabbitMQClient"), \
         patch("agents.base.agent.build_provider"):
        return CEOAgent()


def test_route_marketing(tmp_path):
    agent = make_ceo()
    queues = agent._route("Chúng ta cần một chiến dịch marketing mới")
    assert "marketing" in queues


def test_route_sales(tmp_path):
    agent = make_ceo()
    queues = agent._route("Hãy cải thiện pipeline sale")
    assert "sales" in queues


def test_route_support(tmp_path):
    agent = make_ceo()
    queues = agent._route("Khách hàng phàn nàn về đơn hàng")
    assert "support" in queues


def test_route_no_match(tmp_path):
    agent = make_ceo()
    queues = agent._route("Hôm nay thời tiết đẹp")
    assert queues == []


def test_route_multiple(tmp_path):
    agent = make_ceo()
    queues = agent._route("marketing và sale cùng phối hợp")
    assert "marketing" in queues
    assert "sales" in queues
```

- [ ] **Step 2: Chạy test để xác nhận fail**

```bash
pytest tests/unit/test_ceo_routing.py -v
```

Expected: FAILED — `ModuleNotFoundError: No module named 'agents.ceo.agent'`

- [ ] **Step 3: Tạo agents/ceo/config.yaml**

```yaml
agent_id: ceo
model: claude-opus-4-7
provider: anthropic
fallback_model: gpt-4o
fallback_provider: openai
system_prompt: |
  Bạn là CEO của một công ty bán sản phẩm online. Nhiệm vụ của bạn là:
  1. Phân tích yêu cầu từ người dùng
  2. Phân công task cho các phòng ban phù hợp (marketing, sales, support)
  3. Tổng hợp kết quả và báo cáo lại
  Hãy trả lời bằng tiếng Việt, ngắn gọn và rõ ràng.
routes:
  - trigger: "marketing"
    queue: marketing
  - trigger: "campaign"
    queue: marketing
  - trigger: "sale"
    queue: sales
  - trigger: "bán hàng"
    queue: sales
  - trigger: "khách hàng"
    queue: support
  - trigger: "support"
    queue: support
  - trigger: "phàn nàn"
    queue: support
```

- [ ] **Step 4: Tạo agents/ceo/agent.py**

```python
import asyncio

from agents.base.agent import BaseAgent
from shared.message import MessageType, OPCMessage, Payload


class CEOAgent(BaseAgent):
    def __init__(self):
        super().__init__("agents/ceo/config.yaml")

    async def _on_response(self, original: OPCMessage, response_text: str) -> None:
        queues = self._route(response_text)
        if queues:
            await asyncio.gather(
                *[
                    self._queue.publish(
                        q,
                        OPCMessage(
                            from_agent=self._agent_id,
                            to=q,
                            thread_id=original.thread_id,
                            type=MessageType.TASK,
                            payload=Payload(
                                content=response_text,
                                priority=original.payload.priority,
                            ),
                        ),
                    )
                    for q in queues
                ]
            )

        await self._queue.publish(
            "gateway",
            OPCMessage(
                from_agent=self._agent_id,
                to="gateway",
                thread_id=original.thread_id,
                type=MessageType.REPORT,
                payload=Payload(content=response_text),
            ),
        )


if __name__ == "__main__":
    asyncio.run(CEOAgent().start())
```

- [ ] **Step 5: Chạy test để xác nhận pass**

```bash
pytest tests/unit/test_ceo_routing.py -v
```

Expected: 5 passed.

- [ ] **Step 6: Commit**

```bash
git add agents/ceo/ tests/unit/test_ceo_routing.py
git commit -m "feat: CEO agent with multi-queue fan-out routing"
```

---

## Task 7: Marketing, Sales, Support agents

**Files:**
- Create: `agents/marketing/config.yaml`
- Create: `agents/marketing/agent.py`
- Create: `agents/sales/config.yaml`
- Create: `agents/sales/agent.py`
- Create: `agents/support/config.yaml`
- Create: `agents/support/agent.py`

- [ ] **Step 1: Tạo agents/marketing/config.yaml**

```yaml
agent_id: marketing
model: claude-sonnet-4-6
provider: anthropic
fallback_model: gpt-4o-mini
fallback_provider: openai
system_prompt: |
  Bạn là Marketing Manager của công ty bán sản phẩm online. Nhiệm vụ:
  1. Xây dựng chiến lược marketing và campaign
  2. Đề xuất nội dung quảng cáo, kênh phân phối
  3. Phân tích thị trường và đối thủ cạnh tranh
  Trả lời bằng tiếng Việt, chuyên nghiệp và cụ thể.
routes: []
```

- [ ] **Step 2: Tạo agents/marketing/agent.py**

```python
import asyncio
from agents.base.agent import BaseAgent


class MarketingAgent(BaseAgent):
    def __init__(self):
        super().__init__("agents/marketing/config.yaml")


if __name__ == "__main__":
    asyncio.run(MarketingAgent().start())
```

- [ ] **Step 3: Tạo agents/sales/config.yaml**

```yaml
agent_id: sales
model: claude-sonnet-4-6
provider: anthropic
fallback_model: gpt-4o-mini
fallback_provider: openai
system_prompt: |
  Bạn là Sales Manager của công ty bán sản phẩm online. Nhiệm vụ:
  1. Xử lý pipeline bán hàng và theo dõi leads
  2. Đề xuất chiến lược chốt đơn và upsell
  3. Báo cáo doanh thu và KPI bán hàng
  Trả lời bằng tiếng Việt, tập trung vào kết quả đo lường được.
routes: []
```

- [ ] **Step 4: Tạo agents/sales/agent.py**

```python
import asyncio
from agents.base.agent import BaseAgent


class SalesAgent(BaseAgent):
    def __init__(self):
        super().__init__("agents/sales/config.yaml")


if __name__ == "__main__":
    asyncio.run(SalesAgent().start())
```

- [ ] **Step 5: Tạo agents/support/config.yaml**

```yaml
agent_id: support
model: claude-haiku-4-5-20251001
provider: anthropic
fallback_model: gpt-4o-mini
fallback_provider: openai
system_prompt: |
  Bạn là Customer Care Manager của công ty bán sản phẩm online. Nhiệm vụ:
  1. Xử lý khiếu nại và phản hồi khách hàng
  2. Đề xuất giải pháp hỗ trợ sau bán hàng
  3. Theo dõi satisfaction score và cải thiện trải nghiệm
  Trả lời bằng tiếng Việt, thân thiện và giải quyết vấn đề hiệu quả.
routes: []
```

- [ ] **Step 6: Tạo agents/support/agent.py**

```python
import asyncio
from agents.base.agent import BaseAgent


class SupportAgent(BaseAgent):
    def __init__(self):
        super().__init__("agents/support/config.yaml")


if __name__ == "__main__":
    asyncio.run(SupportAgent().start())
```

- [ ] **Step 7: Chạy toàn bộ unit tests**

```bash
pytest tests/unit/ -v
```

Expected: All tests passed.

- [ ] **Step 8: Commit**

```bash
git add agents/marketing/ agents/sales/ agents/support/
git commit -m "feat: Marketing, Sales, Support agents with YAML config"
```

---

## Task 8: FastAPI Gateway

**Files:**
- Create: `gateway/ws.py`
- Create: `gateway/main.py`

- [ ] **Step 1: Tạo gateway/ws.py**

```python
import json
from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self._active: list[WebSocket] = []

    async def connect(self, ws: WebSocket) -> None:
        await ws.accept()
        self._active.append(ws)

    def disconnect(self, ws: WebSocket) -> None:
        if ws in self._active:
            self._active.remove(ws)

    async def broadcast(self, data: dict) -> None:
        for ws in list(self._active):
            try:
                await ws.send_text(json.dumps(data, ensure_ascii=False))
            except Exception:
                self.disconnect(ws)
```

- [ ] **Step 2: Tạo gateway/main.py**

```python
import asyncio
import json
import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from agents.base.queue import RabbitMQClient
from gateway.ws import ConnectionManager
from shared.message import MessageType, OPCMessage, Payload

load_dotenv()

manager = ConnectionManager()
queue_client = RabbitMQClient(os.environ["RABBITMQ_URL"])


@asynccontextmanager
async def lifespan(app: FastAPI):
    await queue_client.connect()
    asyncio.create_task(_listen_gateway_queue())
    yield
    await queue_client.close()


app = FastAPI(title="OPC Gateway", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


async def _listen_gateway_queue() -> None:
    async def on_message(msg: OPCMessage) -> None:
        await manager.broadcast(msg.to_dict())

    await queue_client.consume("gateway", on_message)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    await manager.connect(websocket)
    try:
        while True:
            raw = await websocket.receive_text()
            data = json.loads(raw)
            msg = OPCMessage(
                from_agent="user",
                to="ceo",
                type=MessageType.TASK,
                payload=Payload(content=data["content"]),
            )
            await queue_client.publish("ceo", msg)
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.get("/agents/status")
async def agents_status() -> dict:
    return {
        "agents": [
            {"id": "ceo", "status": "active"},
            {"id": "marketing", "status": "active"},
            {"id": "sales", "status": "active"},
            {"id": "support", "status": "active"},
        ]
    }


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}
```

- [ ] **Step 3: Test /health endpoint**

```bash
pip install httpx
uvicorn gateway.main:app --port 8000 &
curl http://localhost:8000/health
```

Expected: `{"status":"ok"}`

```bash
kill %1
```

- [ ] **Step 4: Commit**

```bash
git add gateway/ws.py gateway/main.py
git commit -m "feat: FastAPI gateway with WebSocket hub and /agents/status"
```

---

## Task 9: Docker Compose + Dockerfiles

**Files:**
- Create: `docker/agent.Dockerfile`
- Create: `docker/gateway.Dockerfile`
- Create: `docker-compose.yml`
- Create: `docker-compose.test.yml`

- [ ] **Step 1: Tạo docker/agent.Dockerfile**

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY pyproject.toml .
RUN pip install -e .

COPY shared/ shared/
COPY agents/ agents/

ENV PYTHONUNBUFFERED=1
```

- [ ] **Step 2: Tạo docker/gateway.Dockerfile**

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY pyproject.toml .
RUN pip install -e .

COPY shared/ shared/
COPY agents/base/ agents/base/
COPY agents/__init__.py agents/__init__.py
COPY gateway/ gateway/

ENV PYTHONUNBUFFERED=1
CMD ["uvicorn", "gateway.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

- [ ] **Step 3: Tạo docker-compose.yml**

```yaml
services:
  rabbitmq:
    image: rabbitmq:3-management
    ports:
      - "5672:5672"
      - "15672:15672"
    healthcheck:
      test: ["CMD", "rabbitmq-diagnostics", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  gateway:
    build:
      context: .
      dockerfile: docker/gateway.Dockerfile
    ports:
      - "8000:8000"
    env_file: .env
    depends_on:
      rabbitmq:
        condition: service_healthy

  agent-ceo:
    build:
      context: .
      dockerfile: docker/agent.Dockerfile
    command: python -m agents.ceo.agent
    env_file: .env
    depends_on:
      rabbitmq:
        condition: service_healthy

  agent-marketing:
    build:
      context: .
      dockerfile: docker/agent.Dockerfile
    command: python -m agents.marketing.agent
    env_file: .env
    depends_on:
      rabbitmq:
        condition: service_healthy

  agent-sales:
    build:
      context: .
      dockerfile: docker/agent.Dockerfile
    command: python -m agents.sales.agent
    env_file: .env
    depends_on:
      rabbitmq:
        condition: service_healthy

  agent-support:
    build:
      context: .
      dockerfile: docker/agent.Dockerfile
    command: python -m agents.support.agent
    env_file: .env
    depends_on:
      rabbitmq:
        condition: service_healthy
```

- [ ] **Step 4: Tạo docker-compose.test.yml**

```yaml
services:
  rabbitmq-test:
    image: rabbitmq:3
    ports:
      - "5673:5672"
    healthcheck:
      test: ["CMD", "rabbitmq-diagnostics", "ping"]
      interval: 5s
      timeout: 3s
      retries: 10
```

- [ ] **Step 5: Tạo .env từ .env.example**

```bash
cp .env.example .env
# Điền ANTHROPIC_API_KEY và OPENAI_API_KEY vào .env
```

- [ ] **Step 6: Commit**

```bash
git add docker/ docker-compose.yml docker-compose.test.yml
git commit -m "chore: Docker Compose with healthcheck and multi-agent setup"
```

---

## Task 10: Integration test

**Files:**
- Test: `tests/integration/test_agent_flow.py`

- [ ] **Step 1: Viết integration test**

```python
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
```

- [ ] **Step 2: Chạy RabbitMQ test container**

```bash
docker compose -f docker-compose.test.yml up -d
sleep 5
```

- [ ] **Step 3: Chạy integration test**

```bash
RABBITMQ_URL=amqp://guest:guest@localhost:5673/ pytest tests/integration/ -v
```

Expected: 1 passed.

- [ ] **Step 4: Dừng test container**

```bash
docker compose -f docker-compose.test.yml down
```

- [ ] **Step 5: Commit**

```bash
git add tests/integration/test_agent_flow.py
git commit -m "test: integration test for RabbitMQ publish/consume flow"
```

---

## Task 11: Smoke test toàn hệ thống

- [ ] **Step 1: Build và start toàn bộ stack**

```bash
cp .env.example .env
# Đảm bảo .env có ANTHROPIC_API_KEY hợp lệ
docker compose up --build -d
```

- [ ] **Step 2: Đợi services healthy**

```bash
docker compose ps
```

Expected: tất cả services `healthy` hoặc `running`.

- [ ] **Step 3: Kiểm tra gateway**

```bash
curl http://localhost:8000/health
```

Expected: `{"status":"ok"}`

```bash
curl http://localhost:8000/agents/status
```

Expected: JSON với 4 agents, tất cả status `"active"`.

- [ ] **Step 4: Test WebSocket bằng wscat**

```bash
npm install -g wscat
wscat -c ws://localhost:8000/ws
```

Gõ vào terminal:
```json
{"content": "Hãy lên kế hoạch tăng doanh thu tháng này"}
```

Expected: Nhận response JSON từ CEO agent trong vòng 10-30 giây.

- [ ] **Step 5: Xem logs agents**

```bash
docker compose logs agent-ceo --tail=20
docker compose logs agent-marketing --tail=20
```

Expected: Log hiển thị agent đang lắng nghe queue và xử lý message.

- [ ] **Step 6: Dừng stack**

```bash
docker compose down
```

- [ ] **Step 7: Final commit**

```bash
git add .
git commit -m "chore: complete OPC backend — all agents, gateway, docker stack"
git push origin main
```

---

## Self-Review Checklist

- [x] **Spec coverage:**
  - Shared message schema → Task 2
  - RabbitMQ async messaging + DLQ → Task 3
  - Multi-provider adapters (Anthropic, OpenAI, fallback) → Task 4
  - BaseAgent core loop + fallback + error → Task 5
  - CEO agent + routing + fan-out → Task 6
  - Marketing, Sales, Support agents + YAML config → Task 7
  - FastAPI Gateway + WebSocket + /agents/status → Task 8
  - Docker Compose + Dockerfiles + healthcheck → Task 9
  - Integration test → Task 10
  - Smoke test toàn hệ thống → Task 11

- [x] **Placeholder scan:** Không có TBD/TODO/placeholder

- [x] **Type consistency:**
  - `OPCMessage.from_agent` dùng nhất quán (không phải `sender` hay `source`)
  - `build_provider()` return type `ProviderAdapter` dùng nhất quán
  - `RabbitMQClient.publish(queue_name, message)` signature nhất quán qua Tasks 3, 5, 6, 8
