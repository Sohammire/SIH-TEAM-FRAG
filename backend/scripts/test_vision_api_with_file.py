import requests
import json
import glob

API_URL = "http://localhost:8000/api/v1/vision/predict"

def test_upload_image():
    files_list = glob.glob("d:/sihh2/SIH-TEAM-FRAG/backend/data/tire_damage/train/images/*.jpg")
    if not files_list:
        print("No training dataset images found.")
        return

    sample_file = files_list[0]
    print(f"Uploading file: {sample_file} to {API_URL}...")

    with open(sample_file, 'rb') as f:
        files = {'file': (os.path.basename(sample_file), f, 'image/jpeg')}
        data = {'tyre_id': 'TYRE_07_RRI'}
        res = requests.post(API_URL, files=files, data=data)

    print(f"Status Code: {res.status_code}")
    print(f"Response Payload:\n{json.dumps(res.json(), indent=2)}")

    assert res.status_code == 200
    r = res.json()
    assert "image_id" in r
    assert r["tyre_id"] == "TYRE_07_RRI"
    assert "damage_present" in r
    assert "detections" in r
    assert "model_version" in r
    assert "quality_warning" in r

if __name__ == "__main__":
    import os
    test_upload_image()
