# OPC — AI Company Framework

Framework microservices để vận hành một **công ty AI** gồm các agent tự động. Các agent giao tiếp với nhau qua message queue bất đồng bộ, có thể cấu hình model và provider riêng cho từng agent, dễ dàng mở rộng cho nhiều mục tiêu kinh doanh khác nhau.

Use case mặc định: **công ty bán sản phẩm online** với 4 agent (CEO, Marketing, Sales, Customer Care).

---

## Kiến trúc

```
React UI (port 3000)
     │ HTTP / WebSocket
FastAPI Gateway (port 8000)
     │
  RabbitMQ (port 5672)
     ├── CEO Agent
     ├── Marketing Agent
     ├── Sales Agent
     └── Customer Care Agent
```

- **Mỗi agent** là một Python process độc lập, cấu hình qua `config.yaml`
- **CEO** nhận yêu cầu từ user, phân tích và routing task đến các agent phù hợp (chạy song song)
- **Gateway** là REST + WebSocket hub duy nhất cho frontend
- **RabbitMQ** đảm bảo message không mất khi agent gặp sự cố (Dead Letter Queue)

---

## Yêu cầu

- [Docker](https://www.docker.com/) và Docker Compose
- API key của ít nhất một trong hai: [Anthropic](https://console.anthropic.com/) hoặc [OpenAI](https://platform.openai.com/)

---

## Chạy nhanh (Docker Compose)

### 1. Clone repo

```bash
git clone https://github.com/anhkieuthanh/opc_v2.git
cd opc_v2
```

### 2. Tạo file `.env`

```bash
cp .env.example .env
```

Mở `.env` và điền API key:

```env
RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672/
ANTHROPIC_API_KEY=sk-ant-...        # bắt buộc nếu dùng provider anthropic
OPENAI_API_KEY=sk-...               # bắt buộc nếu dùng provider openai
```

> **Lưu ý:** Khi chạy qua Docker Compose, `RABBITMQ_URL` phải dùng hostname `rabbitmq` (tên service), không phải `localhost`.

### 3. Khởi động toàn bộ hệ thống

```bash
docker compose up --build
```

Lần đầu build mất 3-5 phút. Sau khi tất cả service `healthy`:

| Service | URL |
|---------|-----|
| Dashboard (UI) | http://localhost:3000 |
| Gateway API | http://localhost:8000 |
| RabbitMQ Management | http://localhost:15672 (guest/guest) |

### 4. Dừng hệ thống

```bash
docker compose down
```

---

## Chạy local (phát triển)

### Yêu cầu thêm

- Python 3.11+
- Node.js 20+
- RabbitMQ đang chạy (xem bên dưới)

### 1. Khởi động RabbitMQ

```bash
docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3-management
```

### 2. Cài dependencies Python

```bash
pip install -e ".[test]"
```

### 3. Tạo `.env`

```bash
cp .env.example .env
# Điền ANTHROPIC_API_KEY hoặc OPENAI_API_KEY
# RABBITMQ_URL=amqp://guest:guest@localhost:5672/  ← dùng localhost khi chạy local
```

### 4. Khởi động các agent và gateway

Mở 5 terminal riêng biệt:

```bash
# Terminal 1 — CEO Agent
python -m agents.ceo.agent

# Terminal 2 — Marketing Agent
python -m agents.marketing.agent

# Terminal 3 — Sales Agent
python -m agents.sales.agent

# Terminal 4 — Customer Care Agent
python -m agents.support.agent

# Terminal 5 — API Gateway
uvicorn gateway.main:app --port 8000 --reload
```

### 5. Khởi động UI

```bash
cd ui
cp .env.example .env   # VITE_API_URL=http://localhost:8000, VITE_WS_URL=ws://localhost:8000/ws
npm install
npm run dev
```

Truy cập http://localhost:3000.

---

## Cấu hình Agent

Mỗi agent có file `agents/<tên>/config.yaml` riêng:

```yaml
agent_id: ceo
model: claude-opus-4-7          # model LLM
provider: anthropic              # anthropic | openai | openai_compatible | codex
fallback_model: gpt-4o           # dùng khi provider chính lỗi
fallback_provider: openai
system_prompt: |
  Bạn là CEO...
routes:                          # CEO dùng routes để routing task
  - trigger: "marketing"
    queue: marketing
  - trigger: "khách hàng"
    queue: support
```

**Thay đổi model/provider:** Sửa `config.yaml` → restart agent tương ứng. Không cần sửa code.

**Providers được hỗ trợ:**

| Provider | Giá trị config | Env var cần có |
|----------|---------------|----------------|
| Anthropic | `anthropic` | `ANTHROPIC_API_KEY` |
| OpenAI | `openai` | `OPENAI_API_KEY` |
| OpenAI-compatible (Ollama, vLLM...) | `openai_compatible` | `OPENAI_API_KEY` (có thể để bất kỳ) |
| Codex | `codex` | `OPENAI_API_KEY` |

---

## Thêm agent mới

1. Tạo thư mục `agents/<tên>/`
2. Tạo `agents/<tên>/config.yaml` (xem mẫu trên)
3. Tạo `agents/<tên>/agent.py`:

```python
import asyncio
from agents.base.agent import BaseAgent

class MyAgent(BaseAgent):
    def __init__(self):
        super().__init__("agents/<tên>/config.yaml")

if __name__ == "__main__":
    asyncio.run(MyAgent().start())
```

4. Thêm vào `docker-compose.yml`:

```yaml
  agent-<tên>:
    build:
      context: .
      dockerfile: docker/agent.Dockerfile
    command: python -m agents.<tên>.agent
    env_file: .env
    depends_on:
      rabbitmq:
        condition: service_healthy
```

5. Thêm route trong `agents/ceo/config.yaml` để CEO biết khi nào giao task cho agent mới.

---

## Chạy tests

### Unit tests (không cần RabbitMQ)

```bash
pytest tests/unit/ -v
```

### Integration tests (cần RabbitMQ)

```bash
docker compose -f docker-compose.test.yml up -d
RABBITMQ_URL=amqp://guest:guest@localhost:5673/ pytest tests/integration/ -v
docker compose -f docker-compose.test.yml down
```

---

## Cấu trúc thư mục

```
opc_v2/
├── agents/
│   ├── base/               # Core loop, provider adapters, RabbitMQ client
│   ├── ceo/                # CEO agent (routing + fan-out)
│   ├── marketing/          # Marketing agent
│   ├── sales/              # Sales agent
│   └── support/            # Customer Care agent
├── gateway/                # FastAPI — REST API + WebSocket hub
├── shared/                 # OPCMessage schema dùng chung
├── ui/                     # React + TypeScript dashboard
├── docker/                 # Dockerfiles cho agents và gateway
├── tests/
│   ├── unit/               # pytest unit tests (15 tests)
│   └── integration/        # RabbitMQ integration test
├── docker-compose.yml      # Production stack
├── docker-compose.test.yml # Test RabbitMQ
└── pyproject.toml          # Python dependencies
```

---

## API Endpoints

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| `GET` | `/health` | Health check |
| `GET` | `/agents/status` | Trạng thái các agent |
| `WebSocket` | `/ws` | Giao tiếp real-time với CEO |

**WebSocket — Gửi message:**
```json
{ "content": "Hãy lên kế hoạch tăng doanh thu tháng này" }
```

**WebSocket — Nhận response (OPCMessage):**
```json
{
  "message_id": "uuid",
  "from": "ceo",
  "to": "gateway",
  "thread_id": "uuid",
  "type": "report",
  "payload": { "content": "...", "priority": "normal" },
  "created_at": "2026-05-16T..."
}
```

---

## Troubleshooting

**Agent không kết nối được RabbitMQ:**
- Docker Compose: đảm bảo `RABBITMQ_URL` dùng `rabbitmq` (hostname), không phải `localhost`
- Local: đảm bảo RabbitMQ đang chạy trên port 5672

**Agent lỗi "Unknown provider":**
- Kiểm tra giá trị `provider` trong `config.yaml` — phải là một trong: `anthropic`, `openai`, `openai_compatible`, `codex`

**CEO không routing task:**
- Kiểm tra `routes` trong `agents/ceo/config.yaml` — trigger phải xuất hiện trong response của CEO
- Thử gửi message có từ khóa rõ ràng: "marketing", "sale", "khách hàng"

**UI không kết nối WebSocket:**
- Kiểm tra `VITE_WS_URL` trong `ui/.env`
- Đảm bảo gateway đang chạy trên port 8000
