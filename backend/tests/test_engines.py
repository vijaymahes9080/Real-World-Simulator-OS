import pytest
from app.services.rule_engine import Rule, RuleEngine
from app.engines.agent_engine import AgentEngine, Agent, AgentSimulationState
from app.engines.system_dynamics import SystemDynamicsEngine, SDModel, SDStock, SDFlow, SDAuxiliary
from app.engines.monte_carlo_engine import MonteCarloEngine, MonteCarloConfig, DistributionParam

def test_rule_engine_sandboxing():
    # Safe expression
    context = {"agent": {"budget": 1000}, "global": {"market_status": "bull"}}
    cond = "agent['budget'] > 500 and global['market_status'] == 'bull'"
    assert RuleEngine.evaluate_condition(cond, context) is True

    # Action modification
    action = "agent.budget -= 300"
    new_context = RuleEngine.execute_action(action, context)
    assert new_context["agent"]["budget"] == 700

    # Unsafe expression block
    with pytest.raises(ValueError):
        RuleEngine.sanitize_expression("import os; os.system('echo exploit')")

def test_agent_engine_step():
    agents = [
        Agent(
            id="test_agent_1",
            name="Test Rep",
            role="sales",
            agent_type="employee",
            resources={"salary": 100.0, "energy": 5.0}
        )
    ]
    rules = [
        Rule(
            id="r1",
            name="Deplete Energy",
            condition="agent.is_active == True and agent.resources['salary'] < 150",
            # Decreases energy by 1 via built-in depletion check, let's test rule action too
            action="agent.resources['salary'] += 50",
            priority=10
        )
    ]
    state = AgentEngine.initialize_simulation(agents, {"global_val": 10})
    next_state = AgentEngine.step(state, rules)
    
    # Check that salary was incremented by rule and energy depleted by aging
    updated_agent = next_state.agents["test_agent_1"]
    assert updated_agent.resources["salary"] == 150.0
    assert updated_agent.resources["energy"] == 4.0

def test_system_dynamics_integration():
    # Define a simple tank model: Inflow fills the tank stock
    stocks = {
        "tank": SDStock(id="tank", name="Water Tank", initial_value=50.0, inflows=["inflow"], outflows=[])
    }
    flows = {
        "inflow": SDFlow(id="inflow", name="Water Inflow", expression="constants.inflow_rate")
    }
    model = SDModel(
        stocks=stocks,
        flows=flows,
        auxiliaries={},
        constants={"inflow_rate": 5.0}
    )
    
    # Run 2 steps with dt=2.0 (total time delta = 4.0)
    # Expected: tank = 50.0 + (5.0 * 2.0) = 60.0 after step 1
    # tank = 60.0 + (5.0 * 2.0) = 70.0 after step 2
    state = SystemDynamicsEngine.initialize_state(model)
    state = SystemDynamicsEngine.step(model, state, dt=2.0)
    assert state.stock_values["tank"] == 60.0
    state = SystemDynamicsEngine.step(model, state, dt=2.0)
    assert state.stock_values["tank"] == 70.0

def test_monte_carlo_distribution():
    variables = {
        "variable_x": DistributionParam(dist_type="uniform", params={"low": 10.0, "high": 20.0})
    }
    config = MonteCarloConfig(
        iterations=100,
        variables=variables,
        target_expressions={"output_metric": "variable_x * 2.0"}
    )
    
    result = MonteCarloEngine.run_simulation(config, seed=42)
    summary = result.summaries["output_metric"]
    
    # The output value should range from 20 to 40 (mean around 30)
    assert 20.0 <= summary.mean <= 40.0
    assert summary.min_val >= 20.0
    assert summary.max_val <= 40.0
