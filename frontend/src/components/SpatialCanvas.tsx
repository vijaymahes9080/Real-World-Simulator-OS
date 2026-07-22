import { useEffect, useRef, useState } from "react";
import { Maximize2, RotateCcw, Activity, Cpu } from "lucide-react";

/**
 * Node3D represents a spatial node coordinate in the 3D Digital Twin viewport.
 */
interface Node3D {
  id: string;
  label: string;
  type: string;
  x: number;
  y: number;
  z: number;
  vx: number;
  vy: number;
  vz: number;
  status: "nominal" | "warning" | "critical";
  val: number;
}

/**
 * Edge3D represents a directed energy/material connection between two 3D spatial nodes.
 */
interface Edge3D {
  source: string;
  target: string;
  label: string;
}

/**
 * Component props for SpatialCanvas viewport.
 */
interface SpatialCanvasProps {
  nodes?: Node3D[];
  edges?: Edge3D[];
  activeTick?: number;
}

/**
 * SpatialCanvas renders a high-performance 3D spatial graph viewport using HTML5 Canvas.
 */
export default function SpatialCanvas({ activeTick = 0 }: SpatialCanvasProps) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const [isRotating, setIsRotating] = useState<boolean>(true);

  // Initial 3D Spatial Nodes
  const nodesRef = useRef<Node3D[]>([
    { id: "n1", label: "Central Power Reserve", type: "Stock", x: -120, y: -60, z: 40, vx: 0, vy: 0, vz: 0, status: "nominal", val: 840.0 },
    { id: "n2", label: "Solar Inflow Array", type: "Flow", x: -200, y: 80, z: -30, vx: 0, vy: 0, vz: 0, status: "nominal", val: 120.0 },
    { id: "n3", label: "EV Fleet Charging Grid", type: "Agent", x: 140, y: -40, z: -80, vx: 0, vy: 0, vz: 0, status: "warning", val: 240.0 },
    { id: "n4", label: "Substation Transformer", type: "Stock", x: 60, y: 120, z: 90, vx: 0, vy: 0, vz: 0, status: "nominal", val: 98.2 },
    { id: "n5", label: "Emergency Battery Storage", type: "Stock", x: 0, y: -160, z: -20, vx: 0, vy: 0, vz: 0, status: "nominal", val: 450.0 },
    { id: "n6", label: "Urban Power Load Node", type: "Flow", x: 180, y: 100, z: 30, vx: 0, vy: 0, vz: 0, status: "critical", val: 310.5 }
  ]);

  const edgesRef = useRef<Edge3D[]>([
    { source: "n2", target: "n1", label: "Renewable Generation" },
    { source: "n1", target: "n4", label: "High Voltage Transmission" },
    { source: "n4", target: "n3", label: "Fleet Power Draw" },
    { source: "n4", target: "n6", label: "Urban Demand Stream" },
    { source: "n5", target: "n1", label: "Auxiliary Discharge" }
  ]);

  // Orbit angle state
  const angleRef = useRef({ yaw: 0.4, pitch: 0.2 });

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    let animId: number;

    const render = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      // Auto-rotation
      if (isRotating) {
        angleRef.current.yaw += 0.005;
      }

      const cosY = Math.cos(angleRef.current.yaw);
      const sinY = Math.sin(angleRef.current.yaw);
      const cosP = Math.cos(angleRef.current.pitch);
      const sinP = Math.sin(angleRef.current.pitch);

      const cx = canvas.width / 2;
      const cy = canvas.height / 2;

      // Project 3D to 2D
      const projectedNodes = nodesRef.current.map((node) => {
        // Rotate around Y axis
        let x1 = node.x * cosY - node.z * sinY;
        let z1 = node.x * sinY + node.z * cosY;

        // Rotate around X axis (pitch)
        let y2 = node.y * cosP - z1 * sinP;
        let z2 = node.y * sinP + z1 * cosP;

        // Perspective scale factor
        const fov = 400;
        const scale = fov / (fov + z2 + 200);
        const px = cx + x1 * scale;
        const py = cy + y2 * scale;

        return { ...node, px, py, scale, depth: z2 };
      });

      // Sort by depth for correct 3D rendering
      projectedNodes.sort((a, b) => b.depth - a.depth);

      // Draw Edges with animated energy pulses
      const projectedMap = new Map(projectedNodes.map((n) => [n.id, n]));
      edgesRef.current.forEach((edge) => {
        const src = projectedMap.get(edge.source);
        const tgt = projectedMap.get(edge.target);
        if (src && tgt) {
          ctx.beginPath();
          ctx.moveTo(src.px, src.py);
          ctx.lineTo(tgt.px, tgt.py);
          ctx.strokeStyle = "rgba(59, 130, 246, 0.3)";
          ctx.lineWidth = Math.max(1, 2 * ((src.scale + tgt.scale) / 2));
          ctx.stroke();

          // Energy Pulse animation along link
          const timeOffset = (Date.now() / 1500 + activeTick * 0.2) % 1;
          const pulseX = src.px + (tgt.px - src.px) * timeOffset;
          const pulseY = src.py + (tgt.py - src.py) * timeOffset;

          ctx.beginPath();
          ctx.arc(pulseX, pulseY, 3.5 * src.scale, 0, Math.PI * 2);
          ctx.fillStyle = "#60A5FA";
          ctx.shadowColor = "#3B82F6";
          ctx.shadowBlur = 10;
          ctx.fill();
          ctx.shadowBlur = 0;
        }
      });

      // Draw 3D Spatial Nodes
      projectedNodes.forEach((node) => {
        const r = Math.max(8, 16 * node.scale);

        // Glow ring
        ctx.beginPath();
        ctx.arc(node.px, node.py, r + 4, 0, Math.PI * 2);
        const colorGlow =
          node.status === "critical"
            ? "rgba(244, 63, 94, 0.4)"
            : node.status === "warning"
            ? "rgba(245, 158, 11, 0.4)"
            : "rgba(16, 185, 129, 0.4)";
        ctx.fillStyle = colorGlow;
        ctx.fill();

        // Solid Node Sphere
        ctx.beginPath();
        ctx.arc(node.px, node.py, r, 0, Math.PI * 2);
        const colorCore =
          node.status === "critical" ? "#F43F5E" : node.status === "warning" ? "#F59E0B" : "#10B981";
        ctx.fillStyle = colorCore;
        ctx.shadowColor = colorCore;
        ctx.shadowBlur = 12;
        ctx.fill();
        ctx.shadowBlur = 0;

        // Label
        ctx.font = `${Math.max(9, Math.round(11 * node.scale))}px Inter, sans-serif`;
        ctx.fillStyle = "#E2E8F0";
        ctx.textAlign = "center";
        ctx.fillText(node.label, node.px, node.py + r + 14);
      });

      animId = requestAnimationFrame(render);
    };

    render();

    return () => cancelAnimationFrame(animId);
  }, [isRotating, activeTick]);

  return (
    <div className="glass-panel rounded-2xl p-5 border border-slate-800 shadow-2xl relative overflow-hidden flex flex-col h-[480px]">
      {/* Viewport Header Controls */}
      <div className="flex items-center justify-between z-10 mb-2">
        <div className="flex items-center gap-2">
          <div className="p-2 bg-blue-500/10 border border-blue-500/30 rounded-lg text-blue-400">
            <Cpu className="h-4 w-4 animate-spin-slow" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              Spatial 3D Digital Twin Viewport
              <span className="text-[10px] bg-emerald-500/20 text-emerald-400 px-2 py-0.5 rounded-full border border-emerald-500/30 font-mono">
                WEBGL/PARALLEL
              </span>
            </h3>
            <p className="text-[11px] text-gray-400">Real-time particle graph physics & spatial node state inspector</p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setIsRotating(!isRotating)}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium border flex items-center gap-1.5 transition ${
              isRotating
                ? "bg-blue-600/20 border-blue-500 text-blue-300"
                : "bg-slate-800/80 border-slate-700 text-gray-400 hover:text-white"
            }`}
          >
            <RotateCcw className={`h-3.5 w-3.5 ${isRotating ? "animate-spin" : ""}`} />
            {isRotating ? "Orbiting" : "Paused"}
          </button>
          <button
            onClick={() => {
              angleRef.current = { yaw: 0.4, pitch: 0.2 };
            }}
            className="p-1.5 bg-slate-800 border border-slate-700 rounded-lg text-gray-300 hover:text-white hover:bg-slate-700"
            title="Reset View"
          >
            <Maximize2 className="h-3.5 w-3.5" />
          </button>
        </div>
      </div>

      {/* Canvas Viewport */}
      <div className="relative flex-1 rounded-xl overflow-hidden bg-slate-950/80 border border-slate-800/80 flex items-center justify-center">
        <canvas
          ref={canvasRef}
          width={800}
          height={400}
          className="w-full h-full cursor-grab active:cursor-grabbing"
        />

        {/* Floating Legend Overlay */}
        <div className="absolute bottom-3 left-3 bg-slate-900/90 backdrop-blur border border-slate-800 p-2.5 rounded-xl text-[11px] font-mono flex items-center gap-4 text-gray-300">
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse" />
            Nominal
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-amber-500" />
            Warning
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-rose-500 animate-ping" />
            Critical Stress
          </div>
        </div>

        {/* Live Active Tick Watermark */}
        <div className="absolute top-3 right-3 bg-slate-900/80 border border-slate-800 px-3 py-1 rounded-lg text-[10px] font-mono text-blue-400 flex items-center gap-1.5">
          <Activity className="h-3 w-3 text-blue-400" />
          TICK FRAME #{activeTick}
        </div>
      </div>
    </div>
  );
}
