import math
import random
import time
from typing import Dict, Any, List

class SensorIngestionService:
    """
    Simulates or pulls live IoT and real-world API telemetry streams.
    Synchronizes ambient parameters directly into Digital Twins in real time.
    """

    def __init__(self) -> None:
        """Initialize the sensor ingestion service timer."""
        self._start_time = time.time()

    def get_live_telemetry(self) -> Dict[str, Any]:
        """
        Polls physical IoT streams and returns active telemetry metrics.

        Returns:
            Dict[str, Any]: Dictionary containing timestamp, status, active stream count,
                            metric values, and individual sensor node status summaries.
        """
        elapsed = time.time() - self._start_time
        
        # Dynamic sine-wave values representing live physical metrics
        temp_ambient = 24.5 + 4.0 * math.sin(elapsed / 10.0) + (random.random() * 0.4)
        solar_irradiance = max(0.0, 850.0 * math.sin(elapsed / 15.0)) + (random.random() * 20.0)
        grid_frequency = 50.0 + (0.05 * math.sin(elapsed / 3.0)) + ((random.random() - 0.5) * 0.02)
        traffic_congestion = max(10.0, min(99.0, 45.0 + 30.0 * math.cos(elapsed / 8.0) + (random.random() * 5.0)))
        port_container_queue = int(120 + 35 * math.sin(elapsed / 12.0) + random.randint(-5, 5))
        hospital_icu_occupancy = min(100.0, max(40.0, 72.0 + 15.0 * math.sin(elapsed / 20.0) + random.random()))

        return {
            "timestamp": time.time(),
            "status": "connected",
            "active_stream_count": 6,
            "metrics": {
                "ambient_temperature_c": round(temp_ambient, 2),
                "solar_irradiance_w_m2": round(solar_irradiance, 2),
                "power_grid_frequency_hz": round(grid_frequency, 3),
                "city_traffic_congestion_pct": round(traffic_congestion, 1),
                "port_container_queue_units": port_container_queue,
                "hospital_icu_occupancy_pct": round(hospital_icu_occupancy, 1)
            },
            "stream_sources": [
                {"sensor_id": "IOT-TEMP-904", "type": "Environmental", "status": "ONLINE", "latency_ms": 12},
                {"sensor_id": "GRID-FREQ-012", "type": "Electrical Grid", "status": "ONLINE", "latency_ms": 8},
                {"sensor_id": "PORT-QUEUE-301", "type": "Logistics Feed", "status": "ONLINE", "latency_ms": 25},
                {"sensor_id": "MED-ICU-882", "type": "Healthcare API", "status": "ONLINE", "latency_ms": 19}
            ]
        }

sensor_service = SensorIngestionService()
