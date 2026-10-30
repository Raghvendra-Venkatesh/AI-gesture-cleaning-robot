from __future__ import annotations

import argparse
import shutil
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Train a YOLOv8 gesture detector.")
    parser.add_argument("--data", default="dataset/data.yaml")
    parser.add_argument("--model", default="yolov8n.pt")
    parser.add_argument("--epochs", type=int, default=40)
    parser.add_argument("--imgsz", type=int, default=416)
    parser.add_argument("--batch", type=int, default=8)
    parser.add_argument("--project", default="runs")
    parser.add_argument("--name", default="gesture_yolov8")
    parser.add_argument("--device", default=None, help="Use 0 for NVIDIA GPU, cpu for CPU, or omit for auto.")
    parser.add_argument("--output", default="models/yolo_gesture_best.pt")
    args = parser.parse_args()

    from ultralytics import YOLO

    model = YOLO(args.model)
    train_kwargs = {
        "data": args.data,
        "epochs": args.epochs,
        "imgsz": args.imgsz,
        "batch": args.batch,
        "project": args.project,
        "name": args.name,
        "exist_ok": True,
    }
    if args.device:
        train_kwargs["device"] = args.device

    results = model.train(**train_kwargs)
    best = Path(results.save_dir) / "weights" / "best.pt"
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(best, output)
    print(f"Saved best model to {output}")


if __name__ == "__main__":
    main()
