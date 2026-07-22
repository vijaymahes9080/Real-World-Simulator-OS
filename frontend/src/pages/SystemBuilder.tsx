import { useCallback, useState, useEffect } from "react";
import ReactFlow, {
  MiniMap,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  addEdge,
  Connection,
  Edge,
  Node,
} from "reactflow";
import "reactflow/dist/style.css";
import { useStore } from "../hooks/useStore";
import { Database, GitFork, User, Zap, Save, HelpCircle } from "lucide-react";

export default function SystemBuilder() {
  const activeProject = useStore(state => state.activeProject);
  const updateActiveProject = useStore(state => state.updateActiveProject);

  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [selectedNode, setSelectedNode] = useState<Node | null>(null);
  const [saveStatus, setSaveStatus] = useState("");

  // Sync initial layout from active project
  useEffect(() => {
    if (activeProject && activeProject.layout) {
      setNodes(activeProject.layout.nodes || []);
      setEdges(activeProject.layout.edges || []);
    }
  }, [activeProject, setNodes, setEdges]);

  const onConnect = useCallback(
    (params: Connection | Edge) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  );

  const addEntityNode = (type: "stock" | "flow" | "auxiliary" | "agent") => {
    const id = `node_${uuid()}`;
    const labels = {
      stock: "New Stock (Accumulator)",
      flow: "New Flow (Rate)",
      auxiliary: "New Auxiliary Variable",
      agent: "New Agent Model"
    };
    
    const newNode: Node = {
      id,
      type,
      position: { x: 150 + Math.random() * 100, y: 150 + Math.random() * 100 },
      data: { label: labels[type] },
    };
    
    setNodes((nds) => nds.concat(newNode));
  };

  const uuid = () => Math.random().toString(36).substring(2, 9);

  const handleSave = async () => {
    setSaveStatus("Saving schema...");
    await updateActiveProject({
      layout: { nodes, edges }
    });
    setSaveStatus("System saved successfully!");
    setTimeout(() => setSaveStatus(""), 2000);
  };

  const handleNodeClick = (_: React.MouseEvent, node: Node) => {
    setSelectedNode(node);
  };

  const updateSelectedNodeLabel = (newLabel: string) => {
    if (!selectedNode) return;
    setNodes((nds) =>
      nds.map((node) => {
        if (node.id === selectedNode.id) {
          node.data = { ...node.data, label: newLabel };
        }
        return node;
      })
    );
    setSelectedNode((prev) => prev ? { ...prev, data: { ...prev.data, label: newLabel } } : null);
  };

  if (!activeProject) {
    return (
      <div className="flex h-[80vh] items-center justify-center">
        <p className="text-gray-400">Please select a simulation workspace from the dashboard sidebar.</p>
      </div>
    );
  }

  return (
    <div className="flex h-[calc(100vh-80px)] w-full gap-4">
      {/* Left Toolbar */}
      <div className="w-64 glass-panel rounded-xl p-4 flex flex-col gap-4">
        <h2 className="text-sm font-semibold uppercase tracking-wider text-gray-400">Add Components</h2>
        <div className="flex flex-col gap-2">
          <button
            onClick={() => addEntityNode("stock")}
            className="flex items-center gap-3 w-full p-2.5 rounded-lg bg-slate-900 border border-slate-800 hover:border-slate-700 text-left text-xs font-medium"
          >
            <Database className="h-4 w-4 text-accent-blue" />
            Stock (Accumulator)
          </button>
          <button
            onClick={() => addEntityNode("flow")}
            className="flex items-center gap-3 w-full p-2.5 rounded-lg bg-slate-900 border border-slate-800 hover:border-slate-700 text-left text-xs font-medium"
          >
            <GitFork className="h-4 w-4 text-accent-violet" />
            Flow (Rate of Change)
          </button>
          <button
            onClick={() => addEntityNode("agent")}
            className="flex items-center gap-3 w-full p-2.5 rounded-lg bg-slate-900 border border-slate-800 hover:border-slate-700 text-left text-xs font-medium"
          >
            <User className="h-4 w-4 text-accent-emerald" />
            Agent (Intelligent Unit)
          </button>
          <button
            onClick={() => addEntityNode("auxiliary")}
            className="flex items-center gap-3 w-full p-2.5 rounded-lg bg-slate-900 border border-slate-800 hover:border-slate-700 text-left text-xs font-medium"
          >
            <Zap className="h-4 w-4 text-accent-amber" />
            Auxiliary Variable
          </button>
        </div>

        <div className="mt-auto border-t border-slate-800 pt-4 flex flex-col gap-2">
          <button
            onClick={handleSave}
            className="flex items-center justify-center gap-2 w-full p-2.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-medium text-xs shadow-lg shadow-blue-600/10"
          >
            <Save className="h-4 w-4" />
            Save Architecture
          </button>
          {saveStatus && <span className="text-center text-xs text-emerald-400 font-medium">{saveStatus}</span>}
        </div>
      </div>

      {/* Editor Canvas */}
      <div className="flex-1 glass-panel rounded-xl overflow-hidden relative border border-slate-800">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          onNodeClick={handleNodeClick}
          fitView
        >
          <MiniMap nodeColor={(n) => {
            if (n.type === "stock") return "#3b82f6";
            if (n.type === "flow") return "#8b5cf6";
            if (n.type === "agent") return "#10b981";
            return "#f59e0b";
          }} maskColor="rgba(9, 13, 22, 0.7)" />
          <Controls />
          <Background color="#1e293b" gap={16} />
        </ReactFlow>
      </div>

      {/* Right Properties Panel */}
      <div className="w-80 glass-panel rounded-xl p-4 flex flex-col gap-4">
        <h2 className="text-sm font-semibold uppercase tracking-wider text-gray-400">Node Properties</h2>
        {selectedNode ? (
          <div className="space-y-4">
            <div>
              <label className="block text-[10px] uppercase font-bold text-gray-500 mb-1.5">Component ID</label>
              <span className="font-mono text-xs text-gray-400 bg-slate-900 border border-slate-800 rounded px-2 py-1 select-all">{selectedNode.id}</span>
            </div>
            <div>
              <label className="block text-[10px] uppercase font-bold text-gray-500 mb-1.5">Type</label>
              <span className="text-xs font-semibold capitalize text-white bg-slate-900 border border-slate-800 rounded px-2.5 py-1">
                {selectedNode.type}
              </span>
            </div>
            <div>
              <label className="block text-[10px] uppercase font-bold text-gray-500 mb-1.5">Label Name</label>
              <input
                type="text"
                value={selectedNode.data.label || ""}
                onChange={(e) => updateSelectedNodeLabel(e.target.value)}
                className="w-full bg-slate-900 border border-slate-800 rounded px-3 py-2 text-white focus:outline-none focus:ring-1 focus:ring-blue-500 text-xs"
              />
            </div>

            <div className="bg-slate-900/50 border border-slate-800/80 rounded-lg p-3">
              <div className="flex gap-2 items-center text-xs text-blue-400 mb-1 font-semibold">
                <HelpCircle className="h-4 w-4" />
                Causal Connection
              </div>
              <p className="text-[11px] text-gray-400 leading-relaxed">
                Connect outputs to inputs to build execution rules. Stock nodes accumulate numeric integrations, flows dictate the speed of those accumulations, and agents evaluate constraints.
              </p>
            </div>
          </div>
        ) : (
          <div className="flex-1 flex flex-col items-center justify-center text-center text-xs text-gray-500">
            Click on any canvas component to review or modify properties.
          </div>
        )}
      </div>
    </div>
  );
}
