# Food Calorie and Health Tracker

Streamlit app + YOLOv8 food detector that:

- Detects food from uploaded image(s)
- Estimates calories per detected item
- Uses BMI, goal weight, and timeline to compute adjusted calorie targets
- Scores meal health against adjusted per-meal calorie goals

## Features

- Multi-image upload and per-image detection
- Uniform image preview grid
- Single top prediction per image (confidence-controlled)
- Calorie aggregation for meal total
- BMI category and TDEE calculation
- Goal-weight planning with timeline-based calorie adjustment
- Health score based on adjusted daily plan split across meal types

## Project Structure

- `app.py`: Streamlit UI
- `model.py`: YOLO inference wrapper
- `utils/calorie.py`: calorie database + calorie aggregation
- `utils/bmi.py`: BMI, TDEE, goal planning, and health scoring
- `convert.py`: dataset conversion to YOLO format
- `clean_dataset.py`: class-folder filtering utilities
- `data.yaml`: YOLO dataset config

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Make sure trained weights exist (example):

- `runs/detect/train/weights/best.pt`

## Run App

```bash
streamlit run app.py
```

## Train Detector

Fresh train:

```bash
yolo detect train data=data.yaml model=yolo26n.pt epochs=40 imgsz=640 batch=16 device=0 workers=4
```

Continue from previous weights:

```bash
yolo detect train model=runs/detect/train/weights/last.pt epochs=40 imgsz=640 batch=16 device=0 workers=4
```

## Predict

```bash
yolo detect predict model=runs/detect/train/weights/best.pt source=test.jpg conf=0.25
```

## Notes

- This repo ignores local datasets, runs, virtual environments, and weight files in `.gitignore`.
- Calorie values are approximations and should not be treated as medical advice.
