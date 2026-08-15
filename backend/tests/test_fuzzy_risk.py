import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.risk_service import calculate_tyre_risk
from app.services.fuzzy_risk_engine import evaluate_mamdani_fuzzy_risk

client = TestClient(app)

# 1. Normal Tyre -> LOW
def test_normal_tyre_returns_low():
    risk = calculate_tyre_risk(
        pressure_kpa=735.0,
        tyre_temp_c=62.0,
        tkph_current=1400.0,
        rated_tkph=1800.0,
        damage_present=False,
        damage_severity="none",
        wear_rate=0.005,
        recent_impact_g=0.0
    )
    assert risk["risk_label"] == "LOW"
    assert risk["risk_score"] < 40.0
    assert "reasons" in risk
    assert len(risk["reasons"]) > 0

# 2. Severe Damage + Pressure Loss -> HIGH
def test_severe_damage_plus_pressure_loss_returns_high():
    risk = calculate_tyre_risk(
        pressure_kpa=580.0, # Pressure loss
        tyre_temp_c=65.0,
        tkph_current=1400.0,
        rated_tkph=1800.0,
        damage_present=True,
        damage_severity="severe",
        damage_type="cut",
        damage_location="sidewall"
    )
    assert risk["risk_label"] == "HIGH"
    assert risk["risk_score"] >= 70.0
    assert any("Pressure loss" in r or "pressure" in r.lower() for r in risk["reasons"])
    assert any("Severe" in r or "cut" in r for r in risk["reasons"])
    assert "STOP AND INSPECT" in risk["recommended_action"]

# 3. Excessive TKPH + Thermal Stress -> HIGH
def test_excessive_tkph_plus_thermal_stress_returns_high():
    risk = calculate_tyre_risk(
        pressure_kpa=730.0,
        tyre_temp_c=92.0, # High temperature
        tkph_current=2124.0, # Excessive TKPH (ratio 1.18x)
        rated_tkph=1800.0,
        damage_present=False
    )
    assert risk["risk_label"] == "HIGH"
    assert risk["risk_score"] >= 70.0
    assert any("TKPH" in r for r in risk["reasons"])
    assert any("Temperature" in r for r in risk["reasons"])

# 4. Missing Data -> Reduced Confidence
def test_missing_data_reduces_confidence():
    risk = calculate_tyre_risk(
        pressure_kpa=None, # Missing pressure sensor data
        tyre_temp_c=None, # Missing temp sensor data
        tkph_current=1400.0,
        has_missing_data=True
    )
    # Data confidence should be reduced to 0.60
    assert risk["data_confidence"] <= 0.65

# 5. REST API Integration Test
def test_get_tyre_risk_endpoint():
    res = client.get("/api/v1/tyres/TYRE_03_RRO/risk")
    assert res.status_code == 200
    data = res.json()
    assert data["tyre_id"] == "TYRE_03_RRO"
    assert data["risk_label"] in ("LOW", "MEDIUM", "HIGH")
    assert "stress_inputs" in data
    assert "reasons" in data
    assert "recommended_action" in data
