import requests
import json
import os

API_URL = "http://localhost:8000/api/v1/vision/predict"
TEST_IMG = "d:/sihh2/SIH-TEAM-FRAG/backend/data/tire_damage/train/images/train_0000.jpg"

def test_vision_predict_endpoint():
    print(f"[API Test] Sending POST request to {API_URL}...")
    
    if os.path.exists(TEST_IMG):
        with open(TEST_IMG, 'rb') as f:
            files = {'file': ('train_0000.jpg', f, 'image/jpeg')}
            data = {'tyre_id': 'TYRE_03_RRO'}
            res = requests.post(API_URL, files=files, data=data)
    else:
        # Test without file upload (uses synthetic demo fallback)
        data = {'tyre_id': 'TYRE_03_RRO'}
        res = requests.post(API_URL, data=data)

    print(f"HTTP Status Code: {res.status_code}")
    print(f"JSON Response:\n{json.dumps(res.json(), indent=2)}")

    assert res.status_code == 200
    res_json = res.json()
    assert "image_id" in res_json
    assert "damage_present" in res_json
    assert "detections" in res_json
    assert "model_version" in res_json
    assert "quality_warning" in res_json
    print("\nSUCCESS - VISION PREDICT API ENDPOINT VERIFIED CLEANLY!")

if __name__ == "__main__":
    test_vision_predict_endpoint()
