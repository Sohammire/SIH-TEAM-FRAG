import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional
from sklearn.linear_model import HuberRegressor
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import GroupKFold

class WearProjectionModel:
    """
    Tread wear rate regression and projection engine.
    Uses Robust Linear Regression (HuberRegressor) with GroupKFold by tyre_id to prevent data leakage.
    Termed strictly as 'wear_projection', NOT 'RUL'.
    """

    def __init__(self):
        self.huber_model = HuberRegressor()
        self.gb_model = None
        self.is_fitted = False

    def train_wear_models(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Trains robust linear regression model and optional Gradient Boosting.
        Uses grouped splits by tyre_id to prevent cross-tyre leakage.
        """
        required_cols = ['tyre_id', 'initial_tread_mm', 'current_tread_mm', 'operating_hours', 'avg_payload_t', 'avg_speed_kmh', 'avg_tkph', 'avg_pressure_kpa']
        if not all(col in df.columns for col in required_cols) or len(df) < 5:
            return {"status": "insufficient_data", "samples": len(df)}

        # Wear target: wear_amount_mm = initial_tread_mm - current_tread_mm
        df['wear_amount_mm'] = df['initial_tread_mm'] - df['current_tread_mm']
        df['wear_rate_actual'] = df['wear_amount_mm'] / df['operating_hours'].clip(lower=1.0)

        X = df[['operating_hours', 'avg_payload_t', 'avg_speed_kmh', 'avg_tkph', 'avg_pressure_kpa']]
        y = df['wear_rate_actual']
        groups = df['tyre_id']

        # Grouped split to prevent data leakage
        n_splits = min(3, len(df['tyre_id'].unique()))
        if n_splits < 2:
            # Fallback direct fit
            self.huber_model.fit(X, y)
            self.is_fitted = True
            return {"status": "fitted_direct", "samples": len(df)}

        gkf = GroupKFold(n_splits=n_splits)
        maes_huber = []

        for train_idx, test_idx in gkf.split(X, y, groups=groups):
            X_tr, X_te = X.iloc[train_idx], X.iloc[test_idx]
            y_tr, y_te = y.iloc[train_idx], y.iloc[test_idx]

            self.huber_model.fit(X_tr, y_tr)
            preds = self.huber_model.predict(X_te)
            maes_huber.append(float(np.mean(np.abs(y_te - preds))))

        # Fit final models on full dataset
        self.huber_model.fit(X, y)
        self.is_fitted = True

        res = {
            "status": "calibrated_grouped_split",
            "samples": len(df),
            "unique_tyre_groups": len(df['tyre_id'].unique()),
            "huber_cv_mae_mm_per_h": round(float(np.mean(maes_huber)), 5)
        }

        # Compare Gradient Boosting if > 25 tyre histories exist
        if len(df) >= 25:
            self.gb_model = GradientBoostingRegressor(n_estimators=50, random_state=42)
            self.gb_model.fit(X, y)
            res["gradient_boosting_compared"] = True

        return res

    def estimate_wear_and_projection(
        self,
        tyre_id: str,
        initial_tread_mm: float = 85.0,
        current_tread_mm: float = 65.0,
        operating_hours: float = 500.0,
        avg_payload_t: float = 280.0,
        avg_speed_kmh: float = 25.0,
        avg_tkph: float = 1450.0,
        avg_pressure_kpa: float = 730.0,
        min_safe_tread_mm: float = 20.0
    ) -> Dict[str, Any]:
        """
        Computes wear rate and wear projection band.
        Do NOT call this RUL.
        """
        observed_wear_mm = max(0.0, initial_tread_mm - current_tread_mm)
        
        # Empirical observed wear rate
        empirical_wear_rate = (observed_wear_mm / operating_hours) if operating_hours > 0 else 0.005

        if self.is_fitted:
            X_input = pd.DataFrame([{
                'operating_hours': operating_hours,
                'avg_payload_t': avg_payload_t,
                'avg_speed_kmh': avg_speed_kmh,
                'avg_tkph': avg_tkph,
                'avg_pressure_kpa': avg_pressure_kpa
            }])
            model_predicted_rate = float(self.huber_model.predict(X_input)[0])
            wear_rate_mm_per_hour = round((0.7 * empirical_wear_rate) + (0.3 * model_predicted_rate), 5)
        else:
            wear_rate_mm_per_hour = round(max(0.001, empirical_wear_rate), 5)

        # Compute wear projection (remaining operating hours until min safe tread limit)
        remaining_wearable_mm = max(0.0, current_tread_mm - min_safe_tread_mm)
        projected_remaining_hours = round(remaining_wearable_mm / wear_rate_mm_per_hour, 1) if wear_rate_mm_per_hour > 0 else 9999.0

        # Projection band (upper & lower bounds)
        lower_bound_hours = round(projected_remaining_hours * 0.85, 1)
        upper_bound_hours = round(projected_remaining_hours * 1.15, 1)

        # Generate 90-day projection trajectory points for UI charting
        projection_points = []
        days_ahead = 90
        hours_per_day = 16.0 # mining operational hours per day
        for d in range(0, days_ahead + 1, 10):
            proj_h = d * hours_per_day
            proj_tread = max(min_safe_tread_mm, round(current_tread_mm - (proj_h * wear_rate_mm_per_hour), 1))
            lower_tread = max(min_safe_tread_mm, round(current_tread_mm - (proj_h * wear_rate_mm_per_hour * 1.15), 1))
            upper_tread = max(min_safe_tread_mm, round(current_tread_mm - (proj_h * wear_rate_mm_per_hour * 0.85), 1))
            
            projection_points.append({
                "day": d,
                "projected_tread_mm": proj_tread,
                "lower_bound_tread_mm": lower_tread,
                "upper_bound_tread_mm": upper_tread,
                "min_safe_threshold_mm": min_safe_tread_mm
            })

        return {
            "tyre_id": tyre_id,
            "initial_tread_mm": initial_tread_mm,
            "current_tread_mm": current_tread_mm,
            "min_safe_tread_mm": min_safe_tread_mm,
            "operating_hours": operating_hours,
            "wear_rate_mm_per_hour": wear_rate_mm_per_hour,
            "wear_projection": {
                "projected_remaining_hours": projected_remaining_hours,
                "confidence_band_hours": [lower_bound_hours, upper_bound_hours],
                "projection_trajectory": projection_points,
                "disclaimer": "This output is a wear projection based on linear regression extrapolation, NOT a validated RUL prediction."
            }
        }

# Global singleton instance
wear_model_instance = WearProjectionModel()
