# 🌐 Real-World Simulator OS

<div align="center">

![Real-World Simulator OS](https://img.shields.io/badge/version-1.0.0-blue?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)
![React](https://img.shields.io/badge/React-18.2-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-5.0-3178C6?style=for-the-badge&logo=typescript&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green?style=for-the-badge)

**Universal Decision Intelligence & Digital Twin Simulation Platform**

*Simulate. Predict. Prescribe. Act.*

[🚀 Quick Start](#-quick-start) • [🏗️ Architecture](#️-architecture) • [🧩 Features](#-features) • [📦 Templates](#-simulation-templates) • [🤝 Contributing](#-contributing)

</div>

---

## 🎯 What is Real-World Simulator OS?

**Real-World Simulator OS** is an open-source, AI-powered platform that creates **living digital twins** of real-world systems. Model a startup's cash runway, a city's power grid, a hospital's ICU capacity, or a global supply chain — then run Monte Carlo simulations, deploy autonomous AI agents, and get prescriptive policy recommendations — all in real time.

> Think of it as a **flight simulator for decision makers**: a safe environment to crash test your strategy before committing to it in reality.

---

## ✨ Features

### 🤖 Autonomous Multi-Agent AI Engine
- Deploy virtual executive agents (**CFO, COO, Risk Manager, Logistics Lead**) that autonomously negotiate crisis responses.
- Real-time debate feeds with consensus confidence scoring.
- Inject custom crisis directives into the agent loop interactively.

### 🌌 Spatial 3D Digital Twin Viewport
- Interactive 3D particle graph canvas with orbital rotation controls.
- Glowing energy pulse animations along live connections.
- Node status indicators: **Nominal / Warning / Critical Stress**.

### ⏳ Scenario Time Machine & Storytelling Mode
- Scrub simulation ticks forward and backward on a timeline slider.
- Create **counterfactual branch points** (bookmarks) to test alternative decision paths.
- Synthesized Web Audio sound cues for state transitions.

### 🛰️ Live IoT & Sensor Data Ingestor
- Real-world telemetry polling via `/api/sensors/live`.
- Streams: Ambient temperature, grid frequency, solar irradiance, city traffic, port backlog, and hospital ICU occupancy.
- Auto-sync at configurable intervals or manual poll.

### 🧠 Generative Prescriptive Policy Optimizer
- Genetic algorithm solver with SHAP feature correlation attribution.
- Generates actionable **Prescriptive AI Policy Cards** with ranked parameter recommendations.
- Multi-objective optimization with convergence visualization.

### 🌍 12 Pre-Built Domain Simulation Kits
| Kit | Domain |
|-----|--------|
| Startup Growth & Run Rate | Entrepreneurship |
| Smart City Power Grid | Urban Infrastructure |
| Crop Yield & Agriculture | AgriTech |
| University Campus Dynamics | Education |
| Retail Inventory Optimization | Commerce |
| Hospital Emergency Triage | Healthcare |
| Global Supply Chain | Logistics |
| Disaster Response & Evacuation | Emergency Management |
| ⭐ Climate Resilience & Food Security | Climate Tech |
| ⭐ Smart Grid & EV Infrastructure | Energy |
| ⭐ Maritime Supply Chain Fragility | Global Trade |
| ⭐ Pandemic Bed Allocation | Public Health |

> ⭐ = New in Innovation Suite v1.0

---

## 🏗️ Architecture

```
Real-World Simulator OS/
├── backend/                    # Python FastAPI Server
│   ├── app/
│   │   ├── api/               # REST API Routes (auth, projects, runs)
│   │   ├── core/              # Security & Auth (JWT)
│   │   ├── db/                # SQLite via SQLAlchemy
│   │   ├── engines/           # Simulation Engines
│   │   │   ├── agent_engine.py         # Multi-Agent Behavioral Simulation
│   │   │   ├── des_engine.py           # Discrete Event Simulation
│   │   │   ├── monte_carlo_engine.py   # Probabilistic Monte Carlo
│   │   │   └── system_dynamics.py      # System Dynamics (Stocks & Flows)
│   │   ├── services/          # AI & Platform Services
│   │   │   ├── digital_twin.py         # Digital Twin Synchronizer
│   │   │   ├── explainable_ai.py       # XAI / SHAP Analysis
│   │   │   ├── forecasting.py          # Predictive Forecasting
│   │   │   ├── knowledge_graph.py      # Causal Relationship Graph
│   │   │   ├── llm_service.py          # LLM AI Co-Pilot
│   │   │   ├── optimization.py         # GA Optimizer + Prescriptive Engine
│   │   │   ├── predefined_templates.py # 12 Domain Simulation Kits
│   │   │   ├── rule_engine.py          # Business Rule Execution
│   │   │   └── sensor_ingestion.py     # Live IoT Telemetry Ingestor ⭐
│   │   └── main.py            # FastAPI App + WebSocket Streamer
│   ├── tests/                 # Pytest Suite
│   └── requirements.txt
│
├── frontend/                  # React + TypeScript + Vite UI
│   ├── src/
│   │   ├── components/        # Innovation Suite Components ⭐
│   │   │   ├── SpatialCanvas.tsx       # 3D Digital Twin Viewport
│   │   │   ├── MultiAgentHub.tsx       # Autonomous Agent Debate Feed
│   │   │   ├── TimeMachineScrubber.tsx # Scenario Timeline Scrubber
│   │   │   └── LiveSensorFeed.tsx      # Live IoT Telemetry Widget
│   │   ├── pages/             # Application Pages
│   │   │   ├── Dashboard.tsx           # Main Simulation Console
│   │   │   ├── SystemBuilder.tsx       # Architecture Node Designer
│   │   │   ├── ScenarioExplorer.tsx    # Monte Carlo Scenario Analysis
│   │   │   ├── KnowledgeGraphPage.tsx  # Causal Graph Viewer
│   │   │   └── OptimizationPage.tsx    # GA Optimizer + Policy Cards
│   │   └── hooks/
│   │       └── useStore.ts    # Zustand Global State
│   └── package.json
│
├── scripts/                   # Startup Scripts
│   ├── setup_windows.ps1      # Windows Setup
│   ├── setup_unix.sh          # Unix/macOS Setup
│   ├── run_windows.ps1        # Windows Runner
│   └── run_unix.sh            # Unix/macOS Runner
│
├── composer.json              # Project Metadata
├── .gitignore
├── LICENSE
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites
- Python **3.10+**
- Node.js **18+**
- npm **9+**

### Windows
```powershell
# Clone the repository
git clone https://github.com/vijaymahes9080/Real-World-Simulator-OS.git
cd "Real-World Simulator OS"

# Run automated setup
./scripts/setup_windows.ps1

# Start both servers
./scripts/run_windows.ps1
```

### Linux / macOS
```bash
git clone https://github.com/vijaymahes9080/Real-World-Simulator-OS.git
cd "Real-World Simulator OS"

chmod +x scripts/setup_unix.sh scripts/run_unix.sh
./scripts/setup_unix.sh
./scripts/run_unix.sh
```

### Manual Setup
```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

**Access the application:**
- 🖥️ **Frontend UI**: http://localhost:5173
- 📡 **Backend API**: http://localhost:8000
- 📚 **API Docs (Swagger)**: http://localhost:8000/docs

**Default login credentials:**
| Username | Password | Role |
|----------|----------|------|
| `admin` | `admin123` | Admin |
| `analyst` | `analyst123` | Analyst |

---

## 🔌 API Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/login` | POST | Authenticate and receive JWT token |
| `/api/projects` | GET | List all simulation projects |
| `/api/projects/{id}` | GET | Get project details |
| `/api/projects/{id}/run` | POST | Start simulation run |
| `/api/projects/{id}/optimize` | POST | Run GA optimizer |
| `/api/sensors/live` | GET | Live IoT telemetry stream |
| `/api/ws/simulate` | WebSocket | Real-time simulation data stream |

---

## 🧪 Running Tests

```bash
cd backend
python -m pytest tests/ -v
```

---

## 🔧 Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | React 18, TypeScript, Vite, Tailwind CSS |
| **Charting** | Chart.js, React-Chartjs-2 |
| **State** | Zustand |
| **Graph** | ReactFlow |
| **Backend** | Python 3.12, FastAPI |
| **Simulation** | NumPy, SciPy, SimPy |
| **AI/ML** | Custom GA Solver, SHAP Attribution, LLM Integration |
| **Database** | SQLite (SQLAlchemy ORM) |
| **Auth** | JWT (python-jose) |
| **Real-Time** | WebSockets (asyncio) |
| **3D Viewport** | HTML5 Canvas (2.5D projection engine) |

---

## 🤝 Contributing

Contributions are welcome! Here's how:

1. Fork the repository.
2. Create your feature branch: `git checkout -b feat/my-new-feature`
3. Commit your changes: `git commit -m 'feat: add some feature'`
4. Push to the branch: `git push origin feat/my-new-feature`
5. Submit a Pull Request.

### Commit Convention
This project follows [Conventional Commits](https://www.conventionalcommits.org/):
- `feat:` — New feature
- `fix:` — Bug fix
- `docs:` — Documentation updates
- `chore:` — Build/tooling changes

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**Vijay Mahes**
- 📧 Email: [Vijaypradhap2004@gmail.com](mailto:Vijaypradhap2004@gmail.com)
- 🐙 GitHub: [@vijaymahes9080](https://github.com/vijaymahes9080)

---

<div align="center">

Made with ❤️ by Vijay Mahes · Star ⭐ if you find it useful!

</div>
