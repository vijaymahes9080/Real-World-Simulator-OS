import numpy as np
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class TwinAlert(BaseModel):
    metric_name: str
    severity: str  # "info", "warning", "critical"
    deviation_percent: float
    message: str
    timestamp: float

class SyncComparisonResult(BaseModel):
    metric_name: str
    real_value: float
    simulated_value: float
    deviation_percent: float
    rmse: float
    mape: float
    alerts: List[TwinAlert] = Field(default_factory=list)

class DigitalTwinService:
    @staticmethod
    def calculate_metrics(real: List[float], simulated: List[float]) -> Tuple[float, float]:
        """
        Calculates Root Mean Squared Error (RMSE) and Mean Absolute Percentage Error (MAPE).
        """
        if not real or not simulated or len(real) != len(simulated):
            return 0.0, 0.0
            
        r_arr = np.array(real, dtype=float)
        s_arr = np.array(simulated, dtype=float)
        
        # RMSE
        rmse = float(np.sqrt(np.mean((r_arr - s_arr) ** 2)))
        
        # MAPE
        # Avoid division by zero
        r_safe = np.where(r_arr == 0, 1e-5, r_arr)
        mape = float(np.mean(np.abs((r_arr - s_arr) / r_safe)) * 100)
        
        return rmse, mape

    @classmethod
    def synchronize_and_compare(
        cls,
        metric_name: str,
        real_history: List[Tuple[float, float]],  # List of (timestamp, value)
        simulated_history: List[Tuple[float, float]],  # List of (timestamp, value)
        deviation_threshold: float = 15.0  # Percentage threshold for warning alerts
    ) -> SyncComparisonResult:
        """
        Synchronizes historical time series by interpolating onto a common time grid,
        compares values, computes deviation percentages, and alerts if they exceed thresholds.
        """
        if not real_history or not simulated_history:
            return SyncComparisonResult(
                metric_name=metric_name,
                real_value=0.0,
                simulated_value=0.0,
                deviation_percent=0.0,
                rmse=0.0,
                mape=0.0,
                alerts=[]
            )

        # Separate time and value arrays
        t_real = np.array([pt[0] for pt in real_history])
        v_real = np.array([pt[1] for pt in real_history])
        
        t_sim = np.array([pt[0] for pt in simulated_history])
        v_sim = np.array([pt[1] for pt in simulated_history])

        # Intersect time ranges to compare overlaps
        min_t = max(t_real.min(), t_sim.min())
        max_t = min(t_real.max(), t_sim.max())
        
        if min_t >= max_t:
            # Fallback if no timeline overlap exists: compare latest values directly
            latest_real = float(v_real[-1])
            latest_sim = float(v_sim[-1])
            dev = abs(latest_real - latest_sim) / (latest_real or 1e-5) * 100
            
            alerts = []
            if dev > deviation_threshold:
                alerts.append(TwinAlert(
                    metric_name=metric_name,
                    severity="warning" if dev < 30 else "critical",
                    deviation_percent=dev,
                    message=f"Real state deviates from simulated prediction by {dev:.1f}%",
                    timestamp=max(t_real[-1], t_sim[-1])
                ))
            return SyncComparisonResult(
                metric_name=metric_name,
                real_value=latest_real,
                simulated_value=latest_sim,
                deviation_percent=dev,
                rmse=0.0,
                mape=0.0,
                alerts=alerts
            )

        # Create synchronized grid of 20 points
        t_sync = np.linspace(min_t, max_t, 20)
        v_real_sync = np.interp(t_sync, t_real, v_real)
        v_sim_sync = np.interp(t_sync, t_sim, v_sim)

        rmse, mape = cls.calculate_metrics(v_real_sync.tolist(), v_sim_sync.tolist())

        latest_real = float(v_real[-1])
        latest_sim = float(v_sim[-1])
        dev = abs(latest_real - latest_sim) / (latest_real or 1e-5) * 100

        alerts = []
        if dev > deviation_threshold:
            alerts.append(TwinAlert(
                metric_name=metric_name,
                severity="warning" if dev < 30 else "critical",
                deviation_percent=dev,
                message=f"Physical metric '{metric_name}' is experiencing a deviation of {dev:.1f}% from the simulator forecast.",
                timestamp=t_real[-1]
            ))

        return SyncComparisonResult(
            metric_name=metric_name,
            real_value=latest_real,
            simulated_value=latest_sim,
            deviation_percent=dev,
            rmse=rmse,
            mape=mape,
            alerts=alerts
        )
