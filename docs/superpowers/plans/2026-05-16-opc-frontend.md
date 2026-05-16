# OPC Frontend UI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Xây dựng React dashboard với sidebar agent status, panel trạng thái real-time, và chat với CEO qua WebSocket.

**Architecture:** Vite + React + TypeScript app trong thư mục `ui/`. Frontend kết nối tới backend FastAPI gateway qua REST (GET /agents/status) và WebSocket (/ws). Hai custom hooks quản lý state: `useAgentStatus` poll trạng thái agent mỗi 5 giây, `useChat` quản lý WebSocket connection và message history.

**Tech Stack:** Vite 5, React 18, TypeScript 5, Tailwind CSS 3, native WebSocket API, fetch API. Build bằng nginx Docker image.

---

## File Map

```
ui/
├── package.json
├── tsconfig.json
├── vite.config.ts
├── index.html
├── nginx.conf
├── Dockerfile
├── .env.example
├── src/
│   ├── main.tsx                        # React entry point
│   ├── App.tsx                         # Root layout: Sidebar + main area
│   ├── index.css                       # Tailwind directives
│   ├── types.ts                        # OPCMessage, Agent, Payload types
│   ├── hooks/
│   │   ├── useAgentStatus.ts           # Poll GET /agents/status every 5s
│   │   └── useChat.ts                  # WebSocket conn + message state + send()
│   └── components/
│       ├── Sidebar.tsx                 # Left nav: agent list with status dots
│       ├── AgentStatusPanel.tsx        # Top panel: agent status grid
│       ├── ChatPanel.tsx               # Chat area with input form
│       └── MessageBubble.tsx           # Individual chat message bubble
```

Also modifies:
- `docker-compose.yml` — add `ui` service

---

## Task 1: Vite + React + TypeScript + Tailwind scaffolding

**Files:**
- Create: `ui/package.json`
- Create: `ui/tsconfig.json`
- Create: `ui/vite.config.ts`
- Create: `ui/index.html`
- Create: `ui/src/main.tsx`
- Create: `ui/src/index.css`
- Create: `ui/.env.example`

- [ ] **Step 1: Tạo ui/package.json**

```json
{
  "name": "opc-ui",
  "version": "0.1.0",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1"
  },
  "devDependencies": {
    "@types/react": "^18.3.3",
    "@types/react-dom": "^18.3.0",
    "@vitejs/plugin-react": "^4.3.1",
    "autoprefixer": "^10.4.19",
    "postcss": "^8.4.39",
    "tailwindcss": "^3.4.6",
    "typescript": "^5.5.3",
    "vite": "^5.3.4"
  }
}
```

- [ ] **Step 2: Tạo ui/tsconfig.json**

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true
  },
  "include": ["src"]
}
```

- [ ] **Step 3: Tạo ui/vite.config.ts**

```typescript
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
  },
});
```

- [ ] **Step 4: Tạo ui/index.html**

```html
<!doctype html>
<html lang="vi">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>OPC — AI Company Dashboard</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

- [ ] **Step 5: Tạo ui/src/main.tsx**

```tsx
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import App from "./App";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>
);
```

- [ ] **Step 6: Tạo ui/src/index.css**

```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

- [ ] **Step 7: Tạo ui/.env.example**

```bash
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000/ws
```

- [ ] **Step 8: Tạo ui/tailwind.config.js và ui/postcss.config.js**

```bash
cd ui
```

Create `ui/tailwind.config.js`:
```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {},
  },
  plugins: [],
};
```

Create `ui/postcss.config.js`:
```javascript
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
};
```

- [ ] **Step 9: Cài dependencies**

```bash
cd "/Users/atif/Public/Code GenAI/01. Project 2/opc_v2/ui" && npm install
```

Expected: node_modules created, no errors.

- [ ] **Step 10: Tạo placeholder App.tsx để TypeScript check pass**

```tsx
// ui/src/App.tsx
export default function App() {
  return <div className="p-4 text-2xl font-bold">OPC Dashboard</div>;
}
```

- [ ] **Step 11: Verify build**

```bash
cd "/Users/atif/Public/Code GenAI/01. Project 2/opc_v2/ui" && npm run build 2>&1 | tail -10
```

Expected: `dist/` created, no TypeScript errors.

- [ ] **Step 12: Commit**

```bash
cd "/Users/atif/Public/Code GenAI/01. Project 2/opc_v2" && git add ui/ && git commit -m "chore: Vite + React + TypeScript + Tailwind scaffolding for UI"
```

---

## Task 2: TypeScript types

**Files:**
- Create: `ui/src/types.ts`

- [ ] **Step 1: Tạo ui/src/types.ts**

```typescript
export interface Payload {
  content: string;
  context: Record<string, unknown>;
  priority: "high" | "normal" | "low";
}

export interface OPCMessage {
  message_id: string;
  from: string;
  to: string;
  thread_id: string;
  type: "task" | "report" | "error";
  payload: Payload;
  created_at: string;
}

export interface Agent {
  id: string;
  status: "active" | "idle" | "error";
}

export interface AgentsStatusResponse {
  agents: Agent[];
}
```

- [ ] **Step 2: Verify TypeScript nhận types**

```bash
cd "/Users/atif/Public/Code GenAI/01. Project 2/opc_v2/ui" && npm run build 2>&1 | tail -5
```

Expected: Build succeeds.

- [ ] **Step 3: Commit**

```bash
cd "/Users/atif/Public/Code GenAI/01. Project 2/opc_v2" && git add ui/src/types.ts && git commit -m "feat: TypeScript types for OPCMessage and Agent"
```

---

## Task 3: useAgentStatus hook

**Files:**
- Create: `ui/src/hooks/useAgentStatus.ts`

- [ ] **Step 1: Tạo ui/src/hooks/useAgentStatus.ts**

```typescript
import { useEffect, useState } from "react";
import type { Agent, AgentsStatusResponse } from "../types";

const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";
const POLL_INTERVAL_MS = 5000;

export function useAgentStatus() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [error, setError] = useState(false);

  useEffect(() => {
    let cancelled = false;

    const fetchStatus = () => {
      fetch(`${API_URL}/agents/status`)
        .then((r) => {
          if (!r.ok) throw new Error(`HTTP ${r.status}`);
          return r.json() as Promise<AgentsStatusResponse>;
        })
        .then((data) => {
          if (!cancelled) {
            setAgents(data.agents);
            setError(false);
          }
        })
        .catch(() => {
          if (!cancelled) setError(true);
        });
    };

    fetchStatus();
    const id = setInterval(fetchStatus, POLL_INTERVAL_MS);
    return () => {
      cancelled = true;
      clearInterval(id);
    };
  }, []);

  return { agents, error };
}
```

- [ ] **Step 2: Verify build**

```bash
cd "/Users/atif/Public/Code GenAI/01. Project 2/opc_v2/ui" && npm run build 2>&1 | tail -5
```

Expected: Build succeeds.

- [ ] **Step 3: Commit**

```bash
cd "/Users/atif/Public/Code GenAI/01. Project 2/opc_v2" && git add ui/src/hooks/useAgentStatus.ts && git commit -m "feat: useAgentStatus hook polls /agents/status every 5s"
```

---

## Task 4: useChat hook

**Files:**
- Create: `ui/src/hooks/useChat.ts`

- [ ] **Step 1: Tạo ui/src/hooks/useChat.ts**

```typescript
import { useCallback, useEffect, useRef, useState } from "react";
import type { OPCMessage } from "../types";

const WS_URL = import.meta.env.VITE_WS_URL ?? "ws://localhost:8000/ws";

export interface ChatMessage {
  id: string;
  from: string;
  content: string;
  type: "user" | "agent";
  timestamp: string;
}

function opcToChat(msg: OPCMessage): ChatMessage {
  return {
    id: msg.message_id,
    from: msg.from,
    content: msg.payload.content,
    type: "agent",
    timestamp: msg.created_at,
  };
}

export function useChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [connected, setConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    const ws = new WebSocket(WS_URL);
    wsRef.current = ws;

    ws.onopen = () => setConnected(true);
    ws.onclose = () => setConnected(false);
    ws.onerror = () => setConnected(false);

    ws.onmessage = (event: MessageEvent<string>) => {
      const msg = JSON.parse(event.data) as OPCMessage;
      setMessages((prev) => [...prev, opcToChat(msg)]);
    };

    return () => {
      ws.close();
    };
  }, []);

  const send = useCallback((content: string) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      const userMsg: ChatMessage = {
        id: crypto.randomUUID(),
        from: "user",
        content,
        type: "user",
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, userMsg]);
      wsRef.current.send(JSON.stringify({ content }));
    }
  }, []);

  return { messages, connected, send };
}
```

- [ ] **Step 2: Verify build**

```bash
cd "/Users/atif/Public/Code GenAI/01. Project 2/opc_v2/ui" && npm run build 2>&1 | tail -5
```

Expected: Build succeeds.

- [ ] **Step 3: Commit**

```bash
cd "/Users/atif/Public/Code GenAI/01. Project 2/opc_v2" && git add ui/src/hooks/useChat.ts && git commit -m "feat: useChat hook manages WebSocket connection and message state"
```

---

## Task 5: Sidebar component

**Files:**
- Create: `ui/src/components/Sidebar.tsx`

- [ ] **Step 1: Tạo ui/src/components/Sidebar.tsx**

```tsx
import type { Agent } from "../types";

const STATUS_DOT: Record<string, string> = {
  active: "bg-green-500",
  idle: "bg-yellow-400",
  error: "bg-red-500",
};

const AGENT_LABEL: Record<string, string> = {
  ceo: "CEO",
  marketing: "Marketing",
  sales: "Sales",
  support: "Support",
};

interface Props {
  agents: Agent[];
}

export function Sidebar({ agents }: Props) {
  return (
    <aside className="w-56 bg-gray-900 text-white flex flex-col p-4 gap-6 shrink-0">
      <div>
        <p className="text-xs font-semibold uppercase tracking-wider text-gray-400 mb-3">
          Company
        </p>
        <ul className="space-y-2">
          {agents.map((agent) => (
            <li key={agent.id} className="flex items-center gap-2 text-sm">
              <span
                className={`w-2 h-2 rounded-full shrink-0 ${STATUS_DOT[agent.status] ?? "bg-gray-500"}`}
              />
              {AGENT_LABEL[agent.id] ?? agent.id}
            </li>
          ))}
        </ul>
      </div>
      <div className="mt-auto">
        <p className="text-xs text-gray-500">OPC v0.1.0</p>
      </div>
    </aside>
  );
}
```

- [ ] **Step 2: Cập nhật App.tsx để import Sidebar**

```tsx
// ui/src/App.tsx
import { Sidebar } from "./components/Sidebar";
import { useAgentStatus } from "./hooks/useAgentStatus";

export default function App() {
  const { agents } = useAgentStatus();

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar agents={agents} />
      <main className="flex-1 p-6">
        <p className="text-gray-500">Dashboard coming soon...</p>
      </main>
    </div>
  );
}
```

- [ ] **Step 3: Verify build**

```bash
cd "/Users/atif/Public/Code GenAI/01. Project 2/opc_v2/ui" && npm run build 2>&1 | tail -5
```

Expected: Build succeeds, no TypeScript errors.

- [ ] **Step 4: Commit**

```bash
cd "/Users/atif/Public/Code GenAI/01. Project 2/opc_v2" && git add ui/src/components/Sidebar.tsx ui/src/App.tsx && git commit -m "feat: Sidebar component with agent status dots"
```

---

## Task 6: AgentStatusPanel component

**Files:**
- Create: `ui/src/components/AgentStatusPanel.tsx`

- [ ] **Step 1: Tạo ui/src/components/AgentStatusPanel.tsx**

```tsx
import type { Agent } from "../types";

const STATUS_COLOR: Record<string, string> = {
  active: "text-green-600",
  idle: "text-yellow-500",
  error: "text-red-500",
};

const STATUS_LABEL: Record<string, string> = {
  active: "Active",
  idle: "Waiting",
  error: "Error",
};

const AGENT_LABEL: Record<string, string> = {
  ceo: "CEO",
  marketing: "Marketing",
  sales: "Sales",
  support: "Support",
};

interface Props {
  agents: Agent[];
}

export function AgentStatusPanel({ agents }: Props) {
  if (agents.length === 0) {
    return (
      <div className="bg-white rounded-lg border p-4">
        <p className="text-sm text-gray-400">Đang kết nối tới gateway...</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg border p-4">
      <h3 className="text-xs font-semibold uppercase tracking-wider text-gray-400 mb-3">
        Agent Status
      </h3>
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {agents.map((agent) => (
          <div
            key={agent.id}
            className="flex flex-col gap-1 px-3 py-2 rounded-lg bg-gray-50"
          >
            <span className="text-sm font-medium text-gray-700">
              {AGENT_LABEL[agent.id] ?? agent.id}
            </span>
            <span
              className={`text-xs font-semibold ${STATUS_COLOR[agent.status] ?? "text-gray-400"}`}
            >
              {STATUS_LABEL[agent.status] ?? agent.status}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Verify build**

```bash
cd "/Users/atif/Public/Code GenAI/01. Project 2/opc_v2/ui" && npm run build 2>&1 | tail -5
```

Expected: Build succeeds.

- [ ] **Step 3: Commit**

```bash
cd "/Users/atif/Public/Code GenAI/01. Project 2/opc_v2" && git add ui/src/components/AgentStatusPanel.tsx && git commit -m "feat: AgentStatusPanel with 4-column agent grid"
```

---

## Task 7: MessageBubble + ChatPanel components

**Files:**
- Create: `ui/src/components/MessageBubble.tsx`
- Create: `ui/src/components/ChatPanel.tsx`

- [ ] **Step 1: Tạo ui/src/components/MessageBubble.tsx**

```tsx
import type { ChatMessage } from "../hooks/useChat";

const AGENT_LABEL: Record<string, string> = {
  ceo: "CEO",
  marketing: "Marketing",
  sales: "Sales",
  support: "Support",
};

interface Props {
  message: ChatMessage;
}

export function MessageBubble({ message }: Props) {
  const isUser = message.type === "user";
  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-xs lg:max-w-md px-4 py-2 rounded-2xl text-sm ${
          isUser ? "bg-blue-600 text-white" : "bg-gray-100 text-gray-800"
        }`}
      >
        {!isUser && (
          <p className="text-xs font-semibold text-gray-500 mb-1">
            {AGENT_LABEL[message.from] ?? message.from}
          </p>
        )}
        <p className="whitespace-pre-wrap">{message.content}</p>
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Tạo ui/src/components/ChatPanel.tsx**

```tsx
import { useEffect, useRef, useState } from "react";
import type { ChatMessage } from "../hooks/useChat";
import { MessageBubble } from "./MessageBubble";

interface Props {
  messages: ChatMessage[];
  connected: boolean;
  onSend: (content: string) => void;
}

export function ChatPanel({ messages, connected, onSend }: Props) {
  const [input, setInput] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = input.trim();
    if (trimmed && connected) {
      onSend(trimmed);
      setInput("");
    }
  };

  return (
    <div className="bg-white rounded-lg border flex flex-col h-full">
      <div className="px-4 py-3 border-b flex items-center justify-between">
        <h3 className="text-sm font-semibold text-gray-700">Chat với CEO</h3>
        <div className="flex items-center gap-2">
          <span
            className={`w-2 h-2 rounded-full ${connected ? "bg-green-500" : "bg-red-400"}`}
          />
          <span className="text-xs text-gray-400">
            {connected ? "Đã kết nối" : "Đang kết nối..."}
          </span>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {messages.length === 0 && (
          <p className="text-center text-sm text-gray-400 mt-8">
            Gửi tin nhắn để bắt đầu làm việc với CEO
          </p>
        )}
        {messages.map((msg) => (
          <MessageBubble key={msg.id} message={msg} />
        ))}
        <div ref={bottomRef} />
      </div>

      <form onSubmit={handleSubmit} className="p-3 border-t flex gap-2">
        <input
          className="flex-1 border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-50"
          placeholder={connected ? "Nhập tin nhắn cho CEO..." : "Đang kết nối tới gateway..."}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={!connected}
        />
        <button
          type="submit"
          disabled={!input.trim() || !connected}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium disabled:opacity-40 hover:bg-blue-700 transition-colors"
        >
          Gửi
        </button>
      </form>
    </div>
  );
}
```

- [ ] **Step 3: Verify build**

```bash
cd "/Users/atif/Public/Code GenAI/01. Project 2/opc_v2/ui" && npm run build 2>&1 | tail -5
```

Expected: Build succeeds.

- [ ] **Step 4: Commit**

```bash
cd "/Users/atif/Public/Code GenAI/01. Project 2/opc_v2" && git add ui/src/components/MessageBubble.tsx ui/src/components/ChatPanel.tsx && git commit -m "feat: MessageBubble and ChatPanel components"
```

---

## Task 8: App.tsx wiring + .env

**Files:**
- Modify: `ui/src/App.tsx`
- Create: `ui/.env`

- [ ] **Step 1: Cập nhật ui/src/App.tsx với full layout**

```tsx
import { AgentStatusPanel } from "./components/AgentStatusPanel";
import { ChatPanel } from "./components/ChatPanel";
import { Sidebar } from "./components/Sidebar";
import { useAgentStatus } from "./hooks/useAgentStatus";
import { useChat } from "./hooks/useChat";

export default function App() {
  const { agents } = useAgentStatus();
  const { messages, connected, send } = useChat();

  return (
    <div className="flex h-screen bg-gray-50 overflow-hidden">
      <Sidebar agents={agents} />
      <main className="flex-1 flex flex-col p-6 gap-4 min-h-0">
        <AgentStatusPanel agents={agents} />
        <div className="flex-1 min-h-0">
          <ChatPanel messages={messages} connected={connected} onSend={send} />
        </div>
      </main>
    </div>
  );
}
```

- [ ] **Step 2: Tạo ui/.env từ .env.example**

```bash
cp "/Users/atif/Public/Code GenAI/01. Project 2/opc_v2/ui/.env.example" "/Users/atif/Public/Code GenAI/01. Project 2/opc_v2/ui/.env"
```

- [ ] **Step 3: Thêm ui/.env vào .gitignore gốc**

Mở `ui/.gitignore` (tạo mới nếu chưa có):

```
.env
node_modules/
dist/
```

- [ ] **Step 4: Verify build lần cuối**

```bash
cd "/Users/atif/Public/Code GenAI/01. Project 2/opc_v2/ui" && npm run build 2>&1 | tail -10
```

Expected: `dist/` built thành công, không có TypeScript errors.

- [ ] **Step 5: Commit**

```bash
cd "/Users/atif/Public/Code GenAI/01. Project 2/opc_v2" && git add ui/src/App.tsx ui/.env.example ui/.gitignore && git commit -m "feat: wire up App layout with all hooks and components"
```

---

## Task 9: UI Dockerfile + docker-compose update

**Files:**
- Create: `ui/Dockerfile`
- Create: `ui/nginx.conf`
- Modify: `docker-compose.yml`

- [ ] **Step 1: Tạo ui/nginx.conf**

```nginx
server {
    listen 80;
    server_name _;

    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri /index.html;
    }
}
```

- [ ] **Step 2: Tạo ui/Dockerfile**

```dockerfile
FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
```

- [ ] **Step 3: Thêm ui service vào docker-compose.yml**

Mở `docker-compose.yml` và thêm service `ui` sau service `agent-support`:

```yaml
  ui:
    build:
      context: ./ui
      dockerfile: Dockerfile
    ports:
      - "3000:80"
    depends_on:
      - gateway
```

File `docker-compose.yml` sau khi sửa phần cuối trông như thế này (chỉ thêm đoạn trên vào cuối services):

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

  ui:
    build:
      context: ./ui
      dockerfile: Dockerfile
    ports:
      - "3000:80"
    depends_on:
      - gateway
```

- [ ] **Step 4: Validate docker-compose**

```bash
cd "/Users/atif/Public/Code GenAI/01. Project 2/opc_v2" && docker compose config --quiet 2>&1 | head -5
```

Expected: No errors.

- [ ] **Step 5: Commit và push**

```bash
cd "/Users/atif/Public/Code GenAI/01. Project 2/opc_v2" && git add ui/Dockerfile ui/nginx.conf docker-compose.yml && git commit -m "chore: UI Dockerfile with nginx, add ui service to docker-compose" && git push origin main
```

---

## Self-Review Checklist

- [x] **Spec coverage:**
  - React + TypeScript + Tailwind → Task 1
  - TypeScript types (OPCMessage, Agent) → Task 2
  - useAgentStatus (poll /agents/status every 5s) → Task 3
  - useChat (WebSocket + message state + send) → Task 4
  - Sidebar với agent list và status dots → Task 5
  - AgentStatusPanel với grid trạng thái → Task 6
  - Chat với CEO (ChatPanel + MessageBubble) → Task 7
  - App layout wiring → Task 8
  - Docker + docker-compose → Task 9

- [x] **Placeholder scan:** Không có TBD/TODO

- [x] **Type consistency:**
  - `ChatMessage` defined in `useChat.ts`, imported correctly in `MessageBubble.tsx` và `ChatPanel.tsx`
  - `Agent` defined in `types.ts`, used in `useAgentStatus.ts`, `Sidebar.tsx`, `AgentStatusPanel.tsx`
  - `OPCMessage` defined in `types.ts`, used in `useChat.ts`
  - `AgentsStatusResponse` used in `useAgentStatus.ts` fetch
