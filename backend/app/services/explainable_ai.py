import numpy as np
from typing import Any, Dict, List, Optional
from pydantic import BaseModel

class CausalLink(BaseModel):
    source: str
    target: str
    impact: float
    description: str

class CounterfactualQuery(BaseModel):
    target_metric: str
    desired_value: float
    condition_type: str  # "at_least" or "at_most"

class CounterfactualResult(BaseModel):
    achievable: bool
    recommended_changes: Dict[str, float]
    expected_outcome: float
    confidence: float
    explanation: str

class ExplanationReport(BaseModel):
    confidence: float
    key_drivers: List[Dict[str, Any]]  # [{"variable": "v", "impact": 0.8, "direction": "positive"}]
    triggered_rules_count: int
    rule_insights: List[str]
    causal_chains: List[CausalLink]
    alternative_decisions: List[Dict[str, Any]]

class ExplainableAIService:
    @classmethod
    def analyze_simulation(
        cls, 
        history: List[Dict[str, Any]], 
        variables_config: List[str],
        rules_executed: List[Dict[str, Any]]
    ) -> ExplanationReport:
        """
        Analyzes the simulation history to generate a comprehensive explanation of results.
        """
        if not history:
            return ExplanationReport(
                confidence=0.5,
                key_drivers=[],
                triggered_rules_count=0,
                rule_insights=["No historical telemetry available."],
                causal_chains=[],
                alternative_decisions=[]
            )

        # 1. Driver/Sensitivity analysis using correlation in history
        # Create a grid of time points and variables
        steps = len(history)
        drivers = []
        
        # Extract variables from history
        keys = set()
        for h in history:
            keys.update(h.keys())
            # Support nested dict structure (like in system dynamics history)
            if "stocks" in h:
                keys.update(f"stock.{k}" for k in h["stocks"].keys())
            if "variables" in h:
                keys.update(f"variable.{k}" for k in h["variables"].keys())
                
        # Calculate correlations of all metrics against time or final target (e.g., if there's a stock or revenue metric)
        # For simplicity, we find the variables that changed the most or correlate with time
        time_series = np.array([h.get("time", idx) for idx, h in enumerate(history)])
        
        for key in keys:
            if key == "time":
                continue
                
            # Extract series
            series = []
            for h in history:
                if key.startswith("stock."):
                    s_key = key.split(".", 1)[1]
                    series.append(h.get("stocks", {}).get(s_key, 0.0))
                elif key.startswith("variable."):
                    v_key = key.split(".", 1)[1]
                    series.append(h.get("variables", {}).get(v_key, 0.0))
                else:
                    series.append(h.get(key, 0.0))
                    
            series_arr = np.array(series, dtype=float)
            std_val = np.std(series_arr)
            
            if std_val > 0:
                corr = np.corrcoef(time_series, series_arr)[0, 1]
                if not np.isnan(corr):
                    drivers.append({
                        "variable": key,
                        "impact": float(abs(corr)),
                        "direction": "increasing" if corr > 0 else "decreasing"
                    })
                    
        # Sort drivers by absolute impact
        drivers.sort(key=lambda x: x["impact"], reverse=True)
        
        # 2. Extract rule insights
        rule_insights = []
        for rule in rules_executed[:10]:
            rule_insights.append(
                f"Rule '{rule.get('name')}' triggered with condition '{rule.get('condition')}', modifying state: {rule.get('action')}"
            )
            
        if not rule_insights:
            rule_insights.append("No active rule modifications occurred; system progressed purely on deterministic rates.")

        # 3. Formulate alternative decisions
        alternatives = []
        if drivers:
            top_driver = drivers[0]["variable"]
            alternatives.append({
                "action": f"Adjust inputs affecting {top_driver}",
                "rationale": f"This variable is the strongest driver of system state over time.",
                "potential_impact": "High"
            })
        alternatives.append({
            "action": "Increase buffer capacity of constrained stocks",
            "rationale": "Mitigates flow bottlenecks during peak events.",
            "potential_impact": "Medium"
        })

        return ExplanationReport(
            confidence=0.85 if len(history) > 10 else 0.6,
            key_drivers=drivers[:5],
            triggered_rules_count=len(rules_executed),
            rule_insights=rule_insights,
            causal_chains=[
                CausalLink(
                    source="Rules Engine",
                    target="Agent Decision System",
                    impact=0.9,
                    description="Decisions are processed chronologically based on active rule criteria."
                )
            ],
            alternative_decisions=alternatives
        )

    @classmethod
    def generate_counterfactual(
        cls,
        history: List[Dict[str, Any]],
        query: CounterfactualQuery,
        parameter_bounds: Dict[str, Tuple[float, float]],
        simulation_runner: Callable[[Dict[str, float]], Dict[str, float]]
    ) -> CounterfactualResult:
        """
        Calculates counterfactual input values to satisfy a target condition.
        Uses a local grid search/heuristic optimizer over parameter bounds.
        """
        best_diff = float("inf")
        best_params = {}
        best_outcome = 0.0
        
        # Try random perturbation strategies to see if they satisfy the query
        # Let's perform a simple random search for 50 trials
        for _ in range(50):
            candidate_params = {}
            for name, bounds in parameter_bounds.items():
                candidate_params[name] = random_val = np.random.uniform(bounds[0], bounds[1])
                
            try:
                results = simulation_runner(candidate_params)
                outcome = results.get(query.target_metric, 0.0)
                
                # Check condition satisfaction
                satisfied = False
                if query.condition_type == "at_least":
                    satisfied = outcome >= query.desired_value
                    diff = max(0.0, query.desired_value - outcome)
                else:
                    satisfied = outcome <= query.desired_value
                    diff = max(0.0, outcome - query.desired_value)
                    
                if diff < best_diff:
                    best_diff = diff
                    best_params = candidate_params
                    best_outcome = outcome
            except Exception:
                continue

        achieved = best_diff == 0.0
        
        # Write explanatory notes
        if achieved:
            param_changes = ", ".join([f"{k} to {v:.2f}" for k, v in best_params.items()])
            explanation = f"Target was achieved! Setting parameters: {param_changes} produces an expected {query.target_metric} of {best_outcome:.2f}."
        else:
            explanation = f"Target was not fully reached in simulated boundaries. The closest result achieved was {best_outcome:.2f} (short by {best_diff:.2f})."

        return CounterfactualResult(
            achievable=achieved,
            recommended_changes=best_params,
            expected_outcome=best_outcome,
            confidence=0.9 if achieved else 0.4,
            explanation=explanation
        )
