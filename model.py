from ultralytics import YOLO
from utils.calorie import calculate_calories

# Load trained model
model = YOLO("best.pt")

def detect_food(image_path, conf=0.25, max_det=10):
    results = model(image_path, conf=conf, max_det=max_det)

    detections = []

    for r in results:
        boxes = r.boxes
        for box in boxes:
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])

            label = model.names[cls_id]

            detections.append({
                "food": label,
                "confidence": round(conf, 2)
            })

    return detections


# Test
if __name__ == "__main__":
    result = detect_food("test4.jpg", conf=0.1)
    total_calories, details = calculate_calories(result)

    print("Detections:")
    print(result)
    print(f"Total calories: {total_calories} kcal")
    print("Calorie details:")
    print(details)