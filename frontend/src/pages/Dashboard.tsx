import { useEffect, useState, useRef } from "react";
import { useStore, Project } from "../hooks/useStore";
import { Line } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";
import { Play, Pause, SkipForward, RotateCcw, AlertTriangle, Send, Sparkles, Sliders } from "lucide-react";

// Register ChartJS modules
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

export default function Dashboard() {
  const projects = useStore(state => state.projects);
  const setProjects = useStore(state => state.setProjects);
  const activeProject = useStore(state => state.activeProject);
  const setActiveProject = useStore(state => state.setActiveProject);
  const telemetry = useStore(state => state.telemetry);
  const isSimulating = useStore(state => state.isSimulating);
  const startWebSocketSim = useStore(state => state.startWebSocketSim);
  const pauseWebSocketSim = useStore(state => state.pauseWebSocketSim);
  const stepWebSocketSim = useStore(state => state.stepWebSocketSim);
  const adjustGlobalVariable = useStore(state => state.adjustGlobalVariable);

  // Local UI states
  const [prompt, setPrompt] = useState("");
  const [chatLog, setChatLog] = useState<{ sender: "user" | "ai"; message: string }[]>([]);
  const [chatLoading, setChatLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  // Fetch projects on load
  useEffect(() => {
    const fetchProjects = async () => {
      const token = localStorage.getItem("token");
      try {
        const res = await fetch("/api/projects", {
          headers: { "Authorization": `Bearer ${token}` }
        });
        if (res.ok) {
          const list = await res.json();
          setProjects(list);
          if (list.length > 0 && !activeProject) {
            setActiveProject(list[0]);
          }
        }
      } catch (e) {
        console.error(e);
      }
    };
    fetchProjects();
  }, [setProjects, activeProject, setActiveProject]);

  // Scroll chat window on update
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [chatLog]);

  const handleReset = async () => {
    if (!activeProject) return;
    const token = localStorage.getItem("token");
    try {
      const res = await fetch(`/api/projects/${activeProject.id}/reset`, {
        method: "POST",
        headers: { "Authorization": `Bearer ${token}` }
      });
      if (res.ok) {
        const updated = await res.json();
        setActiveProject(updated);
        // Refresh list
        const listRes = await fetch("/api/projects", {
          headers: { "Authorization": `Bearer ${token}` }
        });
        if (listRes.ok) setProjects(await listRes.json());
      }
    } catch (e) {
      console.error(e);
    }
  };

  const handleSendPrompt = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim() || !activeProject) return;
    
    const userMsg = prompt;
    setChatLog(prev => [...prev, { sender: "user", message: userMsg }]);
    setPrompt("");
    setChatLoading(true);
    
    const token = localStorage.getItem("token");
    try {
      const res = await fetch(`/api/projects/${activeProject.id}/assistant`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({ prompt: userMsg })
      });
      if (res.ok) {
        const data = await res.json();
        setChatLog(prev => [...prev, { sender: "ai", message: data.natural_explanation }]);
        
        // Refresh project variables in state if changed
        if (data.parameter_adjustments) {
          const freshProj = { ...activeProject };
          freshProj.global_variables = {
            ...freshProj.global_variables,
            ...data.parameter_adjustments
          };
          setActiveProject(freshProj);
        }
      }
    } catch (e) {
      setChatLog(prev => [...prev, { sender: "ai", message: "Failed to communicate with the local model processor." }]);
    } finally {
      setChatLoading(false);
    }
  };

  // Group telemetry metrics for ChartJS
  const getChartData = () => {
    const ticks = Array.from(new Set(telemetry.map(t => t.tick))).sort((a, b) => a - b);
    const metricNames = Array.from(new Set(telemetry.map(t => t.metric_name)));
    
    const colors = [
      "rgba(59, 130, 246, 1)",   // blue
      "rgba(16, 185, 129, 1)",  // emerald
      "rgba(139, 92, 246, 1)",  // violet
      "rgba(245, 158, 11, 1)",  // amber
      "rgba(244, 63, 94, 1)"    // rose
    ];
    
    const datasets = metricNames.map((name, i) => {
      const dataPoints = ticks.map(tick => {
        const pt = telemetry.find(t => t.tick === tick && t.metric_name === name);
        return pt ? pt.metric_value : null;
      });
      
      return {
        label: name,
        data: dataPoints,
        borderColor: colors[i % colors.length],
        backgroundColor: colors[i % colors.length].replace("1)", "0.1)"),
        tension: 0.25,
        fill: false
      };
    });
    
    return {
      labels: ticks.map(t => `Tick ${t}`),
      datasets
    };
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: "top" as const,
        labels: { color: "rgba(255, 255, 255, 0.7)", font: { family: "Inter", size: 11 } }
      },
      tooltip: {
        mode: "index" as const,
        intersect: false
      }
    },
    scales: {
      x: { grid: { color: "rgba(255, 255, 255, 0.05)" }, ticks: { color: "rgba(255, 255, 255, 0.5)", font: { size: 10 } } },
      y: { grid: { color: "rgba(255, 255, 255, 0.05)" }, ticks: { color: "rgba(255, 255, 255, 0.5)", font: { size: 10 } } }
    }
  };

  const latestAlerts = () => {
    // Collect active warning threshold items
    const alerts: string[] = [];
    if (activeProject?.domain === "startup") {
      const cashPt = telemetry.filter(t => t.metric_name === "Cash Reserves").slice(-1)[0];
      if (cashPt && cashPt.metric_value < 100000) {
        alerts.push("CRITICAL RUNWAY: Reserves depleted under $100,000 threshold!");
      }
    }
    if (activeProject?.domain === "agriculture") {
      const moistPt = telemetry.filter(t => t.metric_name === "Soil Moisture (%)").slice(-1)[0];
      if (moistPt && moistPt.metric_value < 15.0) {
        alerts.push("CLIMATE RISK: Soil moisture is under 15%. Yield forecast dropping.");
      }
    }
    return alerts;
  };

  return (
    <div className="grid grid-cols-1 xl:grid-cols-4 gap-6 w-full min-h-[85vh]">
      {/* Sidebar - Workspace Selector & Controls */}
      <div className="xl:col-span-1 space-y-6 flex flex-col">
        {/* Workspace Card */}
        <div className="glass-panel rounded-xl p-5">
          <label className="block text-[10px] font-bold uppercase tracking-wider text-gray-500 mb-2">Sim Domain Workspace</label>
          <select
            value={activeProject?.id || ""}
            onChange={e => {
              const selected = projects.find(p => p.id === e.target.value);
              if (selected) setActiveProject(selected);
            }}
            className="w-full bg-slate-900 border border-slate-800 rounded-lg p-2.5 text-white focus:outline-none focus:ring-1 focus:ring-blue-500 text-xs"
          >
            {projects.map(p => (
              <option key={p.id} value={p.id}>{p.name}</option>
            ))}
          </select>
          
          <div className="mt-4 text-xs text-gray-400 leading-relaxed border-t border-slate-800/60 pt-3">
            {activeProject?.description}
          </div>
        </div>

        {/* Live Controller Card */}
        <div className="glass-panel rounded-xl p-5">
          <label className="block text-[10px] font-bold uppercase tracking-wider text-gray-500 mb-4">Playback Engine</label>
          <div className="flex gap-2 justify-center mb-4">
            {isSimulating ? (
              <button
                onClick={pauseWebSocketSim}
                className="p-3 bg-amber-500/10 hover:bg-amber-500/20 text-amber-400 border border-amber-500/20 rounded-lg transition"
                title="Pause Simulation"
              >
                <Pause className="h-4.5 w-4.5" />
              </button>
            ) : (
              <button
                onClick={startWebSocketSim}
                className="p-3 bg-blue-600 hover:bg-blue-500 text-white rounded-lg transition shadow-md shadow-blue-500/20"
                title="Start Simulation"
              >
                <Play className="h-4.5 w-4.5 fill-current" />
              </button>
            )}

            <button
              onClick={stepWebSocketSim}
              className="p-3 bg-slate-900 hover:bg-slate-800 border border-slate-800 text-gray-300 rounded-lg transition"
              title="Single step"
            >
              <SkipForward className="h-4.5 w-4.5" />
            </button>

            <button
              onClick={handleReset}
              className="p-3 bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 border border-rose-500/20 rounded-lg transition"
              title="Reset System"
            >
              <RotateCcw className="h-4.5 w-4.5" />
            </button>
          </div>

          <div className="flex justify-between items-center text-xs text-gray-400">
            <span>Status: <strong className={isSimulating ? "text-emerald-400 animate-pulse" : "text-gray-500"}>{isSimulating ? "Running" : "Paused"}</strong></span>
            <span>Tick: <strong className="text-white font-mono">{telemetry.length > 0 ? telemetry[telemetry.length - 1].tick : 0}</strong></span>
          </div>
        </div>

        {/* Global Parameter tuning slider */}
        {activeProject && activeProject.global_variables && (
          <div className="glass-panel rounded-xl p-5 flex-1">
            <div className="flex gap-2 items-center text-[10px] font-bold uppercase tracking-wider text-gray-500 mb-4">
              <Sliders className="h-3.5 w-3.5" />
              Tune System Constraints
            </div>
            
            <div className="space-y-4">
              {Object.keys(activeProject.global_variables).map(key => {
                const val = activeProject.global_variables[key];
                if (typeof val !== "number") return null;
                
                return (
                  <div key={key} className="space-y-1.5">
                    <div className="flex justify-between text-xs font-mono">
                      <span className="text-gray-400 truncate max-w-[120px]">{key}</span>
                      <span className="text-white font-bold">{val.toFixed(2)}</span>
                    </div>
                    <input
                      type="range"
                      min={0.1}
                      max={val * 2.5 || 10.0}
                      step={0.05}
                      value={val}
                      onChange={e => adjustGlobalVariable(key, parseFloat(e.target.value))}
                      className="w-full accent-blue-500 h-1 bg-slate-800 rounded-lg appearance-none cursor-pointer"
                    />
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>

      {/* Main Graph & Live Alerts Area */}
      <div className="xl:col-span-3 space-y-6">
        {/* Dynamic Telemetry Graph */}
        <div className="glass-panel rounded-xl p-5 h-[340px] flex flex-col">
          <h2 className="text-sm font-semibold text-white mb-4">Real-Time Simulation Telemetry (DuckDB Data Stream)</h2>
          <div className="flex-1 relative">
            {telemetry.length > 0 ? (
              <Line data={getChartData()} options={chartOptions} />
            ) : (
              <div className="absolute inset-0 flex flex-col items-center justify-center text-center text-xs text-gray-500">
                <Sliders className="h-8 w-8 text-slate-700 mb-2 animate-bounce" />
                No simulation telemetry active. Click Play button on the left to begin streaming results.
              </div>
            )}
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Smart Alerts Box */}
          <div className="glass-panel rounded-xl p-5 flex flex-col h-[280px]">
            <h2 className="text-sm font-semibold text-white mb-3">Live Simulation Safety Alerts</h2>
            <div className="flex-1 overflow-y-auto space-y-2.5">
              {latestAlerts().map((alert, i) => (
                <div key={i} className="flex gap-3 p-3 rounded-lg bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs">
                  <AlertTriangle className="h-4.5 w-4.5 shrink-0" />
                  <span>{alert}</span>
                </div>
              ))}
              
              {latestAlerts().length === 0 && (
                <div className="flex flex-col items-center justify-center h-full text-xs text-gray-500 text-center">
                  All systems operating within safety parameters. No alerts active.
                </div>
              )}
            </div>
          </div>

          {/* AI Assistant Chat Panel */}
          <div className="glass-panel rounded-xl p-5 flex flex-col h-[280px]">
            <div className="flex gap-2 items-center text-sm font-semibold text-white mb-3">
              <Sparkles className="h-4 w-4 text-amber-400" />
              AI Simulation Co-Pilot
            </div>
            
            <div className="flex-1 overflow-y-auto space-y-3 mb-3 p-1">
              <div className="text-xs p-2.5 rounded-lg bg-slate-900 border border-slate-800 text-gray-400">
                Hi! I am your simulation assistant. Ask me questions such as:
                <div className="font-mono text-blue-400 mt-1 cursor-pointer" onClick={() => setPrompt("What happens if funding drops by 30%?")}>
                  - &quot;What if funding drops by 30%?&quot;
                </div>
                <div className="font-mono text-blue-400 mt-0.5 cursor-pointer" onClick={() => setPrompt("What if rainfall doubles?")}>
                  - &quot;What if rainfall doubles?&quot;
                </div>
              </div>

              {chatLog.map((chat, idx) => (
                <div
                  key={idx}
                  className={`flex flex-col max-w-[85%] rounded-lg p-2.5 text-xs ${
                    chat.sender === "user"
                      ? "bg-blue-600/15 border border-blue-500/20 text-white ml-auto"
                      : "bg-slate-900 border border-slate-800 text-gray-300"
                  }`}
                >
                  <span className="font-bold text-[9px] uppercase tracking-wider text-gray-500 mb-0.5">
                    {chat.sender === "user" ? "You" : "AI Assistant"}
                  </span>
                  {chat.message}
                </div>
              ))}
              {chatLoading && (
                <div className="bg-slate-900 border border-slate-800 text-gray-300 rounded-lg p-2.5 text-xs animate-pulse">
                  Querying local models...
                </div>
              )}
              <div ref={scrollRef} />
            </div>

            <form onSubmit={handleSendPrompt} className="flex gap-2">
              <input
                type="text"
                value={prompt}
                onChange={e => setPrompt(e.target.value)}
                placeholder="Ask what-if scenario..."
                className="flex-1 bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:ring-1 focus:ring-blue-500"
              />
              <button
                type="submit"
                className="p-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg transition"
              >
                <Send className="h-4 w-4" />
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}
