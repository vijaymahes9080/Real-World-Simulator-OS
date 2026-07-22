# 🏗️ Real-World Simulator OS — Architecture Specification

This document details the core system architecture, engine design, data flow, and state synchronization of Real-World Simulator OS.

---

## 🧩 Architectural Layers

```
                               ┌────────────────────────────────┐
                               │   React 18 + TypeScript UI     │
                               │  (Zustand + Chart.js + R3F)    │
                               └───────────────┬────────────────┘
                                               │ WebSockets & REST
                               ┌───────────────▼────────────────┐
                               │       FastAPI Application      │
                               └───────────────┬────────────────┘
                                               │
               ┌───────────────────────────────┼───────────────────────────────┐
               │                               │                               │
    ┌──────────▼──────────┐         ┌──────────▼──────────┐         ┌──────────▼──────────┐
    │  System Dynamics    │         │ Monte Carlo Engine  │         │ Multi-Agent Engine  │
    │  (Stocks & Flows)   │         │ (SciPy Distributions)│         │ (Behavioral Rules)  │
    └──────────┬──────────┘         └──────────┬──────────┘         └──────────┬──────────┘
               │                               │                               │
               └───────────────────────────────┼───────────────────────────────┘
                                               │
                               ┌───────────────▼────────────────┐
                               │  DuckDB / SQLite State Layer   │
                               └────────────────────────────────┘
```

---

## ⚙️ Simulation Engines

### 1. System Dynamics Engine (`system_dynamics.py`)
- Solves ordinary differential equations representing stock-and-flow networks.
- Inflows add to stock levels while outflows deplete them.
- Time integration via Euler's method with configurable step sizes ($dt$).

### 2. Monte Carlo Engine (`monte_carlo_engine.py`)
- Runs 10,000+ parallel probabilistic trials across stochastic variable distributions.
- Computes Value at Risk (VaR 95%), Standard Deviation, and Confidence Bands.

### 3. Autonomous Multi-Agent Engine (`agent_engine.py`)
- Evaluates individual agent personality vectors (Big Five OCEAN traits).
- Executes behavioral rules and state transitions per tick.

### 4. Genetic Algorithm Prescriptive Solver (`optimization.py`)
- Evaluates parameter fitness using tournament selection and uniform crossover.
- Calculates SHAP feature importance via covariance matrix analysis.
