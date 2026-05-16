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
