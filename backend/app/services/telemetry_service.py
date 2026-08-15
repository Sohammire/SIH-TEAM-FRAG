import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from app.models import SensorReading, TKPHRecord
from app.schemas.all_schemas import TelemetryCreate, TelemetryResponse

def process_telemetry(db: Session, data: TelemetryCreate) -> TelemetryResponse:
    """
    Ingests sensor telemetry and updates traceability chain:
    truck_id -> tyre_id -> fitment_id -> wheel_position -> timestamp
    """
    reading_id = f"READ_{uuid.uuid4().hex[:8].upper()}"
    ts = data.timestamp or datetime.utcnow()

    reading = SensorReading(
        reading_id=reading_id,
        timestamp=ts,
        truck_id=data.truck_id,
        tyre_id=data.tyre_id,
        position=data.position,
        pressure_kpa=data.pressure_kpa,
        tyre_temp_c=data.tyre_temp_c,
        ambient_temp_c=data.ambient_temp_c,
        payload_t=data.payload_t,
        speed_kmh=data.speed_kmh,
        gps_lat=data.gps_lat,
        gps_lon=data.gps_lon,
        imu_ax=data.imu_ax,
        imu_ay=data.imu_ay,
        imu_az=data.imu_az,
        gyro_x=data.gyro_x,
        gyro_y=data.gyro_y,
        gyro_z=data.gyro_z,
        source=data.source,
        quality_flag="good" if (400 <= data.pressure_kpa <= 900) else "suspect"
    )

    db.add(reading)

    # Compute rolling TKPH entry
    load_per_tyre = (data.payload_t / 6.0) if data.payload_t > 0 else 0.0
    tkph_val = round(load_per_tyre * data.speed_kmh * 2.5, 1)
    
    tkph_rec = TKPHRecord(
        record_id=f"TKPH_{uuid.uuid4().hex[:8].upper()}",
        timestamp=ts,
        tyre_id=data.tyre_id,
        mean_tyre_load_t=load_per_tyre,
        awss_kmh=data.speed_kmh,
        tkph=tkph_val,
        rated_tkph=1800.0,
        exceedance_ratio=round(tkph_val / 1800.0, 2),
        exceedance_minutes=5.0 if tkph_val > 1800.0 else 0.0
    )
    db.add(tkph_rec)

    db.commit()

    return TelemetryResponse(
        status="accepted",
        reading_id=reading_id,
        quality_flag=reading.quality_flag
    )
