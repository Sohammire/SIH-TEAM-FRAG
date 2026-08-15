import pytest
import pandas as pd
import numpy as np
from fastapi.testclient import TestClient
from app.main import app
from app.services.tkph_service import calculate_rolling_tkph
from app.services.temperature_service import TemperaturePredictionModel
from app.services.wear_service import WearProjectionModel

client = TestClient(app)

# 1. TKPH Tests
def test_tkph_service_zero_speed_exclusion():
    # Samples with zero speeds (idle periods)
    payloads = [300.0, 300.0, 300.0, 0.0, 0.0]
    speeds = [30.0, 30.0, 30.0, 0.0, 0.0] # 2 zero-speed samples

    res = calculate_rolling_tkph(payloads, speeds, rated_tkph=1800.0)
    
    # AWSS should only average non-zero speeds (30.0 km/h), NOT (30*3/5 = 18 km/h)
    assert res["awss_kmh"] == 30.0
    assert "prototype_default_notice" in res

def test_tkph_service_thresholds():
    payloads = [350.0] * 5
    speeds = [40.0] * 5 # High workload

    res = calculate_rolling_tkph(payloads, speeds, rated_tkph=1800.0)
    assert res["workload_status"] == "HIGH"
    assert res["tkph_exceedance_ratio"] > 1.15

# 2. Temperature Model Tests
def test_temperature_service_chronological_split():
    # Create time series sample dataset
    np.random.seed(42)
    n = 100
    df = pd.DataFrame({
        'timestamp': pd.date_range(start='2026-08-16', periods=n, freq='min'),
        'tyre_temp_c': 55.0 + np.cumsum(np.random.randn(n) * 0.5),
        'payload_t': np.random.uniform(200, 350, n),
        'speed_kmh': np.random.uniform(10, 40, n),
        'pressure_kpa': np.random.uniform(700, 750, n),
        'ambient_temp_c': [34.0] * n,
        'is_idle': [False] * n
    })

    model = TemperaturePredictionModel(alpha=1.0)
    fit_res = model.fit_chronological(df)

    assert fit_res["status"] == "calibrated"
    assert fit_res["train_samples"] == 69 # ~70% of 99 delta pairs
    assert fit_res["test_samples"] == 30  # ~30% of 99 delta pairs
    assert "coefficients" in fit_res

def test_temperature_prediction_and_residual():
    model = TemperaturePredictionModel()
    pred = model.predict_temperature_step(
        current_temp_c=92.0, # High temp
        payload_t=320.0,
        speed_kmh=35.0,
        pressure_kpa=580.0, # Underinflated
        ambient_temp_c=34.0,
        is_idle=False
    )

    assert "predicted_temperature_c" in pred
    assert "residual_c" in pred
    assert pred["abnormal_trajectory"] is True
    assert len(pred["abnormal_reasons"]) > 0

# 3. Wear Model Tests
def test_wear_service_grouped_split_leakage_prevention():
    # Create sample tyre dataset across 6 tyre IDs
    data = []
    tyres = ["TYRE_01_FL", "TYRE_01_FR", "TYRE_02_FL", "TYRE_02_FR", "TYRE_03_FL", "TYRE_03_FR"]
    for t_id in tyres:
        for hrs in [100, 200, 300, 400, 500]:
            data.append({
                'tyre_id': t_id,
                'initial_tread_mm': 85.0,
                'current_tread_mm': 85.0 - (hrs * 0.005),
                'operating_hours': float(hrs),
                'avg_payload_t': 280.0,
                'avg_speed_kmh': 25.0,
                'avg_tkph': 1450.0,
                'avg_pressure_kpa': 730.0
            })
    df = pd.DataFrame(data)

    wear_model = WearProjectionModel()
    res = wear_model.train_wear_models(df)

    assert res["status"] == "calibrated_grouped_split"
    assert res["unique_tyre_groups"] == 6

def test_wear_projection_output():
    wear_model = WearProjectionModel()
    proj = wear_model.estimate_wear_and_projection(
        tyre_id="TYRE_01_FL",
        initial_tread_mm=85.0,
        current_tread_mm=65.0,
        operating_hours=500.0
    )

    assert proj["tyre_id"] == "TYRE_01_FL"
    assert "wear_rate_mm_per_hour" in proj
    assert "wear_projection" in proj
    assert "disclaimer" in proj["wear_projection"]
    assert "RUL" not in proj # Strictly prohibited term

# 4. Analytics REST API Endpoints Tests
def test_api_analytics_tkph():
    res = client.get("/api/v1/analytics/tkph/TYRE_01_FL")
    assert res.status_code == 200
    data = res.json()
    assert "tkph_current" in data
    assert "awss_kmh" in data
    assert "workload_status" in data

def test_api_analytics_temperature_prediction():
    res = client.get("/api/v1/analytics/temperature-prediction/TYRE_01_FL")
    assert res.status_code == 200
    data = res.json()
    assert "predicted_temperature_c" in data
    assert "residual_c" in data
    assert "abnormal_trajectory" in data

def test_api_analytics_wear_projection():
    res = client.get("/api/v1/analytics/wear-projection/TYRE_01_FL")
    assert res.status_code == 200
    data = res.json()
    assert "wear_rate_mm_per_hour" in data
    assert "wear_projection" in data

def test_api_calibrate_temperature():
    res = client.post("/api/v1/analytics/calibrate-temperature")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "calibrated"
    assert "test_mae_c" in data
