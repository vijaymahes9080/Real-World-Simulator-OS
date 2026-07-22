import pytest
from app.services.optimization import OptimizationService, OptimizationConfig, OptimizationParam

def test_genetic_algorithm_prescriptive_solver():
    config = OptimizationConfig(
        parameters=[
            OptimizationParam(name="market_demand", min_value=0.5, max_value=2.0),
            OptimizationParam(name="burn_rate", min_value=5000.0, max_value=25000.0)
        ],
        objective_expression="market_demand * 1000 - burn_rate * 0.1",
        target_objective="maximize",
        population_size=10,
        generations=5,
        mutation_rate=0.1
    )

    def dummy_eval(p):
        return p["market_demand"] * 1000 - p["burn_rate"] * 0.1

    result = OptimizationService.genetic_algorithm(config, dummy_eval)

    assert result.best_parameters is not None
    assert "market_demand" in result.best_parameters
    assert len(result.fitness_history) == 5
    assert len(result.prescriptive_recommendations) > 0
