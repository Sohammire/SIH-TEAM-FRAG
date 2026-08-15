import time
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

SUPPORTED_SCENARIOS = [
    "normal_cycle",
    "pressure_leak",
    "high_payload_high_speed",
    "high_temperature",
    "impact_cluster",
    "sidewall_damage_pressure_loss",
    "worn_tyre",
    "sensor_dropout"
]

def generate_telemetry_scenario(
    scenario_id: str = "normal_cycle",
    truck_id: str = "DUMPER_01",
    tyre_id: str = "TYRE_01_FL",
    mine_id: str = "MINE_ALPHA",
    num_samples: int = 10
) -> List[Dict[str, Any]]:
    """
    Synthetic telemetry generator for 8 mining operational scenarios.
    EVERY payload strictly contains 'scenario_id'.
    """
    if scenario_id not in SUPPORTED_SCENARIOS:
        scenario_id = "normal_cycle"

    base_time = datetime.utcnow() - timedelta(seconds=num_samples * 10)
    samples = []

    # Scenario parameters baseline
    press_base = 735.0
    temp_base = 62.0
    payload_val_base = 280.0
    speed_base = 25.0

    for idx in range(num_samples):
        timestamp = (base_time + timedelta(seconds=idx * 10)).isoformat()
        ax, ay, az = 0.1, 0.2, 1.0
        
        # Scenario variations
        if scenario_id == "normal_cycle":
            press = press_base + random.uniform(-5, 5)
            temp = temp_base + random.uniform(-1, 2)
            payload_val = payload_val_base + random.uniform(-10, 10)
            speed = speed_base + random.uniform(-3, 3)

        elif scenario_id == "pressure_leak":
            # Pressure drops gradually over time
            press = max(520.0, press_base - (idx * 15.0))
            temp = temp_base + (idx * 2.0)
            payload_val = payload_val_base
            speed = speed_base

        elif scenario_id == "high_payload_high_speed":
            # Overloaded dumper running fast -> TKPH exceedance
            payload_val = 360.0
            speed = 38.0
            press = press_base
            temp = temp_base + (idx * 2.5)

        elif scenario_id == "high_temperature":
            # Rapid thermal rise
            temp = min(98.0, 70.0 + (idx * 3.0))
            press = press_base + (idx * 2.0)
            payload_val = 320.0
            speed = 30.0

        elif scenario_id == "impact_cluster":
            # Severe IMU acceleration spikes on haul road
            press = press_base
            temp = temp_base
            payload_val = payload_val_base
            speed = 28.0
            if idx in (3, 4, 7):
                ax, ay, az = 2.5, 1.8, 3.8 # Severe bump impact

        elif scenario_id == "sidewall_damage_pressure_loss":
            # Pressure loss + cut defect
            press = max(550.0, 700.0 - (idx * 20.0))
            temp = 75.0 + (idx * 1.5)
            payload_val = 290.0
            speed = 22.0

        elif scenario_id == "worn_tyre":
            # Low tread depth -> elevated thermal slope
            temp = 78.0 + (idx * 2.0)
            press = press_base
            payload_val = payload_val_base
            speed = speed_base

        elif scenario_id == "sensor_dropout":
            # Missing sensor values for test confidence reduction
            if idx >= 5:
                press = None
                temp = None
                speed = 0.0
                payload_val = 0.0
            else:
                press = press_base
                temp = temp_base
                speed = speed_base
                payload_val = payload_val_base

        # Package telemetry sample dictionary
        record_dict = {
            "scenario_id": scenario_id,
            "timestamp": timestamp,
            "mine_id": mine_id,
            "truck_id": truck_id,
            "tyre_id": tyre_id,
            "position": "front_left",
            "pressure_kpa": round(press, 1) if press is not None else None,
            "tyre_temp_c": round(temp, 1) if temp is not None else None,
            "ambient_temp_c": 34.0,
            "payload_t": round(payload_val, 1) if payload_val is not None else 0.0,
            "speed_kmh": round(speed, 1) if speed is not None else 0.0,
            "gps_lat": 20.1234 + (idx * 0.0001),
            "gps_lon": 79.0456 + (idx * 0.0001),
            "imu_ax": round(ax, 2),
            "imu_ay": round(ay, 2),
            "imu_az": round(az, 2),
            "source": "telemetry_simulator"
        }
        samples.append(record_dict)

    return samples
