from typing import Dict, Any, List, Optional
from app.services.fuzzy_risk_engine import evaluate_mamdani_fuzzy_risk

def calculate_tyre_risk(
    pressure_kpa: Optional[float] = 735.0,
    tyre_temp_c: Optional[float] = 62.0,
    tkph_current: Optional[float] = 1400.0,
    rated_tkph: float = 1800.0,
    damage_present: bool = False,
    damage_severity: str = "none", # minor, moderate, severe
    damage_type: str = "none",
    damage_location: str = "none",
    wear_rate: float = 0.005,
    recent_impact_g: float = 0.0,
    has_missing_data: bool = False
) -> Dict[str, Any]:
    """
    Explainable Tyre Failure-Risk Service wrapper around scikit-fuzzy Mamdani engine.
    
    IMPORTANT: This is an explainable risk score.
    Do NOT call it a calibrated probability of failure.
    """
    # Handle missing telemetry data -> reduced confidence
    if pressure_kpa is None or tyre_temp_c is None:
        has_missing_data = True
        pressure_kpa = pressure_kpa or 735.0
        tyre_temp_c = tyre_temp_c or 62.0

    # 1. Stress Normalization (0-100)
    # Pressure stress
    if pressure_kpa < 600:
        pressure_stress = min(100.0, 50.0 + (600 - pressure_kpa) * 0.4)
    else:
        pressure_diff = abs(735.0 - pressure_kpa)
        pressure_stress = min(100.0, (pressure_diff / 150.0) * 50.0)

    # Thermal stress
    if tyre_temp_c > 65.0:
        thermal_stress = min(100.0, ((tyre_temp_c - 65.0) / 25.0) * 100.0)
    else:
        thermal_stress = max(0.0, (tyre_temp_c / 65.0) * 20.0)

    # TKPH stress
    tkph_ratio = (tkph_current / rated_tkph) if (rated_tkph and rated_tkph > 0 and tkph_current) else 1.0
    if tkph_ratio > 1.0:
        tkph_stress = min(100.0, 50.0 + (tkph_ratio - 1.0) * 250.0)
    else:
        tkph_stress = tkph_ratio * 40.0

    # Damage stress
    damage_map = {"none": 0.0, "minor": 25.0, "moderate": 60.0, "severe": 90.0}
    damage_stress = damage_map.get(damage_severity.lower(), 0.0)
    if damage_present and damage_stress == 0.0:
        damage_stress = 35.0

    # Wear stress
    wear_stress = min(100.0, (wear_rate / 0.01) * 50.0)

    # Impact stress
    impact_stress = min(100.0, (recent_impact_g / 5.0) * 100.0)

    # 2. Run Mamdani Fuzzy System Evaluation
    return evaluate_mamdani_fuzzy_risk(
        thermal_stress=thermal_stress,
        pressure_stress=pressure_stress,
        tkph_stress=tkph_stress,
        damage_stress=damage_stress,
        wear_stress=wear_stress,
        impact_stress=impact_stress,
        pressure_kpa=pressure_kpa,
        tyre_temp_c=tyre_temp_c,
        tkph_current=tkph_current,
        rated_tkph=rated_tkph,
        damage_present=damage_present,
        damage_type=damage_type,
        damage_severity=damage_severity,
        damage_location=damage_location,
        has_missing_data=has_missing_data
    )
