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
