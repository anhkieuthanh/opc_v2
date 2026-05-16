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
