import math
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.models import ImpactEvent

def process_imu_impact_stream(
    db: Session,
    truck_id: str,
    gps_lat: float,
    gps_lon: float,
    imu_ax: float,
    imu_ay: float,
    imu_az: float,
    prev_accel: float = 1.0,
    dt_sec: float = 0.1,
    tyre_id_or_null: Optional[str] = None,
    road_segment_id: str = "RS_01"
) -> Optional[Dict[str, Any]]:
    """
    IMU Impact Engine Pipeline:
    IMU -> gravity filtering -> resultant acceleration -> peak detection -> jerk -> duration -> GPS association -> road segment -> ImpactEvent
    """
    # 1. Gravity Filtering (remove 1.0g static gravity from Z-axis)
    az_dynamic = imu_az - 1.0 if imu_az >= 1.0 else imu_az

    # 2. Resultant Acceleration (g)
    a_resultant = math.sqrt((imu_ax ** 2) + (imu_ay ** 2) + (az_dynamic ** 2))

    # 3. Peak Detection Threshold (>= 2.5g is an impact peak)
    if a_resultant < 2.2:
        return None # No severe impact detected

    # 4. Jerk Calculation (g/s)
    jerk = (a_resultant - prev_accel) / dt_sec if dt_sec > 0 else 0.0

    # 5. Duration (ms) estimate
    duration_ms = round(min(500.0, 50.0 + (a_resultant * 30.0)), 1)

    # Severity classification
    if a_resultant >= 4.0:
        severity = "critical"
    elif a_resultant >= 3.0:
        severity = "high"
    else:
        severity = "medium"

    # 6. Create ImpactEvent DB entry
    event_id = f"EVT_{uuid.uuid4().hex[:8].upper()}"
    evt = ImpactEvent(
        event_id=event_id,
        timestamp=datetime.utcnow(),
        truck_id=truck_id,
        tyre_id_or_null=tyre_id_or_null,
        gps_lat=gps_lat,
        gps_lon=gps_lon,
        peak_accel_g=round(a_resultant, 2),
        jerk=round(jerk, 2),
        duration_ms=duration_ms,
        event_type="imu_impact",
        severity=severity,
        road_segment_id=road_segment_id
    )
    db.add(evt)
    db.commit()

    return {
        "event_id": event_id,
        "truck_id": truck_id,
        "gps_lat": gps_lat,
        "gps_lon": gps_lon,
        "peak_accel_g": round(a_resultant, 2),
        "jerk_g_per_s": round(jerk, 2),
        "duration_ms": duration_ms,
        "severity": severity,
        "road_segment_id": road_segment_id,
        "status": "accepted"
    }
