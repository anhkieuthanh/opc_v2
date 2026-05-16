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
