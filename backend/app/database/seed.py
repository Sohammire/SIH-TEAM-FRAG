import json
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models import (
    Truck, Tyre, TyreFitment, SensorReading,
    TKPHRecord, DamageInspection, ImpactEvent, Maintenance, Failure
)

POSITIONS = [
    'front_left', 'front_right',
    'rear_left_inner', 'rear_left_outer',
    'rear_right_inner', 'rear_right_outer'
]

TRUCK_IDS = [f"DUMPER_{i:02d}" for i in range(1, 9)]

def seed_database(db: Session):
    # Check if database is already seeded
    if db.query(Truck).first():
        return

    now = datetime.utcnow()

    # 1. Seed Trucks
    truck_models = ["CAT 797F", "Komatsu 980E-5", "CAT 797F", "Liebherr T 282C", "Komatsu 980E-5", "CAT 797F", "Liebherr T 282C", "CAT 797F"]
    truck_statuses = ["active", "active", "active", "idle", "maintenance", "active", "active", "active"]
    mine_ids = ["MINE_ALPHA", "MINE_ALPHA", "MINE_ALPHA", "MINE_BETA", "MINE_BETA", "MINE_ALPHA", "MINE_ALPHA", "MINE_BETA"]
    speeds = [32.0, 18.0, 25.0, 0.0, 0.0, 28.0, 15.0, 30.0]
    payloads = [280.0, 340.0, 150.0, 0.0, 0.0, 310.0, 220.0, 260.0]
    lats = [20.1234, 20.1256, 20.1198, 20.1301, 20.1278, 20.1212, 20.1245, 20.1189]
    lons = [79.0456, 79.0512, 79.0478, 79.0534, 79.0501, 79.0489, 79.0523, 79.0445]

    for i, t_id in enumerate(TRUCK_IDS):
        truck = Truck(
            truck_id=t_id,
            model=truck_models[i],
            payload_capacity_t=400.0 if "CAT" in truck_models[i] else 370.0,
            mine_id=mine_ids[i],
            status=truck_statuses[i]
        )
        db.add(truck)
    db.commit()

    # 2. Seed Tyres & Fitments
    tyre_counter = 1
    for t_idx, t_id in enumerate(TRUCK_IDS):
        for pos_idx, pos in enumerate(POSITIONS):
            pos_abbr = "".join([w[0].upper() for w in pos.split('_')])
            tyre_id = f"TYRE_{t_idx+1:02d}_{pos_abbr}"
            fitment_id = f"FIT_{tyre_id}"
            
            # Tyre specs
            tyre = Tyre(
                tyre_id=tyre_id,
                manufacturer="Michelin" if pos_idx % 2 == 0 else "Bridgestone",
                model="XDR3" if pos_idx % 2 == 0 else "VRPS",
                size="59/80R63",
                rated_tkph=1800.0,
                install_date="2026-01-15",
                initial_tread_mm=85.0,
                cost=45000.0 + (pos_idx * 1000),
                status="active"
            )
            db.add(tyre)

            fitment = TyreFitment(
                fitment_id=fitment_id,
                tyre_id=tyre_id,
                truck_id=t_id,
                position=pos,
                installed_at=now - timedelta(days=120)
            )
            db.add(fitment)

            # Seed Telemetry reading for each tyre
            # Specific high-risk scenarios
            pressure = 735.0
            temp = 62.0
            if tyre_id == "TYRE_03_RRO": # Severe cut + pressure loss
                pressure = 580.0
                temp = 92.0
            elif tyre_id == "TYRE_07_RRI": # Rapid pressure loss
                pressure = 610.0
                temp = 85.0
            elif tyre_id == "TYRE_02_FL": # TKPH exceedance
                pressure = 730.0
                temp = 78.0

            reading = SensorReading(
                reading_id=f"READ_{tyre_id}_01",
                timestamp=now,
                truck_id=t_id,
                tyre_id=tyre_id,
                position=pos,
                pressure_kpa=pressure,
                tyre_temp_c=temp,
                ambient_temp_c=34.0,
                payload_t=payloads[t_idx],
                speed_kmh=speeds[t_idx],
                gps_lat=lats[t_idx],
                gps_lon=lons[t_idx],
                source="simulator",
                quality_flag="good"
            )
            db.add(reading)

            # TKPH Record
            tkph_val = 1400.0
            if tyre_id == "TYRE_03_RRO":
                tkph_val = 2124.0
            elif tyre_id == "TYRE_02_FL":
                tkph_val = 2016.0

            tkph_rec = TKPHRecord(
                record_id=f"TKPH_{tyre_id}_01",
                timestamp=now,
                tyre_id=tyre_id,
                mean_tyre_load_t=payloads[t_idx] / 6.0,
                awss_kmh=speeds[t_idx],
                tkph=tkph_val,
                rated_tkph=1800.0,
                exceedance_ratio=round(tkph_val / 1800.0, 2),
                exceedance_minutes=35.0 if tkph_val > 1800 else 0.0
            )
            db.add(tkph_rec)

    # 3. Seed Inspections
    inspections_data = [
        ("INS_001", "IMG_001", "TYRE_03_RRO", "DUMPER_03", True, "cut", "sidewall", "severe", 0.91, json.dumps([120, 80, 340, 260])),
        ("INS_002", "IMG_002", "TYRE_05_RLI", "DUMPER_05", True, "embedded_object", "tread", "moderate", 0.84, json.dumps([200, 150, 310, 240])),
        ("INS_003", "IMG_003", "TYRE_01_FL", "DUMPER_01", False, None, None, None, 0.96, None),
        ("INS_004", "IMG_004", "TYRE_07_RRI", "DUMPER_07", True, "crack", "shoulder", "minor", 0.72, json.dumps([150, 200, 280, 260]))
    ]
    for ins in inspections_data:
        insp = DamageInspection(
            inspection_id=ins[0],
            image_id=ins[1],
            tyre_id=ins[2],
            truck_id=ins[3],
            timestamp=now - timedelta(minutes=15),
            damage_present=ins[4],
            damage_type=ins[5],
            location=ins[6],
            severity=ins[7],
            confidence=ins[8],
            bbox_json=ins[9],
            model_version="yolov8n-tyredmg-v0.1",
            reviewer_status="pending",
            source="vision_model"
        )
        db.add(insp)

    # 4. Seed Impact Events
    impacts = [
        ("EVT_001", "DUMPER_03", "TYRE_03_RRO", 20.123, 79.123, 3.5, 45.0, 120.0, "imu_impact", "high", "RS_04"),
        ("EVT_002", "DUMPER_07", "TYRE_07_RRI", 20.125, 79.125, 2.8, 30.0, 90.0, "imu_impact", "medium", "RS_02"),
        ("EVT_003", "DUMPER_02", None, 20.120, 79.120, 4.2, 55.0, 150.0, "imu_impact", "high", "RS_07")
    ]
    for imp in impacts:
        evt = ImpactEvent(
            event_id=imp[0],
            truck_id=imp[1],
            tyre_id_or_null=imp[2],
            gps_lat=imp[3],
            gps_lon=imp[4],
            peak_accel_g=imp[5],
            jerk=imp[6],
            duration_ms=imp[7],
            event_type=imp[8],
            severity=imp[9],
            road_segment_id=imp[10]
        )
        db.add(evt)

    # 5. Seed Maintenance
    maint_list = [
        ("MNT_001", "TYRE_03_RRO", "DUMPER_03", "Inspect and replace", "Severe sidewall cut + pressure loss", 150.0, 45000.0, 4.0, 0.0),
        ("MNT_002", "TYRE_07_RRI", "DUMPER_07", "Check valve and tread", "Rapid pressure loss — possible puncture", 50.0, 0.0, 1.0, 65.0)
    ]
    for m in maint_list:
        db.add(Maintenance(
            maintenance_id=m[0],
            tyre_id=m[1],
            truck_id=m[2],
            timestamp=now - timedelta(hours=2),
            action=m[3],
            reason=m[4],
            labour_cost=m[5],
            parts_cost=m[6],
            downtime_hours=m[7],
            tread_after_mm=m[8]
        ))

    db.commit()
