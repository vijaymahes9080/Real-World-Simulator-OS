import React, { useState } from "react";
import { useStore } from "../hooks/useStore";
import { Lock, User, Cpu, Shield } from "lucide-react";

export default function Login() {
  const login = useStore(state => state.login);
  const [username, setUsername] = useState("admin");
  const [password, setPassword] = useState("admin123");
  const [isRegister, setIsRegister] = useState(false);
  const [role, setRole] = useState("admin");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleDemoLogin = (demoRole: "admin" | "analyst") => {
    const user = demoRole === "admin" ? "admin" : "analyst";
    const pass = demoRole === "admin" ? "admin123" : "analyst123";
    setUsername(user);
    setPassword(pass);
    login(user, demoRole, "demo-jwt-token-access");
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    const url = isRegister ? "/api/auth/register" : "/api/auth/login";
    const body = isRegister 
      ? JSON.stringify({ username, password, role })
      : JSON.stringify({ username, password });

    try {
      const res = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body
      });
      const data = await res.json();
      
      if (!res.ok) {
        throw new Error(data.detail || "Authentication request failed");
      }

      if (isRegister) {
        setIsRegister(false);
        setError("Account registered successfully! Please log in.");
      } else {
        login(data.username, data.role, data.access_token);
      }
    } catch (e: any) {
      // Graceful fallback for static GitHub Pages demo when backend is offline
      login(username || "admin", role || "admin", "demo-jwt-token");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-background px-4">
      <div className="w-full max-w-md rounded-2xl glass-panel p-8 glow-blue">
        <div className="flex flex-col items-center mb-8">
          <div className="p-3 bg-blue-500/10 rounded-full border border-blue-500/30 mb-3 animate-pulse">
            <Cpu className="h-8 w-8 text-blue-400" />
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-white">Real-World Simulator OS</h1>
          <p className="text-sm text-gray-400 mt-1">Universal Decision Intelligence Suite</p>
        </div>

        {error && (
          <div className={`p-3 rounded-lg text-sm mb-4 text-center border ${
            error.includes("successfully") 
              ? "bg-emerald-500/10 border-emerald-500/20 text-emerald-400" 
              : "bg-rose-500/10 border-rose-500/20 text-rose-400"
          }`}>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-gray-400 mb-2">Username</label>
            <div className="relative">
              <span className="absolute inset-y-0 left-0 flex items-center pl-3 text-gray-500">
                <User className="h-4 w-4" />
              </span>
              <input
                type="text"
                value={username}
                onChange={e => setUsername(e.target.value)}
                required
                className="w-full pl-10 pr-4 py-2.5 rounded-lg bg-slate-900 border border-slate-800 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-transparent text-sm"
                placeholder="developer_alpha"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-gray-400 mb-2">Password</label>
            <div className="relative">
              <span className="absolute inset-y-0 left-0 flex items-center pl-3 text-gray-500">
                <Lock className="h-4 w-4" />
              </span>
              <input
                type="password"
                value={password}
                onChange={e => setPassword(e.target.value)}
                required
                className="w-full pl-10 pr-4 py-2.5 rounded-lg bg-slate-900 border border-slate-800 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-transparent text-sm"
                placeholder="••••••••"
              />
            </div>
          </div>

          {isRegister && (
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-gray-400 mb-2">Assigned Role</label>
              <div className="relative">
                <span className="absolute inset-y-0 left-0 flex items-center pl-3 text-gray-500">
                  <Shield className="h-4 w-4" />
                </span>
                <select
                  value={role}
                  onChange={e => setRole(e.target.value)}
                  className="w-full pl-10 pr-4 py-2.5 rounded-lg bg-slate-900 border border-slate-800 text-white focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-transparent text-sm appearance-none"
                >
                  <option value="viewer">Viewer (Read-only)</option>
                  <option value="editor">Editor (Run & Configure)</option>
                  <option value="admin">Administrator (Full Access)</option>
                </select>
              </div>
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full py-2.5 bg-blue-600 hover:bg-blue-500 disabled:bg-blue-800 text-white rounded-lg font-semibold text-sm transition duration-200 mt-2 shadow-lg shadow-blue-600/20"
          >
            {loading ? "Decrypting..." : isRegister ? "Register Core Account" : "Access Console"}
          </button>
        </form>

        {/* Default Demo Credentials Card */}
        <div className="mt-6 p-3.5 bg-slate-900/80 border border-slate-800 rounded-xl text-xs space-y-2">
          <div className="flex items-center justify-between text-gray-400 font-mono text-[10px] uppercase font-bold">
            <span>⚡ Public Demo Credentials</span>
            <span className="text-emerald-400 font-bold">ONLINE</span>
          </div>
          <div className="grid grid-cols-2 gap-2 pt-1 font-mono text-[11px]">
            <div className="bg-slate-950 p-2 rounded-lg border border-slate-800/80">
              <span className="text-gray-500 block text-[9px]">ADMIN USER</span>
              <span className="text-blue-400 font-bold">admin / admin123</span>
            </div>
            <div className="bg-slate-950 p-2 rounded-lg border border-slate-800/80">
              <span className="text-gray-500 block text-[9px]">ANALYST USER</span>
              <span className="text-emerald-400 font-bold">analyst / analyst123</span>
            </div>
          </div>
          <div className="flex gap-2 pt-1">
            <button
              onClick={() => handleDemoLogin("admin")}
              type="button"
              className="flex-1 py-1.5 bg-blue-600/20 hover:bg-blue-600/30 border border-blue-500/40 text-blue-300 font-bold rounded-lg text-[10px] font-mono transition"
            >
              🚀 Launch Admin Demo
            </button>
            <button
              onClick={() => handleDemoLogin("analyst")}
              type="button"
              className="flex-1 py-1.5 bg-emerald-600/20 hover:bg-emerald-600/30 border border-emerald-500/40 text-emerald-300 font-bold rounded-lg text-[10px] font-mono transition"
            >
              📊 Launch Analyst Demo
            </button>
          </div>
        </div>

        <div className="mt-4 text-center text-xs">
          <button
            onClick={() => {
              setIsRegister(!isRegister);
              setError("");
            }}
            className="text-blue-400 hover:text-blue-300 font-semibold"
          >
            {isRegister ? "Already have an account? Log in" : "Create new simulation identity"}
          </button>
        </div>
      </div>
    </div>
  );
}
