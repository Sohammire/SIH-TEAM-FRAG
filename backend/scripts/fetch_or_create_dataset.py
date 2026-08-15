import os
import sys
import yaml
import json
import shutil
import random
import numpy as np
from PIL import Image, ImageDraw

DATASET_DIR = "d:/sihh2/SIH-TEAM-FRAG/backend/data/tire_damage"

def create_yolo_dataset_structure():
    """
    Creates standard YOLO dataset structure:
    data/tire_damage/
        train/images/ train/labels/
        valid/images/ valid/labels/
        test/images/  test/labels/
        dataset.yaml
    """
    os.makedirs(f"{DATASET_DIR}/train/images", exist_ok=True)
    os.makedirs(f"{DATASET_DIR}/train/labels", exist_ok=True)
    os.makedirs(f"{DATASET_DIR}/valid/images", exist_ok=True)
    os.makedirs(f"{DATASET_DIR}/valid/labels", exist_ok=True)
    os.makedirs(f"{DATASET_DIR}/test/images", exist_ok=True)
    os.makedirs(f"{DATASET_DIR}/test/labels", exist_ok=True)

    # Actual Roboflow dataset classes for 'tire-damage'
    # Dataset classes: 0: 'crack', 1: 'cut', 2: 'normal', 3: 'puncture'
    dataset_yaml = {
        'path': DATASET_DIR,
        'train': 'train/images',
        'val': 'valid/images',
        'test': 'test/images',
        'names': {
            0: 'crack',
            1: 'cut',
            2: 'normal',
            3: 'puncture'
        }
    }

    yaml_path = f"{DATASET_DIR}/dataset.yaml"
    with open(yaml_path, 'w') as f:
        yaml.dump(dataset_yaml, f, default_flow_style=False)

    print(f"[Dataset] Created dataset.yaml at {yaml_path}")
    return yaml_path

def generate_synthetic_annotated_samples(num_train=80, num_val=20, num_test=10):
    """
    Generates realistic annotated tyre damage images for YOLO baseline training
    covering classes: crack (0), cut (1), normal (2), puncture (3).
    """
    splits = [
        ('train', num_train),
        ('valid', num_val),
        ('test', num_test)
    ]

    classes = ['crack', 'cut', 'normal', 'puncture']
    img_size = (640, 640)

    total_generated = 0

    for split_name, count in splits:
        for idx in range(count):
            img_id = f"{split_name}_{idx:04d}"
            img_path = f"{DATASET_DIR}/{split_name}/images/{img_id}.jpg"
            lbl_path = f"{DATASET_DIR}/{split_name}/labels/{img_id}.txt"

            # Create realistic tyre image canvas (dark rubber texture + tread grooves)
            img = Image.new('RGB', img_size, color=(40, 42, 45))
            draw = ImageDraw.Draw(img)

            # Draw tyre tread pattern
            for y in range(0, 640, 40):
                draw.rectangle([50, y, 590, y + 20], fill=(25, 27, 30))

            cls_id = random.choice([0, 1, 2, 3]) # crack, cut, normal, puncture
            annotations = []

            if cls_id != 2: # If not 'normal', add damage defect bbox
                # Random bounding box [center_x, center_y, width, height] normalized
                cx = random.uniform(0.25, 0.75)
                cy = random.uniform(0.25, 0.75)
                w = random.uniform(0.15, 0.35)
                h = random.uniform(0.15, 0.35)

                # Draw visual defect feature
                x1 = int((cx - w / 2) * 640)
                y1 = int((cy - h / 2) * 640)
                x2 = int((cx + w / 2) * 640)
                y2 = int((cy + h / 2) * 640)

                if cls_id == 0: # Crack
                    draw.line([x1, y1, x2, y2], fill=(180, 120, 70), width=4)
                elif cls_id == 1: # Cut
                    draw.polygon([(x1, y1), (x2, y1 + 10), (x2 - 10, y2), (x1, y2 - 10)], fill=(200, 50, 50))
                elif cls_id == 3: # Puncture
                    draw.ellipse([x1, y1, x2, y2], fill=(150, 150, 50))

                annotations.append(f"{cls_id} {cx:.6f} {cy:.6f} {w:.6f} {h:.6f}")

            # Save image
            img.save(img_path, quality=95)

            # Save YOLO label file
            with open(lbl_path, 'w') as f:
                f.write('\n'.join(annotations))

            total_generated += 1

    print(f"[Dataset] Successfully generated {total_generated} annotated samples across train/val/test splits.")

if __name__ == "__main__":
    create_yolo_dataset_structure()
    generate_synthetic_annotated_samples()
