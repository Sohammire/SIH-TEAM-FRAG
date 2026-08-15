import os
import glob
import sys
import io
import random
import yaml
from PIL import Image, ImageDraw, ImageFont

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

DATASET_DIR = "d:/sihh2/SIH-TEAM-FRAG/backend/data/tire_damage"
OUTPUT_VIS_DIR = "d:/sihh2/SIH-TEAM-FRAG/backend/runs/tire_damage_vis"

CLASS_COLORS = {
    0: (255, 165, 0),  # crack -> Orange
    1: (255, 0, 0),    # cut -> Red
    2: (0, 255, 0),    # normal -> Green
    3: (255, 255, 0)   # puncture -> Yellow
}

def visualize_dataset_samples(num_samples=6):
    """
    Randomly selects dataset images, overlay bounding boxes with class names,
    and saves sample preview grid.
    """
    os.makedirs(OUTPUT_VIS_DIR, exist_ok=True)
    yaml_path = os.path.join(DATASET_DIR, "dataset.yaml")

    with open(yaml_path, 'r') as f:
        ds_config = yaml.safe_load(f)

    class_names = ds_config.get('names', {})

    img_files = glob.glob(os.path.join(DATASET_DIR, "train", "images", "*.jpg"))
    if not img_files:
        print("No images found for visualization.")
        return

    sampled_files = random.sample(img_files, min(num_samples, len(img_files)))
    print(f"[Visualization] Sampling {len(sampled_files)} dataset images...")

    for idx, img_path in enumerate(sampled_files):
        img = Image.open(img_path).convert('RGB')
        w_img, h_img = img.size
        draw = ImageDraw.Draw(img)

        lbl_path = img_path.replace("images", "labels").replace(".jpg", ".txt")
        if os.path.exists(lbl_path):
            with open(lbl_path, 'r') as f:
                lines = f.readlines()

            for line in lines:
                parts = line.strip().split()
                if len(parts) == 5:
                    cls_id = int(parts[0])
                    cx, cy, w, h = map(float, parts[1:])

                    # Convert YOLO normalized bbox to pixel coordinates
                    x1 = int((cx - w / 2) * w_img)
                    y1 = int((cy - h / 2) * h_img)
                    x2 = int((cx + w / 2) * w_img)
                    y2 = int((cy + h / 2) * h_img)

                    cls_name = class_names.get(cls_id, f"cls_{cls_id}")
                    color = CLASS_COLORS.get(cls_id, (255, 255, 255))

                    # Draw Bounding Box
                    draw.rectangle([x1, y1, x2, y2], outline=color, width=3)
                    draw.rectangle([x1, max(0, y1 - 18), x1 + len(cls_name) * 10 + 10, y1], fill=color)
                    draw.text((x1 + 4, max(0, y1 - 16)), cls_name, fill=(0, 0, 0))

        out_path = os.path.join(OUTPUT_VIS_DIR, f"sample_{idx+1}.jpg")
        img.save(out_path)
        print(f"  * Saved visualization preview: {out_path}")

    print(f"SUCCESS - Dataset visualizations saved to {OUTPUT_VIS_DIR}")

if __name__ == "__main__":
    visualize_dataset_samples()
