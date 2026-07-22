import pytest
from app.services.sensor_ingestion import sensor_service

def test_live_telemetry_structure():
    telemetry = sensor_service.get_live_telemetry()
    assert "timestamp" in telemetry
    assert "status" in telemetry
    assert telemetry["status"] == "connected"
    assert "metrics" in telemetry
    assert "stream_sources" in telemetry

def test_live_telemetry_metrics_range():
    telemetry = sensor_service.get_live_telemetry()
    metrics = telemetry["metrics"]
    assert 15.0 <= metrics["ambient_temperature_c"] <= 35.0
    assert 49.0 <= metrics["power_grid_frequency_hz"] <= 51.0
    assert metrics["port_container_queue_units"] >= 0
    assert 0.0 <= metrics["hospital_icu_occupancy_pct"] <= 100.0

def test_sensor_stream_sources():
    telemetry = sensor_service.get_live_telemetry()
    sources = telemetry["stream_sources"]
    assert len(sources) >= 4
    for src in sources:
        assert src["status"] == "ONLINE"
        assert src["latency_ms"] > 0
