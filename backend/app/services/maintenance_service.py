from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.models import Tyre, SensorReading, DamageInspection, TKPHRecord
from app.services.risk_service import calculate_tyre_risk

def get_maintenance_priorities(db: Session) -> List[Dict[str, Any]]:
    """
    Ranks maintenance queue.
    Priority rule: Severe damage + pressure loss outranks TKPH-only warning.
    """
    tyres = db.query(Tyre).all()
    queue = []

    for tyre in tyres:
        # Latest reading
        reading = (
            db.query(SensorReading)
            .filter(SensorReading.tyre_id == tyre.tyre_id)
            .order_by(SensorReading.timestamp.desc())
            .first()
        )
        
        # Latest inspection
        inspection = (
            db.query(DamageInspection)
            .filter(DamageInspection.tyre_id == tyre.tyre_id)
            .order_by(DamageInspection.timestamp.desc())
            .first()
        )

        # Latest TKPH
        tkph_rec = (
            db.query(TKPHRecord)
            .filter(TKPHRecord.tyre_id == tyre.tyre_id)
            .order_by(TKPHRecord.timestamp.desc())
            .first()
        )

        press = reading.pressure_kpa if reading else 735.0
        temp = reading.tyre_temp_c if reading else 62.0
        tkph_val = tkph_rec.tkph if tkph_rec else 1400.0
        truck_id = reading.truck_id if reading else "DUMPER_01"

        damage_present = inspection.damage_present if inspection else False
        damage_sev = inspection.severity if (inspection and inspection.damage_present) else "none"
        damage_type = inspection.damage_type if (inspection and inspection.damage_present) else "none"
        damage_loc = inspection.location if (inspection and inspection.damage_present) else "none"

        risk_res = calculate_tyre_risk(
            pressure_kpa=press,
            tyre_temp_c=temp,
            tkph_current=tkph_val,
            rated_tkph=tyre.rated_tkph,
            damage_present=damage_present,
            damage_severity=damage_sev,
            damage_type=damage_type,
            damage_location=damage_loc
        )

        # Calculate priority rank score:
        # Base = risk_score
        # Bonus for severe damage + pressure loss
        p_score = risk_res["risk_score"]
        if damage_sev == "severe" and press < 650:
            p_score += 50.0 # Huge priority boost
        elif press < 620:
            p_score += 30.0
        elif damage_sev in ("moderate", "severe"):
            p_score += 20.0

        damage_str = f"{damage_sev} {damage_type} — {damage_loc}" if damage_present else "none"

        queue.append({
            "_priority_score": p_score,
            "tyre_id": tyre.tyre_id,
            "truck_id": truck_id,
            "risk_label": risk_res["risk_label"],
            "risk_score": risk_res["risk_score"],
            "main_reason": risk_res["reasons"][0] if risk_res["reasons"] else "Routine inspection",
            "damage": damage_str,
            "pressure_kpa": press,
            "temperature_c": temp,
            "tkph_current": tkph_val,
            "tkph_rated": tyre.rated_tkph,
            "recommended_action": risk_res["recommended_action"],
            "data_confidence": risk_res["data_confidence"],
            "source": "simulator"
        })

    # Sort queue by priority score descending
    queue.sort(key=lambda x: x["_priority_score"], reverse=True)

    # Assign priority ranks 1..N
    final_list = []
    for idx, item in enumerate(queue):
        item["priority"] = idx + 1
        del item["_priority_score"]
        final_list.append(item)

    return final_list
