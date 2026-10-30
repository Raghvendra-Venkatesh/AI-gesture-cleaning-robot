from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate the trained YOLO gesture detector.")
    parser.add_argument("--model", default="models/yolo_gesture_best.pt")
    parser.add_argument("--data", default="dataset/data.yaml")
    parser.add_argument("--split", default="test", choices=["val", "test"])
    parser.add_argument("--output", default="reports/yolo_evaluation.json")
    args = parser.parse_args()

    from ultralytics import YOLO

    model = YOLO(args.model)
    metrics = model.val(data=args.data, split=args.split)
    summary = {
        "box_map50": float(metrics.box.map50),
        "box_map50_95": float(metrics.box.map),
        "precision_mean": float(metrics.box.mp),
        "recall_mean": float(metrics.box.mr),
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    print(f"Wrote {output}")


if __name__ == "__main__":
    main()
