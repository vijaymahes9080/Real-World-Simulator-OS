from typing import Any, Dict, List, Optional
import uuid
import random
from pydantic import BaseModel, Field
from app.services.rule_engine import Rule, RuleEngine

class AgentMemory(BaseModel):
    tick: int
    event: str
    impact: str
    metadata: Dict[str, Any] = {}

class Agent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    role: str
    agent_type: str  # e.g., "customer", "employee", "crop_cell", "investor"
    goals: List[str] = Field(default_factory=list)
    personality: Dict[str, float] = Field(
        default_factory=lambda: {
            "risk_tolerance": 0.5,
            "extraversion": 0.5,
            "conscientiousness": 0.5,
            "agreeableness": 0.5,
            "neuroticism": 0.5
        }
    )
    resources: Dict[str, float] = Field(default_factory=dict)
    state: Dict[str, Any] = Field(default_factory=dict)
    memory: List[AgentMemory] = Field(default_factory=list)
    relationships: Dict[str, float] = Field(default_factory=dict)  # agent_id -> affinity (-1.0 to 1.0)
    is_active: bool = True

class Message(BaseModel):
    sender_id: str
    receiver_id: str
    content: str
    msg_type: str = "general"
    metadata: Dict[str, Any] = {}

class AgentSimulationState(BaseModel):
    tick: int = 0
    agents: Dict[str, Agent] = Field(default_factory=dict)
    global_variables: Dict[str, Any] = Field(default_factory=dict)
    messages: List[Message] = Field(default_factory=list)

class AgentEngine:
    @staticmethod
    def initialize_simulation(agents: List[Agent], global_vars: Dict[str, Any]) -> AgentSimulationState:
        return AgentSimulationState(
            tick=0,
            agents={a.id: a for a in agents},
            global_variables=global_vars,
            messages=[]
        )

    @staticmethod
    def step(
        state: AgentSimulationState, 
        rules: List[Rule], 
        custom_step_fn: Optional[Any] = None
    ) -> AgentSimulationState:
        """
        Executes one step (tick) of the agent-based simulation.
        For each agent, it evaluates context against rule-engine rules and runs updates.
        """
        next_tick = state.tick + 1
        next_agents = {}
        next_messages = []
        
        # Randomize agent update order to avoid turn bias
        agent_ids = list(state.agents.keys())
        random.shuffle(agent_ids)
        
        # Prepare working copy of globals
        working_globals = dict(state.global_variables)
        
        # Process communication (can affect relationships/state prior to rule run)
        # Agents read messages from state.messages
        inbox: Dict[str, List[Message]] = {}
        for msg in state.messages:
            inbox.setdefault(msg.receiver_id, []).append(msg)
            
        for agent_id in agent_ids:
            agent = state.agents[agent_id]
            if not agent.is_active:
                next_agents[agent.id] = agent
                continue
                
            # Create a mutable clone
            agent_clone = agent.model_copy(deep=True)
            
            # Form standard execution context for the rules engine
            context = {
                "agent": agent_clone.model_dump(),
                "global": working_globals,
                "inbox": [m.model_dump() for m in inbox.get(agent_id, [])]
            }
            
            # Apply Rules
            try:
                updated_context = RuleEngine.run_ruleset(rules, context)
                
                # Apply updates from context back to agent and globals
                agent_clone = Agent(**updated_context["agent"])
                working_globals = updated_context["global"]
                
                # Retrieve any generated outgoing messages from rule engine actions
                if "outgoing_messages" in updated_context:
                    for m_data in updated_context["outgoing_messages"]:
                        next_messages.append(Message(**m_data))
            except Exception as e:
                # Log execution error inside agent memory
                agent_clone.memory.append(
                    AgentMemory(
                        tick=next_tick,
                        event="rule_execution_failure",
                        impact=str(e),
                        metadata={"error": True}
                    )
                )

            # Standard aging / depletion processes based on personality/attributes
            # e.g., energy depletion, budget usage if not handled by rules
            if "energy" in agent_clone.resources:
                agent_clone.resources["energy"] = max(0.0, agent_clone.resources["energy"] - 1.0)
                if agent_clone.resources["energy"] <= 0:
                    agent_clone.is_active = False
                    agent_clone.memory.append(
                        AgentMemory(
                            tick=next_tick,
                            event="exhaustion",
                            impact="Agent became inactive due to zero energy"
                        )
                    )
                    
            # Custom simulation-specific step function
            if custom_step_fn:
                agent_clone, working_globals, extra_msgs = custom_step_fn(
                    agent_clone, working_globals, inbox.get(agent_id, []), next_tick
                )
                next_messages.extend(extra_msgs)

            next_agents[agent_clone.id] = agent_clone

        # Clean messages from processed ticks and set new outgoing messages for next tick
        return AgentSimulationState(
            tick=next_tick,
            agents=next_agents,
            global_variables=working_globals,
            messages=next_messages
        )
