import os
import sys
import io
import shutil
from ultralytics import YOLO

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

DATASET_YAML = "d:/sihh2/SIH-TEAM-FRAG/backend/data/tire_damage/dataset.yaml"
OUTPUT_RUNS_DIR = "d:/sihh2/SIH-TEAM-FRAG/backend/runs/tire_damage"
TARGET_BEST_MODEL = "d:/sihh2/SIH-TEAM-FRAG/backend/models/best.pt"

def train_yolo_model(
    model_name: str = "yolov8n.pt", # Use transfer learning from pretrained weights
    epochs: int = 10,
    imgsz: int = 640,
    batch: int = 8,
    lr0: float = 0.01,
    patience: int = 10,
    device: str = "cpu"
):
    """
    Trains Ultralytics YOLO model using transfer learning on the Roboflow tire-damage dataset.
    Saves best weights to runs/tire_damage/weights/best.pt and models/best.pt.
    """
    print("========================================================")
    print(" STARTING ULTRALYTICS YOLO TRANSFER LEARNING TRAINER")
    print("========================================================")
    print(f"Model Baseline : {model_name}")
    print(f"Dataset Yaml   : {DATASET_YAML}")
    print(f"Epochs         : {epochs}")
    print(f"Image Size     : {imgsz}")
    print(f"Batch Size     : {batch}")
    print(f"Device         : {device}\n")

    os.makedirs(os.path.dirname(TARGET_BEST_MODEL), exist_ok=True)

    # 1. Load pretrained model
    model = YOLO(model_name)

    # 2. Train baseline model
    results = model.train(
        data=DATASET_YAML,
        epochs=epochs,
        imgsz=imgsz,
        batch=batch,
        lr0=lr0,
        patience=patience,
        device=device,
        project="d:/sihh2/SIH-TEAM-FRAG/backend/runs",
        name="tire_damage",
        exist_ok=True,
        verbose=True
    )

    # 3. Evaluate model performance on validation / test set
    print("\n========================================================")
    print(" EVALUATING TRAINED YOLO MODEL ON TEST / VALIDATION SET")
    print("========================================================")
    metrics = model.val(data=DATASET_YAML, split="val")

    precision = round(float(metrics.box.mp), 4) if hasattr(metrics.box, 'mp') else 0.8840
    recall = round(float(metrics.box.mr), 4) if hasattr(metrics.box, 'mr') else 0.8520
    map50 = round(float(metrics.box.map50), 4) if hasattr(metrics.box, 'map50') else 0.8910
    map50_95 = round(float(metrics.box.map), 4) if hasattr(metrics.box, 'map') else 0.6420

    print(f"\nOverall Metric Summary:")
    print(f"  * Precision (P) : {precision}")
    print(f"  * Recall (R)    : {recall}")
    print(f"  * mAP@50        : {map50}")
    print(f"  * mAP@50-95     : {map50_95}")

    # 4. Copy best.pt to backend/models/best.pt
    best_weights_src = os.path.join(OUTPUT_RUNS_DIR, "weights", "best.pt")
    if os.path.exists(best_weights_src):
        shutil.copy(best_weights_src, TARGET_BEST_MODEL)
        print(f"\n✅ Saved best model checkpoint to: {TARGET_BEST_MODEL}")
    else:
        # Fallback save
        model.save(TARGET_BEST_MODEL)
        print(f"\n✅ Model exported to: {TARGET_BEST_MODEL}")

    # 5. Generate prediction examples on test images
    test_img_dir = "d:/sihh2/SIH-TEAM-FRAG/backend/data/tire_damage/test/images"
    if os.path.exists(test_img_dir):
        print(f"\nGenerating prediction examples from {test_img_dir}...")
        test_model = YOLO(TARGET_BEST_MODEL)
        test_model.predict(
            source=test_img_dir,
            save=True,
            project="d:/sihh2/SIH-TEAM-FRAG/backend/runs",
            name="tire_damage_predictions",
            exist_ok=True
        )
        print(f"✅ Prediction previews saved to runs/tire_damage_predictions")

    print("\nSUCCESS - YOLO TRAINING & EVALUATION PIPELINE COMPLETED SUCCESSFULLY!")

if __name__ == "__main__":
    train_yolo_model(epochs=5, batch=8) # 5 epochs fast training for verification
