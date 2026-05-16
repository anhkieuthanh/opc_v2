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
