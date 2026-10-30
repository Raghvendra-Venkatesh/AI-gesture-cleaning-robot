from __future__ import annotations

import argparse
import json
from pathlib import Path

import joblib
import numpy as np
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.svm import LinearSVC, SVC

from training.dataset import load_xy


def build_model(kind: str):
    if kind == "svc":
        return make_pipeline(StandardScaler(), SVC(kernel="rbf", C=10, gamma="scale", probability=True))
    if kind == "linear_svc":
        base = make_pipeline(StandardScaler(), LinearSVC(C=1.0, dual="auto", max_iter=5000))
        return CalibratedClassifierCV(base, cv=3)
    if kind == "rf":
        return RandomForestClassifier(n_estimators=250, random_state=42, n_jobs=-1)
    if kind == "logreg":
        return make_pipeline(StandardScaler(), LogisticRegression(max_iter=3000, n_jobs=-1))
    raise ValueError(f"Unsupported model kind: {kind}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Train a landmark-based gesture classifier.")
    parser.add_argument("--train-dir", default="ann_train_val")
    parser.add_argument("--output", default="models/gesture_model.joblib")
    parser.add_argument("--model", choices=["svc", "linear_svc", "rf", "logreg"], default="linear_svc")
    parser.add_argument("--include-no-gesture", action="store_true")
    parser.add_argument("--validation-size", type=float, default=0.15)
    parser.add_argument("--max-samples", type=int, default=0, help="Optional cap for quick experiments.")
    args = parser.parse_args()

    x, y, _ = load_xy(args.train_dir, include_no_gesture=args.include_no_gesture)
    if args.max_samples and args.max_samples < len(y):
        rng = np.random.default_rng(42)
        idx = rng.choice(len(y), size=args.max_samples, replace=False)
        x = x[idx]
        y = y[idx]

    encoder = LabelEncoder()
    y_encoded = encoder.fit_transform(y)

    x_train, x_val, y_train, y_val = train_test_split(
        x,
        y_encoded,
        test_size=args.validation_size,
        random_state=42,
        stratify=y_encoded,
    )

    model = build_model(args.model)
    model.fit(x_train, y_train)
    pred = model.predict(x_val)
    class_names = encoder.classes_.tolist()
    print(classification_report(y_val, pred, target_names=class_names, digits=4))

    artifact = {
        "model": model,
        "label_encoder": encoder,
        "classes": class_names,
        "feature_type": "normalized_21x2_landmarks",
        "model_kind": args.model,
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(artifact, output)

    metadata = {
        "classes": class_names,
        "feature_type": artifact["feature_type"],
        "model_kind": args.model,
        "train_samples": int(len(y_train)),
        "validation_samples": int(len(y_val)),
        "include_no_gesture": args.include_no_gesture,
    }
    output.with_suffix(".json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(f"Saved model to {output}")


if __name__ == "__main__":
    main()
