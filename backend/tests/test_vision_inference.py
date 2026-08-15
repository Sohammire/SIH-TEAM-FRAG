import pytest
import os
import cv2
import numpy as np
from PIL import Image
from app.services.vision_inference import run_vision_inference, inspect_image_quality

def create_synthetic_image(color=(50, 50, 50), size=(640, 640)):
    img = np.full((size[1], size[0], 3), color, dtype=np.uint8)
    return img

# 1. Image Quality Check Unit Tests
def test_quality_check_blur_detection():
    # Heavily blurred image via large GaussianBlur filter
    base_img = create_synthetic_image(color=(100, 100, 100))
    blurred_img = cv2.GaussianBlur(base_img, (51, 51), 0)
    q_res = inspect_image_quality(blurred_img)
    assert q_res["quality_warning"] is True
    assert "blurred" in q_res["warning_reason"]

def test_quality_check_dark_detection():
    # Extremely dark image (pixel intensity 10 < 20)
    dark_img = create_synthetic_image(color=(10, 10, 10))
    q_res = inspect_image_quality(dark_img)
    assert q_res["quality_warning"] is True
    assert "dark" in q_res["warning_reason"]

def test_quality_check_low_resolution():
    # 64x64 low resolution image
    low_res_img = create_synthetic_image(size=(64, 64))
    q_res = inspect_image_quality(low_res_img)
    assert q_res["quality_warning"] is True
    assert "low_resolution" in q_res["warning_reason"]

# 2. Vision Inference Service Pipeline Tests
def test_vision_inference_valid_image():
    # Normal image with texture (sharp edges to pass quality check)
    img = np.random.randint(50, 200, (640, 640, 3), dtype=np.uint8)
    res = run_vision_inference(img)

    assert "damage_present" in res
    assert "detections" in res
    assert "model_version" in res
    assert "quality_warning" in res
    assert res["quality_warning"] is False

# 3. Test Real Images from Dataset
def test_vision_inference_real_dataset_images():
    test_dir = "d:/sihh2/SIH-TEAM-FRAG/backend/data/tire_damage/train/images"
    if os.path.exists(test_dir):
        files = [os.path.join(test_dir, f) for f in os.listdir(test_dir) if f.endswith('.jpg')]
        if files:
            sample_file = files[0]
            res = run_vision_inference(sample_file)

            assert isinstance(res["damage_present"], bool)
            assert isinstance(res["detections"], list)
            assert res["model_version"] == "yolov8n-tire-damage-v1.0"
            assert res["quality_warning"] is False
            print(f"\n[Real Image Inference Output]: {res}")
