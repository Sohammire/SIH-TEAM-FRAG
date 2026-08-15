import requests
import json
import sys
import io
from datetime import datetime

# Set stdout encoding to utf-8 for Windows console support
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

API_BASE = "http://localhost:8000/api/v1"

def print_step(step_num: int, title: str):
    print(f"\n========================================================")
    print(f" STEP {step_num}: {title.upper()}")
    print(f"========================================================")

def run_e2e_demo():
    print("STARTING E2E MINING DUMPER TYRE INTELLIGENCE SYSTEM DEMONSTRATOR")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"Target API Server: {API_BASE}\n")

    # 1. Health Check
    print_step(1, "Verify System Health")
    try:
        r = requests.get(f"{API_BASE}/health")
        print(f"Health Status: {r.json()}")
    except Exception as e:
        print(f"Backend server not responding on {API_BASE}. Please ensure uvicorn server is running.")
        return

    # 2. Simulate Telemetry Stream with Pressure Drop & Thermal Rise
    print_step(2, "Ingest Telemetry Stream (Pressure Loss + High TKPH)")
    telemetry_payload = {
        "timestamp": datetime.utcnow().isoformat(),
        "truck_id": "DUMPER_03",
        "tyre_id": "TYRE_03_RRO",
        "position": "rear_right_outer",
        "pressure_kpa": 580.0, # Severe pressure loss (target 735)
        "tyre_temp_c": 92.0,   # Thermal excursion (threshold 85)
        "ambient_temp_c": 34.0,
        "payload_t": 340.0,    # Heavy payload
        "speed_kmh": 36.0,     # High speed -> High TKPH
        "gps_lat": 20.1234,
        "gps_lon": 79.0456,
        "imu_ax": 2.5,
        "imu_ay": 1.8,
        "imu_az": 3.8          # Severe acceleration spike
    }
    r = requests.post(f"{API_BASE}/telemetry", json=telemetry_payload)
    print(f"Telemetry Ingested: {r.json()}")

    # 3. Record IMU Impact Event
    print_step(3, "IMU Impact Event Detection on Haul Road")
    impact_payload = {
        "truck_id": "DUMPER_03",
        "tyre_id_or_null": "TYRE_03_RRO",
        "gps_lat": 20.121,
        "gps_lon": 79.047,
        "peak_accel_g": 3.8,
        "jerk": 45.0,
        "duration_ms": 120.0,
        "road_segment_id": "RS_04"
    }
    r = requests.post(f"{API_BASE}/impact-events", json=impact_payload)
    print(f"Impact Event Recorded: {r.json()}")

    # 4. Computer Vision Image Inspection
    print_step(4, "Computer Vision Damage Inspection (YOLO + Severity)")
    r = requests.post(f"{API_BASE}/vision/predict?tyre_id=TYRE_03_RRO")
    vision_res = r.json()
    print(f"Vision Prediction Result:")
    print(f"  * Damage Present : {vision_res.get('damage_present')}")
    print(f"  * Damage Type    : {vision_res.get('damage_type')}")
    print(f"  * Location       : {vision_res.get('location')}")
    print(f"  * Severity Level : {vision_res.get('severity')}")
    print(f"  * Bounding Box   : {vision_res.get('bbox')}")
    print(f"  * Quality Status : {vision_res.get('image_quality_status')}")

    # 5. Mamdani Fuzzy Risk Engine Evaluation
    print_step(5, "Mamdani Fuzzy Risk Engine Evaluation")
    r = requests.get(f"{API_BASE}/tyres/TYRE_03_RRO/risk")
    risk_res = r.json()
    print(f"Risk Assessment Output:")
    print(f"  * Risk Score         : {risk_res.get('risk_score')}/100")
    print(f"  * Risk Label         : {risk_res.get('risk_label')}")
    print(f"  * Data Confidence    : {risk_res.get('data_confidence')}")
    print(f"  * Recommended Action : {risk_res.get('recommended_action')}")
    print(f"  * Triggered Reasons  :")
    for reason in risk_res.get('reasons', []):
        print(f"      - {reason}")

    # 6. Maintenance Queue Ranking Check
    print_step(6, "Ranked Maintenance Priority Queue")
    r = requests.get(f"{API_BASE}/maintenance/priorities")
    maint_queue = r.json()
    top_item = maint_queue[0] if maint_queue else {}
    print(f"Top Priority Maintenance #1:")
    print(f"  * Tyre ID        : {top_item.get('tyre_id')}")
    print(f"  * Truck ID       : {top_item.get('truck_id')}")
    print(f"  * Risk Level     : {top_item.get('risk_label')} ({top_item.get('risk_score')})")
    print(f"  * Main Reason    : {top_item.get('main_reason')}")
    print(f"  * Action         : {top_item.get('recommended_action')}")

    # 7. Active Alerts Check
    print_step(7, "Alert Center Active Alerts Feed")
    r = requests.get(f"{API_BASE}/alerts")
    alerts = r.json()
    print(f"Active Alerts ({len(alerts)} total):")
    for a in alerts[:3]:
        print(f"  * [{a.get('severity').upper()}] {a.get('type')}: {a.get('message')}")

    # 8. Exposure-Normalized Mine Road Hotspot Check
    print_step(8, "Exposure-Normalized Road Segment Hotspots")
    r = requests.get(f"{API_BASE}/hotspots?traffic_multiplier=1.0")
    hotspots = r.json()
    print(f"Top Risk Road Hotspot #1:")
    top_hs = hotspots[0]
    print(f"  * Road Segment   : {top_hs.get('name')} ({top_hs.get('road_segment_id')})")
    print(f"  * Hotspot Score  : {top_hs.get('hotspot_score')}/100")
    print(f"  * Hotspot Type   : {top_hs.get('hotspot_type')}")
    print(f"  * Impact Rate    : {top_hs.get('impact_rate_per_100_truck_km')} per 100 truck-km")

    print("\nSUCCESS - ALL MODULES CONNECTED END-TO-END SUCCESSFULLY!")

if __name__ == "__main__":
    run_e2e_demo()
