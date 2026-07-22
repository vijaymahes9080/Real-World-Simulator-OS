import { useState, useEffect } from "react";
import { Bot, ShieldCheck, Sparkles, Send } from "lucide-react";

interface AgentMessage {
  id: string;
  sender: string;
  role: "CFO" | "COO" | "Risk Manager" | "Medical Officer" | "Logistics Lead" | "System";
  content: string;
  timestamp: string;
  confidence: number;
  vote?: "APPROVE" | "REJECT" | "DEFER";
}

interface MultiAgentHubProps {
  activeTick?: number;
  simMessages?: any[];
}

export default function MultiAgentHub({ activeTick = 0, simMessages = [] }: MultiAgentHubProps) {
  const [messages, setMessages] = useState<AgentMessage[]>([
    {
      id: "m1",
      sender: "CFO Agent (Autonomous)",
      role: "CFO",
      content: "Reserves low under extreme scenario! Recommending 15% capex freeze to extend runway by +4.2 months.",
      timestamp: "07:08:12",
      confidence: 94,
      vote: "APPROVE"
    },
    {
      id: "m2",
      sender: "COO Agent (Autonomous)",
      role: "COO",
      content: "Freezing capex slows engineering velocity by 20%. Suggesting hybrid allocation of $25k to sales ops instead.",
      timestamp: "07:08:15",
      confidence: 88,
      vote: "APPROVE"
    },
    {
      id: "m3",
      sender: "Risk Manager Agent",
      role: "Risk Manager",
      content: "Monte Carlo 95% Var indicates 12.4% probability of stockout if sales velocity spikes unexpectedly.",
      timestamp: "07:08:19",
      confidence: 91,
      vote: "DEFER"
    }
  ]);

  const [customPrompt, setCustomPrompt] = useState("");

  // Sync incoming WebSocket messages
  useEffect(() => {
    if (simMessages && simMessages.length > 0) {
      const latest = simMessages[simMessages.length - 1];
      const newMsg: AgentMessage = {
        id: `sim_${Date.now()}`,
        sender: latest.sender || "System Agent",
        role: latest.role || "COO",
        content: latest.content || `Simulation Tick #${activeTick} parameter check nominal.`,
        timestamp: new Date().toLocaleTimeString(),
        confidence: Math.floor(85 + Math.random() * 12),
        vote: Math.random() > 0.3 ? "APPROVE" : "DEFER"
      };
      setMessages((prev) => [newMsg, ...prev.slice(0, 15)]);
    }
  }, [simMessages, activeTick]);

  const handleInjectPrompt = (e: React.FormEvent) => {
    e.preventDefault();
    if (!customPrompt.trim()) return;

    const userMsg: AgentMessage = {
      id: `user_${Date.now()}`,
      sender: "User Intervention Directive",
      role: "System",
      content: customPrompt,
      timestamp: new Date().toLocaleTimeString(),
      confidence: 100,
      vote: "APPROVE"
    };

    const responseMsg: AgentMessage = {
      id: `ai_resp_${Date.now()}`,
      sender: "Multi-Agent Consensus Engine",
      role: "CFO",
      content: `Evaluated directive: "${customPrompt}". Consensus confidence updated to 96.4%. Re-calculating policy vectors...`,
      timestamp: new Date().toLocaleTimeString(),
      confidence: 96,
      vote: "APPROVE"
    };

    setMessages([responseMsg, userMsg, ...messages]);
    setCustomPrompt("");
  };

  const getRoleBadge = (role: string) => {
    switch (role) {
      case "CFO":
        return "bg-emerald-500/20 text-emerald-400 border-emerald-500/30";
      case "COO":
        return "bg-blue-500/20 text-blue-400 border-blue-500/30";
      case "Risk Manager":
        return "bg-amber-500/20 text-amber-400 border-amber-500/30";
      default:
        return "bg-purple-500/20 text-purple-400 border-purple-500/30";
    }
  };

  return (
    <div className="glass-panel rounded-2xl p-5 border border-slate-800 shadow-2xl flex flex-col h-[480px]">
      {/* Header */}
      <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-800/80">
        <div className="flex items-center gap-2.5">
          <div className="p-2 bg-purple-500/10 border border-purple-500/30 rounded-xl text-purple-400">
            <Bot className="h-5 w-5" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              Autonomous Multi-Agent Crisis Hub
              <span className="text-[10px] bg-purple-500/20 text-purple-300 px-2 py-0.5 rounded-full border border-purple-500/30 font-mono font-bold">
                LLM AGENTS
              </span>
            </h3>
            <p className="text-[11px] text-gray-400">Agents negotiate and reach consensus on strategy counterfactuals</p>
          </div>
        </div>

        <div className="flex items-center gap-2 bg-slate-900 px-3 py-1.5 rounded-xl border border-slate-800 text-xs font-mono text-gray-300">
          <ShieldCheck className="h-4 w-4 text-emerald-400" />
          <span>Consensus Confidence: <strong className="text-emerald-400">92.8%</strong></span>
        </div>
      </div>

      {/* Message Feed */}
      <div className="flex-1 overflow-y-auto space-y-3 pr-1">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`p-3.5 rounded-xl border transition-all ${
              msg.role === "System"
                ? "bg-blue-950/40 border-blue-800/50"
                : "bg-slate-900/60 border-slate-800/80 hover:border-slate-700"
            }`}
          >
            <div className="flex items-center justify-between mb-1.5">
              <div className="flex items-center gap-2">
                <span className={`text-[10px] font-mono px-2 py-0.5 rounded-md border font-bold ${getRoleBadge(msg.role)}`}>
                  {msg.role}
                </span>
                <span className="text-xs font-bold text-gray-200">{msg.sender}</span>
              </div>
              <div className="flex items-center gap-2 text-[10px] font-mono text-gray-500">
                <span>{msg.timestamp}</span>
                {msg.vote && (
                  <span
                    className={`px-1.5 py-0.5 rounded font-bold ${
                      msg.vote === "APPROVE"
                        ? "bg-emerald-900/60 text-emerald-400"
                        : "bg-amber-900/60 text-amber-400"
                    }`}
                  >
                    {msg.vote}
                  </span>
                )}
              </div>
            </div>

            <p className="text-xs text-gray-300 leading-relaxed">{msg.content}</p>

            <div className="mt-2 flex items-center justify-between text-[10px] font-mono text-gray-400 pt-1.5 border-t border-slate-800/50">
              <span className="flex items-center gap-1">
                <Sparkles className="h-3 w-3 text-purple-400" /> Confidence Score: {msg.confidence}%
              </span>
              <span className="text-gray-500">LLM Reasoning Vector #409</span>
            </div>
          </div>
        ))}
      </div>

      {/* User Intervention Directive Input */}
      <form onSubmit={handleInjectPrompt} className="mt-3 flex items-center gap-2 pt-2 border-t border-slate-800">
        <input
          type="text"
          value={customPrompt}
          onChange={(e) => setCustomPrompt(e.target.value)}
          placeholder="Inject custom crisis directive (e.g. 'Force 20% price hike by Q3')..."
          className="flex-1 bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-purple-500 transition"
        />
        <button
          type="submit"
          className="px-3 py-2 bg-purple-600 hover:bg-purple-500 text-white rounded-xl text-xs font-bold flex items-center gap-1.5 transition shadow-lg shadow-purple-900/30"
        >
          <Send className="h-3.5 w-3.5" />
          Inject
        </button>
      </form>
    </div>
  );
}
