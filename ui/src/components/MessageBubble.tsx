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
