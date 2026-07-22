import numpy as np
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class DistributionParam(BaseModel):
    dist_type: str  # "normal", "uniform", "triangular", "exponential", "lognormal", "poisson", "binomial", "constant"
    params: Dict[str, float] = Field(default_factory=dict)
    # normal: mean, std
    # uniform: low, high
    # triangular: left, mode, right
    # exponential: scale
    # lognormal: mean, sigma
    # poisson: lam
    # binomial: n, p
    # constant: value

class MonteCarloConfig(BaseModel):
    iterations: int = 1000
    variables: Dict[str, DistributionParam] = Field(default_factory=dict)
    target_expressions: Dict[str, str] = Field(default_factory=dict)
    # e.g., {"profit": "revenue - expenses", "roi": "profit / investment"}

class TrialResult(BaseModel):
    inputs: Dict[str, float]
    outputs: Dict[str, float]

class MonteCarloSummary(BaseModel):
    target_name: str
    mean: float
    std: float
    min_val: float
    max_val: float
    percentiles: Dict[str, float]  # "p10", "p50", "p90", "p25", "p75"
    histogram: Dict[str, List[float]]  # "bins" (boundaries) and "counts"

class MonteCarloResult(BaseModel):
    trials: List[TrialResult] = Field(default_factory=list)
    summaries: Dict[str, MonteCarloSummary] = Field(default_factory=dict)

class MonteCarloEngine:
    @staticmethod
    def sample_distribution(dist_type: str, params: Dict[str, float], size: int) -> np.ndarray:
        """
        Generates random samples for a given distribution type.
        """
        dtype = dist_type.lower()
        if dtype == "constant":
            val = params.get("value", 0.0)
            return np.full(size, val)
        elif dtype == "normal":
            return np.random.normal(params.get("mean", 0.0), params.get("std", 1.0), size)
        elif dtype == "uniform":
            return np.random.uniform(params.get("low", 0.0), params.get("high", 1.0), size)
        elif dtype == "triangular":
            return np.random.triangular(
                params.get("left", 0.0), 
                params.get("mode", 0.5), 
                params.get("right", 1.0), 
                size
            )
        elif dtype == "exponential":
            return np.random.exponential(params.get("scale", 1.0), size)
        elif dtype == "lognormal":
            return np.random.lognormal(params.get("mean", 0.0), params.get("sigma", 1.0), size)
        elif dtype == "poisson":
            return np.random.poisson(params.get("lam", 1.0), size).astype(float)
        elif dtype == "binomial":
            return np.random.binomial(int(params.get("n", 10)), params.get("p", 0.5), size).astype(float)
        else:
            raise ValueError(f"Unsupported distribution type: {dist_type}")

    @classmethod
    def run_simulation(cls, config: MonteCarloConfig, seed: Optional[int] = None) -> MonteCarloResult:
        if seed is not None:
            np.random.seed(seed)
            
        n = config.iterations
        sampled_inputs: Dict[str, np.ndarray] = {}
        
        # Sample all variables
        for name, param in config.variables.items():
            sampled_inputs[name] = cls.sample_distribution(param.dist_type, param.params, n)
            
        trials = []
        outputs_arrays: Dict[str, np.ndarray] = {k: np.zeros(n) for k in config.target_expressions.keys()}
        
        # Compile expressions
        compiled_exprs = {}
        for target, expr in config.target_expressions.items():
            # Basic validation
            if "__" in expr or "import" in expr:
                raise ValueError("Unsafe expression in Monte Carlo target.")
            compiled_exprs[target] = compile(expr, f"<mc_{target}>", "eval")

        # Evaluate targets for all trials
        # For performance, we can evaluate row-by-row or using eval with arrays if they are vectorized.
        # Let's evaluate using row-by-row to ensure safe dict lookup/compatibility.
        for i in range(n):
            row_inputs = {var_name: float(sampled_inputs[var_name][i]) for var_name in config.variables.keys()}
            row_outputs = {}
            
            # Context for evaluation includes numpy/math functions if needed, and variables
            eval_context = {
                "__builtins__": None,
                "abs": abs, "min": min, "max": max, "round": round,
                "pow": pow, "sum": sum,
            }
            eval_context.update(row_inputs)
            
            for target, compiled in compiled_exprs.items():
                try:
                    val = float(eval(compiled, {"__builtins__": None}, eval_context))
                except Exception:
                    val = 0.0
                row_outputs[target] = val
                outputs_arrays[target][i] = val
                eval_context[target] = val  # Allows chaining outputs
                
            # Store detail for first 100 trials to avoid bloating database/memory
            if i < 200:
                trials.append(TrialResult(inputs=row_inputs, outputs=row_outputs))

        # Compute summary statistics
        summaries = {}
        for target, arr in outputs_arrays.items():
            if len(arr) == 0:
                continue
            
            mean_val = float(np.mean(arr))
            std_val = float(np.std(arr))
            min_val = float(np.min(arr))
            max_val = float(np.max(arr))
            
            # Compute percentiles
            pcts = np.percentile(arr, [10, 25, 50, 75, 90])
            percentiles_dict = {
                "p10": float(pcts[0]),
                "p25": float(pcts[1]),
                "p50": float(pcts[2]),
                "p75": float(pcts[3]),
                "p90": float(pcts[4]),
            }
            
            # Compute histogram
            counts, bins = np.histogram(arr, bins=20)
            histogram_dict = {
                "bins": [float(b) for b in bins],
                "counts": [float(c) for c in counts]
            }
            
            summaries[target] = MonteCarloSummary(
                target_name=target,
                mean=mean_val,
                std=std_val,
                min_val=min_val,
                max_val=max_val,
                percentiles=percentiles_dict,
                histogram=histogram_dict
            )
            
        return MonteCarloResult(trials=trials, summaries=summaries)
