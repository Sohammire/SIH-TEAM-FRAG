import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models import DamageInspection
from app.schemas.all_schemas import InspectionCreate

def create_inspection(db: Session, data: InspectionCreate) -> Dict[str, Any]:
    insp_id = f"INS_{uuid.uuid4().hex[:8].upper()}"
    bbox_str = json.dumps(data.bbox) if data.bbox else None

    insp = DamageInspection(
        inspection_id=insp_id,
        timestamp=datetime.utcnow(),
        tyre_id=data.tyre_id,
        truck_id=data.truck_id,
        image_id=data.image_id or "IMG_UPLOAD",
        damage_present=data.damage_present,
        damage_type=data.damage_type,
        location=data.location,
        severity=data.severity,
        confidence=data.confidence,
        bbox_json=bbox_str,
        model_version=data.model_version,
        reviewer_status="pending",
        source="vision_model"
    )

    db.add(insp)
    db.commit()

    return {
        "inspection_id": insp_id,
        "image_id": insp.image_id,
        "tyre_id": insp.tyre_id,
        "truck_id": insp.truck_id,
        "damage_present": insp.damage_present,
        "damage_type": insp.damage_type,
        "location": insp.location,
        "severity": insp.severity,
        "confidence": insp.confidence,
        "bbox": data.bbox,
        "model_version": insp.model_version,
        "source": "vision_model"
    }

def predict_vision_image(tyre_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Mock vision model pipeline prediction (YOLO detection + severity layer).
    """
    return {
        "inspection_id": f"INS_{uuid.uuid4().hex[:8].upper()}",
        "image_id": f"IMG_{uuid.uuid4().hex[:6].upper()}",
        "tyre_id": tyre_id or "TYRE_03_RRO",
        "truck_id": "DUMPER_03",
        "damage_present": True,
        "damage_type": "cut",
        "location": "sidewall",
        "severity": "moderate",
        "confidence": 0.91,
        "bbox": [145.0, 95.0, 355.0, 275.0],
        "model_version": "yolov8n-tyredmg-v0.1",
        "source": "vision_model"
    }
