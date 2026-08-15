from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict
from datetime import datetime

# --- TELEMETRY ---
class TelemetryCreate(BaseModel):
    timestamp: Optional[datetime] = None
    truck_id: str
    tyre_id: str
    position: str
    pressure_kpa: float
    tyre_temp_c: float
    ambient_temp_c: float = 34.0
    payload_t: float = 0.0
    speed_kmh: float = 0.0
    gps_lat: float = 20.123
    gps_lon: float = 79.123
    imu_ax: float = 0.0
    imu_ay: float = 0.0
    imu_az: float = 0.0
    gyro_x: Optional[float] = None
    gyro_y: Optional[float] = None
    gyro_z: Optional[float] = None
    source: str = "simulator"

class TelemetryResponse(BaseModel):
    status: str = "accepted"
    reading_id: str
    quality_flag: str = "good"

class TelemetryReadingOut(BaseModel):
    reading_id: str
    timestamp: datetime
    truck_id: str
    tyre_id: str
    position: str
    pressure_kpa: float
    tyre_temp_c: float
    ambient_temp_c: float
    payload_t: float
    speed_kmh: float
    gps_lat: float
    gps_lon: float
    imu_ax: float
    imu_ay: float
    imu_az: float
    source: str
    quality_flag: str

    class Config:
        from_attributes = True

# --- TRUCK ---
class TruckOut(BaseModel):
    truck_id: str
    model: str
    payload_capacity_t: float
    mine_id: str
    status: str
    current_speed_kmh: float = 0.0
    current_payload_t: float = 0.0
    gps_lat: float = 20.1234
    gps_lon: float = 79.0456
    total_tyres: int = 6
    highest_risk: str = "LOW"
    current_alert: Optional[str] = None
    last_update: Optional[str] = None
    source: str = "simulator"

    class Config:
        from_attributes = True

class TruckLiveTelemetry(BaseModel):
    truck_id: str
    status: str
    current_speed_kmh: float
    current_payload_t: float
    gps_lat: float
    gps_lon: float
    tyres: List[Dict[str, Any]]
    last_update: str

# --- TYRE ---
class TyreOut(BaseModel):
    tyre_id: str
    truck_id: str
    fitment_id: str
    position: str
    manufacturer: str
    model: str
    size: str
    rated_tkph: float
    install_date: str
    initial_tread_mm: float
    current_tread_mm: float
    cost: float
    status: str
    current_pressure_kpa: float
    current_temp_c: float
    ambient_temp_c: float
    tkph_current: float
    tkph_rated: float
    tkph_exceedance_ratio: float
    wear_rate_mm_per_h: Optional[float] = 0.005
    risk_score: float
    risk_label: str
    last_update: str
    source: str = "simulator"

    class Config:
        from_attributes = True

# --- RISK ---
class RiskResponse(BaseModel):
    tyre_id: str
    timestamp: str
    risk_score: float
    risk_label: str
    reasons: List[str]
    recommended_action: str
    data_confidence: float = 0.91
    stress_inputs: Optional[Dict[str, float]] = None
    source: str = "fuzzy_risk_engine"

# --- INSPECTION / VISION ---
class InspectionCreate(BaseModel):
    tyre_id: str
    truck_id: Optional[str] = None
    image_id: Optional[str] = "IMG_UPLOAD"
    damage_present: bool
    damage_type: Optional[str] = "unknown"
    location: Optional[str] = "unknown"
    severity: Optional[str] = "minor"
    confidence: float = 0.85
    bbox: Optional[List[float]] = None
    model_version: str = "yolov8n-tyredmg-v0.1"

class InspectionResponse(BaseModel):
    inspection_id: Optional[str] = None
    image_id: str
    tyre_id: Optional[str] = None
    truck_id: Optional[str] = None
    damage_present: bool
    damage_type: Optional[str] = None
    location: Optional[str] = None
    severity: Optional[str] = None
    confidence: float
    bbox: Optional[List[float]] = None
    model_version: str
    source: str = "vision_model"

class VisionDetectionItem(BaseModel):
    cls_name: str
    confidence: float
    bbox: List[float]

class VisionPredictResponse(BaseModel):
    image_id: str
    tyre_id: Optional[str] = None
    damage_present: bool
    detections: List[Dict[str, Any]]
    model_version: str = "yolov8n-tire-damage-v1.0"
    quality_warning: bool = False
    warning_reason: Optional[str] = None

# --- IMPACT EVENT ---
class ImpactEventCreate(BaseModel):
    truck_id: str
    tyre_id_or_null: Optional[str] = None
    gps_lat: float
    gps_lon: float
    peak_accel_g: float
    jerk: Optional[float] = None
    duration_ms: Optional[float] = None
    event_type: str = "imu_impact"
    severity: str = "medium"
    road_segment_id: str

class ImpactEventResponse(BaseModel):
    event_id: str
    status: str = "accepted"
    road_segment_id: str

# --- HOTSPOT ---
class HotspotResponse(BaseModel):
    road_segment_id: str
    name: str
    truck_km: float
    impact_events: int
    damage_events: int
    failure_events: int
    impact_rate_per_100_truck_km: float
    damage_rate_per_100_truck_km: float
    failure_rate_per_100_truck_km: float
    hotspot_score: float
    hotspot_type: Optional[str] = "impact"

# --- MAINTENANCE ---
class MaintenancePriorityOut(BaseModel):
    priority: int
    tyre_id: str
    truck_id: str
    risk_label: str
    risk_score: float
    main_reason: str
    damage: str
    pressure_kpa: float
    temperature_c: float
    tkph_current: float
    tkph_rated: float
    recommended_action: str
    data_confidence: float = 0.91
    source: str = "simulator"

# --- ALERT ---
class AlertOut(BaseModel):
    alert_id: str
    timestamp: str
    type: str
    severity: str
    truck_id: str
    tyre_id: Optional[str] = None
    message: str
    status: str
    source: str = "simulator"

# --- DASHBOARD SUMMARY ---
class DashboardSummaryOut(BaseModel):
    total_trucks: int
    active_trucks: int
    total_tyres: int
    high_risk_tyres: int
    medium_risk_tyres: int
    low_risk_tyres: int
    active_alerts: int
    critical_maintenance: int
    avg_temperature_c: float
    avg_pressure_kpa: float
    avg_tkph: float
    road_hotspot_count: int

# --- SIMULATION ---
class SimulationRequest(BaseModel):
    scenario_id: str = "normal_cycle" # normal_cycle, pressure_leak, tkph_exceedance, impact_cluster
    truck_id: Optional[str] = "DUMPER_01"
    tyre_id: Optional[str] = "TYRE_01_FL"
    duration_seconds: int = 60

class SimulationResponse(BaseModel):
    status: str = "started"
    scenario_id: str
    generated_records: int
