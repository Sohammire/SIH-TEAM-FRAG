from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid

from app.database.connection import get_db
from app.schemas.all_schemas import (
    TelemetryCreate, TelemetryResponse, ImpactEventCreate, ImpactEventResponse,
    SimulationRequest, SimulationResponse
)
from app.services import telemetry_service
from app.services.simulator_service import generate_telemetry_scenario, SUPPORTED_SCENARIOS
from app.services.imu_engine import process_imu_impact_stream
from app.services.mqtt_service import mqtt_manager
from app.models import ImpactEvent

router = APIRouter(tags=["Telemetry & Sensors"])

@router.post("/telemetry", response_model=TelemetryResponse, status_code=status.HTTP_201_CREATED)
def ingest_telemetry(data: TelemetryCreate, db: Session = Depends(get_db)):
    """
    Ingests TPMS and IIoT sensor telemetry.
    Maintains traceability: truck_id -> tyre_id -> fitment_id -> wheel_position -> timestamp
    Submits to MQTT topic mine/{mine_id}/truck/{truck_id}/tyre/{tyre_id}/telemetry
    """
    try:
        res = telemetry_service.process_telemetry(db, data)
        
        # Publish payload to MQTT topic
        payload = data.model_dump()
        payload["reading_id"] = res.reading_id
        mqtt_manager.publish_telemetry("MINE_ALPHA", data.truck_id, data.tyre_id, payload)
        
        return res
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/impact-events", response_model=ImpactEventResponse, status_code=status.HTTP_201_CREATED)
def record_impact_event(data: ImpactEventCreate, db: Session = Depends(get_db)):
    """
    Records IMU acceleration impact event tied to road segment.
    Submits IMU impact payload to MQTT topic mine/{mine_id}/truck/{truck_id}/imu
    """
    evt_id = f"EVT_{uuid.uuid4().hex[:8].upper()}"
    evt = ImpactEvent(
        event_id=evt_id,
        truck_id=data.truck_id,
        tyre_id_or_null=data.tyre_id_or_null,
        gps_lat=data.gps_lat,
        gps_lon=data.gps_lon,
        peak_accel_g=data.peak_accel_g,
        jerk=data.jerk,
        duration_ms=data.duration_ms,
        event_type=data.event_type,
        severity=data.severity,
        road_segment_id=data.road_segment_id
    )
    db.add(evt)
    db.commit()

    mqtt_manager.publish_imu("MINE_ALPHA", data.truck_id, data.model_dump())

    return ImpactEventResponse(
        event_id=evt_id,
        status="accepted",
        road_segment_id=data.road_segment_id
    )

@router.post("/telemetry/simulate")
def trigger_telemetry_simulation(req: SimulationRequest, db: Session = Depends(get_db)):
    """
    Simulates real-time telemetry stream scenarios (8 scenarios: normal_cycle, pressure_leak, etc).
    Publishes generated streams over MQTT topics and persists to DB.
    Every sample contains scenario_id.
    """
    scen_id = req.scenario_id if req.scenario_id in SUPPORTED_SCENARIOS else "normal_cycle"
    samples = generate_telemetry_scenario(
        scenario_id=scen_id,
        truck_id=req.truck_id or "DUMPER_01",
        tyre_id=req.tyre_id or "TYRE_01_FL",
        num_samples=10
    )

    processed_cnt = 0
    for sample in samples:
        # Publish MQTT
        mqtt_manager.publish_telemetry("MINE_ALPHA", sample["truck_id"], sample["tyre_id"], sample)
        
        # Check IMU impact detection
        if sample.get("imu_az", 1.0) > 2.2 or sample.get("imu_ax", 0.0) > 2.0:
            process_imu_impact_stream(
                db=db,
                truck_id=sample["truck_id"],
                gps_lat=sample["gps_lat"],
                gps_lon=sample["gps_lon"],
                imu_ax=sample["imu_ax"],
                imu_ay=sample["imu_ay"],
                imu_az=sample["imu_az"],
                tyre_id_or_null=sample["tyre_id"],
                road_segment_id="RS_04"
            )

        processed_cnt += 1

    return {
        "status": "started",
        "scenario_id": scen_id,
        "generated_records": processed_cnt,
        "sample_preview": samples[0] if samples else None
    }
