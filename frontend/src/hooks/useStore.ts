import { create } from "zustand";

export interface Project {
  id: string;
  name: string;
  description: string;
  domain: string;
  layout: {
    nodes: any[];
    edges: any[];
  };
  rules: any[];
  agents: any[];
  system_dynamics: any;
  global_variables: any;
}

export interface TelemetryPoint {
  tick: number;
  time: number;
  metric_name: string;
  metric_value: number;
  entity_id: string;
  entity_type: string;
}

interface User {
  username: string;
  role: string;
  token?: string;
}

interface SimStore {
  user: User | null;
  projects: Project[];
  activeProject: Project | null;
  activeRunId: string | null;
  telemetry: TelemetryPoint[];
  agentStates: any[];
  isSimulating: boolean;
  simTick: number;
  
  // Actions
  login: (username: string, role: string, token: string) => void;
  logout: () => void;
  setProjects: (projects: Project[]) => void;
  setActiveProject: (project: Project | null) => void;
  updateActiveProject: (updated: Partial<Project>) => Promise<void>;
  startWebSocketSim: () => void;
  pauseWebSocketSim: () => void;
  stepWebSocketSim: () => void;
  adjustGlobalVariable: (key: string, value: number) => void;
  fetchTelemetry: (runId: string) => Promise<void>;
}

let ws: WebSocket | null = null;

export const useStore = create<SimStore>((set, get) => ({
  user: localStorage.getItem("user") ? JSON.parse(localStorage.getItem("user")!) : null,
  projects: [],
  activeProject: null,
  activeRunId: null,
  telemetry: [],
  agentStates: [],
  isSimulating: false,
  simTick: 0,

  login: (username, role, token) => {
    const userObj = { username, role, token };
    localStorage.setItem("user", JSON.stringify(userObj));
    localStorage.setItem("token", token);
    set({ user: userObj });
  },

  logout: () => {
    localStorage.removeItem("user");
    localStorage.removeItem("token");
    set({ user: null, activeProject: null, telemetry: [] });
  },

  setProjects: (projects) => set({ projects }),

  setActiveProject: (project) => set({ activeProject: project, telemetry: [], simTick: 0 }),

  updateActiveProject: async (updated) => {
    const active = get().activeProject;
    if (!active) return;
    
    const token = localStorage.getItem("token");
    const merged = { ...active, ...updated };
    
    // Save to server
    try {
      const res = await fetch(`/api/projects/${active.id}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify(merged)
      });
      if (res.ok) {
        const saved = await res.json();
        set({ activeProject: saved });
      }
    } catch (e) {
      // Fallback local update
      set({ activeProject: merged });
    }
  },

  startWebSocketSim: () => {
    const active = get().activeProject;
    if (!active) return;
    
    // Establish WS connection if not open
    if (!ws || ws.readyState !== WebSocket.OPEN) {
      const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
      const host = window.location.host;
      // During dev it proxy through Vite, but we target the websocket route
      ws = new WebSocket(`${protocol}//${host}/api/ws/simulate`);
      
      ws.onopen = () => {
        ws?.send(JSON.stringify({
          action: "start",
          project_id: active.id,
          run_type: active.system_dynamics && Object.keys(active.system_dynamics).length > 0 ? "system_dynamics" : "agent"
        }));
        set({ isSimulating: true });
      };
      
      ws.onmessage = (event) => {
        const msg = JSON.parse(event.data);
        if (msg.event === "tick") {
          const metrics: TelemetryPoint[] = [];
          const t = msg.data.metrics || {};
          
          Object.keys(t).forEach(k => {
            metrics.push({
              tick: msg.tick,
              time: msg.tick,
              metric_name: k,
              metric_value: t[k],
              entity_id: "global",
              entity_type: "global"
            });
          });
          
          set(state => ({
            simTick: msg.tick,
            telemetry: [...state.telemetry, ...metrics]
          }));
        }
      };
      
      ws.onclose = () => {
        set({ isSimulating: false });
      };
    } else {
      ws.send(JSON.stringify({ action: "resume" }));
      set({ isSimulating: true });
    }
  },

  pauseWebSocketSim: () => {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ action: "pause" }));
    }
    set({ isSimulating: false });
  },

  stepWebSocketSim: () => {
    const active = get().activeProject;
    if (!active) return;
    
    if (!ws || ws.readyState !== WebSocket.OPEN) {
      get().startWebSocketSim();
      // Wait for socket to open in start
    } else {
      ws.send(JSON.stringify({ action: "step" }));
    }
  },

  adjustGlobalVariable: (key, value) => {
    const active = get().activeProject;
    if (!active) return;
    
    const updatedGlobals = { ...active.global_variables, [key]: value };
    get().updateActiveProject({ global_variables: updatedGlobals });
    
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({
        action: "adjust",
        variables: { [key]: value }
      }));
    }
  },

  fetchTelemetry: async (runId) => {
    const token = localStorage.getItem("token");
    try {
      const res = await fetch(`/api/runs/${runId}/telemetry`, {
        headers: {
          "Authorization": `Bearer ${token}`
        }
      });
      if (res.ok) {
        const data = await res.json();
        set({
          telemetry: data.telemetry || [],
          agentStates: data.agent_states || []
        });
      }
    } catch (e) {
      console.error(e);
    }
  }
}));
