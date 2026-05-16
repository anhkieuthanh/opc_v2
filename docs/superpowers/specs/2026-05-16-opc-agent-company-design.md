# OPC Agent Company Framework — Design Spec

**Date:** 2026-05-16  
**Status:** Approved  

---

## Overview

OPC là một framework microservices để vận hành một "công ty AI" gồm các agent tự động. Framework được thiết kế để tái cấu hình cho nhiều mục tiêu kinh doanh khác nhau. Use case triển khai đầu tiên: **công ty bán sản phẩm online**.

Lấy cảm hứng từ:
- **Nanobot** — core agent loop gọn nhẹ, dễ mở rộng
- **Paperclip** — layout dashboard, cơ cấu tổ chức agent-company

---

## Agents

| Agent | Vai trò |
|-------|---------|
| CEO | Nhận goal từ user, phân tích, routing task đến agent phù hợp, tổng hợp kết quả |
| Marketing | Xây dựng campaign, content, chiến lược marketing |
| Sales | Xử lý pipeline bán hàng, chốt đơn, báo cáo doanh thu |
| Customer Care | Chăm sóc khách hàng, xử lý khiếu nại, hỗ trợ sau bán hàng |

---

## Architecture

### Tổng quan

```
React UI (TypeScript)
    │ HTTP / WebSocket
API Gateway (FastAPI)
    │
RabbitMQ (message broker)
    ├── CEO Agent (Python)
    ├── Marketing Agent (Python)
    ├── Sales Agent (Python)
    └── Customer Care Agent (Python)
```

### Giao tiếp

- **Async message queue** — mỗi agent lắng nghe queue riêng, hoạt động song song độc lập
- **RabbitMQ Dead Letter Queue (DLQ)** — bắt message lỗi / agent timeout
- **WebSocket** — push real-time từ gateway đến UI

### Message Format

```json
{
  "message_id": "uuid",
  "from": "ceo",
  "to": "marketing",
  "thread_id": "uuid",
  "type": "task | report | error",
  "payload": {
    "content": "Nội dung task...",
    "context": {},
    "priority": "high | normal | low"
  },
  "created_at": "ISO8601"
}
```

---

## Per-Agent Configuration

Mỗi agent có file `config.yaml` riêng — không cần sửa code core để thay đổi model hay provider.

```yaml
agent_id: ceo
model: claude-opus-4-7
provider: anthropic
fallback_model: gpt-4o
fallback_provider: openai
system_prompt: "Bạn là CEO công ty bán hàng online..."
routes:
  - trigger: "marketing"
    queue: marketing
  - trigger: "sale"
    queue: sales
  - trigger: "khách hàng"
    queue: support
```

**Providers được hỗ trợ:** Anthropic, OpenAI-compatible, Codex, Claude Code  
**Mỗi agent cấu hình model độc lập** — CEO có thể dùng Opus, các agent con dùng Haiku/Sonnet.

---

## Cấu trúc Repo

```
opc_v2/
├── agents/
│   ├── base/
│   │   ├── agent.py          # Core loop: nhận message → gọi LLM → gửi response
│   │   ├── provider.py       # Adapter: OpenAI / Anthropic / Codex / Claude Code
│   │   └── queue.py          # RabbitMQ consumer/producer
│   ├── ceo/
│   │   ├── config.yaml
│   │   └── agent.py
│   ├── marketing/
│   │   ├── config.yaml
│   │   └── agent.py
│   ├── sales/
│   │   ├── config.yaml
│   │   └── agent.py
│   └── support/
│       ├── config.yaml
│       └── agent.py
├── gateway/                  # FastAPI — REST API + WebSocket hub
├── ui/                       # React + TypeScript dashboard
├── shared/                   # Message schemas, constants dùng chung
├── docker/
│   ├── agent.Dockerfile
│   └── gateway.Dockerfile
├── docker-compose.yml
├── .env.example
└── docs/
    └── superpowers/
        └── specs/
```

---

## Docker Compose

```yaml
services:
  rabbitmq:
    image: rabbitmq:3-management
    ports: ["15672:15672"]

  gateway:
    build: ./gateway
    ports: ["8000:8000"]
    depends_on: [rabbitmq]

  agent-ceo:
    build: ./agents
    command: python -m ceo
    env_file: .env

  agent-marketing:
    build: ./agents
    command: python -m marketing
    env_file: .env

  agent-sales:
    build: ./agents
    command: python -m sales
    env_file: .env

  agent-support:
    build: ./agents
    command: python -m support
    env_file: .env

  ui:
    build: ./ui
    ports: ["3000:3000"]
    depends_on: [gateway]
```

Thêm agent mới = thêm folder + thêm 5 dòng vào docker-compose.

---

## Frontend UI

**Tech stack:** React + TypeScript + Tailwind CSS + WebSocket

**Layout:**

```
┌─────────────────────────────────────────────────┐
│  SIDEBAR          │  MAIN AREA                  │
│                   │                             │
│  🏢 Company       │  ┌─── Agent Status ───────┐ │
│  ├ CEO       🟢   │  │ CEO        🟢 Active    │ │
│  ├ Marketing 🟢   │  │ Marketing  🟢 Running   │ │
│  ├ Sales     🟡   │  │ Sales      🟡 Waiting   │ │
│  └ Support   🟢   │  │ Support    🟢 Active    │ │
│                   │  └────────────────────────┘ │
│  📊 Goals         │                             │
│  📈 Reports       │  ┌─── Chat với CEO ────────┐ │
│  ⚙️ Settings      │  │ User: Tăng doanh thu... │ │
│                   │  │ CEO: Đã giao Marketing  │ │
│                   │  │ [Marketing] ✓ Done      │ │
│                   │  │ CEO: Tổng hợp kết quả.. │ │
│                   │  │ > _                     │ │
│                   │  └────────────────────────┘ │
└─────────────────────────────────────────────────┘
```

**Tính năng:**
- Agent Status panel — real-time trạng thái từng agent
- Chat với CEO — WebSocket, hiển thị luồng agent đang xử lý
- Goal tracker — list mục tiêu đã giao, tiến độ
- Settings — cấu hình model/provider từng agent qua UI

---

## Error Handling

| Tình huống | Xử lý |
|-----------|-------|
| Agent crash / timeout | Message vào DLQ → Gateway alert → UI hiển thị lỗi |
| LLM provider down | Tự động fallback sang `fallback_model` trong config |
| Message không route được | CEO trả về lỗi rõ ràng cho user |

---

## Testing Strategy

| Layer | Tool | Mục tiêu |
|-------|------|-----------|
| Unit | pytest | Core loop, routing logic, provider adapters |
| Integration | Docker Compose test profile | Agent ↔ RabbitMQ ↔ Gateway |
| E2E | Playwright | User chat → CEO → agents → kết quả UI |
| Load | Locust | Nhiều goal đồng thời, agents song song |

---

## Extensibility

Framework được thiết kế để tái cấu hình:
- **Thêm agent mới** — tạo folder + config.yaml, không sửa core
- **Đổi business domain** — thay system prompt trong config.yaml
- **Đổi provider/model** — sửa config.yaml, không sửa code
- **Scale agent** — chạy nhiều instance của cùng một agent type
