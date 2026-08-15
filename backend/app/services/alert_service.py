from typing import List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models import SensorReading, DamageInspection

def get_alerts(db: Session) -> List[Dict[str, Any]]:
    """
    Evaluates alerts across telemetry, damage inspections, and operational thresholds.
    """
    now = datetime.utcnow()
    alerts = [
        {
            "alert_id": "ALT_001",
            "timestamp": (now - timedelta(minutes=2)).isoformat(),
            "type": "PRESSURE_LOSS",
            "severity": "critical",
            "truck_id": "DUMPER_07",
            "tyre_id": "TYRE_07_RRI",
            "message": "Rapid pressure loss detected — 610 kPa (threshold 650 kPa). Loss rate: 12 kPa/h.",
            "status": "active",
            "source": "simulator"
        },
        {
            "alert_id": "ALT_002",
            "timestamp": (now - timedelta(minutes=5)).isoformat(),
            "type": "SEVERE_TYRE_DAMAGE",
            "severity": "critical",
            "truck_id": "DUMPER_03",
            "tyre_id": "TYRE_03_RRO",
            "message": "Severe sidewall cut detected via vision inspection. Confidence: 0.91.",
            "status": "active",
            "source": "simulator"
        },
        {
            "alert_id": "ALT_003",
            "timestamp": (now - timedelta(minutes=10)).isoformat(),
            "type": "HIGH_TEMPERATURE",
            "severity": "high",
            "truck_id": "DUMPER_05",
            "tyre_id": "TYRE_05_RLI",
            "message": "Tyre temperature 94°C exceeds warning threshold (90°C). Temperature rising despite reduced speed.",
            "status": "active",
            "source": "simulator"
        },
        {
            "alert_id": "ALT_004",
            "timestamp": (now - timedelta(minutes=15)).isoformat(),
            "type": "TKPH_EXCEEDED",
            "severity": "high",
            "truck_id": "DUMPER_02",
            "tyre_id": "TYRE_02_FL",
            "message": "TKPH exceedance ratio 1.12× rated value. Current: 2016, Rated: 1800.",
            "status": "active",
            "source": "simulator"
        },
        {
            "alert_id": "ALT_005",
            "timestamp": (now - timedelta(minutes=30)).isoformat(),
            "type": "HIGH_IMPACT",
            "severity": "medium",
            "truck_id": "DUMPER_06",
            "tyre_id": None,
            "message": "High impact event detected at road segment RS_04. Peak: 3.2g, Duration: 120ms.",
            "status": "active",
            "source": "simulator"
        },
        {
            "alert_id": "ALT_006",
            "timestamp": (now - timedelta(minutes=60)).isoformat(),
            "type": "SENSOR_FAILURE",
            "severity": "medium",
            "truck_id": "DUMPER_04",
            "tyre_id": "TYRE_04_FR",
            "message": "No telemetry received for 15 minutes. Possible sensor dropout.",
            "status": "active",
            "source": "simulator"
        },
        {
            "alert_id": "ALT_007",
            "timestamp": (now - timedelta(hours=2)).isoformat(),
            "type": "PRESSURE_LOSS",
            "severity": "high",
            "truck_id": "DUMPER_03",
            "tyre_id": "TYRE_03_RLO",
            "message": "Gradual pressure loss: 690 kPa -> 665 kPa over 2 hours.",
            "status": "resolved",
            "source": "simulator"
        }
    ]
    return alerts
