import networkx as nx
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, Field

class KGNode(BaseModel):
    id: str
    name: str
    type: str  # "agent", "rule", "event", "location", "resource", "variable"
    properties: Dict[str, Any] = Field(default_factory=dict)

class KGEdge(BaseModel):
    source: str
    target: str
    relation: str  # "affects", "contains", "triggers", "manages", "communicates_with"
    properties: Dict[str, Any] = Field(default_factory=dict)

class KnowledgeGraphService:
    def __init__(self):
        self.graph = nx.DiGraph()

    def clear(self):
        self.graph.clear()

    def add_node(self, node: KGNode):
        self.graph.add_node(
            node.id, 
            name=node.name, 
            type=node.type, 
            **node.properties
        )

    def add_edge(self, edge: KGEdge):
        self.graph.add_edge(
            edge.source, 
            edge.target, 
            relation=edge.relation, 
            **edge.properties
        )

    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        if self.graph.has_node(node_id):
            data = self.graph.nodes[node_id]
            return {"id": node_id, **data}
        return None

    def find_nodes(self, query: str, node_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search for nodes matching a query in their name or properties.
        """
        results = []
        q = query.lower()
        for node_id, data in self.graph.nodes(data=True):
            if node_type and data.get("type") != node_type:
                continue
            
            # Simple substring matching
            name_match = q in data.get("name", "").lower()
            prop_match = any(q in str(val).lower() for val in data.values())
            
            if name_match or prop_match:
                results.append({"id": node_id, **data})
        return results

    def trace_causal_chain(self, start_node_id: str, end_node_id: str) -> List[Tuple[str, str, str]]:
        """
        Finds the shortest path of dependencies/actions between two nodes to explain cause-and-effect.
        Returns a list of (source, target, relation) tuples representing the chain.
        """
        if not (self.graph.has_node(start_node_id) and self.graph.has_node(end_node_id)):
            return []
            
        try:
            path = nx.shortest_path(self.graph, source=start_node_id, target=end_node_id)
            chain = []
            for i in range(len(path) - 1):
                u, v = path[i], path[i+1]
                edge_data = self.graph.get_edge_data(u, v) or {}
                relation = edge_data.get("relation", "connects_to")
                chain.append((u, v, relation))
            return chain
        except nx.NetworkXNoPath:
            return []

    def get_serializable_graph(self) -> Dict[str, Any]:
        """
        Returns the entire graph structured for UI renderers like D3 or React Flow.
        """
        nodes = []
        for node_id, data in self.graph.nodes(data=True):
            nodes.append({
                "id": node_id,
                "label": data.get("name", node_id),
                "type": data.get("type", "unknown"),
                "properties": {k: v for k, v in data.items() if k not in ["name", "type"]}
            })
            
        edges = []
        for u, v, data in self.graph.edges(data=True):
            edges.append({
                "source": u,
                "target": v,
                "relation": data.get("relation", "connects_to"),
                "properties": {k: v for k, v in data.items() if k != "relation"}
            })
            
        return {"nodes": nodes, "edges": edges}

    def import_from_sim_state(self, agents: Dict[str, Any], global_vars: Dict[str, Any], rules: List[Any]):
        """
        Builds graph relationships dynamically based on active agent configurations, variables, and rules.
        """
        self.clear()
        
        # 1. Add agent nodes and relationships
        for a_id, agent in agents.items():
            self.add_node(KGNode(
                id=a_id,
                name=agent.name,
                type="agent",
                properties={"role": agent.role, "agent_type": agent.agent_type}
            ))
            
            # Relationships
            for related_id, affinity in agent.relationships.items():
                if related_id in agents:
                    self.add_edge(KGEdge(
                        source=a_id,
                        target=related_id,
                        relation="communicates_with",
                        properties={"affinity": affinity}
                    ))
                    
        # 2. Add rule nodes
        for rule in rules:
            rule_id = f"rule_{rule.id}"
            self.add_node(KGNode(
                id=rule_id,
                name=rule.name,
                type="rule",
                properties={"condition": rule.condition, "priority": rule.priority}
            ))
            
            # Parse targets out of actions / conditions to build causal edges
            # For simplicity, if standard symbols appear in expressions, connect them
            for a_id, agent in agents.items():
                # If rule condition references "agent", draw a dependency
                if "agent" in rule.condition:
                    self.add_edge(KGEdge(source=rule_id, target=a_id, relation="affects"))
                # If rule action mentions agent variables
                if "agent" in rule.action:
                    self.add_edge(KGEdge(source=rule_id, target=a_id, relation="triggers"))
