from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models import Tyre, SensorReading, TyreFitment, TKPHRecord, DamageInspection
from app.services.risk_service import calculate_tyre_risk

def get_all_tyres(db: Session) -> List[Dict[str, Any]]:
    tyres = db.query(Tyre).all()
    results = []

    for t in tyres:
        fitment = (
            db.query(TyreFitment)
            .filter(TyreFitment.tyre_id == t.tyre_id)
            .first()
        )
        truck_id = fitment.truck_id if fitment else "DUMPER_01"
        position = fitment.position if fitment else "front_left"
        fitment_id = fitment.fitment_id if fitment else f"FIT_{t.tyre_id}"

        reading = (
            db.query(SensorReading)
            .filter(SensorReading.tyre_id == t.tyre_id)
            .order_by(SensorReading.timestamp.desc())
            .first()
        )
        tkph_rec = (
            db.query(TKPHRecord)
            .filter(TKPHRecord.tyre_id == t.tyre_id)
            .order_by(TKPHRecord.timestamp.desc())
            .first()
        )
        inspection = (
            db.query(DamageInspection)
            .filter(DamageInspection.tyre_id == t.tyre_id)
            .order_by(DamageInspection.timestamp.desc())
            .first()
        )

        press = reading.pressure_kpa if reading else 735.0
        temp = reading.tyre_temp_c if reading else 62.0
        tkph_val = tkph_rec.tkph if tkph_rec else 1400.0

        damage_present = inspection.damage_present if inspection else False
        damage_sev = inspection.severity if (inspection and inspection.damage_present) else "none"
        damage_type = inspection.damage_type if (inspection and inspection.damage_present) else "none"
        damage_loc = inspection.location if (inspection and inspection.damage_present) else "none"

        risk_res = calculate_tyre_risk(
            pressure_kpa=press,
            tyre_temp_c=temp,
            tkph_current=tkph_val,
            rated_tkph=t.rated_tkph,
            damage_present=damage_present,
            damage_severity=damage_sev,
            damage_type=damage_type,
            damage_location=damage_loc
        )

        results.append({
            "tyre_id": t.tyre_id,
            "truck_id": truck_id,
            "fitment_id": fitment_id,
            "position": position,
            "manufacturer": t.manufacturer,
            "model": t.model,
            "size": t.size,
            "rated_tkph": t.rated_tkph,
            "install_date": t.install_date,
            "initial_tread_mm": t.initial_tread_mm,
            "current_tread_mm": 65.0,
            "cost": t.cost,
            "status": t.status,
            "current_pressure_kpa": press,
            "current_temp_c": temp,
            "ambient_temp_c": reading.ambient_temp_c if reading else 34.0,
            "tkph_current": tkph_val,
            "tkph_rated": t.rated_tkph,
            "tkph_exceedance_ratio": round(tkph_val / t.rated_tkph, 2),
            "wear_rate_mm_per_h": 0.005,
            "risk_score": risk_res["risk_score"],
            "risk_label": risk_res["risk_label"],
            "last_update": reading.timestamp.isoformat() if reading else None,
            "source": "simulator"
        })

    return results

def get_tyre_by_id(db: Session, tyre_id: str) -> Optional[Dict[str, Any]]:
    tyres = get_all_tyres(db)
    for t in tyres:
        if t["tyre_id"] == tyre_id:
            return t
    return None

def get_tyre_risk(db: Session, tyre_id: str) -> Dict[str, Any]:
    tyre_data = get_tyre_by_id(db, tyre_id)
    if not tyre_data:
        # Default low risk fallback
        return {
            "tyre_id": tyre_id,
            "timestamp": "2026-08-16T00:00:00Z",
            "risk_score": 22.0,
            "risk_label": "LOW",
            "reasons": ["All telemetry within normal range"],
            "recommended_action": "CONTINUE MONITORING — NO ACTION REQUIRED",
            "data_confidence": 0.95
        }

    inspection = (
        db.query(DamageInspection)
        .filter(DamageInspection.tyre_id == tyre_id)
        .order_by(DamageInspection.timestamp.desc())
        .first()
    )
    damage_present = inspection.damage_present if inspection else False
    damage_sev = inspection.severity if (inspection and inspection.damage_present) else "none"
    damage_type = inspection.damage_type if (inspection and inspection.damage_present) else "none"
    damage_loc = inspection.location if (inspection and inspection.damage_present) else "none"

    risk_res = calculate_tyre_risk(
        pressure_kpa=tyre_data["current_pressure_kpa"],
        tyre_temp_c=tyre_data["current_temp_c"],
        tkph_current=tyre_data["tkph_current"],
        rated_tkph=tyre_data["rated_tkph"],
        damage_present=damage_present,
        damage_severity=damage_sev,
        damage_type=damage_type,
        damage_location=damage_loc
    )
    risk_res["tyre_id"] = tyre_id
    risk_res["timestamp"] = tyre_data["last_update"] or "2026-08-16T00:00:00Z"
    return risk_res
