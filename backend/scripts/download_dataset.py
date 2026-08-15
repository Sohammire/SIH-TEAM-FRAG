import os
from roboflow import Roboflow

def download_tire_damage_dataset():
    """
    Downloads the 'tire-damage' dataset from Roboflow Universe into backend/data/tire_damage.
    """
    api_key = os.getenv("ROBOFLOW_API_KEY", "rf_demo") # Use demo or public API key
    rf = Roboflow(api_key=api_key)
    
    # Target dataset: yoloing/tire-damage
    try:
        project = rf.workspace("yoloing").project("tire-damage")
        version = project.version(1)
        dataset = version.download("yolov8", location="d:/sihh2/SIH-TEAM-FRAG/backend/data/tire_damage")
        print(f"Dataset successfully downloaded to {dataset.location}")
    except Exception as e:
        print(f"Roboflow API download error: {e}")

if __name__ == "__main__":
    download_tire_damage_dataset()
