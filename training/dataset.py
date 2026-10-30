from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Iterable

import numpy as np


GESTURE_NONE = "no_gesture"


def annotation_files(split_dir: str | Path) -> list[Path]:
    return sorted(Path(split_dir).glob("*.json"))


def normalize_landmarks(coords: Iterable[Iterable[float]]) -> np.ndarray:
    points = np.asarray(list(coords), dtype=np.float32)
    if points.shape != (21, 2):
        raise ValueError(f"Expected 21x2 landmarks, got {points.shape}")

    wrist = points[0].copy()
    points = points - wrist
    scale = np.linalg.norm(points, axis=1).max()
    if scale > 0:
        points = points / scale
    return points.reshape(-1)


def iter_samples(split_dir: str | Path, include_no_gesture: bool = False):
    for file_path in annotation_files(split_dir):
        with file_path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        for sample_id, sample in data.items():
            labels = sample.get("labels") or []
            landmarks = sample.get("landmarks") or []
            if not labels or not landmarks:
                continue

            for idx, label in enumerate(labels):
                if label == GESTURE_NONE and not include_no_gesture:
                    continue
                if idx >= len(landmarks):
                    continue
                try:
                    features = normalize_landmarks(landmarks[idx])
                except (TypeError, ValueError):
                    continue
                yield {
                    "sample_id": sample_id,
                    "source_file": file_path.name,
                    "label": label,
                    "features": features,
                    "leading_hand": sample.get("leading_hand"),
                    "leading_conf": sample.get("leading_conf"),
                    "user_id": sample.get("user_id"),
                }


def load_xy(split_dir: str | Path, include_no_gesture: bool = False):
    rows = list(iter_samples(split_dir, include_no_gesture=include_no_gesture))
    if not rows:
        raise ValueError(f"No valid landmark samples found in {split_dir}")
    x = np.stack([row["features"] for row in rows])
    y = np.asarray([row["label"] for row in rows])
    return x, y, rows


def count_labels(split_dir: str | Path) -> Counter:
    counts = Counter()
    for row in iter_samples(split_dir, include_no_gesture=True):
        counts[row["label"]] += 1
    return counts
