from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.connection import Base

class Truck(Base):
    __tablename__ = "trucks"

    truck_id = Column(String, primary_key=True, index=True)
    model = Column(String, nullable=False)
    payload_capacity_t = Column(Float, nullable=False)
    mine_id = Column(String, nullable=False)
    status = Column(String, default="active") # active, idle, maintenance, offline

    fitments = relationship("TyreFitment", back_populates="truck")
    readings = relationship("SensorReading", back_populates="truck")
    inspections = relationship("DamageInspection", back_populates="truck")
    impact_events = relationship("ImpactEvent", back_populates="truck")

class Tyre(Base):
    __tablename__ = "tyres"

    tyre_id = Column(String, primary_key=True, index=True)
    manufacturer = Column(String, nullable=False)
    model = Column(String, nullable=False)
    size = Column(String, nullable=False)
    rated_tkph = Column(Float, nullable=False)
    install_date = Column(String, nullable=False)
    initial_tread_mm = Column(Float, nullable=False)
    cost = Column(Float, nullable=False)
    status = Column(String, default="active")

    fitments = relationship("TyreFitment", back_populates="tyre")
    readings = relationship("SensorReading", back_populates="tyre")
    tkph_records = relationship("TKPHRecord", back_populates="tyre")
    inspections = relationship("DamageInspection", back_populates="tyre")
    maintenance_records = relationship("Maintenance", back_populates="tyre")
    failures = relationship("Failure", back_populates="tyre")

class TyreFitment(Base):
    __tablename__ = "tyre_fitments"

    fitment_id = Column(String, primary_key=True, index=True)
    tyre_id = Column(String, ForeignKey("tyres.tyre_id"), nullable=False)
    truck_id = Column(String, ForeignKey("trucks.truck_id"), nullable=False)
    position = Column(String, nullable=False) # front_left, front_right, etc.
    installed_at = Column(DateTime, default=datetime.utcnow)
    removed_at = Column(DateTime, nullable=True)
    installation_hours = Column(Float, nullable=True)
    removal_reason = Column(String, nullable=True)

    tyre = relationship("Tyre", back_populates="fitments")
    truck = relationship("Truck", back_populates="fitments")

class SensorReading(Base):
    __tablename__ = "sensor_readings"

    reading_id = Column(String, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    truck_id = Column(String, ForeignKey("trucks.truck_id"), nullable=False)
    tyre_id = Column(String, ForeignKey("tyres.tyre_id"), nullable=False)
    position = Column(String, nullable=False)
    pressure_kpa = Column(Float, nullable=False)
    tyre_temp_c = Column(Float, nullable=False)
    ambient_temp_c = Column(Float, nullable=False)
    payload_t = Column(Float, nullable=False)
    speed_kmh = Column(Float, nullable=False)
    gps_lat = Column(Float, nullable=False)
    gps_lon = Column(Float, nullable=False)
    imu_ax = Column(Float, default=0.0)
    imu_ay = Column(Float, default=0.0)
    imu_az = Column(Float, default=0.0)
    gyro_x = Column(Float, nullable=True)
    gyro_y = Column(Float, nullable=True)
    gyro_z = Column(Float, nullable=True)
    source = Column(String, default="simulator")
    quality_flag = Column(String, default="good")

    truck = relationship("Truck", back_populates="readings")
    tyre = relationship("Tyre", back_populates="readings")

class OperationWindow(Base):
    __tablename__ = "operation_windows"

    window_id = Column(String, primary_key=True, index=True)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    truck_id = Column(String, ForeignKey("trucks.truck_id"), nullable=False)
    route_id = Column(String, nullable=False)
    distance_km = Column(Float, nullable=False)
    mean_payload_t = Column(Float, nullable=False)
    mean_speed_kmh = Column(Float, nullable=False)
    ambient_temp_c = Column(Float, nullable=False)
    idle_seconds = Column(Float, default=0.0)
    loaded_seconds = Column(Float, default=0.0)
    empty_seconds = Column(Float, default=0.0)

class TKPHRecord(Base):
    __tablename__ = "tkph_records"

    record_id = Column(String, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    tyre_id = Column(String, ForeignKey("tyres.tyre_id"), nullable=False)
    mean_tyre_load_t = Column(Float, nullable=False)
    awss_kmh = Column(Float, nullable=False)
    tkph = Column(Float, nullable=False)
    rated_tkph = Column(Float, nullable=False)
    exceedance_ratio = Column(Float, nullable=False)
    exceedance_minutes = Column(Float, default=0.0)
    method_version = Column(String, default="rolling_v1")

    tyre = relationship("Tyre", back_populates="tkph_records")

class DamageInspection(Base):
    __tablename__ = "damage_inspections"

    inspection_id = Column(String, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    tyre_id = Column(String, ForeignKey("tyres.tyre_id"), nullable=False)
    truck_id = Column(String, ForeignKey("trucks.truck_id"), nullable=True)
    image_id = Column(String, nullable=False)
    damage_present = Column(Boolean, nullable=False)
    damage_type = Column(String, nullable=True) # cut, crack, puncture, embedded_object, tear, abrasion, unknown
    location = Column(String, nullable=True) # tread, shoulder, sidewall, bead, unknown
    severity = Column(String, nullable=True) # minor, moderate, severe
    confidence = Column(Float, default=0.0)
    bbox_json = Column(Text, nullable=True) # JSON string representation of bbox
    model_version = Column(String, default="yolov8n-tyredmg-v0.1")
    reviewer_status = Column(String, default="pending") # pending, confirmed, rejected
    source = Column(String, default="vision_model")

    tyre = relationship("Tyre", back_populates="inspections")
    truck = relationship("Truck", back_populates="inspections")

class ImpactEvent(Base):
    __tablename__ = "impact_events"

    event_id = Column(String, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    truck_id = Column(String, ForeignKey("trucks.truck_id"), nullable=False)
    tyre_id_or_null = Column(String, ForeignKey("tyres.tyre_id"), nullable=True)
    gps_lat = Column(Float, nullable=False)
    gps_lon = Column(Float, nullable=False)
    peak_accel_g = Column(Float, nullable=False)
    jerk = Column(Float, nullable=True)
    duration_ms = Column(Float, nullable=True)
    event_type = Column(String, default="imu_impact")
    severity = Column(String, default="medium")
    road_segment_id = Column(String, nullable=False)

    truck = relationship("Truck", back_populates="impact_events")

class Maintenance(Base):
    __tablename__ = "maintenance"

    maintenance_id = Column(String, primary_key=True, index=True)
    tyre_id = Column(String, ForeignKey("tyres.tyre_id"), nullable=False)
    truck_id = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    action = Column(String, nullable=False)
    reason = Column(String, nullable=False)
    labour_cost = Column(Float, nullable=True)
    parts_cost = Column(Float, nullable=True)
    downtime_hours = Column(Float, nullable=True)
    tread_after_mm = Column(Float, nullable=True)

    tyre = relationship("Tyre", back_populates="maintenance_records")

class Failure(Base):
    __tablename__ = "failures"

    failure_id = Column(String, primary_key=True, index=True)
    tyre_id = Column(String, ForeignKey("tyres.tyre_id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    failure_mode = Column(String, nullable=False)
    cause = Column(String, nullable=False)
    downtime_hours = Column(Float, nullable=True)
    replacement_cost = Column(Float, nullable=True)
    confirmed_by = Column(String, nullable=False)

    tyre = relationship("Tyre", back_populates="failures")
