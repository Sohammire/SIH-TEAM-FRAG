import numpy as np
import pandas as pd
from typing import List, Dict, Any, Tuple
from sklearn.linear_model import Ridge

class TemperaturePredictionModel:
    """
    First-order physical thermal state model calibrated via Ridge Regression.
    Enforces strict 70/30 chronological time-series split for fitting/testing.
    """

    def __init__(self, alpha: float = 1.0):
        self.model = Ridge(alpha=alpha)
        self.is_fitted = False
        # Default physical parameters if model not yet fitted
        self.k_heat = 0.0012
        self.k_press = 0.05
        self.k_cool = 0.03
        self.k_idle = 0.08

    def fit_chronological(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Fits Ridge Regression model using 70% chronological train set and 30% test set.
        df must contain: ['tyre_temp_c', 'payload_t', 'speed_kmh', 'pressure_kpa', 'ambient_temp_c', 'is_idle']
        """
        if len(df) < 10:
            return {"status": "insufficient_data", "samples": len(df)}

        # Sort chronologically
        if 'timestamp' in df.columns:
            df = df.sort_values('timestamp')

        # Feature Engineering: Predict temperature increment delta_T
        # Target: delta_T = T(t+1) - T(t)
        df['temp_next'] = df['tyre_temp_c'].shift(-1)
        df['delta_T'] = df['temp_next'] - df['tyre_temp_c']

        # Feature matrix X
        # f1: load * speed (heat generation)
        # f2: pressure factor (P_rated / P)
        # f3: temp difference (T(t) - T_amb) (cooling)
        # f4: idle state
        df['f_heat'] = df['payload_t'] * df['speed_kmh']
        df['f_press'] = 735.0 / df['pressure_kpa'].clip(lower=400.0)
        df['f_cool'] = df['tyre_temp_c'] - df['ambient_temp_c']
        df['f_idle'] = df['is_idle'].astype(float)

        clean_df = df.dropna(subset=['delta_T', 'f_heat', 'f_press', 'f_cool', 'f_idle'])
        if len(clean_df) < 10:
            return {"status": "insufficient_clean_data"}

        # STAGE: 70% Train, 30% Test (Chronological Split - NEVER RANDOM SPLIT)
        split_idx = int(len(clean_df) * 0.70)
        train_df = clean_df.iloc[:split_idx]
        test_df = clean_df.iloc[split_idx:]

        X_train = train_df[['f_heat', 'f_press', 'f_cool', 'f_idle']]
        y_train = train_df['delta_T']

        X_test = test_df[['f_heat', 'f_press', 'f_cool', 'f_idle']]
        y_test = test_df['delta_T']

        # Fit Ridge Regression
        self.model.fit(X_train, y_train)
        self.is_fitted = True

        # Test Evaluation
        y_pred_test = self.model.predict(X_test)
        mae_test = float(np.mean(np.abs(y_test - y_pred_test)))
        rmse_test = float(np.sqrt(np.mean((y_test - y_pred_test) ** 2)))

        return {
            "status": "calibrated",
            "train_samples": len(train_df),
            "test_samples": len(test_df),
            "test_mae_c": round(mae_test, 3),
            "test_rmse_c": round(rmse_test, 3),
            "coefficients": {
                "k_heat": round(float(self.model.coef_[0]), 6),
                "k_press": round(float(self.model.coef_[1]), 6),
                "k_cool": round(float(self.model.coef_[2]), 6),
                "k_idle": round(float(self.model.coef_[3]), 6)
            }
        }

    def predict_temperature_step(
        self,
        current_temp_c: float,
        payload_t: float,
        speed_kmh: float,
        pressure_kpa: float,
        ambient_temp_c: float = 34.0,
        is_idle: bool = False,
        historical_temps: Optional[List[float]] = None
    ) -> Dict[str, Any]:
        """
        Predicts temperature for next step and computes residual, slope, and abnormal trajectory.
        """
        f_heat = payload_t * speed_kmh
        f_press = 735.0 / max(400.0, pressure_kpa)
        f_cool = current_temp_c - ambient_temp_c
        f_idle = 1.0 if is_idle else 0.0

        if self.is_fitted:
            delta_T = float(self.model.predict([[f_heat, f_press, f_cool, f_idle]])[0])
        else:
            # Fallback first-order physical estimate
            delta_T = (self.k_heat * f_heat) + (self.k_press * f_press) - (self.k_cool * f_cool) - (self.k_idle * f_idle)

        predicted_temp = round(current_temp_c + delta_T, 1)
        residual = round(current_temp_c - predicted_temp, 1)

        # Calculate slope (°C/hour assuming 1-min reading interval)
        if historical_temps and len(historical_temps) >= 2:
            temp_slope = round((historical_temps[-1] - historical_temps[0]) * (60.0 / len(historical_temps)), 2)
        else:
            temp_slope = round(delta_T * 60.0, 2)

        # Abnormal Trajectory Detection
        abnormal_reasons = []
        abnormal_trajectory = False

        if current_temp_c > 90.0:
            abnormal_trajectory = True
            abnormal_reasons.append(f"Temperature {current_temp_c}°C exceeds critical threshold (90°C)")

        if residual > 8.0:
            abnormal_trajectory = True
            abnormal_reasons.append(f"Positive thermal residual anomaly (+{residual}°C above model prediction)")

        if is_idle and temp_slope > 2.0:
            abnormal_trajectory = True
            abnormal_reasons.append(f"Tyre temperature rising (+{temp_slope}°C/h) while vehicle is idle")

        if pressure_kpa < 620.0 and residual > 5.0:
            abnormal_trajectory = True
            abnormal_reasons.append("Under-inflation coupled with elevated thermal residual")

        return {
            "current_temperature_c": current_temp_c,
            "predicted_temperature_c": predicted_temp,
            "residual_c": residual,
            "temperature_slope_c_per_h": temp_slope,
            "abnormal_trajectory": abnormal_trajectory,
            "abnormal_reasons": abnormal_reasons,
            "calibration_status": "ridge_regression_calibrated" if self.is_fitted else "physical_baseline"
        }

# Global singleton instance for service calls
temp_model_instance = TemperaturePredictionModel()
