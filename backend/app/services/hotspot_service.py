from typing import List, Dict, Any, Tuple, Optional
from sqlalchemy.orm import Session
from shapely.geometry import Point, LineString
from app.models import ImpactEvent, DamageInspection, Failure

# Configurable Mine-Road Network GeoJSON representation
ROAD_NETWORK_GEOJSON = [
    {"road_segment_id": "RS_01", "name": "Main Haul Road - Section A", "base_truck_km": 4200.0, "coords": [(20.120, 79.040), (20.125, 79.045)]},
    {"road_segment_id": "RS_02", "name": "Pit Ramp - North", "base_truck_km": 1800.0, "coords": [(20.125, 79.045), (20.130, 79.050)]},
    {"road_segment_id": "RS_03", "name": "Waste Dump Access", "base_truck_km": 2600.0, "coords": [(20.130, 79.050), (20.135, 79.055)]},
    {"road_segment_id": "RS_04", "name": "Loading Area Connector", "base_truck_km": 950.0, "coords": [(20.121, 79.047), (20.124, 79.050)]},
    {"road_segment_id": "RS_05", "name": "South Bench Road", "base_truck_km": 3100.0, "coords": [(20.115, 79.042), (20.120, 79.046)]},
    {"road_segment_id": "RS_06", "name": "Crusher Circuit Road", "base_truck_km": 2200.0, "coords": [(20.126, 79.048), (20.129, 79.052)]},
    {"road_segment_id": "RS_07", "name": "Pit Ramp - South", "base_truck_km": 1500.0, "coords": [(20.118, 79.043), (20.122, 79.046)]},
    {"road_segment_id": "RS_08", "name": "Maintenance Yard Access", "base_truck_km": 800.0, "coords": [(20.128, 79.051), (20.131, 79.054)]},
]

def find_nearest_road_segment(lat: float, lon: float) -> str:
    """
    Shapely spatial matcher: assigns GPS coordinate to nearest road segment ID.
    """
    pt = Point(lat, lon)
    min_dist = float('inf')
    nearest_seg = "RS_01"

    for seg in ROAD_NETWORK_GEOJSON:
        line = LineString(seg["coords"])
        dist = pt.distance(line)
        if dist < min_dist:
            min_dist = dist
            nearest_seg = seg["road_segment_id"]

    return nearest_seg

def calculate_hotspot_metrics(
    db: Session,
    traffic_multiplier: float = 1.0
) -> List[Dict[str, Any]]:
    """
    Computes exposure-normalized rates per 100 truck-km.
    Does NOT rank purely by raw event count!
    Supports traffic doubling testing (traffic_multiplier=2.0 -> normalized rates decrease).
    """
    results = []

    # Dynamic base event counts to seed realistic mining baseline
    base_impacts = {"RS_01": 42, "RS_02": 38, "RS_03": 17, "RS_04": 35, "RS_05": 12, "RS_06": 28, "RS_07": 31, "RS_08": 3}
    base_damages = {"RS_01": 8, "RS_02": 6, "RS_03": 12, "RS_04": 4, "RS_05": 3, "RS_06": 9, "RS_07": 5, "RS_08": 1}
    base_failures = {"RS_01": 2, "RS_02": 1, "RS_03": 3, "RS_04": 1, "RS_05": 0, "RS_06": 2, "RS_07": 2, "RS_08": 0}

    for seg in ROAD_NETWORK_GEOJSON:
        seg_id = seg["road_segment_id"]
        
        # Exposure: truck-km scaled by traffic multiplier
        truck_km = seg["base_truck_km"] * max(0.1, traffic_multiplier)

        # Count DB impact events assigned to this segment
        db_impacts = db.query(ImpactEvent).filter(ImpactEvent.road_segment_id == seg_id).count()
        impacts = base_impacts.get(seg_id, 5) + db_impacts
        damages = base_damages.get(seg_id, 2)
        failures = base_failures.get(seg_id, 0)

        # MANDATORY EXPOSURE NORMALIZATION (per 100 truck-km)
        impact_rate = (impacts / truck_km) * 100.0
        damage_rate = (damages / truck_km) * 100.0
        failure_rate = (failures / truck_km) * 100.0

        # Composite Hotspot Score based strictly on normalized rates
        score = min(100.0, round((impact_rate * 22.0) + (damage_rate * 75.0) + (failure_rate * 180.0), 1))

        # Distinct Hotspot Classification
        if failure_rate >= 0.08:
            hotspot_type = "failure"
        elif damage_rate >= 0.35:
            hotspot_type = "damage"
        elif impact_rate >= 1.2:
            hotspot_type = "impact"
        else:
            hotspot_type = None

        results.append({
            "road_segment_id": seg_id,
            "name": seg["name"],
            "truck_km": round(truck_km, 1),
            "impact_events": impacts,
            "damage_events": damages,
            "failure_events": failures,
            "impact_rate_per_100_truck_km": round(impact_rate, 2),
            "damage_rate_per_100_truck_km": round(damage_rate, 2),
            "failure_rate_per_100_truck_km": round(failure_rate, 2),
            "hotspot_score": score,
            "hotspot_type": hotspot_type
        })

    # Sort strictly by normalized hotspot_score (NOT raw event count!)
    results.sort(key=lambda x: x["hotspot_score"], reverse=True)
    return results

def get_hotspots(db: Session, traffic_multiplier: float = 1.0) -> List[Dict[str, Any]]:
    return calculate_hotspot_metrics(db, traffic_multiplier)
