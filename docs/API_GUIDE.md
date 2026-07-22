# 📡 Real-World Simulator OS — API Reference Guide

Detailed specification for REST endpoints, WebSocket simulation protocol, and IoT telemetry streams.

---

## 🔐 Authentication API

### POST `/api/auth/login`
Authenticates a user and returns a Bearer JWT token.

**Request Body:**
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1Ni...",
  "token_type": "bearer",
  "role": "admin"
}
```

---

## 📦 Projects API

### GET `/api/projects`
Retrieves all configured simulation projects and preset domain kits.

### GET `/api/projects/{project_id}`
Retrieves layout nodes, global variables, rules, and system dynamics configuration for a specific project.

### POST `/api/projects/{project_id}/optimize`
Triggers the Genetic Algorithm solver to compute optimal parameters and SHAP feature importance.

**Request Body:**
```json
{
  "config": {
    "parameters": [
      { "name": "order_rate", "min_value": 50, "max_value": 250 }
    ],
    "objective_expression": "profit",
    "target_objective": "maximize",
    "population_size": 50,
    "generations": 30
  }
}
```

---

## 🛰️ Sensor Telemetry API

### GET `/api/sensors/live`
Returns real-time IoT sensor telemetry streams from physical digital twin devices.

**Response (200 OK):**
```json
{
  "timestamp": 1721612400,
  "status": "connected",
  "metrics": {
    "ambient_temperature_c": 24.8,
    "power_grid_frequency_hz": 50.02,
    "port_container_queue_units": 142,
    "hospital_icu_occupancy_pct": 74.2
  }
}
```

---

## ⚡ WebSocket Simulation API

### WS `/api/ws/simulate`
Real-time bidirectional WebSocket connection for streaming simulation ticks.

**Client Commands:**
- `{"action": "start", "project_id": "template_smart_grid"}`
- `{"action": "pause"}`
- `{"action": "step"}`
- `{"action": "stop"}`

**Server Events:**
```json
{
  "event": "tick",
  "tick": 42,
  "data": {
    "metrics": { "EV Fleet Demand (MW)": 184.2 },
    "alerts": [],
    "agent_messages": [{ "sender": "Grid Controller AI", "content": "Throttling charger rates." }]
  }
}
```
