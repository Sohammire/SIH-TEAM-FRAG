from typing import Dict, Any, List, Optional

SUPPORTED_DAMAGE_CLASSES = ["cut", "crack", "puncture", "embedded_object", "tear", "abrasion", "unknown"]
SUPPORTED_LOCATIONS = ["tread", "shoulder", "sidewall", "bead", "unknown"]
SEVERITY_LEVELS = ["minor", "moderate", "severe"]

def assess_damage_severity(
    bbox: Optional[List[float]],
    damage_type: str,
    location: str,
    confidence: float,
    img_width: float = 640.0,
    img_height: float = 640.0
) -> str:
    """
    Operational severity classification layer based on visual features:
    - Minor: small localized discontinuity (<2% frame area), no visible structural exposure
    - Moderate: medium size (2%-8% frame area), shoulder/sidewall involvement
    - Severe: large open defect (>8% frame area), bead damage, or deep cut
    """
    if not bbox or len(bbox) != 4:
        return "minor"

    x1, y1, x2, y2 = bbox
    bbox_area = (x2 - x1) * (y2 - y1)
    img_area = img_width * img_height
    area_fraction = (bbox_area / img_area) if img_area > 0 else 0.0

    # Rule-based operational severity
    if damage_type.lower() in ("tear", "puncture") or location.lower() == "bead" or area_fraction > 0.08:
        return "severe"
    elif damage_type.lower() == "cut" and location.lower() in ("sidewall", "shoulder"):
        return "severe" if area_fraction > 0.04 else "moderate"
    elif area_fraction > 0.03 or location.lower() in ("sidewall", "shoulder"):
        return "moderate"
    else:
        return "minor"
