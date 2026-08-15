import cv2
import numpy as np
import uuid
from typing import Dict, Any, Optional
from app.ml.vision.preprocessing import load_image_from_bytes, preprocess_image
from app.ml.vision.quality_check import check_image_quality
from app.ml.vision.detector import YOLODamageDetector
from app.ml.vision.severity import assess_damage_severity

detector_instance = YOLODamageDetector()

def run_vision_inspection_pipeline(
    image_bytes: bytes,
    tyre_id: Optional[str] = None,
    truck_id: Optional[str] = None,
    image_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Executes complete end-to-end Computer Vision Inspection Pipeline:
    IMAGE -> resize/normalize -> quality_check -> YOLO -> bbox -> ROI crop -> severity layer -> inspection result
    """
    img_id = image_id or f"IMG_{uuid.uuid4().hex[:6].upper()}"
    insp_id = f"INS_{uuid.uuid4().hex[:8].upper()}"

    # 1. Load image from raw bytes
    img_bgr = load_image_from_bytes(image_bytes)

    # 2. Resize & Normalize
    img_resized, img_normalized, pil_img = preprocess_image(img_bgr, target_size=(640, 640))

    # 3. Image Quality Check (blur, darkness, visibility)
    quality_res = check_image_quality(img_resized)

    # LOW-QUALITY IMAGE GUARDRAIL:
    # Produces quality_warning instead of a confident classification!
    if not quality_res["is_valid"]:
        return {
            "inspection_id": insp_id,
            "image_id": img_id,
            "tyre_id": tyre_id,
            "truck_id": truck_id,
            "damage_present": False,
            "damage_type": "quality_warning",
            "location": "unknown",
            "severity": "minor",
            "confidence": 0.30,
            "bbox": None,
            "model_version": detector_instance.model_version,
            "source": "quality_checker",
            "image_quality_status": quality_res["quality_status"],
            "quality_warning": quality_res["quality_warning"],
            "metrics": quality_res["metrics"]
        }

    # 4. YOLO Object Detection
    detection_res = detector_instance.detect_damage(img_resized)

    damage_present = detection_res["damage_present"]
    damage_type = detection_res.get("damage_type")
    location = detection_res.get("location")
    confidence = detection_res.get("confidence", 0.85)
    bbox = detection_res.get("bbox")

    # 5. ROI Crop & Operational Severity Assessment
    severity = "minor"
    if damage_present and bbox:
        # ROI Crop for audit
        x1, y1, x2, y2 = [int(c) for c in bbox]
        roi = img_resized[y1:y2, x1:x2]
        
        severity = assess_damage_severity(
            bbox=bbox,
            damage_type=damage_type or "cut",
            location=location or "sidewall",
            confidence=confidence,
            img_width=640.0,
            img_height=640.0
        )

    return {
        "inspection_id": insp_id,
        "image_id": img_id,
        "tyre_id": tyre_id,
        "truck_id": truck_id,
        "damage_present": damage_present,
        "damage_type": damage_type if damage_present else None,
        "location": location if damage_present else None,
        "severity": severity if damage_present else None,
        "confidence": confidence,
        "bbox": bbox,
        "model_version": detector_instance.model_version,
        "source": "vision_model",
        "image_quality_status": "good",
        "quality_warning": None
    }
