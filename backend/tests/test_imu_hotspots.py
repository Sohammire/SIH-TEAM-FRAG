import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database.connection import SessionLocal
from app.services.imu_engine import process_imu_impact_stream
from app.services.hotspot_service import find_nearest_road_segment, get_hotspots
from app.services.simulator_service import generate_telemetry_scenario, SUPPORTED_SCENARIOS
from app.models import ImpactEvent

client = TestClient(app)

# 1. IMU Impact Detection Test
def test_imu_impact_detection():
    db = SessionLocal()
    try:
        # High acceleration peak (imu_az = 4.2 -> dynamic az = 3.2, total resultant = 3.5g)
        res = process_imu_impact_stream(
            db=db,
            truck_id="DUMPER_06",
            gps_lat=20.123,
            gps_lon=79.047,
            imu_ax=1.2,
            imu_ay=0.8,
            imu_az=4.2,
            prev_accel=1.0,
            dt_sec=0.1,
            tyre_id_or_null="TYRE_06_FL",
            road_segment_id="RS_04"
        )
        assert res is not None
        assert res["status"] == "accepted"
        assert res["peak_accel_g"] >= 2.5
        assert "jerk_g_per_s" in res
        assert "duration_ms" in res

        # Verify DB entry creation
        evt = db.query(ImpactEvent).filter(ImpactEvent.event_id == res["event_id"]).first()
        assert evt is not None
        assert evt.road_segment_id == "RS_04"
    finally:
        db.close()

# 2. GeoJSON Nearest Road Segment Spatial Matcher Test
def test_geojson_nearest_road_segment():
    # Coordinates near RS_04 (Loading Area Connector: 20.121, 79.047)
    seg_id = find_nearest_road_segment(20.122, 79.048)
    assert seg_id in ("RS_04", "RS_01")

# 3. High Impact Cluster Generates Hotspot Test
def test_high_impact_cluster_generates_hotspot():
    db = SessionLocal()
    try:
        # Ingest impact cluster on RS_04
        for _ in range(5):
            process_imu_impact_stream(
                db=db,
                truck_id="DUMPER_03",
                gps_lat=20.123,
                gps_lon=79.047,
                imu_ax=2.0,
                imu_ay=1.5,
                imu_az=3.8,
                road_segment_id="RS_04"
            )

        hotspots = get_hotspots(db, traffic_multiplier=1.0)
        rs04_hs = next((h for h in hotspots if h["road_segment_id"] == "RS_04"), None)
        
        assert rs04_hs is not None
        assert rs04_hs["hotspot_score"] >= 60.0
        assert rs04_hs["impact_events"] >= 35
    finally:
        db.close()

# 4. Doubling Traffic Decreases Normalized Rate Test
def test_doubling_traffic_decreases_normalized_rate():
    db = SessionLocal()
    try:
        # Base traffic (1.0x)
        hotspots_base = get_hotspots(db, traffic_multiplier=1.0)
        base_rate = hotspots_base[0]["impact_rate_per_100_truck_km"]

        # Doubled traffic (2.0x) without extra events
        hotspots_doubled = get_hotspots(db, traffic_multiplier=2.0)
        doubled_rate = next(h["impact_rate_per_100_truck_km"] for h in hotspots_doubled if h["road_segment_id"] == hotspots_base[0]["road_segment_id"])

        # Doubling traffic MUST decrease normalized rate!
        assert doubled_rate < base_rate
        assert doubled_rate == pytest.approx(base_rate / 2.0, abs=0.1)
    finally:
        db.close()

# 5. Simulator Scenarios Contain scenario_id Test
def test_simulator_scenarios_contain_scenario_id():
    for scen in SUPPORTED_SCENARIOS:
        samples = generate_telemetry_scenario(scenario_id=scen, num_samples=3)
        assert len(samples) == 3
        for sample in samples:
            assert "scenario_id" in sample
            assert sample["scenario_id"] == scen

# 6. REST API Hotspots Endpoint Test
def test_api_hotspots_endpoint():
    res = client.get("/api/v1/hotspots?traffic_multiplier=1.0")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "impact_rate_per_100_truck_km" in data[0]
    assert "hotspot_type" in data[0]
