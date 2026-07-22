import { BrowserRouter as Router, Routes, Route, Link, Navigate } from "react-router-dom";
import { useStore } from "./hooks/useStore";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import SystemBuilder from "./pages/SystemBuilder";
import ScenarioExplorer from "./pages/ScenarioExplorer";
import KnowledgeGraphPage from "./pages/KnowledgeGraphPage";
import OptimizationPage from "./pages/OptimizationPage";
import { LayoutDashboard, Database, TrendingUp, Network, Award, LogOut, Terminal } from "lucide-react";

export default function App() {
  const user = useStore(state => state.user);
  const logout = useStore(state => state.logout);

  if (!user) {
    return <Login />;
  }

  return (
    <Router>
      <div className="min-h-screen bg-background text-gray-100 flex flex-col">
        {/* Navigation Header */}
        <header className="h-16 border-b border-slate-800/80 bg-slate-950/70 backdrop-blur-md sticky top-0 z-50 px-6 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Terminal className="h-6 w-6 text-blue-500 animate-pulse" />
            <div>
              <span className="font-bold text-white text-sm tracking-wide">Real-World Simulator OS</span>
              <span className="text-[10px] bg-blue-500/10 border border-blue-500/30 text-blue-400 rounded-full px-2 py-0.5 ml-2 font-mono font-bold">V1.0</span>
            </div>
          </div>
          
          {/* Main Navigation Links */}
          <nav className="hidden md:flex items-center gap-1.5">
            <Link
              to="/"
              className="flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-semibold text-gray-300 hover:text-white hover:bg-slate-900 transition"
            >
              <LayoutDashboard className="h-4 w-4" />
              Console Dashboard
            </Link>
            <Link
              to="/builder"
              className="flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-semibold text-gray-300 hover:text-white hover:bg-slate-900 transition"
            >
              <Database className="h-4 w-4" />
              Architecture Designer
            </Link>
            <Link
              to="/scenarios"
              className="flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-semibold text-gray-300 hover:text-white hover:bg-slate-900 transition"
            >
              <TrendingUp className="h-4 w-4" />
              Scenario Explorer
            </Link>
            <Link
              to="/graph"
              className="flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-semibold text-gray-300 hover:text-white hover:bg-slate-900 transition"
            >
              <Network className="h-4 w-4" />
              Causal Graph
            </Link>
            <Link
              to="/optimize"
              className="flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-semibold text-gray-300 hover:text-white hover:bg-slate-900 transition"
            >
              <Award className="h-4 w-4" />
              GA Optimizer
            </Link>
          </nav>

          {/* User Profile & Logout */}
          <div className="flex items-center gap-4">
            <div className="text-right hidden sm:block">
              <p className="text-xs font-bold text-white leading-none">{user.username}</p>
              <span className="text-[9px] font-mono text-gray-500 capitalize">{user.role} role</span>
            </div>
            <button
              onClick={logout}
              className="p-2 bg-slate-900 hover:bg-slate-800 text-rose-400 border border-slate-800 rounded-lg transition"
              title="Sign Out"
            >
              <LogOut className="h-4 w-4" />
            </button>
          </div>
        </header>

        {/* Main Workspace Frame */}
        <main className="flex-1 max-w-7xl w-full mx-auto p-6">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/builder" element={<SystemBuilder />} />
            <Route path="/scenarios" element={<ScenarioExplorer />} />
            <Route path="/graph" element={<KnowledgeGraphPage />} />
            <Route path="/optimize" element={<OptimizationPage />} />
            <Route path="*" element={<Navigate to="/" />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}
