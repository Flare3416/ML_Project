import random
from pathlib import Path

import cv2

DATASET_PATH = Path("UECFOOD256")
OUTPUT_PATH = Path("dataset")
TRAIN_RATIO = 0.8
SEED = 42


def convert_bbox(img_w, img_h, x1, y1, x2, y2):
    x_center = ((x1 + x2) / 2.0) / img_w
    y_center = ((y1 + y2) / 2.0) / img_h
    width = (x2 - x1) / img_w
    height = (y2 - y1) / img_h
    return x_center, y_center, width, height


def get_numeric_class_dirs(dataset_path: Path):
    dirs = [p for p in dataset_path.iterdir() if p.is_dir() and p.name.isdigit()]
    return sorted(dirs, key=lambda p: int(p.name))


def sanitize_bbox(img_w, img_h, x1, y1, x2, y2):
    x_min = max(0, min(x1, x2))
    y_min = max(0, min(y1, y2))
    x_max = min(img_w - 1, max(x1, x2))
    y_max = min(img_h - 1, max(y1, y2))

    if x_max <= x_min or y_max <= y_min:
        return None

    return convert_bbox(img_w, img_h, x_min, y_min, x_max, y_max)


for split in ["train", "val"]:
    (OUTPUT_PATH / "images" / split).mkdir(parents=True, exist_ok=True)
    (OUTPUT_PATH / "labels" / split).mkdir(parents=True, exist_ok=True)

rng = random.Random(SEED)
class_dirs = get_numeric_class_dirs(DATASET_PATH)

if not class_dirs:
    raise FileNotFoundError(f"No numeric class folders found in {DATASET_PATH}")

total_written = 0

for class_id, folder_path in enumerate(class_dirs):
    bb_file = folder_path / "bb_info.txt"
    if not bb_file.exists():
        continue

    with open(bb_file, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    rng.shuffle(lines)

    split_idx = int(len(lines) * TRAIN_RATIO)
    train_lines = lines[:split_idx]
    val_lines = lines[split_idx:]

    for split, split_lines in [("train", train_lines), ("val", val_lines)]:
        for line in split_lines:
            parts = line.split()
            if len(parts) < 5:
                continue

            img_name = parts[0]
            if "." not in img_name:
                img_name = f"{img_name}.jpg"

            try:
                x1, y1, x2, y2 = map(int, parts[1:5])
            except ValueError:
                continue

            img_path = folder_path / img_name
            img = cv2.imread(str(img_path))
            if img is None:
                continue

            h, w = img.shape[:2]
            bbox = sanitize_bbox(w, h, x1, y1, x2, y2)
            if bbox is None:
                continue

            x, y, bw, bh = bbox

            stem = Path(img_name).stem
            suffix = Path(img_name).suffix or ".jpg"
            new_stem = f"{folder_path.name}_{stem}"
            new_name = f"{new_stem}{suffix}"

            out_img = OUTPUT_PATH / "images" / split / new_name
            out_label = OUTPUT_PATH / "labels" / split / f"{new_stem}.txt"

            cv2.imwrite(str(out_img), img)

            with open(out_label, "w", encoding="utf-8") as f:
                f.write(f"{class_id} {x:.6f} {y:.6f} {bw:.6f} {bh:.6f}")

            total_written += 1

print(f"Conversion complete. Wrote {total_written} labeled images.")