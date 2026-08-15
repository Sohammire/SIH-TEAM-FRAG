import os
import glob
import sys
import io
import yaml
from PIL import Image

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

DATASET_DIR = "d:/sihh2/SIH-TEAM-FRAG/backend/data/tire_damage"

def validate_yolo_dataset():
    """
    Validates YOLO dataset integrity across train, valid, test splits:
    - missing images / labels
    - invalid class IDs
    - invalid bounding boxes
    - corrupted images
    - empty annotations
    """
    yaml_path = os.path.join(DATASET_DIR, "dataset.yaml")
    if not os.path.exists(yaml_path):
        print(f"[ERROR] Missing dataset.yaml at {yaml_path}")
        return False

    with open(yaml_path, 'r') as f:
        ds_config = yaml.safe_load(f)

    class_names = ds_config.get('names', {})
    num_classes = len(class_names)
    print(f"Dataset Configuration:")
    print(f"  * Path: {ds_config.get('path')}")
    print(f"  * Num Classes: {num_classes} -> {class_names}")

    splits = ['train', 'valid', 'test']
    total_images = 0
    total_annotations = 0
    corrupted_images = 0
    missing_labels = 0
    empty_annotations = 0
    invalid_bboxes = 0
    invalid_class_ids = 0

    class_counts = {cls_id: 0 for cls_id in class_names.keys()}

    for split in splits:
        img_dir = os.path.join(DATASET_DIR, split, "images")
        lbl_dir = os.path.join(DATASET_DIR, split, "labels")

        image_files = glob.glob(os.path.join(img_dir, "*.[jJ][pP]*[gG]")) + glob.glob(os.path.join(img_dir, "*.png"))
        print(f"\nEvaluating Split: '{split}' ({len(image_files)} images)")

        for img_path in image_files:
            total_images += 1
            # 1. Check corrupted image
            try:
                with Image.open(img_path) as img:
                    img.verify()
            except Exception as e:
                print(f"  [WARN] Corrupted image found: {img_path} ({e})")
                corrupted_images += 1
                continue

            # 2. Check corresponding label file
            basename = os.path.splitext(os.path.basename(img_path))[0]
            lbl_path = os.path.join(lbl_dir, f"{basename}.txt")

            if not os.path.exists(lbl_path):
                print(f"  [WARN] Missing label file for image: {img_path}")
                missing_labels += 1
                continue

            # 3. Inspect annotations
            with open(lbl_path, 'r') as f:
                lines = [line.strip() for line in f.readlines() if line.strip()]

            if len(lines) == 0:
                empty_annotations += 1
                continue

            for line in lines:
                parts = line.split()
                if len(parts) != 5:
                    print(f"  [WARN] Invalid label format line in {lbl_path}: '{line}'")
                    invalid_bboxes += 1
                    continue

                try:
                    cls_id = int(parts[0])
                    cx, cy, w, h = map(float, parts[1:])
                except ValueError:
                    print(f"  [WARN] Non-numeric bounding box in {lbl_path}: '{line}'")
                    invalid_bboxes += 1
                    continue

                # Check Class ID bounds
                if cls_id not in class_names:
                    print(f"  [WARN] Invalid Class ID {cls_id} in {lbl_path} (Expected 0..{num_classes-1})")
                    invalid_class_ids += 1
                else:
                    class_counts[cls_id] += 1

                # Check Bounding Box coordinates (0.0 to 1.0)
                if not (0.0 <= cx <= 1.0 and 0.0 <= cy <= 1.0 and 0.0 < w <= 1.0 and 0.0 < h <= 1.0):
                    print(f"  [WARN] Bounding box coordinates out of bounds in {lbl_path}: cx={cx}, cy={cy}, w={w}, h={h}")
                    invalid_bboxes += 1

                total_annotations += 1

    print("\n========================================================")
    print(" DATASET VALIDATION SUMMARY REPORT")
    print("========================================================")
    print(f"Total Images Analyzed   : {total_images}")
    print(f"Total Bounding Boxes    : {total_annotations}")
    print(f"Corrupted Images        : {corrupted_images}")
    print(f"Missing Label Files     : {missing_labels}")
    print(f"Empty Annotation Files  : {empty_annotations} (Background/Normal samples)")
    print(f"Invalid Bounding Boxes  : {invalid_bboxes}")
    print(f"Invalid Class IDs       : {invalid_class_ids}")
    print(f"Class Distribution      : {class_counts}")

    success = (corrupted_images == 0 and missing_labels == 0 and invalid_bboxes == 0 and invalid_class_ids == 0)
    if success:
        print("SUCCESS - DATASET VALIDATION PASSED -- READY FOR YOLO TRAINING!")
    else:
        print("FAILED - DATASET VALIDATION FAILED WITH ERRORS")

    return success

if __name__ == "__main__":
    validate_yolo_dataset()
