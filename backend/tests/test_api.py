import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    res = client.get("/api/v1/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"

def test_dashboard_summary():
    res = client.get("/api/v1/dashboard/summary")
    assert res.status_code == 200
    data = res.json()
    assert "total_trucks" in data
    assert data["total_trucks"] >= 8
    assert "active_trucks" in data

def test_get_trucks():
    res = client.get("/api/v1/trucks")
    assert res.status_code == 200
    trucks = res.json()
    assert isinstance(trucks, list)
    assert len(trucks) >= 8
    assert trucks[0]["truck_id"].startswith("DUMPER_")

def test_get_single_truck():
    res = client.get("/api/v1/trucks/DUMPER_01")
    assert res.status_code == 200
    truck = res.json()
    assert truck["truck_id"] == "DUMPER_01"

def test_get_truck_live():
    res = client.get("/api/v1/trucks/DUMPER_01/live")
    assert res.status_code == 200
    data = res.json()
    assert data["truck_id"] == "DUMPER_01"
    assert "tyres" in data
    assert len(data["tyres"]) > 0

def test_get_tyres():
    res = client.get("/api/v1/tyres")
    assert res.status_code == 200
    tyres = res.json()
    assert isinstance(tyres, list)
    assert len(tyres) >= 48

def test_get_single_tyre():
    res = client.get("/api/v1/tyres/TYRE_03_RRO")
    assert res.status_code == 200
    tyre = res.json()
    assert tyre["tyre_id"] == "TYRE_03_RRO"

def test_get_tyre_risk():
    res = client.get("/api/v1/tyres/TYRE_03_RRO/risk")
    assert res.status_code == 200
    risk = res.json()
    assert risk["tyre_id"] == "TYRE_03_RRO"
    assert risk["risk_label"] in ("LOW", "MEDIUM", "HIGH")
    assert "reasons" in risk
    assert "recommended_action" in risk

def test_post_telemetry():
    payload = {
        "timestamp": "2026-08-16T00:00:00Z",
        "truck_id": "DUMPER_07",
        "tyre_id": "TYRE_07_RRO",
        "position": "rear_right_outer",
        "pressure_kpa": 735.0,
        "tyre_temp_c": 82.0,
        "ambient_temp_c": 34.0,
        "payload_t": 120.0,
        "speed_kmh": 28.0,
        "gps_lat": 20.123,
        "gps_lon": 79.123,
        "imu_ax": 0.2,
        "imu_ay": 0.4,
        "imu_az": 1.1
    }
    res = client.post("/api/v1/telemetry", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data["status"] == "accepted"
    assert "reading_id" in data

def test_post_inspection():
    payload = {
        "tyre_id": "TYRE_03_RRO",
        "truck_id": "DUMPER_03",
        "damage_present": True,
        "damage_type": "cut",
        "location": "sidewall",
        "severity": "severe",
        "confidence": 0.91,
        "bbox": [120, 80, 340, 260]
    }
    res = client.post("/api/v1/inspections", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data["damage_type"] == "cut"
    assert data["severity"] == "severe"

def test_vision_predict():
    res = client.post("/api/v1/vision/predict?tyre_id=TYRE_03_RRO")
    assert res.status_code == 200
    data = res.json()
    assert "image_id" in data
    assert data["tyre_id"] == "TYRE_03_RRO"
    assert "damage_present" in data
    assert "detections" in data

def test_post_impact_event():
    payload = {
        "truck_id": "DUMPER_06",
        "gps_lat": 20.122,
        "gps_lon": 79.048,
        "peak_accel_g": 3.8,
        "road_segment_id": "RS_04"
    }
    res = client.post("/api/v1/impact-events", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data["status"] == "accepted"
    assert data["road_segment_id"] == "RS_04"

def test_get_hotspots():
    res = client.get("/api/v1/hotspots")
    assert res.status_code == 200
    hotspots = res.json()
    assert isinstance(hotspots, list)
    assert len(hotspots) > 0
    assert "hotspot_score" in hotspots[0]

def test_get_maintenance_priorities():
    res = client.get("/api/v1/maintenance/priorities")
    assert res.status_code == 200
    queue = res.json()
    assert isinstance(queue, list)
    assert len(queue) > 0
    assert queue[0]["priority"] == 1
    # Verify priority rule: Severe damage + pressure loss (TYRE_03_RRO) should be #1
    assert queue[0]["tyre_id"] == "TYRE_03_RRO"

def test_get_alerts():
    res = client.get("/api/v1/alerts")
    assert res.status_code == 200
    alerts = res.json()
    assert isinstance(alerts, list)
    assert len(alerts) > 0

def test_simulate_telemetry():
    res = client.post("/api/v1/telemetry/simulate", json={"scenario_id": "pressure_leak"})
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "started"
