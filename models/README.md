# Models

The runtime uses the included YOLO gesture detector at `models/yolo_gesture_best.pt`.
It is tracked in Git so a clone can run the camera application without training first.

To retrain the YOLO model from the repository root:

```powershell
python -m training.train_yolo --data dataset/data.yaml --epochs 40
```

Training outputs and intermediate weights under `runs/` are excluded from Git.
