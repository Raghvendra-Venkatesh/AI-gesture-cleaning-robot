# Dataset

This workspace contains a YOLO-format hand-gesture object-detection dataset:

- `train/images/` and `train/labels/`
- `valid/images/` and `valid/labels/`
- `test/images/` and `test/labels/`

The class names and split paths are in `data.yaml`. The seven classes are `Down`, `Left`, `Right`, `Stop`, `Thumbs Down`, `Thumbs up`, and `Up`. Keep the test split out of training and use it only for final evaluation.

The runtime loads `models/yolo_gesture_best.pt`, trained for these classes. Retrain from the repository root with `python -m training.train_yolo --data dataset/data.yaml`, then evaluate with `python -m training.evaluate_yolo --data dataset/data.yaml --split test`.
