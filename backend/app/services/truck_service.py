from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models import Truck, SensorReading, TyreFitment, Tyre
from app.services.risk_service import calculate_tyre_risk

def get_all_trucks(db: Session) -> List[Dict[str, Any]]:
    trucks = db.query(Truck).all()
    results = []

    for t in trucks:
        # Get latest reading for speed, payload, gps
        latest_reading = (
            db.query(SensorReading)
            .filter(SensorReading.truck_id == t.truck_id)
            .order_by(SensorReading.timestamp.desc())
            .first()
        )

        speed = latest_reading.speed_kmh if latest_reading else 0.0
        payload = latest_reading.payload_t if latest_reading else 0.0
        lat = latest_reading.gps_lat if latest_reading else 20.1234
        lon = latest_reading.gps_lon if latest_reading else 79.0456

        # Determine highest tyre risk for this truck
        fitments = db.query(TyreFitment).filter(TyreFitment.truck_id == t.truck_id).all()
        highest_risk = "LOW"
        current_alert = None

        for fit in fitments:
            reading = (
                db.query(SensorReading)
                .filter(SensorReading.tyre_id == fit.tyre_id)
                .order_by(SensorReading.timestamp.desc())
                .first()
            )
            if reading:
                r_risk = calculate_tyre_risk(reading.pressure_kpa, reading.tyre_temp_c, 1400.0)
                if r_risk["risk_label"] == "HIGH":
                    highest_risk = "HIGH"
                    if reading.pressure_kpa < 620:
                        current_alert = "PRESSURE_LOSS"
                    elif reading.tyre_temp_c >= 88.0:
                        current_alert = "HIGH_TEMPERATURE"
                    else:
                        current_alert = "SEVERE_TYRE_DAMAGE"
                elif r_risk["risk_label"] == "MEDIUM" and highest_risk != "HIGH":
                    highest_risk = "MEDIUM"

        results.append({
            "truck_id": t.truck_id,
            "model": t.model,
            "payload_capacity_t": t.payload_capacity_t,
            "mine_id": t.mine_id,
            "status": t.status,
            "current_speed_kmh": speed,
            "current_payload_t": payload,
            "gps_lat": lat,
            "gps_lon": lon,
            "total_tyres": len(fitments) if fitments else 6,
            "highest_risk": highest_risk,
            "current_alert": current_alert,
            "last_update": latest_reading.timestamp.isoformat() if latest_reading else None,
            "source": "simulator"
        })

    return results

def get_truck_by_id(db: Session, truck_id: str) -> Optional[Dict[str, Any]]:
    trucks = get_all_trucks(db)
    for t in trucks:
        if t["truck_id"] == truck_id:
            return t
    return None

def get_truck_live_telemetry(db: Session, truck_id: str) -> Optional[Dict[str, Any]]:
    truck = db.query(Truck).filter(Truck.truck_id == truck_id).first()
    if not truck:
        return None

    fitments = db.query(TyreFitment).filter(TyreFitment.truck_id == truck_id).all()
    tyres_data = []

    for fit in fitments:
        reading = (
            db.query(SensorReading)
            .filter(SensorReading.tyre_id == fit.tyre_id)
            .order_by(SensorReading.timestamp.desc())
            .first()
        )
        press = reading.pressure_kpa if reading else 735.0
        temp = reading.tyre_temp_c if reading else 62.0
        risk_res = calculate_tyre_risk(press, temp, 1400.0)

        tyres_data.append({
            "tyre_id": fit.tyre_id,
            "position": fit.position,
            "pressure_kpa": press,
            "tyre_temp_c": temp,
            "risk_label": risk_res["risk_label"],
            "risk_score": risk_res["risk_score"]
        })

    latest_reading = (
        db.query(SensorReading)
        .filter(SensorReading.truck_id == truck_id)
        .order_by(SensorReading.timestamp.desc())
        .first()
    )

    return {
        "truck_id": truck.truck_id,
        "status": truck.status,
        "current_speed_kmh": latest_reading.speed_kmh if latest_reading else 0.0,
        "current_payload_t": latest_reading.payload_t if latest_reading else 0.0,
        "gps_lat": latest_reading.gps_lat if latest_reading else 20.1234,
        "gps_lon": latest_reading.gps_lon if latest_reading else 79.0456,
        "tyres": tyres_data,
        "last_update": latest_reading.timestamp.isoformat() if latest_reading else None
    }
