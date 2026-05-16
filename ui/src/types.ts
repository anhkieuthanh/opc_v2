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
