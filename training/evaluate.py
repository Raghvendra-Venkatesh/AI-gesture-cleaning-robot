from __future__ import annotations

import argparse
import json
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import classification_report, confusion_matrix

from training.dataset import load_xy


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate a trained gesture classifier.")
    parser.add_argument("--model-path", default="models/gesture_model.joblib")
    parser.add_argument("--test-dir", default="ann_test")
    parser.add_argument("--include-no-gesture", action="store_true")
    parser.add_argument("--report-dir", default="reports")
    args = parser.parse_args()

    artifact = joblib.load(args.model_path)
    model = artifact["model"]
    encoder = artifact["label_encoder"]
    class_names = encoder.classes_.tolist()

    x, y, _ = load_xy(args.test_dir, include_no_gesture=args.include_no_gesture)
    y_true = encoder.transform(y)
    y_pred = model.predict(x)

    report = classification_report(y_true, y_pred, target_names=class_names, output_dict=True, digits=4)
    print(classification_report(y_true, y_pred, target_names=class_names, digits=4))

    report_dir = Path(args.report_dir)
    report_dir.mkdir(parents=True, exist_ok=True)
    (report_dir / "evaluation_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    matrix = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(13, 10))
    sns.heatmap(matrix, xticklabels=class_names, yticklabels=class_names, cmap="Blues", cbar=False)
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.tight_layout()
    plt.savefig(report_dir / "confusion_matrix.png", dpi=180)
    print(f"Wrote {report_dir / 'evaluation_report.json'}")
    print(f"Wrote {report_dir / 'confusion_matrix.png'}")


if __name__ == "__main__":
    main()
