import json
import uuid
import logging
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional
from app.database.connection import get_db
from app.schemas.all_schemas import InspectionCreate, InspectionResponse, VisionPredictResponse
from app.services import inspection_service
from app.services.vision_inference import run_vision_inference
from app.models import DamageInspection
import cv2
import numpy as np

logger = logging.getLogger("tyreiq_backend.vision_api")
router = APIRouter(tags=["Computer Vision & Inspections"])

@router.post("/inspections", response_model=InspectionResponse, status_code=status.HTTP_201_CREATED)
def submit_inspection(data: InspectionCreate, db: Session = Depends(get_db)):
    """
    Submits a damage inspection record.
    """
    try:
        return inspection_service.create_inspection(db, data)
    except Exception as e:
        logger.error(f"Error submitting inspection: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/vision/predict", response_model=VisionPredictResponse, status_code=status.HTTP_200_OK)
async def predict_vision_damage(
    file: Optional[UploadFile] = File(None),
    image: Optional[UploadFile] = File(None), # Accepts either 'file' or 'image' parameter
    tyre_id: Optional[str] = Form(None),
    truck_id: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    FastAPI Vision Prediction Endpoint:
    Accepts multipart/form-data image input -> Image Quality Check -> YOLO (best.pt) -> Class Mapping -> Bounding Boxes -> JSON Response
    """
    target_upload = file or image
    image_id = f"IMG_{uuid.uuid4().hex[:8].upper()}"

    try:
        if target_upload and target_upload.filename:
            image_bytes = await target_upload.read()
            logger.info(f"Processing uploaded image: {target_upload.filename} ({len(image_bytes)} bytes)")
        else:
            # Generate synthetic demo image for Swagger / curl fallback testing
            img = np.full((640, 640, 3), 60, dtype=np.uint8)
            cv2.circle(img, (320, 320), 200, (140, 140, 140), 20)
            noise = np.random.randint(0, 30, (640, 640, 3), dtype=np.uint8)
            img = cv2.add(img, noise)
            cv2.rectangle(img, (220, 160), (340, 280), (200, 50, 50), -1)
            cv2.line(img, (180, 120), (380, 320), (255, 255, 255), 6)
            _, encoded = cv2.imencode('.jpg', img)
            image_bytes = encoded.tobytes()
            logger.info("No file uploaded; generated synthetic demo image for vision prediction.")

        # Execute Vision Inference Service Pipeline
        res = run_vision_inference(image_bytes)

        # Construct Vision Predict Response
        response = {
            "image_id": image_id,
            "tyre_id": tyre_id or "TYRE_03_RRO",
            "damage_present": res.get("damage_present", False),
            "detections": res.get("detections", []),
            "model_version": res.get("model_version", "yolov8n-tire-damage-v1.0"),
            "quality_warning": res.get("quality_warning", False),
            "warning_reason": res.get("warning_reason")
        }

        # Save to DB if valid inspection
        if not response["quality_warning"]:
            top_det = response["detections"][0] if response["detections"] else {}
            insp = DamageInspection(
                inspection_id=f"INS_{uuid.uuid4().hex[:8].upper()}",
                image_id=image_id,
                tyre_id=response["tyre_id"],
                truck_id=truck_id or "DUMPER_03",
                damage_present=response["damage_present"],
                damage_type=top_det.get("class", "none" if not response["damage_present"] else "unknown"),
                location="sidewall",
                severity="moderate" if response["damage_present"] else "minor",
                confidence=top_det.get("confidence", 0.95),
                bbox_json=json.dumps(top_det.get("bbox")) if top_det.get("bbox") else None,
                model_version=response["model_version"],
                reviewer_status="pending",
                source="vision_model"
            )
            db.add(insp)
            db.commit()

        return response

    except Exception as e:
        logger.error(f"Failed to execute vision prediction API: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Vision inference execution failed: {str(e)}"
        )
