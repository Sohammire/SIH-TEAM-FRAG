from typing import List, Dict, Any, Optional

def calculate_rolling_tkph(
    payload_samples: List[float],
    speed_samples: List[float],
    rated_tkph: float = 1800.0,
    tyre_position_axle_factor: float = 1.0/6.0,
    empty_tyre_tare_t: float = 25.0,
    sample_interval_sec: float = 60.0
) -> Dict[str, Any]:
    """
    Computes rolling TKPH, AWSS (excluding zero-speed samples), shift summary, and exceedance metrics.
    
    Inputs:
        - payload_samples: List of truck payload measurements (tonnes)
        - speed_samples: List of truck speed measurements (km/h)
        - rated_tkph: Manufacturer rated TKPH limit
        - tyre_position_axle_factor: Axle load distribution factor (default 1/6 for 6-tyre dumper)
        - empty_tyre_tare_t: Base tare load per tyre when dumper is empty (tonnes)
        - sample_interval_sec: Time delta per sample in seconds
    """
    if not payload_samples or not speed_samples or len(payload_samples) != len(speed_samples):
        # Default fallback
        return {
            "tkph_current": 0.0,
            "tkph_shift": 0.0,
            "awss_kmh": 0.0,
            "mean_tyre_load_t": empty_tyre_tare_t,
            "tkph_exceedance_ratio": 0.0,
            "exceedance_minutes": 0.0,
            "workload_status": "NORMAL",
            "prototype_default_notice": "Thresholds (<0.80 NORMAL, 0.80-1.00 MONITOR, 1.00-1.15 WARNING, >1.15 HIGH) are prototype defaults."
        }

    # 1. Zero-speed sample exclusion for AWSS (Average Work-Shift Speed)
    non_zero_speeds = [s for s in speed_samples if s > 0.5]
    awss_kmh = sum(non_zero_speeds) / len(non_zero_speeds) if non_zero_speeds else 0.0

    # 2. Mean Tyre Load Calculation (tonnes)
    mean_payload = sum(payload_samples) / len(payload_samples) if payload_samples else 0.0
    mean_tyre_load_t = empty_tyre_tare_t + (mean_payload * tyre_position_axle_factor)

    # 3. Current Rolling TKPH & Shift Summary
    tkph_current = round(mean_tyre_load_t * awss_kmh, 1)
    
    # Calculate sample-by-sample instantaneous TKPH to track exceedance duration
    instantaneous_tkph = []
    exceedance_samples = 0
    for p, s in zip(payload_samples, speed_samples):
        if s > 0.5: # moving
            t_load = empty_tyre_tare_t + (p * tyre_position_axle_factor)
            inst_val = t_load * s
            instantaneous_tkph.append(inst_val)
            if inst_val > rated_tkph:
                exceedance_samples += 1

    tkph_shift = round(sum(instantaneous_tkph) / len(instantaneous_tkph), 1) if instantaneous_tkph else tkph_current
    exceedance_minutes = round((exceedance_samples * sample_interval_sec) / 60.0, 1)

    exceedance_ratio = round(tkph_current / rated_tkph, 2) if rated_tkph > 0 else 0.0

    # 4. Workload Classification (Prototype Defaults)
    if exceedance_ratio > 1.15:
        workload_status = "HIGH"
    elif exceedance_ratio >= 1.00:
        workload_status = "WARNING"
    elif exceedance_ratio >= 0.80:
        workload_status = "MONITOR"
    else:
        workload_status = "NORMAL"

    return {
        "tkph_current": tkph_current,
        "tkph_shift": tkph_shift,
        "awss_kmh": round(awss_kmh, 1),
        "mean_tyre_load_t": round(mean_tyre_load_t, 1),
        "rated_tkph": rated_tkph,
        "tkph_exceedance_ratio": exceedance_ratio,
        "exceedance_minutes": exceedance_minutes,
        "workload_status": workload_status,
        "prototype_default_notice": "Thresholds (<0.80 NORMAL, 0.80-1.00 MONITOR, 1.00-1.15 WARNING, >1.15 HIGH) are prototype defaults."
    }
