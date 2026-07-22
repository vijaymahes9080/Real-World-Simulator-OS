import uuid
import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Any, Dict, List, Optional
from pydantic import BaseModel

from app.db.session import get_db, DuckDBManager
from app.models.project import SimulationProject, SimulationRun, User
from app.schemas.project import RunResponse, RunCreate
from app.api.auth import get_current_user

# Engines and services imports
from app.engines.agent_engine import AgentEngine, Agent, AgentSimulationState
from app.engines.system_dynamics import SystemDynamicsEngine, SDModel, SDStock, SDFlow, SDAuxiliary
from app.engines.monte_carlo_engine import MonteCarloEngine, MonteCarloConfig, DistributionParam
from app.engines.des_engine import DESEngine, Event, DESSimulationState
from app.services.rule_engine import Rule
from app.services.forecasting import ForecastingService
from app.services.optimization import OptimizationService, OptimizationConfig, OptimizationParam
from app.services.explainable_ai import ExplainableAIService, CounterfactualQuery, CounterfactualResult
from app.services.llm_service import LLMService

router = APIRouter(tags=["Simulation Execution"])
llm_service = LLMService()

class AssistantRequest(BaseModel):
    prompt: str

class OptimizationRequest(BaseModel):
    config: OptimizationConfig

# Create a simulation run
@router.post("/runs", response_model=RunResponse, status_code=status.HTTP_201_CREATED)
def execute_run(run_in: RunCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    project = db.query(SimulationProject).filter(SimulationProject.id == run_in.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    run_id = f"run_{uuid.uuid4().hex[:12]}"
    
    # Initialize run record in SQLite
    run = SimulationRun(
        id=run_id,
        project_id=project.id,
        status="running",
        run_type=run_in.run_type,
        started_at=datetime.datetime.utcnow(),
        metrics_summary={}
    )
    db.add(run)
    db.commit()

    conn = DuckDBManager.get_connection()
    try:
        if run_in.run_type == "system_dynamics":
            # 1. Parse SD Config
            sd_config = project.system_dynamics or {}
            stocks_data = {k: SDStock(**v) for k, v in sd_config.get("stocks", {}).items()}
            flows_data = {k: SDFlow(**v) for k, v in sd_config.get("flows", {}).items()}
            aux_data = {k: SDAuxiliary(**v) for k, v in sd_config.get("auxiliaries", {}).items()}
            constants_data = {k: float(v) for k, v in sd_config.get("constants", {}).items()}
            
            model = SDModel(
                stocks=stocks_data,
                flows=flows_data,
                auxiliaries=aux_data,
                constants=constants_data
            )
            
            # Execute Euler steps (50 ticks, dt=1.0)
            state = SystemDynamicsEngine.initialize_state(model, start_time=0.0)
            dt = 1.0
            ticks_count = 50
            
            # Record initial values
            for stock_id, val in state.stock_values.items():
                conn.execute(
                    "INSERT INTO sim_telemetry VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (run_id, 0, 0.0, stock_id, float(val), stock_id, "stock")
                )
                
            for tick in range(1, ticks_count + 1):
                state = SystemDynamicsEngine.step(model, state, dt)
                # Write to DuckDB
                for stock_id, val in state.stock_values.items():
                    conn.execute(
                        "INSERT INTO sim_telemetry VALUES (?, ?, ?, ?, ?, ?, ?)",
                        (run_id, tick, state.time, stock_id, float(val), stock_id, "stock")
                    )
                for flow_id, val in state.flow_values.items():
                    conn.execute(
                        "INSERT INTO sim_telemetry VALUES (?, ?, ?, ?, ?, ?, ?)",
                        (run_id, tick, state.time, flow_id, float(val), flow_id, "flow")
                    )
                for aux_id, val in state.auxiliary_values.items():
                    conn.execute(
                        "INSERT INTO sim_telemetry VALUES (?, ?, ?, ?, ?, ?, ?)",
                        (run_id, tick, state.time, aux_id, float(val), aux_id, "auxiliary")
                    )
            
            run.metrics_summary = {
                "ticks_run": ticks_count,
                "final_stocks": {k: float(v) for k, v in state.stock_values.items()}
            }
            
        elif run_in.run_type == "agent":
            # 2. Parse Agent Config
            agents_list = []
            for a_data in (project.agents or []):
                agents_list.append(Agent(**a_data))
                
            rules_list = []
            for r_data in (project.rules or []):
                rules_list.append(Rule(**r_data))
                
            globals_dict = project.global_variables or {}
            
            state = AgentEngine.initialize_simulation(agents_list, globals_dict)
            ticks_count = 30
            
            # Log initial states to DuckDB
            for a_id, agent in state.agents.items():
                for res_name, res_val in agent.resources.items():
                    conn.execute(
                        "INSERT INTO agent_states VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                        (run_id, 0, a_id, agent.name, agent.role, agent.agent_type, res_name, float(res_val))
                    )
            for var_name, var_val in state.global_variables.items():
                if isinstance(var_val, (int, float)):
                    conn.execute(
                        "INSERT INTO sim_telemetry VALUES (?, ?, ?, ?, ?, ?, ?)",
                        (run_id, 0, 0.0, var_name, float(var_val), "global", "global")
                    )
            
            for tick in range(1, ticks_count + 1):
                state = AgentEngine.step(state, rules_list)
                
                # Write state to DuckDB
                for a_id, agent in state.agents.items():
                    for res_name, res_val in agent.resources.items():
                        conn.execute(
                            "INSERT INTO agent_states VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                            (run_id, tick, a_id, agent.name, agent.role, agent.agent_type, res_name, float(res_val))
                        )
                for var_name, var_val in state.global_variables.items():
                    if isinstance(var_val, (int, float)):
                        conn.execute(
                            "INSERT INTO sim_telemetry VALUES (?, ?, ?, ?, ?, ?, ?)",
                            (run_id, tick, float(tick), var_name, float(var_val), "global", "global")
                        )
            
            # Summarize results
            run.metrics_summary = {
                "ticks_run": ticks_count,
                "agent_count": len(state.agents),
                "final_globals": {k: float(v) for k, v in state.global_variables.items() if isinstance(v, (int, float))}
            }
            
        elif run_in.run_type == "monte_carlo":
            # 3. Running Monte Carlo Simulation
            variables_raw = project.global_variables or {}
            mc_variables = {}
            for k, v in variables_raw.items():
                # Form simple distribution boundaries
                mc_variables[k] = DistributionParam(
                    dist_type="uniform",
                    params={"low": float(v) * 0.75, "high": float(v) * 1.25}
                )
                
            # Default target outputs
            expressions = {}
            if project.domain == "startup":
                expressions = {"projected_runway": "cash_burn_rate * 1.5", "burn_impact": "cash_burn_rate"}
            else:
                first_var = list(variables_raw.keys())[0] if variables_raw else "var"
                expressions = {f"{first_var}_ratio": f"{first_var} * 1.2"}

            config = MonteCarloConfig(
                iterations=500,
                variables=mc_variables,
                target_expressions=expressions
            )
            
            mc_result = MonteCarloEngine.run_simulation(config)
            
            # Log summary statistics
            run.metrics_summary = {
                "iterations": config.iterations,
                "summaries": {k: v.model_dump() for k, v in mc_result.summaries.items()}
            }
            
        elif run_in.run_type == "des":
            # 4. Discrete Event Simulation Engine
            engine = DESEngine()
            # Simple queue handler mock
            engine.register_handler(
                "arrival",
                lambda evt, st: [
                    Event(id=f"evt_{uuid.uuid4().hex[:6]}", time=evt.time + 4.0, event_type="service"),
                    Event(id=f"evt_{uuid.uuid4().hex[:6]}", time=evt.time + 8.0, event_type="arrival")
                ]
            )
            engine.register_handler(
                "service",
                lambda evt, st: []
            )
            
            initial_events = [Event(id="init", time=0.0, event_type="arrival")]
            state = engine.initialize_simulation(initial_events, {"processed": 0})
            final_state = engine.run_until(state, max_time=100.0)
            
            # Write history logs to DuckDB
            for event in final_state.history:
                conn.execute(
                    "INSERT INTO sim_telemetry VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (run_id, int(event["time"]), float(event["time"]), event["event_type"], 1.0, event["event_id"], "event")
                )
                
            run.metrics_summary = {
                "events_processed": final_state.processed_events_count,
                "total_time": final_state.current_time
            }
            
        else:
            raise HTTPException(status_code=400, detail="Invalid run_type parameter")

        run.status = "completed"
        run.completed_at = datetime.datetime.utcnow()
        db.commit()
        db.refresh(run)
        return run
        
    except Exception as e:
        run.status = "failed"
        run.completed_at = datetime.datetime.utcnow()
        run.metrics_summary = {"error": str(e)}
        db.commit()
        raise HTTPException(status_code=500, detail=f"Simulation run execution failed: {str(e)}")
    finally:
        conn.close()

# Fetch run metadata
@router.get("/runs/{run_id}", response_model=RunResponse)
def get_run(run_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    run = db.query(SimulationRun).filter(SimulationRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Simulation run not found")
    return run

# Fetch historical time-series telemetry logs from DuckDB
@router.get("/runs/{run_id}/telemetry")
def get_run_telemetry(run_id: str, current_user: User = Depends(get_current_user)):
    conn = DuckDBManager.get_connection()
    try:
        # Fetch telemetry
        telemetry_rows = conn.execute(
            "SELECT tick, time, metric_name, metric_value, entity_id, entity_type FROM sim_telemetry WHERE run_id = ? ORDER BY tick, metric_name",
            (run_id,)
        ).fetchall()
        
        # Fetch agent resources if any
        agent_rows = conn.execute(
            "SELECT tick, agent_id, agent_name, role, agent_type, resource_name, resource_value FROM agent_states WHERE run_id = ? ORDER BY tick, agent_id",
            (run_id,)
        ).fetchall()
        
        telemetry = []
        for r in telemetry_rows:
            telemetry.append({
                "tick": r[0],
                "time": r[1],
                "metric_name": r[2],
                "metric_value": r[3],
                "entity_id": r[4],
                "entity_type": r[5]
            })
            
        agents = []
        for r in agent_rows:
            agents.append({
                "tick": r[0],
                "agent_id": r[1],
                "agent_name": r[2],
                "role": r[3],
                "agent_type": r[4],
                "resource_name": r[5],
                "resource_value": r[6]
            })
            
        return {"run_id": run_id, "telemetry": telemetry, "agent_states": agents}
    finally:
        conn.close()

# Explainable AI report generator
@router.get("/runs/{run_id}/explain")
def get_run_explanation(run_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    run = db.query(SimulationRun).filter(SimulationRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Simulation run not found")

    conn = DuckDBManager.get_connection()
    try:
        # Pull simulation telemetry to pass to XAI analyzer
        rows = conn.execute(
            "SELECT tick, time, metric_name, metric_value FROM sim_telemetry WHERE run_id = ? ORDER BY tick",
            (run_id,)
        ).fetchall()
        
        history = []
        for r in rows:
            history.append({
                "tick": r[0],
                "time": r[1],
                r[2]: r[3]
            })
            
        report = ExplainableAIService.analyze_simulation(history, [], [])
        return report
    finally:
        conn.close()

# Post-run Counterfactual solver
@router.post("/runs/{run_id}/counterfactual", response_model=CounterfactualResult)
def solve_counterfactual(
    run_id: str,
    query: CounterfactualQuery,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    run = db.query(SimulationRun).filter(SimulationRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Simulation run not found")

    project = db.query(SimulationProject).filter(SimulationProject.id == run.project_id).first()
    
    # Configure parameter search bounds based on current global variables
    current_vars = project.global_variables or {}
    bounds = {}
    for k, v in current_vars.items():
        if isinstance(v, (int, float)):
            bounds[k] = (float(v) * 0.2, float(v) * 2.0)

    # Simulator runner simulation callback function
    def run_callback(params: Dict[str, float]) -> Dict[str, float]:
        # Simple mathematical proxy of variable impacts
        out = {}
        for k, v in params.items():
            out[k] = v
        # Add basic interactions
        if "market_demand" in params:
            out["revenue"] = params["market_demand"] * 1000.0
            out["profit"] = out["revenue"] - 400.0
        return out

    result = ExplainableAIService.generate_counterfactual(
        history=[],
        query=query,
        parameter_bounds=bounds,
        simulation_runner=run_callback
    )
    return result

# AI Assistant natural language query router
@router.post("/projects/{project_id}/assistant")
async def ask_assistant(
    project_id: str, 
    req: AssistantRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project = db.query(SimulationProject).filter(SimulationProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    current_params = {}
    for k, v in (project.global_variables or {}).items():
        if isinstance(v, (int, float)):
            current_params[k] = float(v)

    response = await llm_service.query_assistant(req.prompt, current_params)
    
    # If parameter adjustments are requested, we execute them in the DB
    if response.parameter_adjustments:
        updated_globals = dict(project.global_variables or {})
        updated_globals.update(response.parameter_adjustments)
        project.global_variables = updated_globals
        db.commit()
        
    return response

# Genetic Algorithm Optimization
@router.post("/projects/{project_id}/optimize", response_model=OptimizationResult)
def run_optimization(
    project_id: str,
    req: OptimizationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project = db.query(SimulationProject).filter(SimulationProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Objective function evaluator callback
    def fitness_evaluator(params: Dict[str, float]) -> float:
        # Simple proxy representation: evaluate profit target
        score = 0.0
        for k, v in params.items():
            score += v
        if "market_demand" in params:
            score += params["market_demand"] * 50.0
        return score

    result = OptimizationService.genetic_algorithm(req.config, fitness_evaluator)
    return result
