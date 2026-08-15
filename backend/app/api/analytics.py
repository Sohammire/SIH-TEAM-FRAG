from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
import pandas as pd

from app.database.connection import get_db
from app.models import SensorReading, Tyre, TKPHRecord
from app.services.tkph_service import calculate_rolling_tkph
from app.services.temperature_service import temp_model_instance
from app.services.wear_service import wear_model_instance

router = APIRouter(prefix="/analytics", tags=["ML Analytics Core"])

@router.get("/tkph/{tyre_id}")
def get_tyre_tkph_analytics(tyre_id: str, db: Session = Depends(get_db)):
    """
    Computes rolling TKPH, AWSS (zero-speed samples excluded), shift summary, and exceedance.
    """
    readings = (
        db.query(SensorReading)
        .filter(SensorReading.tyre_id == tyre_id)
        .order_by(SensorReading.timestamp.asc())
        .all()
    )
    tyre = db.query(Tyre).filter(Tyre.tyre_id == tyre_id).first()
    rated_tkph = tyre.rated_tkph if tyre else 1800.0

    if not readings:
        payloads = [280.0, 310.0, 290.0, 320.0, 0.0, 275.0]
        speeds = [25.0, 32.0, 28.0, 30.0, 0.0, 26.0]
    else:
        payloads = [r.payload_t for r in readings]
        speeds = [r.speed_kmh for r in readings]

    return calculate_rolling_tkph(
        payload_samples=payloads,
        speed_samples=speeds,
        rated_tkph=rated_tkph
    )

@router.get("/temperature-prediction/{tyre_id}")
def get_tyre_temperature_prediction(tyre_id: str, db: Session = Depends(get_db)):
    """
    Evaluates first-order heat/cooling model, temperature residual, slope, and abnormal trajectory.
    """
    reading = (
        db.query(SensorReading)
        .filter(SensorReading.tyre_id == tyre_id)
        .order_by(SensorReading.timestamp.desc())
        .first()
    )

    current_temp = reading.tyre_temp_c if reading else 65.0
    payload = reading.payload_t if reading else 280.0
    speed = reading.speed_kmh if reading else 25.0
    press = reading.pressure_kpa if reading else 735.0
    ambient = reading.ambient_temp_c if reading else 34.0
    is_idle = (speed < 1.0)

    # Get recent historical temperatures for slope calculation
    recent_readings = (
        db.query(SensorReading)
        .filter(SensorReading.tyre_id == tyre_id)
        .order_by(SensorReading.timestamp.desc())
        .limit(10)
        .all()
    )
    hist_temps = [r.tyre_temp_c for r in reversed(recent_readings)] if recent_readings else [current_temp - 2.0, current_temp]

    return temp_model_instance.predict_temperature_step(
        current_temp_c=current_temp,
        payload_t=payload,
        speed_kmh=speed,
        pressure_kpa=press,
        ambient_temp_c=ambient,
        is_idle=is_idle,
        historical_temps=hist_temps
    )

@router.get("/wear-projection/{tyre_id}")
def get_tyre_wear_projection(tyre_id: str, db: Session = Depends(get_db)):
    """
    Computes robust linear wear rate (mm/h) and 90-day wear projection band.
    Strictly termed 'wear_projection', NOT RUL.
    """
    tyre = db.query(Tyre).filter(Tyre.tyre_id == tyre_id).first()
    init_tread = tyre.initial_tread_mm if tyre else 85.0

    reading = (
        db.query(SensorReading)
        .filter(SensorReading.tyre_id == tyre_id)
        .order_by(SensorReading.timestamp.desc())
        .first()
    )
    press = reading.pressure_kpa if reading else 730.0
    payload = reading.payload_t if reading else 280.0
    speed = reading.speed_kmh if reading else 25.0

    tkph_rec = (
        db.query(TKPHRecord)
        .filter(TKPHRecord.tyre_id == tyre_id)
        .order_by(TKPHRecord.timestamp.desc())
        .first()
    )
    tkph_val = tkph_rec.tkph if tkph_rec else 1450.0

    return wear_model_instance.estimate_wear_and_projection(
        tyre_id=tyre_id,
        initial_tread_mm=init_tread,
        current_tread_mm=65.0,
        operating_hours=500.0,
        avg_payload_t=payload,
        avg_speed_kmh=speed,
        avg_tkph=tkph_val,
        avg_pressure_kpa=press
    )

@router.post("/calibrate-temperature")
def calibrate_temperature_model(db: Session = Depends(get_db)):
    """
    Calibrates Ridge Regression thermal model using chronological 70/30 train/test split.
    """
    readings = db.query(SensorReading).order_by(SensorReading.timestamp.asc()).all()
    if not readings:
        raise HTTPException(status_code=400, detail="No sensor readings available for calibration")

    data = []
    for r in readings:
        data.append({
            'timestamp': r.timestamp,
            'tyre_temp_c': r.tyre_temp_c,
            'payload_t': r.payload_t,
            'speed_kmh': r.speed_kmh,
            'pressure_kpa': r.pressure_kpa,
            'ambient_temp_c': r.ambient_temp_c,
            'is_idle': (r.speed_kmh < 1.0)
        })

    df = pd.DataFrame(data)
    res = temp_model_instance.fit_chronological(df)
    return res
