import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
from typing import Dict, Any, List, Optional

def build_mamdani_fuzzy_system():
    """
    Constructs scikit-fuzzy Mamdani Control System for Tyre Failure-Risk evaluation.
    """
    # 1. Antecedents (Inputs 0-100)
    thermal = ctrl.Antecedent(np.arange(0, 101, 1), 'thermal_stress')
    pressure = ctrl.Antecedent(np.arange(0, 101, 1), 'pressure_stress')
    tkph = ctrl.Antecedent(np.arange(0, 101, 1), 'tkph_stress')
    damage = ctrl.Antecedent(np.arange(0, 101, 1), 'damage_stress')
    wear = ctrl.Antecedent(np.arange(0, 101, 1), 'wear_stress')
    impact = ctrl.Antecedent(np.arange(0, 101, 1), 'impact_stress')

    # Consequent (Output 0-100)
    risk = ctrl.Consequent(np.arange(0, 101, 1), 'risk_score')

    # 2. Membership Functions
    # Pressure
    pressure['normal'] = fuzz.trimf(pressure.universe, [0, 0, 25])
    pressure['low'] = fuzz.trimf(pressure.universe, [15, 37.5, 60])
    pressure['critical'] = fuzz.trapmf(pressure.universe, [50, 75, 100, 100])

    # Thermal
    thermal['normal'] = fuzz.trimf(thermal.universe, [0, 0, 30])
    thermal['elevated'] = fuzz.trimf(thermal.universe, [20, 45, 70])
    thermal['critical'] = fuzz.trapmf(thermal.universe, [60, 80, 100, 100])

    # TKPH
    tkph['normal'] = fuzz.trimf(tkph.universe, [0, 0, 40])
    tkph['high'] = fuzz.trimf(tkph.universe, [30, 55, 80])
    tkph['excessive'] = fuzz.trapmf(tkph.universe, [70, 85, 100, 100])

    # Damage
    damage['none'] = fuzz.trimf(damage.universe, [0, 0, 15])
    damage['minor'] = fuzz.trimf(damage.universe, [10, 22.5, 35])
    damage['moderate'] = fuzz.trimf(damage.universe, [30, 50, 70])
    damage['severe'] = fuzz.trapmf(damage.universe, [65, 82.5, 100, 100])

    # Wear
    wear['low'] = fuzz.trimf(wear.universe, [0, 0, 40])
    wear['medium'] = fuzz.trimf(wear.universe, [30, 52.5, 75])
    wear['high'] = fuzz.trapmf(wear.universe, [65, 82.5, 100, 100])

    # Impact
    impact['low'] = fuzz.trimf(impact.universe, [0, 0, 35])
    impact['medium'] = fuzz.trimf(impact.universe, [25, 47.5, 70])
    impact['high'] = fuzz.trapmf(impact.universe, [60, 80, 100, 100])

    # Risk Score Output
    risk['low'] = fuzz.trimf(risk.universe, [0, 0, 35])
    risk['medium'] = fuzz.trimf(risk.universe, [25, 47.5, 70])
    risk['high'] = fuzz.trapmf(risk.universe, [60, 80, 100, 100])

    # Defuzzification method: Centroid
    risk.defuzzify_method = 'centroid'

    # 3. Transparent Safety Rules
    r1 = ctrl.Rule(pressure['critical'], risk['high'])
    r2 = ctrl.Rule(thermal['critical'], risk['high'])
    r3 = ctrl.Rule(damage['severe'], risk['high'])
    r4 = ctrl.Rule(damage['moderate'] & (pressure['low'] | pressure['critical']), risk['high'])
    r5 = ctrl.Rule(tkph['excessive'] & (thermal['elevated'] | thermal['critical']), risk['high'])
    r6 = ctrl.Rule(wear['high'] & (thermal['elevated'] | thermal['critical']), risk['high'])
    r7 = ctrl.Rule(impact['high'] & damage['moderate'], risk['high'])
    r8 = ctrl.Rule(thermal['elevated'] & pressure['low'], risk['high'])
    
    # Compound medium/high rules
    r9 = ctrl.Rule((thermal['elevated'] & tkph['high']) | (pressure['low'] & tkph['high']), risk['high'])
    r10 = ctrl.Rule(damage['minor'] & thermal['elevated'], risk['medium'])
    r11 = ctrl.Rule(wear['medium'] & (thermal['elevated'] | tkph['high']), risk['medium'])
    r12 = ctrl.Rule(impact['medium'] & (damage['minor'] | pressure['low']), risk['medium'])
    
    # Low risk rule
    r13 = ctrl.Rule(
        thermal['normal'] & pressure['normal'] & tkph['normal'] & 
        damage['none'] & wear['low'] & impact['low'],
        risk['low']
    )
    r14 = ctrl.Rule(
        thermal['normal'] & pressure['normal'] & tkph['normal'] & damage['none'],
        risk['low']
    )

    rules = [r1, r2, r3, r4, r5, r6, r7, r8, r9, r10, r11, r12, r13, r14]

    risk_ctrl = ctrl.ControlSystem(rules)
    return ctrl.ControlSystemSimulation(risk_ctrl)

# Global compiled simulation instance
_fuzzy_sim = build_mamdani_fuzzy_system()

def evaluate_mamdani_fuzzy_risk(
    thermal_stress: float,
    pressure_stress: float,
    tkph_stress: float,
    damage_stress: float,
    wear_stress: float,
    impact_stress: float,
    # Contextual data for human-readable reasons
    pressure_kpa: Optional[float] = 735.0,
    tyre_temp_c: Optional[float] = 62.0,
    tkph_current: Optional[float] = 1400.0,
    rated_tkph: Optional[float] = 1800.0,
    damage_present: bool = False,
    damage_type: str = "none",
    damage_severity: str = "none",
    damage_location: str = "none",
    has_missing_data: bool = False
) -> Dict[str, Any]:
    """
    Executes Mamdani fuzzy logic engine using scikit-fuzzy.
    Returns explainable risk_score, risk_label, reasons, recommended_action, and data_confidence.
    """
    # 1. Inputs clipping to 0-100
    t_val = float(np.clip(thermal_stress, 0, 100))
    p_val = float(np.clip(pressure_stress, 0, 100))
    k_val = float(np.clip(tkph_stress, 0, 100))
    d_val = float(np.clip(damage_stress, 0, 100))
    w_val = float(np.clip(wear_stress, 0, 100))
    i_val = float(np.clip(impact_stress, 0, 100))

    # 2. Run Fuzzy Control Simulation
    try:
        _fuzzy_sim.input['thermal_stress'] = t_val
        _fuzzy_sim.input['pressure_stress'] = p_val
        _fuzzy_sim.input['tkph_stress'] = k_val
        _fuzzy_sim.input['damage_stress'] = d_val
        _fuzzy_sim.input['wear_stress'] = w_val
        _fuzzy_sim.input['impact_stress'] = i_val

        _fuzzy_sim.compute()
        raw_score = float(_fuzzy_sim.output['risk_score'])
    except Exception:
        # Fallback weighted estimate if fuzzy boundary edge case
        raw_score = (0.25 * p_val + 0.25 * t_val + 0.20 * d_val + 0.15 * k_val + 0.10 * w_val + 0.05 * i_val)

    # 3. Rule Safety Overrides & Direct Firing Boosts
    # Critical single stressors must force HIGH risk
    if damage_severity == "severe" or p_val > 75 or t_val > 75:
        raw_score = max(raw_score, 78.0)
    elif damage_severity == "moderate" and (p_val > 40 or pressure_kpa < 650):
        raw_score = max(raw_score, 76.0)
    elif k_val > 75 and t_val > 45:
        raw_score = max(raw_score, 76.0)

    risk_score = round(min(100.0, max(0.0, raw_score)), 1)

    # 4. Determine Risk Label
    if risk_score >= 70.0:
        risk_label = "HIGH"
    elif risk_score >= 40.0:
        risk_label = "MEDIUM"
    else:
        risk_label = "LOW"

    # 5. Generate Human-Readable Reasons
    reasons: List[str] = []

    if rated_tkph and tkph_current and (tkph_current / rated_tkph) > 1.0:
        ratio = tkph_current / rated_tkph
        reasons.append(f"TKPH is {ratio:.2f}× rated value ({tkph_current:.0f} / {rated_tkph:.0f})")

    if tyre_temp_c and tyre_temp_c > 75.0:
        if tyre_temp_c >= 90.0:
            reasons.append(f"Temperature is rising critically ({tyre_temp_c:.1f}°C, threshold 85°C)")
        else:
            reasons.append(f"Elevated chamber temperature trajectory ({tyre_temp_c:.1f}°C)")

    if pressure_kpa and pressure_kpa < 650:
        reasons.append(f"Pressure loss detected: {pressure_kpa:.0f} kPa (threshold 650 kPa)")

    if damage_present or damage_severity in ("minor", "moderate", "severe"):
        if damage_type != "none" and damage_location != "none":
            reasons.append(f"{damage_severity.capitalize()} {damage_type} defect on {damage_location}")
        else:
            reasons.append(f"{damage_severity.capitalize()} surface damage defect detected")

    if impact_stress > 60:
        reasons.append("High peak acceleration impact cluster on road segment")

    if wear_stress > 65:
        reasons.append("High tread wear rate accelerating thermal accumulation")

    if not reasons:
        reasons.append("All telemetry, pressure, temperature, and inspection parameters within normal operational limits")

    # 6. Recommended Action
    if risk_label == "HIGH":
        if damage_severity == "severe" or (pressure_kpa and pressure_kpa < 620):
            recommended_action = "STOP AND INSPECT BEFORE NEXT LOADED CYCLE"
        elif t_val > 70:
            recommended_action = "REDUCE SPEED OR LOAD — MONITOR COOLING TRAJECTORY"
        else:
            recommended_action = "IMMEDIATE INSPECTION REQUIRED AT NEXT SHIFT STOP"
    elif risk_label == "MEDIUM":
        recommended_action = "MONITOR CLOSELY — INSPECT AT NEXT SCHEDULED MAINTENANCE WINDOW"
    else:
        recommended_action = "CONTINUE MONITORING — NO ACTION REQUIRED"

    # 7. Data Confidence
    data_confidence = 0.60 if has_missing_data else 0.91

    return {
        "risk_score": risk_score,
        "risk_label": risk_label,
        "reasons": reasons[:4],
        "recommended_action": recommended_action,
        "data_confidence": data_confidence,
        "stress_inputs": {
            "thermal_stress": round(t_val, 1),
            "pressure_stress": round(p_val, 1),
            "tkph_stress": round(k_val, 1),
            "damage_stress": round(d_val, 1),
            "wear_stress": round(w_val, 1),
            "impact_stress": round(i_val, 1),
        },
        "source": "scikit_fuzzy_mamdani_engine"
    }
