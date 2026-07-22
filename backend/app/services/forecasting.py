import numpy as np
from scipy.optimize import curve_fit
from typing import Any, Dict, List, Tuple
from pydantic import BaseModel

class ForecastPoint(BaseModel):
    time: float
    value: float
    lower_bound: float
    upper_bound: float

class ForecastResult(BaseModel):
    target_name: str
    historical_points: List[Tuple[float, float]]
    forecast_points: List[ForecastPoint]
    model_used: str
    fit_metrics: Dict[str, float]

class ForecastingService:
    @staticmethod
    def linear_trend(t: np.ndarray, a: float, b: float) -> np.ndarray:
        return a * t + b

    @staticmethod
    def quadratic_trend(t: np.ndarray, a: float, b: float, c: float) -> np.ndarray:
        return a * t**2 + b * t + c

    @classmethod
    def fit_and_forecast(
        cls, 
        history: List[Tuple[float, float]], 
        steps: int = 12, 
        dt: float = 1.0
    ) -> ForecastResult:
        """
        Fits a curve to the given time-series data and projects it forward with 95% confidence intervals.
        """
        if len(history) < 3:
            # Fallback for insufficient data
            t_hist = np.array([pt[0] for pt in history]) if history else np.array([0.0])
            y_hist = np.array([pt[1] for pt in history]) if history else np.array([0.0])
            last_val = y_hist[-1] if len(y_hist) > 0 else 0.0
            
            forecast = []
            last_t = t_hist[-1] if len(t_hist) > 0 else 0.0
            for i in range(1, steps + 1):
                ft = last_t + i * dt
                forecast.append(ForecastPoint(time=ft, value=last_val, lower_bound=last_val, upper_bound=last_val))
            return ForecastResult(
                target_name="unknown",
                historical_points=history,
                forecast_points=forecast,
                model_used="Constant Fallback",
                fit_metrics={"mse": 0.0}
            )

        t_hist = np.array([pt[0] for pt in history], dtype=float)
        y_hist = np.array([pt[1] for pt in history], dtype=float)
        
        # Fit two candidate models: Linear and Quadratic, and choose the one with the lowest MSE
        models = [
            ("Linear Trend", cls.linear_trend, [0.0, y_hist[0]]),
            ("Quadratic Trend", cls.quadratic_trend, [0.0, 0.0, y_hist[0]])
        ]
        
        best_model_name = ""
        best_popt = None
        best_fn = None
        min_mse = float("inf")
        
        for name, fn, p0 in models:
            try:
                popt, pcov = curve_fit(fn, t_hist, y_hist, p0=p0, maxfev=2000)
                y_fit = fn(t_hist, *popt)
                mse = float(np.mean((y_hist - y_fit) ** 2))
                if mse < min_mse:
                    min_mse = mse
                    best_model_name = name
                    best_popt = popt
                    best_fn = fn
            except Exception:
                continue

        # If fitting failed, fallback to average growth rate
        if best_popt is None or best_fn is None:
            mean_val = float(np.mean(y_hist))
            std_val = float(np.std(y_hist)) if len(y_hist) > 1 else 1.0
            best_model_name = "Mean Baseline"
            best_fn = lambda t: np.full_like(t, mean_val)
            best_popt = []
            min_mse = float(np.mean((y_hist - mean_val) ** 2))

        # Generate future timeline
        last_t = t_hist[-1]
        t_future = np.array([last_t + i * dt for i in range(1, steps + 1)], dtype=float)
        
        # Forecast values
        if best_model_name == "Mean Baseline":
            y_future = best_fn(t_future)
        else:
            y_future = best_fn(t_future, *best_popt)

        # Standard error estimation for confidence intervals
        # Variance of residuals
        residuals = y_hist - (best_fn(t_hist) if best_model_name == "Mean Baseline" else best_fn(t_hist, *best_popt))
        residual_std = np.std(residuals)
        if residual_std == 0:
            residual_std = 1e-3

        forecast_points = []
        for i, ft in enumerate(t_future):
            pred_val = float(y_future[i])
            # Confidence interval widens over time: std_error * sqrt(1 + steps_forward * 0.1)
            uncertainty = 1.96 * residual_std * np.sqrt(1 + (i + 1) * 0.15)
            forecast_points.append(ForecastPoint(
                time=ft,
                value=pred_val,
                lower_bound=pred_val - uncertainty,
                upper_bound=pred_val + uncertainty
            ))

        return ForecastResult(
            target_name="Target Variable",
            historical_points=history,
            forecast_points=forecast_points,
            model_used=best_model_name,
            fit_metrics={"mse": min_mse}
        )
