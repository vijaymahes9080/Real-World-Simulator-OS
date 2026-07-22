from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.services.rule_engine import RuleEngine

class SDStock(BaseModel):
    id: str
    name: str
    initial_value: float
    inflows: List[str] = Field(default_factory=list)   # IDs of flows increasing this stock
    outflows: List[str] = Field(default_factory=list)  # IDs of flows decreasing this stock

class SDFlow(BaseModel):
    id: str
    name: str
    expression: str  # Formula, e.g. "stocks.population * variables.birth_rate"

class SDAuxiliary(BaseModel):
    id: str
    name: str
    expression: str  # Formula, e.g. "0.02 * (1 - stocks.population / 100000)"

class SDModel(BaseModel):
    stocks: Dict[str, SDStock] = Field(default_factory=dict)
    flows: Dict[str, SDFlow] = Field(default_factory=dict)
    auxiliaries: Dict[str, SDAuxiliary] = Field(default_factory=dict)
    constants: Dict[str, float] = Field(default_factory=dict)

class SDSimulationState(BaseModel):
    time: float = 0.0
    stock_values: Dict[str, float] = Field(default_factory=dict)
    flow_values: Dict[str, float] = Field(default_factory=dict)
    auxiliary_values: Dict[str, float] = Field(default_factory=dict)
    history: List[Dict[str, Any]] = Field(default_factory=list)

class SystemDynamicsEngine:
    @staticmethod
    def initialize_state(model: SDModel, start_time: float = 0.0) -> SDSimulationState:
        stock_vals = {s.id: s.initial_value for s in model.stocks.values()}
        return SDSimulationState(
            time=start_time,
            stock_values=stock_vals,
            flow_values={f_id: 0.0 for f_id in model.flows.keys()},
            auxiliary_values={a_id: 0.0 for a_id in model.auxiliaries.keys()},
            history=[]
        )

    @classmethod
    def step(cls, model: SDModel, state: SDSimulationState, dt: float) -> SDSimulationState:
        """
        Executes a single step of Euler integration.
        1. Calculate auxiliaries (in dependency order or iteratively to resolve dependencies)
        2. Calculate flows
        3. Accumulate flows into stocks: stock = stock + (inflows - outflows) * dt
        """
        import math
        from app.services.rule_engine import make_namespaces
        
        # Build evaluation context
        eval_context = {
            "stocks": make_namespaces(dict(state.stock_values)),
            "variables": make_namespaces({}),  # Will contain auxiliaries
            "constants": make_namespaces(dict(model.constants)),
            "math": math,
            "time": state.time
        }

        # Auxiliaries and flows can depend on stocks, constants, and each other.
        # We perform iterative evaluations to resolve dependencies, or order them if acyclic.
        # A simple iterative solver to update auxiliary values until they stabilize (max 10 iterations)
        aux_values = {a_id: state.auxiliary_values.get(a_id, 0.0) for a_id in model.auxiliaries.keys()}
        
        # Safe built-in scope
        global_scope = {"__builtins__": None, "math": math, "abs": abs, "min": min, "max": max}
        
        for _ in range(5):
            eval_context["variables"] = make_namespaces(dict(aux_values))
            changed = False
            for a_id, aux in model.auxiliaries.items():
                try:
                    # Sanitize expression before run
                    sanitized = RuleEngine.sanitize_expression(aux.expression)
                    new_val = float(eval(sanitized, global_scope, eval_context))
                    if abs(aux_values[a_id] - new_val) > 1e-6:
                        aux_values[a_id] = new_val
                        changed = True
                except Exception:
                    pass  # Keep previous or default to 0
            if not changed:
                break
                
        eval_context["variables"] = make_namespaces(dict(aux_values))

        # 2. Compute flows
        flow_values = {}
        for f_id, flow in model.flows.items():
            try:
                sanitized = RuleEngine.sanitize_expression(flow.expression)
                flow_values[f_id] = float(eval(sanitized, global_scope, eval_context))
            except Exception:
                flow_values[f_id] = 0.0

        # Update eval context with flow values for stock calculations
        eval_context["flows"] = make_namespaces(flow_values)

        # 3. Update stocks using Euler method
        next_stocks = {}
        for s_id, stock in model.stocks.items():
            current_val = state.stock_values.get(s_id, stock.initial_value)
            
            # Sum up inflow rates and outflow rates
            inflow_sum = sum(flow_values.get(inf_id, 0.0) for inf_id in stock.inflows)
            outflow_sum = sum(flow_values.get(outf_id, 0.0) for outf_id in stock.outflows)
            
            net_rate = inflow_sum - outflow_sum
            next_val = current_val + net_rate * dt
            
            # Stocks cannot represent negative physical quantities usually, 
            # but we let the mathematical definition be general. We'll clip at 0 if wanted, 
            # but standard system dynamics allows negative stocks unless constrained.
            next_stocks[s_id] = next_val

        # 4. Advance time
        next_time = state.time + dt
        
        # Save historical snapshot
        history_entry = {
            "time": state.time,
            "stocks": dict(state.stock_values),
            "flows": dict(state.flow_values),
            "auxiliaries": dict(state.auxiliary_values)
        }
        
        next_history = list(state.history)
        next_history.append(history_entry)
        
        return SDSimulationState(
            time=next_time,
            stock_values=next_stocks,
            flow_values=flow_values,
            auxiliary_values=aux_values,
            history=next_history
        )

    @classmethod
    def run_simulation(
        cls, 
        model: SDModel, 
        start_time: float, 
        end_time: float, 
        dt: float
    ) -> SDSimulationState:
        state = cls.initialize_state(model, start_time)
        while state.time < end_time:
            state = cls.step(model, state, dt)
        return state
