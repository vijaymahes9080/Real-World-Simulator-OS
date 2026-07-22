import asyncio
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from app.db.session import engine, Base
from app.api import auth, projects, runs

# Create SQLite tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Real-World Simulator OS",
    description="Universal Decision Intelligence & Digital Twin Simulation Platform",
    version="1.0.0"
)

# Enable CORS for frontend Vite development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.services.sensor_ingestion import sensor_service

# Register REST Routers
app.include_router(auth.router, prefix="/api")
app.include_router(projects.router, prefix="/api")
app.include_router(runs.router, prefix="/api")

@app.get("/")
def read_root():
    return {
        "status": "online",
        "service": "Real-World Simulator OS Backend",
        "api_docs": "/docs"
    }

@app.get("/api/sensors/live")
def get_live_sensors():
    """Returns live IoT sensor telemetry for real-time Digital Twin synchronization."""
    return sensor_service.get_live_telemetry()

# WebSockets Server for Real-Time Simulation Streaming
@app.websocket("/api/ws/simulate")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    # Session state variables
    project_id = None
    run_type = None
    is_running = False
    tick_delay = 0.5  # seconds
    
    # Engine state
    tick = 0
    sim_state = None
    
    try:
        while True:
            # Check for messages from client with a small timeout or non-blocking read
            # Since asyncio.wait_for is used, we can check for incoming commands and run the simulation loop concurrently.
            try:
                # Listen for commands from client
                data = await asyncio.wait_for(websocket.receive_text(), timeout=0.05)
                command = json.loads(data)
                action = command.get("action")
                
                if action == "start":
                    project_id = command.get("project_id")
                    run_type = command.get("run_type", "system_dynamics")
                    tick = 0
                    is_running = True
                    # In a production layout we'd fetch project config and initialize the engine state.
                    # For simplicity, we initialize a mock stream matching the domain of project.
                    await websocket.send_text(json.dumps({
                        "event": "started",
                        "project_id": project_id,
                        "run_type": run_type,
                        "tick": tick
                    }))
                    
                elif action == "pause":
                    is_running = False
                    await websocket.send_text(json.dumps({"event": "paused", "tick": tick}))
                    
                elif action == "resume":
                    is_running = True
                    await websocket.send_text(json.dumps({"event": "resumed", "tick": tick}))
                    
                elif action == "step":
                    tick += 1
                    # Stream next single tick state
                    sim_frame = generate_mock_sim_frame(project_id, tick)
                    await websocket.send_text(json.dumps({
                        "event": "tick",
                        "tick": tick,
                        "data": sim_frame
                    }))
                    
                elif action == "adjust":
                    adjustments = command.get("variables", {})
                    await websocket.send_text(json.dumps({
                        "event": "adjusted",
                        "variables": adjustments
                    }))
                    
                elif action == "stop":
                    is_running = False
                    tick = 0
                    await websocket.send_text(json.dumps({"event": "stopped"}))
                    
            except asyncio.TimeoutError:
                # No new commands received, progress simulation if active
                if is_running:
                    tick += 1
                    sim_frame = generate_mock_sim_frame(project_id, tick)
                    await websocket.send_text(json.dumps({
                        "event": "tick",
                        "tick": tick,
                        "data": sim_frame
                    }))
                    await asyncio.sleep(tick_delay)
                    
    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            await websocket.send_text(json.dumps({"event": "error", "message": str(e)}))
        except Exception:
            pass

def generate_mock_sim_frame(project_id: str, tick: int) -> dict:
    """
    Generates realistic dynamic metrics for WebSocket real-time visual demonstration.
    """
    import math
    import random
    
    # Calculate a sine wave-like growth pattern
    val_sin = math.sin(tick / 5.0)
    
    if project_id == "template_startup":
        cash = 500000.0 - (tick * 12000.0) + (max(0, tick - 10) * 25000.0)
        revenue = 5000.0 + (tick * 2200.0) + (random.random() * 800)
        burn = 15000.0 + (random.random() * 500)
        return {
            "metrics": {
                "Cash Reserves": cash,
                "Monthly Revenue": revenue,
                "Cash Burn Rate": burn
            },
            "alerts": [] if cash > 100000 else [{"severity": "warning", "message": "Reserves low! Runway under 6 months."}],
            "agent_positions": {
                "sales_1": {"deals_closed": tick // 2},
                "eng_1": {"bugs": max(0, 15 - tick // 3)}
            }
        }
    elif project_id == "template_smart_city":
        load = 2200.0 + (100.0 * val_sin) + (random.random() * 50)
        solar = max(0.0, 1000.0 * math.cos(tick / 4.0))
        grid = 100000.0 + solar - load
        return {
            "metrics": {
                "Grid Electricity": grid,
                "Solar Input": solar,
                "City Power Load": load
            },
            "alerts": [] if load < 2400.0 else [{"severity": "info", "message": "Grid load approaching warning levels."}]
        }
    elif project_id == "template_crop_yield":
        moisture = max(0.0, 40.0 - (tick * 0.8) + (20.0 * max(0.0, math.sin(tick / 2.0))))
        biomass = 1.0 + (tick * 0.4) + (random.random() * 0.05)
        return {
            "metrics": {
                "Soil Moisture (%)": moisture,
                "Wheat Biomass (kg)": biomass,
                "Precipitation (mm)": 5.0 if moisture > 35.0 else 0.2
            },
            "alerts": [] if moisture > 15.0 else [{"severity": "critical", "message": "Critical moisture level: crops wilting!"}]
        }
    elif project_id == "template_climate_agri":
        gw = max(10.0, 85.0 - (tick * 0.9) + (15.0 * val_sin))
        yield_idx = min(100.0, 45.0 + (tick * 1.5) - (5.0 if gw < 50 else 0))
        return {
            "metrics": {"Groundwater Level (m)": gw, "Crop Yield Index": yield_idx, "Ambient Temp (°C)": 32.0 + (tick * 0.2)},
            "alerts": [] if gw > 40.0 else [{"severity": "critical", "message": "Aquifer depletion warning! Crop stress detected."}],
            "agent_messages": [{"sender": "Agronomist AI", "role": "CFO", "content": f"Tick {tick}: Recommending drip irrigation transition."}]
        }
    elif project_id == "template_smart_grid":
        load = 180.0 + (40.0 * val_sin) + (random.random() * 5.0)
        battery = max(0.0, 450.0 - (tick * 5.0) + (12.0 * max(0.0, math.cos(tick / 3.0))))
        return {
            "metrics": {"EV Fleet Demand (MW)": load, "Grid Storage Reserve (MWh)": battery, "Frequency (Hz)": 50.0 + (val_sin * 0.04)},
            "alerts": [] if load < 210.0 else [{"severity": "warning", "message": "Peak EV fast-charging draw detected!"}],
            "agent_messages": [{"sender": "Grid Controller AI", "role": "COO", "content": f"Tick {tick}: Throttling commercial charger rates by 15%."}]
        }
    elif project_id == "template_supply_chain_fragility":
        queue = max(10, int(8500 + (tick * 120) - (max(0, tick - 5) * 80)))
        lead_time = round(18.0 + (tick * 0.4), 1)
        return {
            "metrics": {"Port Container Backlog": queue, "Avg Freight Lead Time (Days)": lead_time, "Freight Rate ($/TEU)": 4200 + (tick * 110)},
            "alerts": [] if queue < 9000 else [{"severity": "warning", "message": "Port bottleneck escalating freight lead times."}],
            "agent_messages": [{"sender": "Logistics AI", "role": "Risk Manager", "content": f"Tick {tick}: Rerouting 3 vessels to secondary berth."}]
        }
    elif project_id == "template_hospital_response":
        icu = min(120, max(20, int(82 + (tick * 1.8) - (max(0, tick - 12) * 2.2))))
        er_wait = max(5, int(22 + (tick * 2.1)))
        return {
            "metrics": {"ICU Occupancy (Beds)": icu, "ER Wait Time (mins)": er_wait, "Ventilators in Use": min(45, int(icu * 0.35))},
            "alerts": [] if icu < 110 else [{"severity": "critical", "message": "ICU capacity near 95%! Trigger overflow protocol."}],
            "agent_messages": [{"sender": "Triage Chief AI", "role": "Medical Officer", "content": f"Tick {tick}: Transferring non-critical cases to step-down ward."}]
        }
    else:
        # Generic backup
        val = 100.0 + tick * 5.0 + (random.random() * 5.0)
        return {
            "metrics": {
                "Operational Status": val,
                "System Health Index": round(98.5 - (tick * 0.1), 2)
            },
            "alerts": [],
            "agent_messages": [{"sender": "System Autonomous Engine", "role": "System", "content": f"Tick {tick}: Baseline simulation run nominal."}]
        }
