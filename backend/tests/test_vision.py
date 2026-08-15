import pytest
import cv2
import numpy as np
from io import BytesIO
from fastapi.testclient import TestClient
from app.main import app
from app.ml.vision.pipeline import run_vision_inspection_pipeline

client = TestClient(app)

def create_synthetic_image(mode: str = "normal") -> bytes:
    """Helper to generate realistic synthetic test image bytes"""
    img = np.full((480, 640, 3), 120, dtype=np.uint8)
    
    if mode == "dark":
        img.fill(15) # Very dark (<40 brightness)
    elif mode == "blurred":
        # Draw some lines then heavily blur
        cv2.circle(img, (320, 240), 180, (200, 200, 200), 20)
        img = cv2.GaussianBlur(img, (99, 99), 0) # Extremely low Laplacian variance
    elif mode == "damaged":
        # Add texture & high contrast ring
        cv2.circle(img, (320, 240), 180, (230, 230, 230), 25)
        # Add noise texture for high Laplacian variance
        noise = np.random.randint(0, 50, (480, 640, 3), dtype=np.uint8)
        img = cv2.add(img, noise)
        # Draw high-contrast cut defect
        cv2.rectangle(img, (220, 160), (340, 280), (255, 255, 255), -1)
        cv2.line(img, (180, 120), (380, 320), (0, 0, 0), 10)
    else: # normal sharp
        cv2.circle(img, (320, 240), 180, (220, 220, 220), 25)
        # Add noise texture for high Laplacian variance (>100)
        noise = np.random.randint(0, 60, (480, 640, 3), dtype=np.uint8)
        img = cv2.add(img, noise)

    _, encoded = cv2.imencode('.jpg', img)
    return encoded.tobytes()

# 1. Normal Image Test
def test_normal_image_inspection():
    img_bytes = create_synthetic_image("normal")
    res = run_vision_inspection_pipeline(img_bytes, tyre_id="TYRE_01_FL")
    
    assert res["image_quality_status"] == "good"
    assert res["quality_warning"] is None
    assert "model_version" in res

# 2. Damaged Image Test
def test_damaged_image_inspection():
    img_bytes = create_synthetic_image("damaged")
    res = run_vision_inspection_pipeline(img_bytes, tyre_id="TYRE_03_RRO")
    
    assert res["image_quality_status"] == "good"
    assert res["damage_present"] is True
    assert res["bbox"] is not None
    assert res["severity"] in ("minor", "moderate", "severe")

# 3. Blurred / Low Quality Image Test -> quality_warning
def test_blurred_image_produces_quality_warning():
    img_bytes = create_synthetic_image("blurred")
    res = run_vision_inspection_pipeline(img_bytes, tyre_id="TYRE_04_FR")
    
    assert res["damage_type"] == "quality_warning"
    assert res["quality_warning"] is not None
    assert "QUALITY WARNING" in res["quality_warning"]
    assert res["confidence"] <= 0.50

# 4. Dark Image Test -> quality_warning
def test_dark_image_produces_quality_warning():
    img_bytes = create_synthetic_image("dark")
    res = run_vision_inspection_pipeline(img_bytes, tyre_id="TYRE_04_FR")
    
    assert res["damage_type"] == "quality_warning"
    assert res["quality_warning"] is not None
    assert "dark" in res["quality_warning"].lower()

# 5. REST API Endpoint Integration Test
def test_post_vision_predict_endpoint():
    img_bytes = create_synthetic_image("damaged")
    files = {"file": ("test_tyre.jpg", BytesIO(img_bytes), "image/jpeg")}
    data = {"tyre_id": "TYRE_03_RRO"}
    
    res = client.post("/api/v1/vision/predict", files=files, data=data)
    assert res.status_code == 200
    res_data = res.json()
    assert "image_id" in res_data
    assert res_data["tyre_id"] == "TYRE_03_RRO"
    assert "damage_present" in res_data
    assert isinstance(res_data["detections"], list)
    assert "model_version" in res_data
    assert "quality_warning" in res_data
