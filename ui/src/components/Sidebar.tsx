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
